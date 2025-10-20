"""
RevDog LeanFlow - VWAP/TWAP Algorithmic Trading Strategy
SEBI White Box Execution Algo Compliant
License: MIT

This strategy implements Volume Weighted Average Price (VWAP) and
Time Weighted Average Price (TWAP) execution algorithms for NSE equities.
"""

from AlgorithmImports import *
import time
from datetime import timedelta


class RevDogLeanFlow(QCAlgorithm):
    """
    VWAP/TWAP Trading Strategy using QuantConnect LEAN.
    
    Strategy Logic (White Box):
    1. VWAP: Buy when price < VWAP by threshold, Sell when price > VWAP
    2. TWAP: Time-sliced order execution over trading session
    3. OPS Limiter: Maximum 10 orders per second (SEBI compliance)
    4. Kill Switch: Liquidate all positions if drawdown > 5% (SEBI compliance)
    
    SEBI White Box Compliant.
    """

    def Initialize(self):
        """Initialize algorithm parameters and risk controls."""
        
        # Backtest period (1 year: Oct 20, 2024 to Oct 20, 2025)
        self.SetStartDate(2024, 10, 20)
        self.SetEndDate(2025, 10, 20)
        self.SetCash(100000)
        
        # Add RELIANCE equity (NSE)
        # Note: LEAN uses symbol "RELIANCE" for NSE stocks
        self.symbol = self.AddEquity("RELIANCE", Resolution.Minute).Symbol
        
        # VWAP parameters
        self.vwap_window_size = int(self.GetParameter("vwap-window-size", 100))
        self.vwap_window = RollingWindow[TradeBar](self.vwap_window_size)
        self.vwap_threshold = 0.02  # 2% deviation threshold
        
        # TWAP parameters
        self.twap_slices = int(self.GetParameter("twap-slices", 10))
        self.order_size = int(self.GetParameter("order-size", 10))
        self.time_interval = timedelta(minutes=375 / self.twap_slices)  # 375 min session
        self.last_twap_time = None
        
        # SEBI compliance: OPS Limiter (max 10 orders/second)
        self.ops_counter = 0
        self.last_order_time = None
        self.max_ops = 10
        
        # SEBI compliance: Kill Switch (5% drawdown)
        self.drawdown_threshold = 0.05
        self.peak_portfolio_value = self.Portfolio.TotalPortfolioValue
        
        # Logging
        self.Debug("=== RevDog LeanFlow Initialized ===")
        self.Debug(f"VWAP Window: {self.vwap_window_size}")
        self.Debug(f"TWAP Slices: {self.twap_slices}")
        self.Debug(f"Order Size: {self.order_size}")
        self.Debug(f"SEBI Compliance: OPS<{self.max_ops}, Kill Switch at {self.drawdown_threshold*100}%")

    def OnData(self, data: Slice):
        """Called for each data point (minute bars)."""
        
        # Check if we have data
        if not data.ContainsKey(self.symbol):
            return
        
        bar = data[self.symbol]
        
        # Add to VWAP rolling window
        self.vwap_window.Add(bar)
        
        # Wait for window to fill
        if not self.vwap_window.IsReady:
            return
        
        # Calculate VWAP
        total_value = sum([b.Close * b.Volume for b in self.vwap_window])
        total_volume = sum([b.Volume for b in self.vwap_window])
        vwap_price = total_value / total_volume if total_volume > 0 else bar.Close
        
        # Check OPS limit (SEBI compliance)
        if not self._check_ops_limit():
            self.Debug(f"OPS threshold exceeded, skipping order at {self.Time}")
            return
        
        # VWAP Strategy Logic
        current_price = bar.Close
        deviation = (current_price - vwap_price) / vwap_price
        
        # Generate signal based on VWAP deviation
        signal = None
        if deviation < -self.vwap_threshold:
            signal = "BUY"  # Price significantly below VWAP
        elif deviation > self.vwap_threshold:
            signal = "SELL"  # Price significantly above VWAP
        
        # Execute trade
        if signal == "BUY" and not self.Portfolio[self.symbol].Invested:
            # Buy signal and no position
            quantity = self.order_size
            self.MarketOrder(self.symbol, quantity)
            self._record_order()
            self.Debug(f"VWAP BUY: {quantity} @ {current_price:.2f} (VWAP: {vwap_price:.2f}, Dev: {deviation*100:.2f}%)")
        
        elif signal == "SELL" and self.Portfolio[self.symbol].Invested:
            # Sell signal and have position
            quantity = -self.order_size
            self.MarketOrder(self.symbol, quantity)
            self._record_order()
            self.Debug(f"VWAP SELL: {abs(quantity)} @ {current_price:.2f} (VWAP: {vwap_price:.2f}, Dev: {deviation*100:.2f}%)")
        
        # TWAP execution (time-sliced orders)
        self._execute_twap(bar)

    def OnEndOfDay(self):
        """Called at end of each trading day."""
        
        # Update peak portfolio value
        current_value = self.Portfolio.TotalPortfolioValue
        if current_value > self.peak_portfolio_value:
            self.peak_portfolio_value = current_value
        
        # Check kill switch (SEBI compliance)
        drawdown = (self.peak_portfolio_value - current_value) / self.peak_portfolio_value
        
        if drawdown >= self.drawdown_threshold:
            self.Liquidate()
            self.Debug(f"!!! KILL SWITCH ACTIVATED !!! Drawdown: {drawdown*100:.2f}%")
            self.Quit("Kill switch triggered due to excessive drawdown")
        
        # Log daily performance
        self.Debug(f"EOD: Portfolio ${current_value:.2f}, Drawdown: {drawdown*100:.2f}%, Peak: ${self.peak_portfolio_value:.2f}")

    def _check_ops_limit(self) -> bool:
        """
        Check if order placement would exceed OPS limit.
        
        Returns:
            True if order can be placed, False otherwise
        """
        current_time = time.time()
        
        # Reset counter if more than 1 second has passed
        if self.last_order_time is None or (current_time - self.last_order_time) >= 1.0:
            self.ops_counter = 0
            return True
        
        # Check if under limit
        return self.ops_counter < self.max_ops

    def _record_order(self):
        """Record that an order was placed (for OPS tracking)."""
        self.ops_counter += 1
        self.last_order_time = time.time()

    def _execute_twap(self, bar: TradeBar):
        """
        Execute TWAP sliced orders.
        
        TWAP divides total order into equal slices executed at regular intervals
        throughout the trading session.
        """
        # Check if it's time for next TWAP slice
        if self.last_twap_time is None:
            self.last_twap_time = self.Time
        
        if (self.Time - self.last_twap_time) >= self.time_interval:
            # Execute TWAP slice
            if bar.Time.hour < 15:  # Only during market hours (9:15 AM - 3:30 PM)
                slice_size = int(self.order_size / self.twap_slices)
                
                if slice_size > 0 and self.Portfolio.Cash > slice_size * bar.Close:
                    self.MarketOrder(self.symbol, slice_size)
                    self._record_order()
                    self.last_twap_time = self.Time
                    self.Debug(f"TWAP SLICE: {slice_size} @ {bar.Close:.2f}")

    def OnOrderEvent(self, orderEvent: OrderEvent):
        """Called when order status changes."""
        if orderEvent.Status == OrderStatus.Filled:
            order = self.Transactions.GetOrderById(orderEvent.OrderId)
            self.Debug(f"Order Filled: {orderEvent.Symbol} {orderEvent.FillQuantity} @ {orderEvent.FillPrice:.2f}")

