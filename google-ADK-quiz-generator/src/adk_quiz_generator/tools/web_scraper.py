from google.adk.tools import FunctionTool
import requests
from bs4 import BeautifulSoup
import re

def scrape_main_content(url: str) -> str:
    """
    Scrapes and cleans the main textual content from a given URL.
    Focuses on headings (h1-h3), paragraphs, and list items.
    
    Args:
        url: The URL to scrape content from.

    Returns:
        The cleaned, summarized text content of the page.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove scripts, styles, nav, footer, header, ads
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        
        content_blocks = []

        # Extract headings
        for heading_tag in ["h1", "h2", "h3"]:
            for h in soup.find_all(heading_tag):
                text = h.get_text(strip=True)
                if text and len(text) > 5:
                    content_blocks.append(text.upper())  # headings in uppercase

        # Extract paragraphs
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if text and len(text) > 20:
                content_blocks.append(text)

        # Extract list items
        for li in soup.find_all("li"):
            text = li.get_text(strip=True)
            if text and len(text) > 20:
                content_blocks.append(f"- {text}")

        # Remove duplicates and very short lines
        unique_blocks = []
        seen = set()
        for block in content_blocks:
            block_clean = re.sub(r'\s+', ' ', block)
            if block_clean not in seen:
                seen.add(block_clean)
                unique_blocks.append(block_clean)

        if not unique_blocks:
            return "Error: No meaningful content found at the URL."

        # Join top N blocks to avoid overly long briefs
        cleaned_text = "\n".join(unique_blocks[:50])
        return cleaned_text

    except requests.RequestException as e:
        return f"Error: Could not retrieve URL. {e}"

# Register as ADK FunctionTool
web_scraper_tool = FunctionTool(func=scrape_main_content)
