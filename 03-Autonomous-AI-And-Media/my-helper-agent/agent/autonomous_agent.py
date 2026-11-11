import os
import sys
import json
import time
import requests
from .resource_mgr import ResourceManager
from .memory import AgentMemory
from .tools.terminal import TerminalTool
from .tools.files import FileTool
from .tools.web import WebResearchTool
from .tools.finance import LiveFinanceTool
from .tools.creative import CreativeTools

def safe_print(text: str):
    try:
        sys.stdout.write(text)
        sys.stdout.flush()
    except UnicodeEncodeError:
        try:
            sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
            sys.stdout.buffer.flush()
        except Exception:
            pass

class AutonomousAgent:
    """
    True Autonomous Agent powered by Qwen3.5 4B native tool-calling:
    Qwen itself decides what tools to call, what to search, what Windows commands to run.
    """
    def __init__(self, model_name="qwen3.5:4b", endpoint="http://localhost:11434"):
        self.model_name = model_name
        self.endpoint = endpoint
        self.memory = AgentMemory()
        self.terminal = TerminalTool()
        self.files = FileTool()
        self.web = WebResearchTool()
        self.finance = LiveFinanceTool()
        self.creative = CreativeTools()

        # Tools definition passed directly to Qwen
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "run_terminal",
                    "description": "Execute any PowerShell command on the user's Windows system (e.g. check system, run scripts, start apps, list files).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "The exact PowerShell command to execute"}
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the live internet for news, current events, recent deaths, general queries using clean English search terms.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search keywords in English for best accuracy"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_live_market",
                    "description": "Fetch 100% verified real-time prices for Crypto (BTC, ETH, SOL) and Stocks (NIFTY 50, SENSEX, NASDAQ) directly from live exchange feeds.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "market_type": {
                                "type": "string",
                                "enum": ["all", "crypto", "stocks"],
                                "description": "Specify crypto, stocks, or all"
                            }
                        },
                        "required": ["market_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a local file on the user's Windows PC.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Relative or absolute path of the file"}
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Create or modify a file on the user's PC with automatic safety backups.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path where the file should be written"},
                            "content": {"type": "string", "description": "Text content of the file"}
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_voice",
                    "description": "Convert text into natural Hindi/Hinglish speech audio (MP3).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to speak"}
                        },
                        "required": ["text"]
                    }
                }
            }
        ]

    def _execute_tool(self, name: str, args: dict) -> str:
        """Executes the specific tool called by Qwen and returns output string."""
        safe_print(f"\n  [⚡ AUTONOMOUS ACTION] Qwen Calling Tool: '{name}'\n  Args: {json.dumps(args)}\n")

        try:
            if name == "web_search":
                query = args.get("query", "")
                safe_print(f"  [🔍 WEB SEARCHING] '{query}'...\n")
                res = self.web.search(query, max_results=4)
                if not res.get("online"):
                    return "Error: Offline mode. No internet available."
                items = res.get("results", [])
                safe_print(f"  [📄 SOURCES FOUND] {len(items)} live articles retrieved.\n")
                for idx, item in enumerate(items[:3]):
                    safe_print(f"    - [{idx+1}] {item['title'][:45]}... ({item.get('link','')[:45]})\n")
                formatted = "\n".join([f"Title: {r['title']}\nSnippet: {r['snippet']}\nLink: {r['link']}\n---" for r in items])
                return formatted if formatted else "No results found."

            elif name == "get_live_market":
                mtype = args.get("market_type", "all")
                safe_print(f"  [📈 LIVE EXCHANGE] Fetching direct live market tickers ({mtype})...\n")
                out_lines = []
                if mtype in ["all", "stocks"]:
                    stocks = self.finance.get_stock_indices_live()
                    out_lines.append("STOCK INDICES (LIVE):")
                    for k, v in stocks.items():
                        out_lines.append(f"- {k}: {v['price']} ({v['change_pct']}%)")
                if mtype in ["all", "crypto"]:
                    crypto = self.finance.get_crypto_live()
                    out_lines.append("\nCRYPTOCURRENCY (LIVE):")
                    for k, v in crypto.items():
                        out_lines.append(f"- {k}: ${v['price_usd']:,} (Rs {v['price_inr']:,}) | 24h Change: {v['change_24h']}%")
                return "\n".join(out_lines)

            elif name == "run_terminal":
                cmd = args.get("command", "")
                safe_print(f"  [💻 TERMINAL EXEC] Running on Windows: '{cmd}'\n")
                r = self.terminal.run(cmd, timeout=30)
                output = r.get("stdout", "") or r.get("stderr", "") or "Command executed successfully (no output)."
                safe_print(f"  [💻 TERMINAL OUTPUT] {output[:200]}...\n")
                return output[:2000]

            elif name == "read_file":
                path = args.get("file_path", "")
                safe_print(f"  [📂 READING FILE] '{path}'\n")
                r = self.files.read_file(path)
                return r.get("content", "") if r.get("success") else f"Error: {r.get('error')}"

            elif name == "write_file":
                path = args.get("file_path", "")
                content = args.get("content", "")
                safe_print(f"  [💾 WRITING FILE] '{path}'\n")
                r = self.files.write_file(path, content)
                return f"File saved at: {r.get('path')}" if r.get("success") else f"Error: {r.get('error')}"

            elif name == "generate_voice":
                txt = args.get("text", "")
                r = self.creative.text_to_speech_edge(txt, "voice_output.mp3")
                return f"Audio generated at {r.get('output_path')}" if r.get("success") else f"Error: {r.get('error')}"

            return f"Unknown tool: {name}"

        except Exception as e:
            return f"Tool execution failed: {str(e)}"

    def chat(self, user_prompt: str) -> str:
        """
        Full Autonomous Agent Loop:
        1. Sends prompt + tools to Qwen
        2. Qwen decides whether to call tools
        3. Executes tools and returns data to Qwen
        4. Qwen delivers final Hinglish answer
        """
        system_prompt = (
            "You are the user's Personal Autonomous AI Agent on Windows 11.\n"
            "Hardware: Ryzen 7 7435HS, 16GB RAM, RTX 2050 4GB.\n"
            "You have actual tools to search the web, check live market prices, run Windows terminal commands, and read/write files.\n"
            "RULES:\n"
            "1. When user asks about real-world facts, events, deaths, news, stocks, crypto, system info -> ALWAYS use the appropriate tool autonomously!\n"
            "2. Never claim you don't have access to live data; you HAVE web_search and get_live_market tools. USE THEM.\n"
            "3. Default response language: Conversational Hinglish (Hindi in Roman English script).\n"
            "4. Be direct, helpful, friendly ('bhai')."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # Iteration 1: Let Qwen decide what to do
        payload = {
            "model": self.model_name,
            "messages": messages,
            "tools": self.tools,
            "stream": False,
            "options": {
                "temperature": 0.5,
                "num_ctx": 2048,
                "num_predict": 800
            }
        }

        try:
            res = requests.post(f"{self.endpoint}/api/chat", json=payload, timeout=60)
            if res.status_code != 200:
                return f"Error from Ollama: {res.text}"

            resp_data = res.json()
            message = resp_data.get("message", {})
            thinking = message.get("thinking", "")
            if thinking:
                safe_print(f"\n  [🧠 QWEN'S OWN THOUGHTS]:\n  " + thinking.replace("\n", "\n  ") + "\n")

            tool_calls = message.get("tool_calls", [])

            # If Qwen didn't call any tools, return its direct text
            if not tool_calls:
                return message.get("content", "").strip()

            # Execute tools that Qwen requested
            messages.append(message)
            for tool in tool_calls:
                fn = tool.get("function", {})
                name = fn.get("name")
                args = fn.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {}

                tool_result = self._execute_tool(name, args)
                messages.append({
                    "role": "tool",
                    "content": tool_result
                })

            # Iteration 2: Send tool results back to Qwen for final Hinglish synthesis
            safe_print("  [⚙️ SYNTHESIZING] Qwen processing tool results into final answer...\n")
            followup_payload = {
                "model": self.model_name,
                "messages": messages,
                "think": False,
                "stream": False,
                "options": {
                    "temperature": 0.4,
                    "num_ctx": 2048,
                    "num_predict": 600
                }
            }

            final_res = requests.post(f"{self.endpoint}/api/chat", json=followup_payload, timeout=60)
            if final_res.status_code == 200:
                final_msg = final_res.json().get("message", {})
                final_text = final_msg.get("content", "").strip()
                if final_text:
                    return final_text

            # If model didn't return text, return the actual last tool result
            last_tool_output = messages[-1].get("content", "")
            return f"Bhai command execute hui, output ye raha:\n\n{last_tool_output}"

        except Exception as e:
            return f"Agent execution error: {str(e)}"
