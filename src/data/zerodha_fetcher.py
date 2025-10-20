"""
Zerodha Kite API data fetcher with LEAN export support.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional
import pandas as pd
from kiteconnect import KiteConnect
import structlog

from backend.core.config import settings

logger = structlog.get_logger()


class ZerodhaDataFetcher:
    """Fetch historical data from Zerodha Kite API and export to LEAN format."""
    
    # NSE instrument tokens (symbol: token)
    INSTRUMENTS = {
        "RELIANCE": 738561,
        "TCS": 2953217,
        "INFY": 408065,
        "HDFC": 340481,
    }
    
    def __init__(self):
        """Initialize Kite Connect client."""
        self.api_key = settings.KITE_API_KEY
        self.access_token = settings.KITE_ACCESS_TOKEN
        
        if self.api_key and self.access_token:
            self.kite = KiteConnect(api_key=self.api_key)
            self.kite.set_access_token(self.access_token)
            logger.info("Zerodha Kite API initialized")
        else:
            self.kite = None
            logger.warning("Zerodha API credentials not configured")
    
    def fetch_for_symbol(
        self,
        symbol: str,
        from_date: datetime,
        to_date: datetime,
        interval: str = "minute",
    ) -> pd.DataFrame:
        """
        Fetch historical data for a symbol.
        
        Args:
            symbol: Symbol name (e.g., "RELIANCE")
            from_date: Start date
            to_date: End date
            interval: Data interval ("minute", "5minute", "day")
            
        Returns:
            DataFrame with columns: open, high, low, close, volume
        """
        if not self.kite:
            raise ValueError("Zerodha API not configured")
        
        # Get instrument token
        instrument_token = self.INSTRUMENTS.get(symbol.upper())
        if not instrument_token:
            raise ValueError(f"Symbol {symbol} not found")
        
        logger.info("Fetching historical data", symbol=symbol)
        
        try:
            data = self.kite.historical_data(
                instrument_token=instrument_token,
                from_date=from_date,
                to_date=to_date,
                interval=interval,
            )
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df = df[['open', 'high', 'low', 'close', 'volume']]
            
            logger.info("Data fetched", rows=len(df))
            return df
            
        except Exception as e:
            logger.error("Failed to fetch data", error=str(e))
            raise
    
    def export_to_lean_format(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Export DataFrame to LEAN CSV format.
        
        LEAN Format:
        Date,Open,High,Low,Close,Volume
        20241020 09:15,2244.50,2246.00,2244.00,2245.50,125000
        """
        lean_df = df.copy()
        lean_df.index = lean_df.index.strftime('%Y%m%d %H:%M')
        lean_df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        lean_df.insert(0, 'Date', lean_df.index)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        lean_df.to_csv(output_path, index=False)
        
        logger.info("Exported to LEAN format", path=output_path)
