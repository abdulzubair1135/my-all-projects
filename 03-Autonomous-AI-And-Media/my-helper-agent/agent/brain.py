import requests
import json
import os
import sys

def safe_write(text: str):
    """Safely writes unicode text to stdout on Windows terminals."""
    try:
        sys.stdout.write(text)
        sys.stdout.flush()
    except UnicodeEncodeError:
        try:
            sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
            sys.stdout.buffer.flush()
        except Exception:
            pass

MASTER_SYSTEM_PROMPT = """
You are the user's Personal Autonomous AI Agent.
Operating Environment: Windows 11, Ryzen 7 7435HS, 16GB RAM, RTX 2050 4GB.

CORE RULES:
1. USER LANGUAGE: HINGLISH.
   - Reply naturally in conversational Hinglish (Hindi in Roman script).
   - Use English for technical terms (API, GPU, RAM, Python, Browser).
2. OUTPUT-FIRST:
   - Keep internal thinking brief. Always deliver the complete final answer in Hinglish.
"""

class Brain:
    """
    Ollama Qwen3.5:4B Master Brain Interface.
    Supports Live Token Streaming with Visible Internal Thinking!
    """
    def __init__(self, model_name="qwen3.5:4b", endpoint="http://localhost:11434", num_ctx=2048):
        self.model_name = model_name
        self.endpoint = endpoint
        self.num_ctx = num_ctx

    def is_alive(self) -> bool:
        try:
            r = requests.get(f"{self.endpoint}/api/tags", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def generate(self, prompt: str, system_override: str = None, stream: bool = True, show_thoughts: bool = True) -> str:
        if not self.is_alive():
            return "Ollama service running nahi hai bhai. Make sure Ollama background me on hai."

        system_prompt = system_override or MASTER_SYSTEM_PROMPT
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True,
            "options": {
                "num_ctx": self.num_ctx,
                "temperature": 0.6,
                "top_p": 0.9,
                "num_predict": 1200
            },
            "keep_alive": "5m"
        }

        try:
            res = requests.post(f"{self.endpoint}/api/generate", json=payload, stream=True, timeout=120)
            
            full_response = ""
            thinking_started = False
            response_started = False

            for line in res.iter_lines():
                if line:
                    data = json.loads(line)
                    think_tok = data.get("thinking", "")
                    resp_tok = data.get("response", "")

                    if think_tok and show_thoughts:
                        if not thinking_started:
                            safe_write("\n  [🧠 MODEL INTERNAL THINKING]:\n  ")
                            thinking_started = True
                        safe_write(think_tok.replace("\n", "\n  "))

                    if resp_tok:
                        if not response_started:
                            if thinking_started:
                                safe_write("\n\n  --------------------------------------------------\n  [FINAL ANSWER]:\n  ")
                            response_started = True
                        full_response += resp_tok
                        safe_write(resp_tok)

                    if data.get("done"):
                        break

            # Fallback guarantee: If response was cut off by long thinking, get direct answer instantly
            if not full_response.strip():
                quick_payload = {
                    "model": self.model_name,
                    "prompt": prompt,
                    "system": system_prompt + "\nDo not output thinking, provide direct Hinglish answer.",
                    "think": False,
                    "stream": False,
                    "options": {"num_ctx": 1536, "num_predict": 400}
                }
                fb_res = requests.post(f"{self.endpoint}/api/generate", json=quick_payload, timeout=30)
                if fb_res.status_code == 200:
                    direct_ans = fb_res.json().get("response", "").strip()
                    safe_write("\n  " + direct_ans)
                    return direct_ans

            return full_response.strip()

        except requests.exceptions.Timeout:
            return "Model generation timed out. Hardware currently busy."
        except Exception as e:
            return f"Brain connection error: {str(e)}"
