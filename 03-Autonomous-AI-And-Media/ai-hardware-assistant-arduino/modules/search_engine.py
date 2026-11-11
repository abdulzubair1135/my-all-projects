# modules/search_engine.py
"""
Google Search Engine
"""

import urllib.parse
import urllib.request
import time
from bs4 import BeautifulSoup

class SearchEngine:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
    def get_answer(self, query):
        try:
            query_encoded = urllib.parse.quote_plus(query)
            url = f"https://www.google.com/search?q={query_encoded}"
            
            headers = {'User-Agent': self.user_agent}
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req, timeout=5)
            html = response.read().decode('utf-8')
            
            soup = BeautifulSoup(html, 'html.parser')
            
            answer = soup.find('div', class_='Z0LcW')
            if answer:
                return answer.get_text()
            
            result = soup.find('div', class_='VwiC3b')
            if result:
                return result.get_text()[:200] + "..."
            
            return f"Here's what I found about {query}"
            
        except Exception as e:
            return f"Search error: {e}"