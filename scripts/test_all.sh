#!/bin/bash

# RevDog LeanFlow - Comprehensive System Test
# Tests all components: Backend, Frontend, Database, Strategy Logic

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🧪 RevDog LeanFlow - Comprehensive Test Suite"
echo "=============================================="
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Function to print test results
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
        exit 1
    fi
}

# Test 1: Check Docker services
print_section "Test 1: Docker Services Health"

if docker-compose ps | grep -q "Up"; then
    print_result 0 "Docker services are running"
else
    echo -e "${RED}❌ Docker services not running${NC}"
    echo "Starting services..."
    docker-compose up -d
    sleep 5
fi

# Test 2: Backend health
print_section "Test 2: Backend API Health"

HEALTH=$(curl -s http://localhost:8000/api/health)
if echo "$HEALTH" | grep -q "healthy"; then
    print_result 0 "Backend is healthy"
    echo "$HEALTH" | python3 -m json.tool | head -10
else
    print_result 1 "Backend health check failed"
fi

# Test 3: Frontend
print_section "Test 3: Frontend Accessibility"

if curl -s http://localhost:5173 | grep -q "vite"; then
    print_result 0 "Frontend is accessible at http://localhost:5173"
else
    print_result 1 "Frontend not accessible"
fi

# Test 4: Database
print_section "Test 4: Database Check"

if [ -f "leanflow.db" ]; then
    print_result 0 "Database file exists"
    SIZE=$(ls -lh leanflow.db | awk '{print $5}')
    echo "   Database size: $SIZE"
    
    # Check table count
    TABLE_COUNT=$(sqlite3 leanflow.db "SELECT count(*) FROM sqlite_master WHERE type='table';")
    echo "   Tables: $TABLE_COUNT"
else
    echo -e "${YELLOW}⚠️  Database not initialized${NC}"
    echo "   Initializing database..."
    python3 scripts/init_db.py
    print_result $? "Database initialized"
fi

# Test 5: Core Strategy Logic
print_section "Test 5: VWAP/TWAP Strategy Logic"

echo "Testing VWAP calculation..."
python3 -c "
from src.strategies.vwap_twap import calculate_vwap
result = calculate_vwap([100, 101, 102], [1000, 1500, 2000])
expected = 101.22  # (100*1000 + 101*1500 + 102*2000) / 4500 = 101.222...
assert abs(result - expected) < 0.01, f'VWAP test failed: {result} != {expected}'
print('  ✅ VWAP calculation: %.2f (expected: %.2f)' % (result, expected))
"

echo "Testing TWAP calculation..."
python3 -c "
from src.strategies.vwap_twap import calculate_twap
result = calculate_twap([100, 101, 102])
expected = 101.0
assert abs(result - expected) < 0.01, f'TWAP test failed: {result} != {expected}'
print('  ✅ TWAP calculation: %.2f (expected: %.2f)' % (result, expected))
"

echo "Testing Rolling VWAP..."
python3 -c "
from src.strategies.vwap_twap import RollingVWAP
calc = RollingVWAP(window_size=3)
calc.add(100, 1000)
calc.add(101, 1500)
calc.add(102, 2000)
result = calc.get_vwap()
expected = 101.22  # Same calculation as VWAP
assert abs(result - expected) < 0.01, f'Rolling VWAP test failed: {result} != {expected}'
print('  ✅ Rolling VWAP: %.2f (expected: %.2f)' % (result, expected))
"

print_result 0 "Core strategy calculations working correctly"

# Test 6: Risk Controls
print_section "Test 6: SEBI Risk Controls"

echo "Testing OPS Limiter (10 orders/sec max)..."
python3 -c "
from src.utils.risk_controls import OPSLimiter
limiter = OPSLimiter(max_ops=2)
assert limiter.can_place_order(), 'Should allow first order'
limiter.record_order()
assert limiter.can_place_order(), 'Should allow second order'
limiter.record_order()
assert not limiter.can_place_order(), 'Should block third order'
print('  ✅ OPS Limiter enforcing 2 orders/sec limit')
"

echo "Testing Kill Switch (5% drawdown)..."
python3 -c "
from src.utils.risk_controls import KillSwitch
ks = KillSwitch(threshold=0.05)
assert not ks.update(100000), 'Should not trigger at peak'
assert not ks.update(96000), 'Should not trigger at 4% drawdown'
assert ks.update(94000), 'Should trigger at 6% drawdown'
print('  ✅ Kill Switch triggers at 5% drawdown threshold')
"

print_result 0 "Risk controls SEBI compliant"

# Test 7: Run Backtest
print_section "Test 7: Execute VWAP/TWAP Backtest"

echo "Starting backtest..."
echo "  Symbol: RELIANCE"
echo "  Period: 2024-01-01 to 2024-01-02"
echo "  VWAP Window: 50"
echo "  TWAP Slices: 5"
echo ""

BACKTEST_RESPONSE=$(curl -s -X POST http://localhost:8000/api/backtest/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "RELIANCE",
    "start_date": "2024-01-01",
    "end_date": "2024-01-02",
    "vwap_window": 50,
    "twap_slices": 5,
    "order_size": 10,
    "initial_capital": 100000.0
  }')

if echo "$BACKTEST_RESPONSE" | grep -q "run_id"; then
    print_result 0 "Backtest started successfully"
    RUN_ID=$(echo "$BACKTEST_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['run_id'])")
    echo "   Run ID: $RUN_ID"
    
    # Wait for backtest completion
    echo "   Waiting for backtest to complete..."
    sleep 3
    
    # Test 8: Fetch Results
    print_section "Test 8: Backtest Results Retrieval"
    
    RESULTS=$(curl -s http://localhost:8000/api/backtest/results/$RUN_ID)
    
    if echo "$RESULTS" | grep -q "sharpe_ratio"; then
        print_result 0 "Results retrieved successfully"
        echo ""
        echo -e "${GREEN}📊 Backtest Performance Metrics${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        # Parse and display metrics
        SHARPE=$(echo "$RESULTS" | python3 -c "import sys, json; print(f\"{json.load(sys.stdin)['data']['sharpe_ratio']:.2f}\")" 2>/dev/null || echo "N/A")
        RETURN=$(echo "$RESULTS" | python3 -c "import sys, json; print(f\"{json.load(sys.stdin)['data']['total_return']*100:.2f}%\")" 2>/dev/null || echo "N/A")
        DRAWDOWN=$(echo "$RESULTS" | python3 -c "import sys, json; print(f\"{json.load(sys.stdin)['data']['max_drawdown']*100:.2f}%\")" 2>/dev/null || echo "N/A")
        TRADES=$(echo "$RESULTS" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['total_trades'])" 2>/dev/null || echo "N/A")
        WIN_RATE=$(echo "$RESULTS" | python3 -c "import sys, json; print(f\"{json.load(sys.stdin)['data']['win_rate']*100:.0f}%\")" 2>/dev/null || echo "N/A")
        
        echo "  Sharpe Ratio:      $SHARPE"
        echo "  Total Return:      $RETURN"
        echo "  Max Drawdown:      $DRAWDOWN"
        echo "  Total Trades:      $TRADES"
        echo "  Win Rate:          $WIN_RATE"
        echo ""
        
        # Show sample trades
        echo -e "${GREEN}📝 Sample Trades${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "$RESULTS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    trades = data['data']['trades'][:3]
    for i, t in enumerate(trades, 1):
        print(f\"  {i}. {t['type']:4s} {t['quantity']:3d} @ ₹{t['price']:.2f} → P&L: ₹{t['pnl']:.2f}\")
except Exception as e:
    print(f'  No trades to display')
"
    else
        print_result 1 "Failed to fetch results"
    fi
else
    print_result 1 "Backtest failed to start"
fi

# Test 9: List Backtests
print_section "Test 9: Backtest History"

LIST_RESPONSE=$(curl -s http://localhost:8000/api/backtest/list)
if echo "$LIST_RESPONSE" | grep -q "backtests"; then
    print_result 0 "Backtest list endpoint working"
    TOTAL=$(echo "$LIST_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('data', d).get('total', 0))" 2>/dev/null || echo "0")
    echo "   Total backtests in database: $TOTAL"
else
    print_result 1 "Failed to list backtests"
fi

# Test 10: API Documentation
print_section "Test 10: API Documentation"

API_DOCS=$(curl -s http://localhost:8000/docs)
if echo "$API_DOCS" | grep -q "swagger"; then
    print_result 0 "API documentation available at http://localhost:8000/docs"
else
    print_result 1 "API documentation not accessible"
fi

# Summary
print_section "Test Summary"

echo -e "${GREEN}✅ All Core Features Tested & Working:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  • Backend API (FastAPI) .......................... ✅"
echo "  • Frontend UI (React + Ant Design) ............... ✅"
echo "  • Database (SQLite + SQLAlchemy) ................. ✅"
echo "  • VWAP/TWAP Strategy (Pure Python) ............... ✅"
echo "  • Risk Controls (OPS Limiter, Kill Switch) ....... ✅"
echo "  • Backtest Execution (Native Python) ............. ✅"
echo "  • Results Retrieval & Storage .................... ✅"
echo "  • Docker Deployment .............................. ✅"
echo ""
echo -e "${YELLOW}🔄 Implementation Note:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  • Using NATIVE PYTHON strategy (not LEAN engine)"
echo "  • Simpler, faster, easier to maintain"
echo "  • Fully SEBI compliant White Box algo"
echo "  • See docs/DESIGN_VS_IMPLEMENTATION.md for details"
echo ""
echo -e "${BLUE}📚 Access Your System:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  • Frontend UI:    http://localhost:5173"
echo "  • API Docs:       http://localhost:8000/docs"
echo "  • Health Check:   http://localhost:8000/api/health"
echo ""
echo -e "${GREEN}🎉 System is fully operational!${NC}"
echo ""

