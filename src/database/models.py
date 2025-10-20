"""
Database models for trades, backtest runs, and strategy configurations.

Uses SQLAlchemy ORM for persistence and audit trail compliance.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class BacktestRun(Base):
    """Backtest execution record."""

    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(50), unique=True, index=True, nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    # Strategy parameters
    vwap_window = Column(Integer, nullable=False)
    twap_slices = Column(Integer, nullable=False)
    order_size = Column(Integer, nullable=False)
    initial_capital = Column(Float, nullable=False)
    
    # Results
    sharpe_ratio = Column(Float)
    total_return = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)
    total_trades = Column(Integer, default=0)
    
    # Status
    status = Column(
        String(20),
        nullable=False,
        default="pending"
    )  # pending, running, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    trades = relationship("Trade", back_populates="backtest_run", cascade="all, delete-orphan")
    equity_curve = relationship(
        "EquityPoint",
        back_populates="backtest_run",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<BacktestRun(run_id={self.run_id}, symbol={self.symbol}, status={self.status})>"


class Trade(Base):
    """Individual trade record for audit trail."""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    backtest_run_id = Column(Integer, ForeignKey("backtest_runs.id"), nullable=False, index=True)
    
    # Trade details
    timestamp = Column(DateTime, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    trade_type = Column(String(20), nullable=False)  # VWAP_BUY, VWAP_SELL, TWAP_BUY, TWAP_SELL
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    # P&L
    pnl = Column(Float, default=0.0)
    commission = Column(Float, default=0.0)
    
    # Order execution details
    order_id = Column(String(50))
    fill_time = Column(DateTime)
    
    # Compliance tracking
    ops_at_time = Column(Integer)  # Orders per second counter at time of trade
    
    # Relationships
    backtest_run = relationship("BacktestRun", back_populates="trades")

    def __repr__(self):
        return f"<Trade(symbol={self.symbol}, type={self.trade_type}, qty={self.quantity}, price={self.price})>"


class EquityPoint(Base):
    """Equity curve data point."""

    __tablename__ = "equity_points"

    id = Column(Integer, primary_key=True, index=True)
    backtest_run_id = Column(Integer, ForeignKey("backtest_runs.id"), nullable=False, index=True)
    
    timestamp = Column(DateTime, nullable=False)
    portfolio_value = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    holdings_value = Column(Float, nullable=False)
    
    # Relationships
    backtest_run = relationship("BacktestRun", back_populates="equity_curve")

    def __repr__(self):
        return f"<EquityPoint(value={self.portfolio_value}, timestamp={self.timestamp})>"


class StrategyConfig(Base):
    """Stored strategy configurations."""

    __tablename__ = "strategy_configs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    
    # VWAP/TWAP parameters
    vwap_window = Column(Integer, nullable=False, default=100)
    twap_slices = Column(Integer, nullable=False, default=10)
    order_size = Column(Integer, nullable=False, default=10)
    
    # Risk controls
    drawdown_threshold = Column(Float, nullable=False, default=0.05)
    ops_limit = Column(Integer, nullable=False, default=10)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<StrategyConfig(name={self.name}, vwap_window={self.vwap_window})>"


class LiveTradingSession(Base):
    """Live trading session tracking."""

    __tablename__ = "live_trading_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Session details
    symbol = Column(String(20), nullable=False)
    mode = Column(String(10), nullable=False)  # paper, live
    
    # Strategy parameters
    vwap_window = Column(Integer, nullable=False)
    twap_slices = Column(Integer, nullable=False)
    order_size = Column(Integer, nullable=False)
    
    # Session state
    status = Column(String(20), nullable=False)  # active, stopped, error
    initial_capital = Column(Float, nullable=False)
    current_value = Column(Float)
    peak_value = Column(Float)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    stopped_at = Column(DateTime)
    
    # Kill switch tracking
    kill_switch_triggered = Column(Boolean, default=False)
    kill_switch_reason = Column(String(200))
    
    def __repr__(self):
        return f"<LiveTradingSession(session_id={self.session_id}, status={self.status})>"

