"""Financial Modeling Prep API client."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://financialmodelingprep.com/api/v4"
BASE_URL_V3 = "https://financialmodelingprep.com/api/v3"

_last_request_time: float = 0
_MIN_REQUEST_INTERVAL: float = 0.5


def _rate_limit() -> None:
    """Enforce rate limiting between API calls."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < _MIN_REQUEST_INTERVAL:
        time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


def _get(url: str, params: dict[str, Any]) -> Any:
    """Make a rate-limited GET request to FMP API."""
    _rate_limit()
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error("FMP API request timed out: %s", url)
        return []
    except requests.exceptions.HTTPError as e:
        logger.error("FMP API HTTP error: %s — %s", e.response.status_code, url)
        return []
    except requests.exceptions.RequestException as e:
        logger.error("FMP API request failed: %s", e)
        return []
    except ValueError:
        logger.error("FMP API returned invalid JSON: %s", url)
        return []


def fetch_insider_trades(
    api_key: str,
    days: int = 7,
    page: int = 0,
) -> list[dict[str, Any]]:
    """Fetch recent insider trades from FMP.

    Args:
        api_key: FMP API key.
        days: Number of days to look back.
        page: Pagination page number.

    Returns:
        List of insider trade records.
    """
    date_from = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    date_to = datetime.utcnow().strftime("%Y-%m-%d")

    data = _get(f"{BASE_URL}/insider-trading", {
        "apikey": api_key,
        "page": page,
        "transactionDateFrom": date_from,
        "transactionDateTo": date_to,
    })

    if not isinstance(data, list):
        logger.warning("Unexpected FMP insider trades response: %s", type(data))
        return []

    trades = []
    for item in data:
        trades.append({
            "source": "fmp",
            "ticker": item.get("symbol", ""),
            "insider_name": item.get("reportingName", ""),
            "insider_title": item.get("typeOfOwner", ""),
            "transaction_type": item.get("acquistionOrDisposition", ""),
            "shares": item.get("securitiesTransacted", 0),
            "price": item.get("price", 0),
            "value": item.get("securitiesTransacted", 0) * item.get("price", 0),
            "date": item.get("transactionDate", ""),
            "filing_date": item.get("filingDate", ""),
            "raw": item,
        })

    logger.info("Fetched %d insider trades from FMP (last %d days)", len(trades), days)
    return trades


def fetch_company_profile(api_key: str, ticker: str) -> Optional[dict[str, Any]]:
    """Fetch company profile for a ticker.

    Args:
        api_key: FMP API key.
        ticker: Stock ticker symbol.

    Returns:
        Company profile dict or None.
    """
    data = _get(f"{BASE_URL_V3}/profile/{ticker.upper()}", {"apikey": api_key})
    if isinstance(data, list) and data:
        return data[0]
    return None


def fetch_quote(api_key: str, ticker: str) -> Optional[dict[str, Any]]:
    """Fetch real-time quote for a ticker.

    Args:
        api_key: FMP API key.
        ticker: Stock ticker symbol.

    Returns:
        Quote dict or None.
    """
    data = _get(f"{BASE_URL_V3}/quote/{ticker.upper()}", {"apikey": api_key})
    if isinstance(data, list) and data:
        return data[0]
    return None
