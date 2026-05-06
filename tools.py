
from dotenv import load_dotenv
load_dotenv()
import requests
import os
from bs4 import BeautifulSoup
from langchain.tools import tool
from tavily import TavilyClient
from rich.console import Console
from rich.table import Table
import requests

console = Console()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
@tool
def web_search(query: str):
    """Search the web and display formatted results."""

    results = tavily.search(query=query, max_results=5)["results"]

    table = Table(title=f"🔎 Search Results for: {query}")

    table.add_column("Title", style="cyan")
    table.add_column("URL", style="green")
    table.add_column("Snippet", style="white")

    for r in results:
        table.add_row(
            r["title"],
            r["url"],
            r["content"][:200]
        )

    console.print(table, markup=False)

    return results

@tool
def scrape_url(url:str)-> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://www.google.com/"
})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return text[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
    

