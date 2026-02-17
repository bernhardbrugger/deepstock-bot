<div align="center">

# 🤖📊 deepstock-bot

**AI-powered stock & crypto intelligence bot**

*Monitors insider trades, detects market patterns, and delivers actionable insights — powered by LLMs and financial APIs.*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Stars](https://img.shields.io/github/stars/bernhardbrugger/deepstock-bot?style=social)](https://github.com/bernhardbrugger/deepstock-bot)

[Features](#-features) · [Quick Start](#-quick-start) · [Configuration](#%EF%B8%8F-configuration) · [Architecture](#-architecture) · [Roadmap](#-roadmap) · [Contributing](#-contributing)

</div>

---

## 🤔 Why deepstock-bot?

Every day, corporate insiders and members of Congress trade millions in stocks — and it's all public data. **deepstock-bot** monitors these trades in real time, uses AI to separate signal from noise, and delivers actionable insights directly to your inbox or Telegram.

> **Stop scrolling through SEC filings. Let AI do it for you.**

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Insider Trade Scanner** | Monitors SEC Form 4 filings for significant insider buys/sells |
| 🏛️ **Congress Trade Tracker** | Tracks stock trades by US Congress members |
| 📊 **Earnings Surprise Detector** | Flags unusual trading before earnings announcements |
| 🧠 **AI Market Analyst** | LLM-powered analysis of trade significance (OpenAI & Anthropic) |
| 👀 **Portfolio Watchlist** | Monitor specific tickers for insider activity |
| 📬 **Multi-Channel Alerts** | Get notified via Email, Telegram, or both |
| 🔄 **Continuous Monitoring** | Set it and forget it — runs on a configurable schedule |

## 🖥️ Demo

```
╔══════════════════════════════════════════════════════════════╗
║  🚨 DEEPSTOCK ALERT — Significant Insider Trade Detected   ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📋 Trade Details                                            ║
║  ─────────────────────────────────────────────────────────   ║
║  Insider:    Lisa Su (CEO)                                   ║
║  Company:    Advanced Micro Devices (AMD)                    ║
║  Action:     BUY · 50,000 shares @ $142.30                  ║
║  Value:      $7,115,000                                      ║
║  Filed:      2026-02-15                                      ║
║                                                              ║
║  🧠 AI Analysis                                              ║
║  ─────────────────────────────────────────────────────────   ║
║  Significance: ██████████ HIGH (9.2/10)                      ║
║                                                              ║
║  CEO Lisa Su purchasing $7.1M in AMD shares is a strong      ║
║  bullish signal. This is her largest open-market buy in 18   ║
║  months, occurring just 3 weeks before earnings. Historical  ║
║  data shows AMD rallied 12% on average within 60 days of     ║
║  similar insider purchases.                                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/bernhardbrugger/deepstock-bot.git
cd deepstock-bot
pip install -e .
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your API keys (see Configuration below)
```

### 3. Run

```bash
# Run a single scan
deepstock scan

# Continuous monitoring (default: every 30 minutes)
deepstock watch

# Validate your configuration
deepstock config
```

## ⚙️ Configuration

Create a `.env` file in the project root:

```env
# ── Required: At least one data source ──────────────────────
FMP_API_KEY=your_financial_modeling_prep_key
FINNHUB_API_KEY=your_finnhub_key

# ── Optional: Additional data sources ───────────────────────
ALPHAVANTAGE_API_KEY=your_alphavantage_key

# ── Required: At least one AI provider ──────────────────────
OPENAI_API_KEY=your_openai_key
# ANTHROPIC_API_KEY=your_anthropic_key      # Alternative to OpenAI

# ── Optional: Alert channels ────────────────────────────────
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL_TO=you@gmail.com

# ── Scan settings ───────────────────────────────────────────
SCAN_INTERVAL_MINUTES=30
MIN_TRADE_VALUE=100000
WATCHLIST=AAPL,MSFT,NVDA,TSLA,AMD,GOOGL
```

**Where to get API keys:**

| Service | Free Tier | Sign Up |
|---------|-----------|---------|
| [Financial Modeling Prep](https://financialmodelingprep.com/) | 250 req/day | [Get Key](https://financialmodelingprep.com/developer/docs/) |
| [Finnhub](https://finnhub.io/) | 60 req/min | [Get Key](https://finnhub.io/register) |
| [AlphaVantage](https://www.alphavantage.co/) | 25 req/day | [Get Key](https://www.alphavantage.co/support/#api-key) |
| [OpenAI](https://openai.com/) | Pay-as-you-go | [Get Key](https://platform.openai.com/api-keys) |

## 📖 Feature Details

### 🔍 Insider Trade Scanner
Scans SEC EDGAR Form 4 filings and FMP insider trade data. Filters by trade value, insider role, and historical patterns. Catches the trades that matter.

### 🏛️ Congress Trade Tracker
Monitors stock trades disclosed by US Congress members via Finnhub. Congress members consistently outperform the market — now you can follow their moves.

### 📊 Earnings Surprise Detector
Detects unusual insider trading patterns before earnings announcements. Clusters of insider buys before earnings? That's a signal.

### 🧠 AI Market Analyst
Sends trade data to GPT-4 or Claude for contextual analysis. Gets a significance score (1-10), plain-English explanation, and historical comparison. Not financial advice — but very useful context.

### 👀 Portfolio Watchlist Monitor
Set your watchlist in `.env` and get instant alerts when insiders trade stocks you care about.

### 📬 Multi-Channel Alerts
Beautiful formatted alerts via:
- **Telegram** — instant push notifications
- **Email** — HTML-formatted daily digests and breaking alerts

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    deepstock-bot                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────┐  ┌───────────┐  ┌───────────────────┐   │
│  │  FMP API  │  │  Finnhub  │  │  SEC EDGAR RSS    │   │
│  └─────┬─────┘  └─────┬─────┘  └────────┬──────────┘   │
│        │              │                  │              │
│        └──────────────┼──────────────────┘              │
│                       ▼                                 │
│              ┌────────────────┐                          │
│              │  Trade Filter  │                          │
│              │  & Scorer      │                          │
│              └───────┬────────┘                          │
│                      ▼                                  │
│              ┌────────────────┐                          │
│              │  AI Analyst    │                          │
│              │  (GPT/Claude)  │                          │
│              └───────┬────────┘                          │
│                      ▼                                  │
│              ┌────────────────┐                          │
│              │  Alert         │──▶ Telegram              │
│              │  Formatter     │──▶ Email                 │
│              └────────────────┘                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 📡 Supported Data Sources

| Source | Data | API Key Required |
|--------|------|:---:|
| **Financial Modeling Prep** | Insider trades, company profiles, quotes | ✅ |
| **Finnhub** | Congress trades, insider sentiment, news | ✅ |
| **SEC EDGAR** | Form 4 filings (direct RSS) | ❌ |
| **AlphaVantage** | Historical prices, fundamentals | ✅ |
| **Yahoo Finance** | Backup quotes and data | ❌ |

## 🗺️ Roadmap

- [x] Core insider trade scanning
- [x] AI-powered trade analysis
- [x] Telegram & email alerts
- [x] SEC EDGAR integration
- [x] Congress trade tracking
- [ ] Web dashboard (Streamlit)
- [ ] Discord bot integration
- [ ] Options flow analysis
- [ ] Crypto whale wallet tracking
- [ ] Backtesting engine
- [ ] Portfolio performance tracking
- [ ] Mobile app (React Native)
- [ ] Custom LLM fine-tuning on financial data

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=bernhardbrugger/deepstock-bot&type=Date)](https://star-history.com/#bernhardbrugger/deepstock-bot&Date)

---

<div align="center">

**⚠️ Disclaimer:** This tool is for informational purposes only. Not financial advice. Always do your own research before making investment decisions.

Built with ❤️ by [bernhardbrugger](https://github.com/bernhardbrugger)

</div>
