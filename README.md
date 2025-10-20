# RevDog LeanFlow

**Open-source algorithmic trading system powered by QuantConnect LEAN**  
_VWAP/TWAP strategies for NSE (India) with SEBI White Box compliance_

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](./VERSION_1.0_RELEASE.md)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![LEAN Engine](https://img.shields.io/badge/LEAN-Docker-green.svg)](https://www.quantconnect.com/lean)
[![SEBI Compliant](https://img.shields.io/badge/SEBI-White%20Box-orange.svg)](./docs/ENGINEERING_DESIGN.md)

## ⚡ Quick Start

```bash
# Clone the repository
git clone https://github.com/revdog/leanflow.git
cd leanflow

# Copy environment variables
cp env.example .env
# Edit .env and add your Zerodha API credentials

# Start development environment
./scripts/dev.sh

# Or with docker-compose directly
docker-compose up
```

**Access the application:**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🎯 Features

- ✅ **Enterprise-Grade Backtesting** - Powered by QuantConnect LEAN engine
- ✅ **VWAP/TWAP Strategies** - Transparent, rule-based execution algorithms
- ✅ **SEBI White Box Compliant** - OPS limiter (≤10/sec) + 5% drawdown kill switch
- ✅ **Professional Dashboard** - React + Ant Design with dark mode
- ✅ **RESTful API** - FastAPI with WebSocket support for real-time updates
- ✅ **Docker Deployment** - Production-ready in 5 minutes
- ✅ **Clean V1.0** - No legacy code, pure LEAN implementation

## 📚 Documentation

**Quick Start:**

- [Version 1.0 Release Notes](./VERSION_1.0_RELEASE.md) - What's in v1.0
- [5-Minute Quick Start](./LEAN_QUICKSTART.md) - Get running fast

**Detailed Guides:**

- [LEAN Integration Guide](./docs/LEAN_INTEGRATION_COMPLETE.md) - Technical implementation
- [Engineering Design](./docs/ENGINEERING_DESIGN.md) - System architecture
- [AI Coding Guide](./docs/AI_CODING_GUIDE.md) - Using `.cursorrules` for development

## 🛡️ SEBI Compliance

This project implements **White Box Execution Algorithms** as defined by SEBI guidelines (Circular SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013):

- ✅ Transparent, rule-based logic (no AI/ML decision-making)
- ✅ Orders Per Second (OPS) limiter: Maximum 10 orders/second
- ✅ Automated kill switch: Triggers at >5% drawdown
- ✅ Complete audit trail with timestamps

## 🚀 Technology Stack

**Engine:** QuantConnect LEAN (Docker) - Enterprise-grade backtesting  
**Backend:** Python 3.13, FastAPI, SQLAlchemy, SQLite  
**Frontend:** React 18, TypeScript, Ant Design, Vite, Zustand  
**Data:** Zerodha Kite Connect API (NSE historical & live data)  
**DevOps:** Docker Compose (Docker-in-Docker for LEAN execution)

## ⚠️ Disclaimer

**TRADING RISK:** This software is for educational and research purposes. Trading involves substantial risk of loss. Always test thoroughly in paper trading mode before using real capital.

**NOT AFFILIATED:** This project is not affiliated with, endorsed by, or sponsored by QuantConnect or Zerodha.

**COMPLIANCE:** Users are responsible for ensuring compliance with SEBI and applicable regulations in their jurisdiction.

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

## 🙏 Attribution

- Uses [QuantConnect LEAN Engine](https://github.com/QuantConnect/Lean) (Apache 2.0)
- Integrates with [Zerodha Kite Connect API](https://kite.trade/)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./docs/CONTRIBUTING.md) for guidelines.

---

**Made with ❤️ by RevDog AI**
