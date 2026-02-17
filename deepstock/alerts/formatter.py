"""Alert message formatting templates."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional


def format_breaking_alert(trade: dict[str, Any], analysis: Optional[dict[str, Any]] = None) -> str:
    """Format a breaking insider trade alert as HTML.

    Args:
        trade: Trade record dict.
        analysis: Optional AI analysis dict.

    Returns:
        HTML-formatted alert string.
    """
    tx_type = trade.get("transaction_type", "").upper()
    action_emoji = "🟢 BUY" if tx_type in ("P", "BUY", "A") else "🔴 SELL"
    value = trade.get("value", 0)
    score = trade.get("score", 0)

    lines = [
        "🚨 <b>DEEPSTOCK ALERT — Insider Trade Detected</b>",
        "",
        f"📋 <b>Trade Details</b>",
        f"  Insider: <b>{trade.get('insider_name', 'Unknown')}</b> ({trade.get('insider_title', '')})",
        f"  Company: <b>{trade.get('ticker', '???')}</b>",
        f"  Action:  {action_emoji} · {trade.get('shares', 0):,} shares @ ${trade.get('price', 0):.2f}",
        f"  Value:   <b>${value:,.0f}</b>",
        f"  Date:    {trade.get('date', 'Unknown')}",
        f"  Score:   {'█' * int(score)} {score:.1f}/10",
    ]

    if analysis:
        lines.extend([
            "",
            f"🧠 <b>AI Analysis</b>",
            f"  Significance: {analysis.get('significance_score', 'N/A')}/10 — {analysis.get('sentiment', 'N/A').upper()}",
            f"  💬 {analysis.get('headline', '')}",
            f"  {analysis.get('analysis', '')}",
        ])
        if analysis.get("historical_note"):
            lines.append(f"  📊 {analysis['historical_note']}")

    lines.extend(["", "— deepstock-bot 🤖"])
    return "\n".join(lines)


def format_breaking_alert_text(trade: dict[str, Any], analysis: Optional[dict[str, Any]] = None) -> str:
    """Format a breaking alert as plain text."""
    import re
    html = format_breaking_alert(trade, analysis)
    return re.sub(r"<[^>]+>", "", html)


def format_daily_digest(
    trades: list[dict[str, Any]],
    patterns: Optional[dict[str, Any]] = None,
) -> str:
    """Format a daily digest of trades as HTML.

    Args:
        trades: List of scored/analyzed trade records.
        patterns: Optional pattern detection results.

    Returns:
        HTML-formatted daily digest.
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")
    lines = [
        f"📊 <b>DEEPSTOCK DAILY DIGEST — {today}</b>",
        f"Found <b>{len(trades)}</b> notable insider trades today.",
        "",
    ]

    if patterns and patterns.get("patterns"):
        lines.append("🔍 <b>Patterns Detected:</b>")
        for p in patterns["patterns"]:
            tickers = ", ".join(p.get("tickers", []))
            lines.append(f"  • [{p.get('type', '')}] {tickers}: {p.get('description', '')}")
        lines.append("")

    lines.append("<b>Top Trades:</b>")
    for i, trade in enumerate(trades[:10], 1):
        tx_type = trade.get("transaction_type", "").upper()
        emoji = "🟢" if tx_type in ("P", "BUY", "A") else "🔴"
        lines.append(
            f"  {i}. {emoji} <b>{trade.get('ticker', '???')}</b> — "
            f"{trade.get('insider_name', 'Unknown')} — "
            f"${trade.get('value', 0):,.0f} — "
            f"Score: {trade.get('score', 0):.1f}/10"
        )

    if patterns and patterns.get("summary"):
        lines.extend(["", f"📈 <b>Market Sentiment:</b> {patterns['summary']}"])

    lines.extend(["", "— deepstock-bot 🤖"])
    return "\n".join(lines)


def format_pattern_alert(patterns: dict[str, Any]) -> str:
    """Format a pattern detection alert as HTML.

    Args:
        patterns: Pattern detection results from AI analyst.

    Returns:
        HTML-formatted pattern alert.
    """
    lines = [
        "🔍 <b>DEEPSTOCK — Pattern Detection Alert</b>",
        f"Detected <b>{patterns.get('patterns_found', 0)}</b> notable patterns.",
        "",
    ]

    for p in patterns.get("patterns", []):
        confidence = p.get("confidence", 0)
        bar = "█" * int(confidence * 10)
        tickers = ", ".join(p.get("tickers", []))
        lines.extend([
            f"<b>{p.get('type', 'unknown').upper()}</b> — {tickers}",
            f"  Confidence: {bar} {confidence:.0%}",
            f"  {p.get('description', '')}",
            "",
        ])

    if patterns.get("summary"):
        lines.append(f"📈 {patterns['summary']}")

    lines.extend(["", "— deepstock-bot 🤖"])
    return "\n".join(lines)
