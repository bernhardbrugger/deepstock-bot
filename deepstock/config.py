"""Configuration management for deepstock-bot."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    # Data source API keys
    fmp_api_key: Optional[str] = None
    finnhub_api_key: Optional[str] = None
    alphavantage_api_key: Optional[str] = None

    # AI provider keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # Telegram alerts
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    # Email alerts
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    alert_email_to: Optional[str] = None

    # Scan settings
    scan_interval_minutes: int = 30
    min_trade_value: int = 100_000
    watchlist: list[str] = field(default_factory=lambda: ["AAPL", "MSFT", "NVDA", "TSLA", "AMD", "GOOGL"])

    # AI settings
    ai_provider: str = "openai"
    ai_model: str = "gpt-4"

    @property
    def has_data_source(self) -> bool:
        """Check if at least one data source is configured."""
        return bool(self.fmp_api_key or self.finnhub_api_key)

    @property
    def has_ai_provider(self) -> bool:
        """Check if at least one AI provider is configured."""
        return bool(self.openai_api_key or self.anthropic_api_key)

    @property
    def has_telegram(self) -> bool:
        """Check if Telegram alerts are configured."""
        return bool(self.telegram_bot_token and self.telegram_chat_id)

    @property
    def has_email(self) -> bool:
        """Check if email alerts are configured."""
        return bool(self.smtp_user and self.smtp_password and self.alert_email_to)

    def validate(self) -> list[str]:
        """Validate configuration and return list of warnings/errors."""
        issues: list[str] = []

        if not self.has_data_source:
            issues.append(
                "❌ No data source configured. Set at least one of: "
                "FMP_API_KEY, FINNHUB_API_KEY"
            )

        if not self.has_ai_provider:
            issues.append(
                "❌ No AI provider configured. Set at least one of: "
                "OPENAI_API_KEY, ANTHROPIC_API_KEY"
            )

        if not self.has_telegram and not self.has_email:
            issues.append(
                "⚠️  No alert channel configured. Set TELEGRAM_BOT_TOKEN or SMTP credentials "
                "to receive alerts."
            )

        return issues


def load_settings(env_path: Optional[str] = None) -> Settings:
    """Load settings from .env file and environment variables.

    Args:
        env_path: Path to .env file. Defaults to .env in current directory.

    Returns:
        Configured Settings instance.
    """
    if env_path:
        load_dotenv(env_path)
    else:
        load_dotenv()

    watchlist_str = os.getenv("WATCHLIST", "AAPL,MSFT,NVDA,TSLA,AMD,GOOGL")
    watchlist = [t.strip().upper() for t in watchlist_str.split(",") if t.strip()]

    # Determine AI provider
    ai_provider = "openai"
    ai_model = "gpt-4"
    if os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        ai_provider = "anthropic"
        ai_model = "claude-3-5-sonnet-20241022"

    return Settings(
        fmp_api_key=os.getenv("FMP_API_KEY"),
        finnhub_api_key=os.getenv("FINNHUB_API_KEY"),
        alphavantage_api_key=os.getenv("ALPHAVANTAGE_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=os.getenv("SMTP_USER"),
        smtp_password=os.getenv("SMTP_PASSWORD"),
        alert_email_to=os.getenv("ALERT_EMAIL_TO"),
        scan_interval_minutes=int(os.getenv("SCAN_INTERVAL_MINUTES", "30")),
        min_trade_value=int(os.getenv("MIN_TRADE_VALUE", "100000")),
        watchlist=watchlist,
        ai_provider=ai_provider,
        ai_model=ai_model,
    )


def print_config_status(settings: Settings) -> None:
    """Print a friendly configuration status report."""
    print("\n🤖 deepstock-bot Configuration Status")
    print("=" * 45)

    print("\n📡 Data Sources:")
    print(f"  FMP API:         {'✅ configured' if settings.fmp_api_key else '❌ not set'}")
    print(f"  Finnhub API:     {'✅ configured' if settings.finnhub_api_key else '❌ not set'}")
    print(f"  AlphaVantage:    {'✅ configured' if settings.alphavantage_api_key else '⚪ not set (optional)'}")
    print(f"  SEC EDGAR:       ✅ no key needed")

    print("\n🧠 AI Provider:")
    print(f"  OpenAI:          {'✅ configured' if settings.openai_api_key else '❌ not set'}")
    print(f"  Anthropic:       {'✅ configured' if settings.anthropic_api_key else '⚪ not set (optional)'}")
    if settings.has_ai_provider:
        print(f"  Active provider: {settings.ai_provider} ({settings.ai_model})")

    print("\n📬 Alert Channels:")
    print(f"  Telegram:        {'✅ configured' if settings.has_telegram else '⚪ not set (optional)'}")
    print(f"  Email:           {'✅ configured' if settings.has_email else '⚪ not set (optional)'}")

    print("\n⚙️  Scan Settings:")
    print(f"  Interval:        {settings.scan_interval_minutes} minutes")
    print(f"  Min trade value: ${settings.min_trade_value:,}")
    print(f"  Watchlist:       {', '.join(settings.watchlist)}")

    issues = settings.validate()
    if issues:
        print("\n" + "\n".join(issues))
    else:
        print("\n✅ All good! Ready to scan.")
    print()
