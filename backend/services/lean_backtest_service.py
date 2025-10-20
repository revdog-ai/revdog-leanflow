"""
LEAN Backtest Service - Bridge between FastAPI and LEAN Engine.
Executes backtests using LEAN Docker container.
"""

import uuid
import json
import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import structlog

from src.database.connection import get_db_session
from src.database.models import BacktestRun, Trade, EquityPoint

logger = structlog.get_logger()


class LEANBacktestService:
    """Execute backtests using LEAN engine via Docker."""
    
    def __init__(self):
        self.lean_image = "quantconnect/lean:latest"
        
        # For Docker-in-Docker, we need the HOST path (not container path)
        # This is passed via LEAN_HOST_PATH environment variable
        lean_host_path = os.getenv("LEAN_HOST_PATH")
        if not lean_host_path:
            # Fallback to relative path (works when not in Docker)
            lean_host_path = str(Path("./lean").resolve())
        
        self.lean_host_dir = Path(lean_host_path)
        self.lean_dir = Path("./lean")  # Container path for local file operations
        self.config_dir = self.lean_dir / "Config"
        self.results_dir = self.lean_dir / "Results"
        self.algorithm_file = "RevDogLeanFlow.py"
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    async def run_backtest(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        vwap_window: int,
        twap_slices: int,
        order_size: int,
        initial_capital: float,
    ) -> str:
        """Execute backtest using LEAN engine and return run_id."""
        run_id = f"lean_{uuid.uuid4().hex[:12]}"
        
        logger.info("Starting LEAN backtest", run_id=run_id, symbol=symbol)
        
        db = get_db_session()
        try:
            # 1. Create database record
            backtest_run = BacktestRun(
                run_id=run_id,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                vwap_window=vwap_window,
                twap_slices=twap_slices,
                order_size=order_size,
                initial_capital=initial_capital,
                status="running",
                started_at=datetime.utcnow(),
            )
            db.add(backtest_run)
            db.commit()
            
            # 2. Generate LEAN config
            config_path = self._generate_config(
                run_id=run_id,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                vwap_window=vwap_window,
                twap_slices=twap_slices,
                order_size=order_size,
                initial_capital=initial_capital,
            )
            
            # 3. Run LEAN engine via Docker
            self._run_lean_docker(config_path, run_id)
            
            # 4. Parse results and update database
            self._parse_lean_results(db, backtest_run, run_id)
            
            logger.info("LEAN backtest completed", run_id=run_id)
            return run_id
            
        except Exception as e:
            logger.error("LEAN backtest failed", error=str(e), run_id=run_id)
            if backtest_run:
                backtest_run.status = "failed"
                db.commit()
            raise
        finally:
            db.close()
    
    def _generate_config(
        self,
        run_id: str,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        vwap_window: int,
        twap_slices: int,
        order_size: int,
        initial_capital: float,
    ) -> Path:
        """Generate LEAN config.json for this backtest."""
        
        config = {
            "environment": "backtesting",
            "algorithm-type-name": "RevDogLeanFlow",
            "algorithm-language": "Python",
            "algorithm-location": f"/Lean/Algorithm.Python/{self.algorithm_file}",
            "data-folder": "/Lean/Data",
            "results-destination-folder": f"/Lean/Results/{run_id}",
            "parameters": {
                "vwap-window-size": str(vwap_window),
                "twap-slices": str(twap_slices),
                "order-size": str(order_size),
            },
            "job-user-id": "1",
            "api-access-token": "",
            "job-project-id": "1",
        }
        
        config_path = self.config_dir / f"config_{run_id}.json"
        config_path.write_text(json.dumps(config, indent=2))
        
        logger.info("Generated LEAN config", config_path=str(config_path))
        return config_path
    
    def _run_lean_docker(self, config_path: Path, run_id: str):
        """Run LEAN engine in Docker container."""
        
        logger.info("Launching LEAN Docker container", run_id=run_id)
        
        # Use the HOST path for Docker mount (not container path)
        # This is crucial for Docker-in-Docker to work
        lean_host_path_abs = self.lean_host_dir.resolve()
        
        logger.info("LEAN paths", 
                   host_path=str(lean_host_path_abs),
                   container_path=str(self.lean_dir))
        
        # Docker run command
        # QuantConnect LEAN image has built-in entrypoint
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{lean_host_path_abs}:/Lean",
            self.lean_image,
            "--config", f"/Lean/Config/{config_path.name}",
            "--algorithm-location", "/Lean/Algorithm.Python",
        ]
        
        logger.debug("Docker command", cmd=" ".join(cmd))
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,  # 1 hour max
        )
        
        if result.returncode != 0:
            logger.error("LEAN Docker failed", 
                        returncode=result.returncode,
                        stdout=result.stdout,
                        stderr=result.stderr)
            raise RuntimeError(f"LEAN failed with code {result.returncode}: {result.stderr}")
        
        logger.info("LEAN Docker completed successfully", run_id=run_id)
        logger.debug("LEAN output", stdout=result.stdout[:500])  # First 500 chars
    
    def _parse_lean_results(self, db, backtest_run: BacktestRun, run_id: str):
        """Parse LEAN JSON results and store in database."""
        
        results_dir = self.results_dir / run_id
        
        # LEAN outputs results to multiple files
        # Main file is usually the algorithm name + timestamp
        result_files = list(results_dir.glob("*.json"))
        
        if not result_files:
            logger.error("No LEAN results found", run_id=run_id, path=str(results_dir))
            raise FileNotFoundError(f"LEAN results not found in {results_dir}")
        
        # Use the first JSON file (usually the main result)
        results_file = result_files[0]
        logger.info("Parsing LEAN results", file=str(results_file))
        
        with open(results_file) as f:
            lean_results = json.load(f)
        
        # Extract statistics
        stats = lean_results.get("Statistics", {})
        
        # Update backtest record
        backtest_run.sharpe_ratio = float(stats.get("Sharpe Ratio", 0))
        backtest_run.total_return = float(stats.get("Total Net Profit", "0%").replace("%", "")) / 100
        backtest_run.max_drawdown = abs(float(stats.get("Drawdown", "0%").replace("%", ""))) / 100
        backtest_run.total_trades = int(stats.get("Total Orders", 0))
        backtest_run.win_rate = float(stats.get("Win Rate", "0%").replace("%", "")) / 100
        backtest_run.status = "completed"
        backtest_run.completed_at = datetime.utcnow()
        
        # Parse orders/trades
        orders = lean_results.get("Orders", {})
        for order_id, order in orders.items():
            trade = Trade(
                backtest_run_id=backtest_run.id,
                timestamp=datetime.fromisoformat(order["Time"].replace("Z", "+00:00")),
                symbol=order["Symbol"],
                trade_type=order["Type"],
                quantity=abs(order["Quantity"]),
                price=order["Price"],
                pnl=order.get("Value", 0),
            )
            db.add(trade)
        
        # Parse equity curve
        charts = lean_results.get("Charts", {})
        equity_chart = charts.get("Strategy Equity", {})
        equity_series = equity_chart.get("Series", {}).get("Equity", {}).get("Values", [])
        
        # Sample equity points (100 max)
        sample_rate = max(1, len(equity_series) // 100)
        for i, point in enumerate(equity_series[::sample_rate]):
            equity_point = EquityPoint(
                backtest_run_id=backtest_run.id,
                timestamp=datetime.fromtimestamp(point["x"]),
                portfolio_value=point["y"],
                cash=0,  # LEAN doesn't separate this easily
                holdings_value=point["y"],
            )
            db.add(equity_point)
        
        db.commit()
        
        logger.info("LEAN results parsed and stored", 
                   run_id=run_id,
                   trades=backtest_run.total_trades,
                   sharpe=backtest_run.sharpe_ratio)
    
    async def get_results(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get backtest results from database."""
        db = get_db_session()
        try:
            backtest = db.query(BacktestRun).filter(BacktestRun.run_id == run_id).first()
            
            if not backtest:
                return None
            
            trades = db.query(Trade).filter(Trade.backtest_run_id == backtest.id).all()
            
            return {
                "run_id": backtest.run_id,
                "symbol": backtest.symbol,
                "status": backtest.status,
                "sharpe_ratio": backtest.sharpe_ratio,
                "total_return": backtest.total_return,
                "max_drawdown": backtest.max_drawdown,
                "win_rate": backtest.win_rate,
                "total_trades": backtest.total_trades,
                "trades": [
                    {
                        "timestamp": t.timestamp.isoformat(),
                        "symbol": t.symbol,
                        "type": t.trade_type,
                        "quantity": t.quantity,
                        "price": t.price,
                        "pnl": t.pnl,
                    }
                    for t in trades
                ],
            }
        finally:
            db.close()
    
    async def list_backtests(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """List backtest runs with pagination."""
        db = get_db_session()
        try:
            total = db.query(BacktestRun).count()
            backtests = db.query(BacktestRun).order_by(BacktestRun.created_at.desc()).limit(limit).offset(offset).all()
            
            return {
                "backtests": [
                    {
                        "run_id": bt.run_id,
                        "symbol": bt.symbol,
                        "status": bt.status,
                        "start_date": bt.start_date.isoformat() if bt.start_date else None,
                        "end_date": bt.end_date.isoformat() if bt.end_date else None,
                        "sharpe_ratio": bt.sharpe_ratio,
                        "total_return": bt.total_return,
                        "max_drawdown": bt.max_drawdown,
                        "total_trades": bt.total_trades,
                        "created_at": bt.created_at.isoformat() if bt.created_at else None,
                    }
                    for bt in backtests
                ],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        finally:
            db.close()
