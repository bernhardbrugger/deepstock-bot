"""Finnhub API client."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://finnhub.io/api/v1"

_last_request_time: float = 0
_MIN_REQUEST_INTERVAL: float = 1.0


def _rate_limit() -> None:
    """Enforce rate limiting between API calls."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < _MIN_REQUEST_INTERVAL:
        time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


def _get(endpoint: str, api_key: str, params: Optional[dict[str, Any]] = None) -> Any:
    """Make a rate-limited GET request to Finnhub API."""
    _rate_limit()
    all_params = {"token": api_key}
    if params:
        all_params.update(params)

    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=all_params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error("Finnhub API request timed out: %s", endpoint)
        return None
    except requests.exceptions.HTTPError as e:
        logger.error("Finnhub API HTTP error: %s — %s", e.response.status_code, endpoint)
        return None
    except requests.exceptions.RequestException as e:
        logger.error("Finnhub API request failed: %s", e)
        return None
    except ValueError:
        logger.error("Finnhub API returned invalid JSON: %s", endpoint)
        return None


def fetch_congress_trades(api_key: str) -> list[dict[str, Any]]:
    """Fetch recent Congressional trading activity.

    Args:
        api_key: Finnhub API key.

    Returns:
        List of congress trade records.
    """
    data = _get("stock/congressional-trading", api_key)
    if not data or not isinstance(data, dict):
        return []

    trades = []
    for item in data.get("data", []):
        amount_str = item.get("amountFrom", "0")
        try:
            estimated_value = float(str(amount_str).replace(",", "").replace("$", ""))
        except (ValueError, TypeError):
            estimated_value = 0

        trades.append({
            "source": "finnhub_congress",
            "ticker": item.get("symbol", ""),
            "insider_name": item.get("name", ""),
            "insider_title": f"Congress — {item.get('chamber', '')}",
            "transaction_type": item.get("transactionType", ""),
            "shares": 0,
            "price": 0,
            "value": estimated_value,
            "date": item.get("transactionDate", ""),
            "filing_date": item.get("filingDate", ""),
            "raw": item,
        })

    logger.info("Fetched %d congress trades from Finnhub", len(trades))
    return trades


def fetch_insider_sentiment(api_key: str, ticker: str) -> Optional[dict[str, Any]]:
    """Fetch insider sentiment for a ticker.

    Args:
        api_key: Finnhub API key.
        ticker: Stock ticker symbol.

    Returns:
        Insider sentiment data or None.
    """
    data = _get("stock/insider-sentiment", api_key, {"symbol": ticker.upper()})
    if data and isinstance(data, dict):
        return data
    return None


def fetch_company_news(
    api_key: str, ticker: str, days: int = 7
) -> list[dict[str, Any]]:
    """Fetch recent company news.

    Args:
        api_key: Finnhub API key.
        ticker: Stock ticker symbol.
        days: Number of days to look back.

    Returns:
        List of news articles.
    """
    date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    date_to = datetime.utcnow().strftime("%Y-%m-%d")

    data = _get("company-news", api_key, {
        "symbol": ticker.upper(),
        "from": date_from,
        "to": date_to,
    })

    if isinstance(data, list):
        logger.info("Fetched %d news articles for %s", len(data), ticker)
        return data
    return []
