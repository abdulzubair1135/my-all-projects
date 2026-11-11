import urllib.request
import urllib.parse
import socket
import re
from bs4 import BeautifulSoup

class WebResearchTool:
    """
    Autonomous Internet Research:
    - Connectivity detection
    - DuckDuckGo Lite scraper (no API key required, fast)
    - Content extraction and summarization
    - Offline fallback
    """
    @staticmethod
    def is_online(host="8.8.8.8", port=53, timeout=3) -> bool:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            return False

    def search(self, query: str, max_results: int = 5) -> dict:
        if not self.is_online():
            return {
                "online": False,
                "query": query,
                "results": [],
                "message": "Offline mode active. No internet connection."
            }

        results = []
        try:
            url = "https://lite.duckduckgo.com/lite/"
            data = urllib.parse.urlencode({"q": query}).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")

            soup = BeautifulSoup(html, "html.parser")
            snippets = soup.find_all("td", class_="result-snippet")
            links = soup.find_all("a", class_="result-link")

            count = min(len(snippets), len(links), max_results)
            for i in range(count):
                title = links[i].get_text(strip=True)
                href = links[i].get("href", "")
                snippet = snippets[i].get_text(strip=True)
                results.append({"title": title, "link": href, "snippet": snippet})

            return {
                "online": True,
                "query": query,
                "results": results,
                "message": f"Found {len(results)} sources."
            }
        except Exception as e:
            return {
                "online": True,
                "query": query,
                "results": [],
                "message": f"Search error: {str(e)}"
            }

    def fetch_page_text(self, url: str, max_chars: int = 4000) -> str:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="replace")
            soup = BeautifulSoup(html, "html.parser")
            for script in soup(["script", "style", "nav", "footer"]):
                script.extract()
            text = soup.get_text(separator=" ", strip=True)
            text = re.sub(r"\s+", " ", text)
            return text[:max_chars]
        except Exception as e:
            return f"Failed to fetch content from {url}: {e}"
