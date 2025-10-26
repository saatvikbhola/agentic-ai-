from duckduckgo_search import DDGS
from google.adk.tools import FunctionTool
import json

def search_web(query: str) -> str:
    """
    Performs a web search using DuckDuckGo to get relevant snippets
    for fact-checking.
    
    Args:
        query: The search term to use for finding factual information.
    
    Returns:
        A JSON string containing search snippets and their sources.
    """
    try:
        with DDGS() as ddgs:
            # Get top 3 results
            results = list(ddgs.text(query, max_results=3))
            
        if not results:
            return "No search results found."
            
        # Format snippets for the LLM
        snippets = [
            {"snippet": r['body'], "source": r['href']} 
            for r in results
        ]
        return json.dumps(snippets)
        
    except Exception as e:
        return f"Error during web search: {e}"

# FIX: Use 'func' instead of 'impl' and rely on the docstring for description
web_search_tool = FunctionTool(
    func=search_web
)
