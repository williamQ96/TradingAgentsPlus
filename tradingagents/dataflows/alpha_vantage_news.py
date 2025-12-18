import json
from .alpha_vantage_common import _make_api_request, format_datetime_for_api

def _minify_news_feed(news_json_str: str) -> str:
    """Parses raw news JSON and returns a minified version with only essential fields."""
    try:
        data = json.loads(news_json_str)
        if "feed" not in data:
            return news_json_str # Return raw if unexpected format
        
        minified_feed = []
        for item in data["feed"]:
            minified_feed.append({
                "title": item.get("title"),
                "summary": item.get("summary"),
                "url": item.get("url"),
                "time_published": item.get("time_published"),
                "overall_sentiment_score": item.get("overall_sentiment_score"),
                "overall_sentiment_label": item.get("overall_sentiment_label")
            })
        return json.dumps(minified_feed)
    except Exception as e:
        print(f"Error minifying news: {e}")
        return news_json_str

def get_news(ticker, start_date, end_date) -> str:
    """Returns live and historical market news & sentiment data from premier news outlets worldwide.

    Covers stocks, cryptocurrencies, forex, and topics like fiscal policy, mergers & acquisitions, IPOs.

    Args:
        ticker: Stock symbol for news articles.
        start_date: Start date for news search.
        end_date: End date for news search.

    Returns:
        JSON string of minified news data.
    """

    params = {
        "tickers": ticker,
        "time_from": format_datetime_for_api(start_date),
        "time_to": format_datetime_for_api(end_date),
        "sort": "LATEST",
        "limit": "15", # Reduced from 50 to prevent context overflow
    }
    
    raw_response = _make_api_request("NEWS_SENTIMENT", params)
    return _minify_news_feed(raw_response)

def get_insider_transactions(symbol: str) -> dict[str, str] | str:
    """Returns latest and historical insider transactions by key stakeholders.

    Covers transactions by founders, executives, board members, etc.

    Args:
        symbol: Ticker symbol. Example: "IBM".

    Returns:
        Dictionary containing insider transaction data or JSON string.
    """

    params = {
        "symbol": symbol,
    }

    return _make_api_request("INSIDER_TRANSACTIONS", params)

def get_global_news(curr_date=None, look_back_days=7, limit=50) -> str:
    """Returns global financial and macroeconomic news.
    
    Uses 'financial_markets', 'economy_macro', and 'finance' topics.
    """
    params = {
        "topics": "financial_markets,economy_macro,finance",
        "sort": "LATEST",
        "limit": str(min(limit, 10)),  # Hard cap at 10 to prevent context overflow with local models
    }
    
    if curr_date:
        pass

    raw_response = _make_api_request("NEWS_SENTIMENT", params)
    return _minify_news_feed(raw_response)