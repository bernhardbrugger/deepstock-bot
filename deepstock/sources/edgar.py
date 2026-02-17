"""SEC EDGAR RSS feed client for Form 4 filings."""

from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "deepstock-bot/0.1.0 (https://github.com/bernhardbrugger/deepstock-bot)",
    "Accept": "application/atom+xml",
}


def fetch_latest_form4_filings(count: int = 40) -> list[dict[str, Any]]:
    """Fetch the latest Form 4 filings from SEC EDGAR RSS feed.

    Args:
        count: Number of filings to fetch (max 40 per request).

    Returns:
        List of Form 4 filing summaries.

    Note:
        SEC EDGAR requires a descriptive User-Agent header.
        No API key is needed.
    """
    url = (
        f"https://www.sec.gov/cgi-bin/browse-edgar"
        f"?action=getcurrent&type=4&dateb=&owner=include"
        f"&count={min(count, 40)}&search_text=&start=0&output=atom"
    )

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch EDGAR RSS: %s", e)
        return []

    try:
        root = ET.fromstring(response.text)
    except ET.ParseError as e:
        logger.error("Failed to parse EDGAR RSS XML: %s", e)
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    filings = []

    for entry in root.findall("atom:entry", ns):
        title = entry.findtext("atom:title", "", ns)
        link_el = entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        updated = entry.findtext("atom:updated", "", ns)
        summary = entry.findtext("atom:summary", "", ns)

        ticker_match = re.search(r"\(([A-Z]{1,5})\)", title)
        company_match = re.search(r"4\s*-\s*(.+?)\s*\(", title)

        filings.append({
            "source": "edgar",
            "title": title.strip(),
            "link": link,
            "updated": updated,
            "summary": summary.strip() if summary else "",
            "ticker": ticker_match.group(1) if ticker_match else "",
            "company": company_match.group(1).strip() if company_match else "",
        })

    logger.info("Fetched %d Form 4 filings from EDGAR", len(filings))
    return filings


def parse_filing(url: str) -> Optional[dict[str, Any]]:
    """Parse a Form 4 filing page for trade details.

    Args:
        url: URL to the EDGAR filing page.

    Returns:
        Parsed filing data or None on failure.
    """
    try:
        response = requests.get(url, headers={**HEADERS, "Accept": "text/html"}, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch filing %s: %s", url, e)
        return None

    html = response.text

    insider_match = re.search(
        r'<span class="FormData">\s*1\.\s*Name.*?</span>.*?'
        r'<span class="FormData">(.+?)</span>',
        html, re.DOTALL
    )
    ticker_match = re.search(
        r'<span class="FormData">\s*3\.\s*Ticker.*?</span>.*?'
        r'<span class="FormData">(.+?)</span>',
        html, re.DOTALL
    )

    transactions: list[dict[str, Any]] = []
    tx_pattern = re.findall(
        r"<td.*?>\s*(\d{2}/\d{2}/\d{4})\s*</td>.*?"
        r"<td.*?>\s*([PSMADFGCW])\s*</td>.*?"
        r"<td.*?>\s*([\d,]+)\s*</td>.*?"
        r"<td.*?>\s*\$?([\d,.]+)\s*</td>",
        html, re.DOTALL
    )
    for date_str, code, shares_str, price_str in tx_pattern:
        try:
            shares = int(shares_str.replace(",", ""))
            price = float(price_str.replace(",", ""))
            transactions.append({
                "date": date_str,
                "code": code,
                "shares": shares,
                "price": price,
                "value": shares * price,
            })
        except (ValueError, TypeError):
            continue

    return {
        "url": url,
        "insider_name": insider_match.group(1).strip() if insider_match else "",
        "ticker": ticker_match.group(1).strip() if ticker_match else "",
        "transactions": transactions,
    }
