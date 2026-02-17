"""Trade filtering and scoring engine."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Notable insiders: congress members, famous CEOs, known investors
NOTABLE_INSIDERS: set[str] = {
    # Congress
    "Nancy Pelosi", "Dan Crenshaw", "Tommy Tuberville", "Mark Green",
    "Josh Gottheimer", "Michael McCaul", "Pat Fallon", "Virginia Foxx",
    "Ro Khanna", "Marjorie Taylor Greene",
    # Famous CEOs
    "Elon Musk", "Tim Cook", "Satya Nadella", "Lisa Su", "Jensen Huang",
    "Jamie Dimon", "Warren Buffett", "Mark Zuckerberg", "Sundar Pichai",
    "Andy Jassy", "Pat Gelsinger", "Hock Tan",
    # Known investors
    "Cathie Wood", "Michael Burry", "Carl Icahn", "Bill Ackman",
    "George Soros", "Ken Griffin", "Ray Dalio", "Stanley Druckenmiller",
    "David Tepper", "Howard Marks",
}

HIGH_SIGNAL_TITLES: set[str] = {
    "ceo", "cfo", "coo", "cto", "president", "chairman",
    "chief executive", "chief financial", "chief operating",
    "director", "10% owner", "officer",
}


def is_notable_insider(name: str) -> bool:
    """Check if an insider is in the notable insiders list."""
    name_lower = name.lower().strip()
    return any(notable.lower() in name_lower or name_lower in notable.lower()
               for notable in NOTABLE_INSIDERS)


def is_high_signal_title(title: str) -> bool:
    """Check if the insider's title indicates a high-signal trade."""
    title_lower = title.lower()
    return any(t in title_lower for t in HIGH_SIGNAL_TITLES)


def score_trade(trade: dict[str, Any]) -> float:
    """Score a trade by 'interestingness' on a 0-10 scale.

    Scoring factors:
    - Trade value (higher = more interesting)
    - Notable insider bonus
    - C-suite title bonus
    - Buy vs sell (buys are more notable)
    - Congress trade bonus

    Args:
        trade: Trade record dict.

    Returns:
        Interest score from 0.0 to 10.0.
    """
    score = 0.0
    value = trade.get("value", 0)

    # Value scoring (0-4 points)
    if value >= 10_000_000:
        score += 4.0
    elif value >= 1_000_000:
        score += 3.0
    elif value >= 500_000:
        score += 2.0
    elif value >= 100_000:
        score += 1.0
    elif value >= 50_000:
        score += 0.5

    # Notable insider bonus (0-2 points)
    if is_notable_insider(trade.get("insider_name", "")):
        score += 2.0

    # Title bonus (0-1.5 points)
    if is_high_signal_title(trade.get("insider_title", "")):
        score += 1.5

    # Buy bonus (0-1.5 points)
    tx_type = trade.get("transaction_type", "").upper()
    if tx_type in ("P", "BUY", "A"):
        score += 1.5
    elif tx_type in ("S", "SELL", "D"):
        score += 0.5

    # Congress trade bonus (0-1 point)
    if "congress" in trade.get("source", "").lower():
        score += 1.0

    return min(score, 10.0)


def filter_trades(
    trades: list[dict[str, Any]],
    min_value: int = 100_000,
    min_score: float = 2.0,
    watchlist: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Filter and score a list of trades.

    Args:
        trades: Raw trade records.
        min_value: Minimum trade value to include.
        min_score: Minimum interest score to include.
        watchlist: If set, also include any trade matching these tickers.

    Returns:
        Filtered and scored trades, sorted by score descending.
    """
    watchlist_set = {t.upper() for t in (watchlist or [])}
    scored_trades: list[dict[str, Any]] = []

    for trade in trades:
        trade_score = score_trade(trade)
        trade["score"] = trade_score
        value = trade.get("value", 0)
        ticker = trade.get("ticker", "").upper()

        if (value >= min_value and trade_score >= min_score) or ticker in watchlist_set:
            scored_trades.append(trade)

    scored_trades.sort(key=lambda t: t.get("score", 0), reverse=True)

    logger.info(
        "Filtered %d trades down to %d (min_value=%d, min_score=%.1f)",
        len(trades), len(scored_trades), min_value, min_score,
    )
    return scored_trades
