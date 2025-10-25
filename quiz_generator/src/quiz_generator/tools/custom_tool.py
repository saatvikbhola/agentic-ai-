import requests
from bs4 import BeautifulSoup
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class WebsiteScrapingToolInput(BaseModel):
    """Input schema for WebsiteScrapingTool."""
    url: str = Field(..., description="The URL of the website to scrape.")

class WebsiteScrapingTool(BaseTool):
    name: str = "Website Scraping Tool"
    description: str = "A tool that scrapes the text content from a given website URL. It strips HTML, ads, and navigation."
    args_schema: Type[BaseModel] = WebsiteScrapingToolInput

    def _run(self, url: str) -> str:
        """
        Scrapes the text content from the given URL.
        """
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()  # Raise an exception for bad status codes

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script, style, nav, footer, and header tags
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()

            # Get text from common content tags
            # This is a basic implementation; more complex sites might need refinement
            text_parts = []
            for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'article', 'main', 'div']):
                # Avoid capturing text from heavily nested divs that might be UI elements
                # This is a heuristic: check if the tag is a div and has many children
                if tag.name == 'div' and len(tag.find_all()) > 5:
                    continue
                
                text = tag.get_text(separator=' ', strip=True)
                if text:
                    text_parts.append(text)
            
            # Join all text parts and clean up whitespace
            full_text = ' '.join(text_parts)
            # Remove excessive whitespace
            clean_text = ' '.join(full_text.split())

            if not clean_text:
                return "Error: No meaningful text content could be extracted from the URL."

            return clean_text
        
        except requests.exceptions.RequestException as e:
            return f"Error: Failed to retrieve the URL. {e}"
        except Exception as e:
            return f"Error: An unexpected error occurred during scraping. {e}"
