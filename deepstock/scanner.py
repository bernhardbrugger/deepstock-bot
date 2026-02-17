"""Main scanner orchestrator for deepstock-bot."""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from deepstock.config import Settings
from deepstock.sources import fmp, finnhub, edgar
from deepstock.analysis.filter import filter_trades
from deepstock.analysis.ai_analyst import analyze_trade, detect_patterns
from deepstock.alerts import telegram, email, formatter

logger = logging.getLogger(__name__)


class DeepStockScanner:
    """Main scanning pipeline: fetch → filter → analyze → alert."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def fetch_all_trades(self) -> list[dict[str, Any]]:
        """Fetch trades from all configured data sources."""
        all_trades: list[dict[str, Any]] = []

        if self.settings.fmp_api_key:
            logger.info("Fetching insider trades from FMP...")
            trades = fmp.fetch_insider_trades(self.settings.fmp_api_key)
            all_trades.extend(trades)

        if self.settings.finnhub_api_key:
            logger.info("Fetching congress trades from Finnhub...")
            trades = finnhub.fetch_congress_trades(self.settings.finnhub_api_key)
            all_trades.extend(trades)

        logger.info("Fetching Form 4 filings from SEC EDGAR...")
        filings = edgar.fetch_latest_form4_filings()
        for filing in filings:
            all_trades.append({
                "source": "edgar",
                "ticker": filing.get("ticker", ""),
                "insider_name": filing.get("title", ""),
                "insider_title": "",
                "transaction_type": "",
                "shares": 0,
                "price": 0,
                "value": 0,
                "date": filing.get("updated", ""),
                "filing_date": filing.get("updated", ""),
                "raw": filing,
            })

        logger.info("Total trades fetched: %d", len(all_trades))
        return all_trades

    def run_scan(self) -> dict[str, Any]:
        """Run a complete scan cycle: fetch, filter, analyze, alert.

        Returns:
            Scan results summary.
        """
        logger.info("=" * 50)
        logger.info("Starting deepstock scan...")
        logger.info("=" * 50)

        # 1. Fetch
        all_trades = self.fetch_all_trades()

        # 2. Filter
        filtered = filter_trades(
            all_trades,
            min_value=self.settings.min_trade_value,
            watchlist=self.settings.watchlist,
        )

        if not filtered:
            logger.info("No notable trades found this scan.")
            return {"trades_fetched": len(all_trades), "trades_filtered": 0, "alerts_sent": 0}

        logger.info("Found %d notable trades", len(filtered))

        # 3. AI Analysis (top trades only)
        analyzed_trades: list[dict[str, Any]] = []
        ai_key = self.settings.openai_api_key or self.settings.anthropic_api_key or ""

        if ai_key and self.settings.has_ai_provider:
            for trade in filtered[:5]:
                analysis = analyze_trade(
                    trade,
                    provider=self.settings.ai_provider,
                    api_key=ai_key,
                    model=self.settings.ai_model,
                )
                trade["ai_analysis"] = analysis
                analyzed_trades.append(trade)

            patterns = detect_patterns(
                filtered,
                provider=self.settings.ai_provider,
                api_key=ai_key,
                model=self.settings.ai_model,
            ) if len(filtered) >= 3 else None
        else:
            analyzed_trades = filtered[:5]
            patterns = None
            logger.warning("No AI provider configured — skipping analysis")

        # 4. Send alerts
        alerts_sent = 0

        for trade in analyzed_trades:
            alert_html = formatter.format_breaking_alert(trade, trade.get("ai_analysis"))

            if self.settings.has_telegram:
                if telegram.send_message(
                    self.settings.telegram_bot_token,
                    self.settings.telegram_chat_id,
                    alert_html,
                ):
                    alerts_sent += 1

            if self.settings.has_email:
                headline = (trade.get("ai_analysis") or {}).get("headline", "")
                subject = f"🚨 Insider Trade: {trade.get('ticker', '???')} — {headline or 'Notable Activity'}"
                if email.send_email(
                    smtp_host=self.settings.smtp_host,
                    smtp_port=self.settings.smtp_port,
                    smtp_user=self.settings.smtp_user,
                    smtp_password=self.settings.smtp_password,
                    to_address=self.settings.alert_email_to,
                    subject=subject,
                    body_html=alert_html,
                ):
                    alerts_sent += 1

        # Daily digest
        if len(filtered) >= 2:
            digest_html = formatter.format_daily_digest(filtered, patterns)

            if self.settings.has_telegram:
                telegram.send_message(
                    self.settings.telegram_bot_token,
                    self.settings.telegram_chat_id,
                    digest_html,
                )

            if self.settings.has_email:
                email.send_email(
                    smtp_host=self.settings.smtp_host,
                    smtp_port=self.settings.smtp_port,
                    smtp_user=self.settings.smtp_user,
                    smtp_password=self.settings.smtp_password,
                    to_address=self.settings.alert_email_to,
                    subject=f"📊 DeepStock Daily Digest — {len(filtered)} Notable Trades",
                    body_html=digest_html,
                )

        results = {
            "trades_fetched": len(all_trades),
            "trades_filtered": len(filtered),
            "trades_analyzed": len(analyzed_trades),
            "patterns_found": patterns.get("patterns_found", 0) if patterns else 0,
            "alerts_sent": alerts_sent,
        }

        logger.info("Scan complete: %s", results)
        return results

    def watch(self) -> None:
        """Run continuous monitoring at configured intervals."""
        import schedule

        logger.info(
            "Starting continuous monitoring (every %d minutes)...",
            self.settings.scan_interval_minutes,
        )

        self.run_scan()
        schedule.every(self.settings.scan_interval_minutes).minutes.do(self.run_scan)

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping deepstock watch...")
