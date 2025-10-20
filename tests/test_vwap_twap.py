"""Tests for VWAP/TWAP strategy calculations."""

import pytest
from src.strategies.vwap_twap import (
    calculate_vwap,
    calculate_twap,
    get_twap_slices,
    RollingVWAP,
)


class TestVWAP:
    """Test VWAP calculations."""

    def test_calculate_vwap_basic(self):
        """Test basic VWAP calculation."""
        prices = [100.0, 101.0, 102.0]
        volumes = [1000, 1500, 2000]
        
        vwap = calculate_vwap(prices, volumes)
        
        # Expected: (100*1000 + 101*1500 + 102*2000) / (1000+1500+2000)
        expected = (100000 + 151500 + 204000) / 4500
        assert abs(vwap - expected) < 0.01

    def test_calculate_vwap_zero_volume(self):
        """Test VWAP with zero total volume raises error."""
        prices = [100.0, 101.0]
        volumes = [0, 0]
        
        with pytest.raises(ValueError, match="Total volume cannot be zero"):
            calculate_vwap(prices, volumes)

    def test_calculate_vwap_mismatched_length(self):
        """Test VWAP with mismatched arrays raises error."""
        prices = [100.0, 101.0]
        volumes = [1000]
        
        with pytest.raises(ValueError, match="same length"):
            calculate_vwap(prices, volumes)

    def test_rolling_vwap(self):
        """Test rolling VWAP calculator."""
        rolling = RollingVWAP(window_size=3)
        
        rolling.add(100.0, 1000)
        rolling.add(101.0, 1500)
        rolling.add(102.0, 2000)
        
        assert rolling.is_ready()
        vwap = rolling.get_vwap()
        expected = (100*1000 + 101*1500 + 102*2000) / 4500
        assert abs(vwap - expected) < 0.01

    def test_rolling_vwap_window_overflow(self):
        """Test rolling VWAP removes oldest values."""
        rolling = RollingVWAP(window_size=2)
        
        rolling.add(100.0, 1000)
        rolling.add(101.0, 1000)
        rolling.add(102.0, 1000)  # Should remove 100.0
        
        vwap = rolling.get_vwap()
        expected = (101*1000 + 102*1000) / 2000
        assert abs(vwap - expected) < 0.01


class TestTWAP:
    """Test TWAP calculations."""

    def test_calculate_twap_basic(self):
        """Test basic TWAP calculation."""
        prices = [100.0, 101.0, 102.0]
        
        twap = calculate_twap(prices)
        
        expected = (100 + 101 + 102) / 3
        assert abs(twap - expected) < 0.01

    def test_calculate_twap_empty(self):
        """Test TWAP with empty list raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            calculate_twap([])

    def test_get_twap_slices_even(self):
        """Test TWAP slicing with even division."""
        slices = get_twap_slices(100, 10)
        
        assert len(slices) == 10
        assert sum(slices) == 100
        assert all(s == 10 for s in slices)

    def test_get_twap_slices_remainder(self):
        """Test TWAP slicing with remainder."""
        slices = get_twap_slices(105, 10)
        
        assert len(slices) == 10
        assert sum(slices) == 105
        # First 5 should have remainder distributed
        assert slices[0] == 11
        assert slices[4] == 11
        assert slices[5] == 10

    def test_get_twap_slices_invalid_quantity(self):
        """Test TWAP slicing with invalid quantity."""
        with pytest.raises(ValueError, match="must be positive"):
            get_twap_slices(0, 10)

    def test_get_twap_slices_invalid_num_slices(self):
        """Test TWAP slicing with invalid num_slices."""
        with pytest.raises(ValueError, match="must be positive"):
            get_twap_slices(100, 0)

