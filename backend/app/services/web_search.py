import logging
from typing import List, Dict, Any
from duckduckgo_search import DDGS
import datetime

logger = logging.getLogger("adhi.services.web_search")

def search_internet_snippets(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search DuckDuckGo text search and return snippet results.
    Useful for quick factual lookups and RAG context augmentation.
    """
    try:
        results = []
        # Use DDGS Context Manager to ensure resources are cleaned up
        with DDGS() as ddgs:
            # text search
            responses = ddgs.text(keywords=query, max_results=max_results)
            for r in responses:
                results.append({
                    "title": r.get("title", "Unknown"),
                    "link": r.get("href", ""),
                    "snippet": r.get("body", "")
                })
        return results
    except Exception as e:
        logger.error("web_search_failed", extra={"error": str(e), "query": query})
        return []

def search_internet_news(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search DuckDuckGo News and return latest articles.
    Useful for Regulation updates.
    """
    try:
        results = []
        with DDGS() as ddgs:
            responses = ddgs.news(keywords=query, max_results=max_results)
            for r in responses:
                # r is typically: {'date': '2025-01-20T10:00:00Z', 'title': '...', 'body': '...', 'url': '...', 'source': '...'}
                results.append(r)
        return results
    except Exception as e:
        logger.error("news_search_failed", extra={"error": str(e), "query": query})
        return []

def get_live_regulations() -> List[Dict[str, Any]]:
    """
    Fetches the latest AI regulation news and formats them as Regulation objects.
    """
    news_items = search_internet_news("AI regulatory compliance latest updates framework eu ai act", max_results=10)
    
    live_regs = []
    
    import uuid
    for row in news_items:
        # Determine pseudo jurisdiction
        title_lower = row.get("title", "").lower()
        if "eu" in title_lower or "european" in title_lower:
            juris = "European Union"
        elif "uk" in title_lower or "britain" in title_lower:
            juris = "United Kingdom"
        elif "us " in title_lower or "biden" in title_lower or "nist" in title_lower:
            juris = "United States"
        elif "california" in title_lower or "sb 1047" in title_lower:
            juris = "California, US"
        elif "india" in title_lower:
            juris = "India"
        else:
            juris = "International"

        iso_date = datetime.datetime.now().date().isoformat()
        if row.get("date"):
            try:
                # Try to parse ISO8601 DDG date
                iso_date = row.get("date").split("T")[0]
            except:
                pass

        live_regs.append({
            "id": f"live-{uuid.uuid4()}",
            "name": row.get("title", "Live Internet Update"),
            "description": f"(LIVE NEWS - {row.get('source', 'Web')}): {row.get('body', '')}",
            "jurisdiction": juris,
            "status": "UPCOMING",  # Mark news as upcoming or active randomly or just upcoming
            "effectiveDate": iso_date,
            "tags": ["live-internet", "recent-news"],
            "applicableSystems": [],
            "sourceUrl": row.get("url", "")
        })

    return live_regs
