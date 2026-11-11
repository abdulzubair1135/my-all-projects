"""
Ollama integration for local AI responses.
"""

import requests
import json
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, url="http://localhost:11434", model="gemma3:1b"):
        self.url = url.rstrip('/')
        self.model = model
        self.base_url = f"{self.url}/api/generate"

    def generate(self, prompt, stream=False, timeout=120):
        """Send a prompt to Ollama and return the response."""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream
            }
            response = requests.post(self.base_url, json=payload, timeout=timeout)
            response.raise_for_status()
            if not stream:
                data = response.json()
                return data.get('response', '').strip()
            else:
                # Stream handling (if needed)
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if 'response' in chunk:
                            full_response += chunk['response']
                        if chunk.get('done', False):
                            break
                return full_response.strip()
        except requests.exceptions.ConnectionError:
            logger.error("Ollama connection error: server not reachable")
            return "Error: Could not connect to Ollama. Is it running?"
        except requests.exceptions.Timeout:
            logger.error("Ollama request timeout")
            return "Error: Ollama request timed out."
        except requests.exceptions.HTTPError as e:
            logger.error(f"Ollama HTTP error: {e}")
            return f"Error: Ollama returned {e.response.status_code}"
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"Error: {str(e)}"

    def set_model(self, model):
        self.model = model
        logger.info(f"Ollama model changed to {model}")

    def test_connection(self):
        """Test if Ollama server is reachable and model exists.""" 
        try:
            # Check server
            tags_url = f"{self.url}/api/tags"
            response = requests.get(tags_url, timeout=2)
            if response.status_code != 200:
                return False, f"Server error: {response.status_code}"

            data = response.json()






+           models = [m['name'] for m in data.get('models', [])]
            if self.model in models:
                return True, f"Model '{self.model}' found."
            else:
                return False, f"Model '{self.model}' not found. Available: {', '.join(models)}"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to Ollama. Is it running?"
        except Exception as e:
            return False, f"Error: {e}"  