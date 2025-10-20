#!/usr/bin/env python3
"""
Fetch historical data from Zerodha and export to LEAN format.

Usage:
    python3 scripts/fetch_data.py --symbol RELIANCE --from 2024-10-20 --to 2024-10-21
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.zerodha_fetcher import ZerodhaDataFetcher


def main():
    parser = argparse.ArgumentParser(description="Fetch Zerodha data for LEAN")
    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="Stock symbol (e.g., RELIANCE)",
    )
    parser.add_argument(
        "--from",
        dest="from_date",
        type=str,
        required=True,
        help="Start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--to",
        dest="to_date",
        type=str,
        required=True,
        help="End date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--interval",
        type=str,
        default="minute",
        choices=["minute", "day"],
        help="Data interval (default: minute)",
    )
    
    args = parser.parse_args()
    
    # Parse dates
    try:
        from_date = datetime.strptime(args.from_date, "%Y-%m-%d")
        to_date = datetime.strptime(args.to_date, "%Y-%m-%d")
    except ValueError as e:
        print(f"❌ Error parsing dates: {e}")
        print("   Use format: YYYY-MM-DD")
        sys.exit(1)
    
    print(f"📡 Fetching {args.symbol} data from Zerodha...")
    print(f"   Period: {from_date.date()} to {to_date.date()}")
    print(f"   Interval: {args.interval}")
    print()
    
    try:
        # Initialize fetcher
        fetcher = ZerodhaDataFetcher()
        
        # Fetch data
        print("⏳ Downloading data...")
        df = fetcher.fetch_for_symbol(
            symbol=args.symbol,
            from_date=from_date,
            to_date=to_date,
            interval=args.interval,
        )
        
        if df.empty:
            print("❌ No data fetched! Check:")
            print("   1. Your Zerodha API credentials in .env")
            print("   2. Symbol name is correct")
            print("   3. Date range is valid (market days)")
            sys.exit(1)
        
        print(f"✅ Fetched {len(df)} records")
        print()
        
        # Export to LEAN format
        symbol_lower = args.symbol.lower()
        start_date_str = from_date.strftime("%Y%m%d")
        
        lean_data_path = Path(f"lean/Data/equity/nse/{args.interval}/{symbol_lower}/{start_date_str}_trade.csv")
        
        print(f"💾 Exporting to LEAN format: {lean_data_path}")
        fetcher.export_to_lean_format(df, lean_data_path)
        
        print("✅ Data export complete!")
        print()
        print("📊 Summary:")
        print(f"   Records: {len(df)}")
        print(f"   Period: {df.index[0]} to {df.index[-1]}")
        print(f"   LEAN file: {lean_data_path}")
        print()
        print("🚀 You can now run a backtest!")
        print()
        print("Example:")
        print(f'''
curl -X POST http://localhost:8000/api/backtest/run \\
  -H "Content-Type: application/json" \\
  -d '{{
    "symbol": "{args.symbol}",
    "start_date": "{args.from_date}",
    "end_date": "{args.to_date}",
    "vwap_window": 50,
    "twap_slices": 5,
    "order_size": 10,
    "initial_capital": 100000
  }}'
''')
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Make sure you have a .env file with:")
        print("   KITE_API_KEY=your_key_here")
        print("   KITE_API_SECRET=your_secret_here")
        print("   KITE_ACCESS_TOKEN=your_token_here")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

