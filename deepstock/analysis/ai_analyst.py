"""AI-powered trade analysis using LLMs."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

TRADE_ANALYSIS_PROMPT = """You are an expert financial analyst specializing in insider trading patterns. Analyze the following insider trade and provide a concise, actionable assessment.

TRADE DETAILS:
- Insider: {insider_name} ({insider_title})
- Company: {ticker}
- Action: {transaction_type}
- Shares: {shares:,}
- Price: ${price:.2f}
- Total Value: ${value:,.0f}
- Date: {date}

{context}

Provide your analysis in this exact JSON format:
{{
    "significance_score": <1-10 float>,
    "sentiment": "<bullish|bearish|neutral>",
    "headline": "<one-line punchy headline, max 100 chars>",
    "analysis": "<2-3 sentence analysis explaining why this trade matters>",
    "historical_note": "<brief comparison to past similar trades if relevant, otherwise null>"
}}

Be direct, specific, and avoid generic statements. If this is a notable insider (CEO, Congress member, famous investor), emphasize that."""

PATTERN_DETECTION_PROMPT = """You are an expert financial analyst. Analyze these insider trades for patterns, clusters, or unusual activity.

TRADES (last 7 days):
{trades_json}

Look for:
1. Multiple insiders buying/selling the same stock (cluster trades)
2. Unusual timing (before earnings, before announcements)
3. Congress members trading similar sectors
4. Abnormally large positions

Provide your analysis in this JSON format:
{{
    "patterns_found": <number of patterns>,
    "patterns": [
        {{
            "type": "<cluster_buy|cluster_sell|pre_earnings|sector_trend|unusual_size>",
            "tickers": ["<ticker1>", "<ticker2>"],
            "description": "<1-2 sentence description>",
            "confidence": <0.0-1.0>
        }}
    ],
    "summary": "<brief overall market insider sentiment summary>"
}}"""


def _call_openai(api_key: str, model: str, prompt: str) -> Optional[str]:
    """Call OpenAI API for completion."""
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except ImportError:
        logger.error("openai package not installed. Run: pip install openai")
        return None
    except Exception as e:
        logger.error("OpenAI API error: %s", e)
        return None


def _call_anthropic(api_key: str, model: str, prompt: str) -> Optional[str]:
    """Call Anthropic API for completion."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except ImportError:
        logger.error("anthropic package not installed. Run: pip install anthropic")
        return None
    except Exception as e:
        logger.error("Anthropic API error: %s", e)
        return None


def _call_llm(provider: str, api_key: str, model: str, prompt: str) -> Optional[str]:
    """Route to the appropriate LLM provider."""
    if provider == "openai":
        return _call_openai(api_key, model, prompt)
    elif provider == "anthropic":
        return _call_anthropic(api_key, model, prompt)
    else:
        logger.error("Unknown AI provider: %s", provider)
        return None


def _parse_json_response(text: Optional[str]) -> Optional[dict[str, Any]]:
    """Extract and parse JSON from LLM response."""
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"```(?:json)?\s*(.+?)```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass
    logger.warning("Failed to parse JSON from LLM response")
    return None


def analyze_trade(
    trade: dict[str, Any],
    provider: str = "openai",
    api_key: str = "",
    model: str = "gpt-4",
    context: str = "",
) -> Optional[dict[str, Any]]:
    """Analyze a single trade using an LLM.

    Args:
        trade: Trade record dict with standard fields.
        provider: AI provider ("openai" or "anthropic").
        api_key: API key for the provider.
        model: Model name to use.
        context: Additional context (news, company info).

    Returns:
        Analysis dict with significance_score, sentiment, headline, analysis.
    """
    prompt = TRADE_ANALYSIS_PROMPT.format(
        insider_name=trade.get("insider_name", "Unknown"),
        insider_title=trade.get("insider_title", "Unknown"),
        ticker=trade.get("ticker", "???"),
        transaction_type=trade.get("transaction_type", "Unknown"),
        shares=trade.get("shares", 0),
        price=trade.get("price", 0),
        value=trade.get("value", 0),
        date=trade.get("date", "Unknown"),
        context=f"ADDITIONAL CONTEXT:\n{context}" if context else "",
    )

    response = _call_llm(provider, api_key, model, prompt)
    result = _parse_json_response(response)

    if result:
        logger.info(
            "AI analysis for %s: score=%.1f, sentiment=%s",
            trade.get("ticker", "?"),
            result.get("significance_score", 0),
            result.get("sentiment", "?"),
        )
    return result


def detect_patterns(
    trades: list[dict[str, Any]],
    provider: str = "openai",
    api_key: str = "",
    model: str = "gpt-4",
) -> Optional[dict[str, Any]]:
    """Detect patterns across multiple trades using an LLM.

    Args:
        trades: List of trade records.
        provider: AI provider.
        api_key: API key.
        model: Model name.

    Returns:
        Pattern analysis dict.
    """
    simplified = []
    for t in trades[:50]:
        simplified.append({
            "ticker": t.get("ticker", ""),
            "insider": t.get("insider_name", ""),
            "title": t.get("insider_title", ""),
            "type": t.get("transaction_type", ""),
            "value": t.get("value", 0),
            "date": t.get("date", ""),
            "source": t.get("source", ""),
        })

    prompt = PATTERN_DETECTION_PROMPT.format(trades_json=json.dumps(simplified, indent=2))
    response = _call_llm(provider, api_key, model, prompt)
    result = _parse_json_response(response)

    if result:
        logger.info("Pattern detection found %d patterns", result.get("patterns_found", 0))
    return result
