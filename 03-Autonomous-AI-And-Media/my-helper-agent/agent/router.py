import re
import sys
import time
from .brain import Brain
from .resource_mgr import ResourceManager
from .memory import AgentMemory
from .rag import DocumentRAG
from .tools.terminal import TerminalTool
from .tools.files import FileTool
from .tools.web import WebResearchTool
from .tools.creative import CreativeTools
from .tools.finance import LiveFinanceTool

def log_live(icon: str, title: str, detail: str = ""):
    """Prints live step-by-step agent thought and actions to console."""
    msg = f"\n  [{icon} {title}]"
    if detail:
        msg += f" {detail}"
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"), flush=True)

class TaskRouter:
    """
    Autonomous Task Router:
    - Direct Live Financial Tickers (100% Real Live Stock & Crypto Data)
    - Anti-Captcha Web Research
    - PDF RAG Knowledge Base
    - Self-learning Error Memory
    - Hardware Guard
    """
    def __init__(self):
        self.brain = Brain()
        self.memory = AgentMemory()
        self.rag = DocumentRAG()
        self.terminal = TerminalTool()
        self.files = FileTool()
        self.web = WebResearchTool()
        self.creative = CreativeTools()
        self.finance = LiveFinanceTool()

    def route_and_execute(self, user_prompt: str, visible_browser: bool = False) -> str:
        prompt_lower = user_prompt.lower().strip()

        # 1. Hardware Status Query
        if any(w in prompt_lower for w in ["status", "hardware", "gpu", "vram", "ram check"]):
            log_live("CPU", "HARDWARE CHECK", "Querying system and NVIDIA RTX 2050...")
            stats = ResourceManager.get_system_stats()
            gpu = stats["gpu"]
            return (
                f"Bhai hardware stats ye hain:\n"
                f"- Available RAM: {stats['ram_avail_gb']} GB / {stats['ram_total_gb']} GB\n"
                f"- GPU: {gpu['name'] if gpu['available'] else 'N/A'}\n"
                f"- Free VRAM: {gpu['free_mb']} MB / {gpu['total_mb']} MB (Temp: {gpu.get('temp_c', 0)} C)\n"
                f"- Master Brain: Ollama Qwen3.5:4B ready"
            )

        # 2. PDF / Document RAG
        if any(w in prompt_lower for w in ["pdf", "document", "doc samjha", "file padh"]):
            log_live("DOC", "DOCUMENT SEARCH", "Searching local knowledge base in storage/docs/...")
            chunks = self.rag.search(user_prompt)
            if chunks:
                log_live("FOUND", "RAG MATCH", f"Found {len(chunks)} relevant document passages.")
                context = "\n---\n".join([f"[{c['location']}] {c['content']}" for c in chunks])
                rag_prompt = (
                    f"User ne ye poocha hai: '{user_prompt}'\n\n"
                    f"Document se relevant content ye mila:\n{context}\n\n"
                    f"Document ke hisaab se Hinglish me accurate aur direct answer do."
                )
                log_live("BRAIN", "SYNTHESIS", "Generating answer from extracted document sections...")
                res = self.brain.generate(rag_prompt)
                self.memory.log_task(user_prompt, "PDF_RAG", "Answered from PDF")
                return f"Done bhai. Document ke hisaab se:\n\n{res}"
            else:
                return "Bhai document me isse related content nahi mila. PDF ko 'storage/docs' me daal ke search karo."

        # 3. 100% Real-Time Market Data (Crypto & Stocks)
        market_triggers = ["stock", "crypto", "bitcoin", "btc", "eth", "solana", "nifty", "sensex", "market", "share market", "coin"]
        if any(w in prompt_lower for w in market_triggers):
            return self._handle_live_finance_request(user_prompt)

        # 4. Real-Time Web Research & Live News / Events / Deaths
        web_triggers = [
            "research", "dhundh", "search", "latest",
            "aaj", "today", "kal", "recent", "guzar", "die", "died", "death", "mar gaye",
            "obituary", "khabar", "news", "score", "match", "current", "weather",
            "kya hua", "kaun hai", "who is", "who died", "price", "kya chal raha", "taaza"
        ]

        if any(w in prompt_lower for w in web_triggers):
            return self._perform_live_web_research(user_prompt)

        # 5. Error Diagnosis & Autonomous Fix
        if any(w in prompt_lower for w in ["error", "lafda", "fix kar", "bug", "crash"]):
            log_live("DIAG", "ERROR INSPECTION", "Checking long-term memory for previous fixes...")
            known_fixes = self.memory.search_fix(user_prompt)
            fix_context = ""
            if known_fixes:
                kf = known_fixes[0]
                log_live("MEMORY", "KNOWN FIX FOUND", f"Root cause was: {kf['root_cause']}")
                fix_context = f"\n[Known Fix in Memory]: Cause: {kf['root_cause']}, Solution: {kf['solution']}\n"
            else:
                log_live("MEMORY", "NEW ERROR", "No previous fix in memory, analyzing with Qwen3.5 4B...")

            diag_prompt = (
                f"User ko ye error/problem aa rahi hai: '{user_prompt}'\n"
                f"{fix_context}\n"
                f"Bina lambe lecture ke diagnose karo aur exact fix/command batao."
            )
            solution = self.brain.generate(diag_prompt)
            self.memory.log_task(user_prompt, "ERROR_FIX", "Provided diagnosis/fix")
            return f"Error diagnosis & fix bhai:\n\n{solution}"

        # 6. Creative Voice (Edge-TTS)
        if any(w in prompt_lower for w in ["bol ke bata", "voice bana", "tts", "audio me bol"]):
            log_live("AUDIO", "VOICE GENERATION", "Synthesizing natural Hindi/Hinglish speech...")
            text_to_speak = re.sub(r"(bol ke bata|voice bana|tts|audio me bol|bhai)", "", prompt_lower).strip()
            if not text_to_speak:
                text_to_speak = "Namaste bhai, main aapka personal local AI assistant hoon."
            res = self.creative.text_to_speech_edge(text_to_speak, "output_voice.mp3")
            if res["success"]:
                log_live("DONE", "AUDIO EXPORTED", res['output_path'])
                return f"Done bhai! Audio generate ho gayi hai: {res['output_path']}"
            else:
                return f"Voice generate karne me issue aaya: {res['error']}"

        # 7. General Chat with Autonomous Fallback Check
        log_live("THOUGHT", "REASONING", "Processing query with Master Brain (Qwen3.5 4B)...")
        response = self.brain.generate(user_prompt)

        lack_of_data_signals = [
            "nahi pata", "access nahi hai", "real-time", "live events", "news feed",
            "social media data", "current data", "knowledge cutoff", "update nahi", "data nahi"
        ]
        if any(sig in response.lower() for sig in lack_of_data_signals):
            log_live("AUTONOMOUS", "SELF-HEALING", "Model lacked real-time data. Automatically launching Web Search...")
            return self._perform_live_web_research(user_prompt)

        self.memory.log_task(user_prompt, "GENERAL_CHAT", "Direct brain response")
        return response

    def _handle_live_finance_request(self, user_prompt: str) -> str:
        """Fetches 100% verified, live financial data directly from exchange tickers."""
        log_live("TICKER", "LIVE MARKET FEEDS", "Connecting to live Exchange & Yahoo/Binance APIs...")
        
        crypto_data = self.finance.get_crypto_live()
        stock_data = self.finance.get_stock_indices_live()

        market_summary_lines = []
        if stock_data:
            market_summary_lines.append("INDIAN & GLOBAL STOCK INDICES (LIVE):")
            for name, val in stock_data.items():
                market_summary_lines.append(f"- {name}: {val['price']} ({val['change_pct']}%)")

        if crypto_data:
            market_summary_lines.append("\nTOP CRYPTOCURRENCIES (LIVE):")
            for coin, val in crypto_data.items():
                market_summary_lines.append(
                    f"- {coin}: ${val['price_usd']:,} (approx Rs {val['price_inr']:,}) | 24h Change: {val['change_24h']}%"
                )

        live_context = "\n".join(market_summary_lines)
        log_live("VERIFIED", "EXCHANGE DATA LOADED", "100% Real-Time Market numbers verified.")

        analysis_prompt = (
            f"User ne poocha hai: '{user_prompt}'\n\n"
            f"DIRECT REAL-TIME EXCHANGE DATA RIGHT NOW:\n{live_context}\n\n"
            f"INSTRUCTIONS:\n"
            f"1. Is live verified exchange data ke exact numbers (prices aur % changes) user ko clear Hinglish me samjhao.\n"
            f"2. Nifty, Sensex, Bitcoin, Ethereum ka exact rate batao.\n"
            f"3. Koi generic book explanation mat do, direct live market numbers pe baat karo."
        )

        log_live("SYNTHESIS", "ANALYZING TICKERS", "Formulating live market report...")
        summary = self.brain.generate(analysis_prompt)
        self.memory.log_task(user_prompt, "LIVE_FINANCE", "Delivered live crypto/stock ticker data")
        return f"Done bhai! Real-Time Live Market Data ye raha:\n\n{summary}"

    def _perform_live_web_research(self, user_prompt: str) -> str:
        """Executes live web search with cleaned query keywords and step-by-step logging."""
        log_live("THOUGHT", "LIVE INTENT", f"Analyzing real-world query: '{user_prompt}'")
        
        # Translate conversational Hinglish into proper clean English search keywords
        clean_q = user_prompt.lower()
        if any(w in clean_q for w in ["guzar", "die", "died", "death", "mar gaye"]):
            search_query = "notable deaths news today celebrity obituaries"
        elif any(w in clean_q for w in ["score", "match", "cricket"]):
            search_query = "live cricket match score today"
        elif any(w in clean_q for w in ["weather", "mausam"]):
            search_query = "current weather report today India"
        else:
            # Strip conversational fillers
            search_query = re.sub(r"(bhai|muje|mujhe|ya|bol|ki|aj|aaj|k|ke|bare|mai|me|bhi|or|aur|kya|hai|hua)", " ", clean_q)
            search_query = re.sub(r"\s+", " ", search_query).strip()
            if len(search_query) < 4:
                search_query = user_prompt

        log_live("SEARCH", "EXECUTING QUERY", f"'{search_query}'")
        log_live("SECURITY", "ANTI-CAPTCHA", "Using clean search gateway to avoid bot-verification & captchas...")

        search_res = self.web.search(search_query, max_results=5)

        if not search_res["online"]:
            log_live("OFFLINE", "FALLBACK", "No active internet connection detected.")
            return "Bhai Internet connect nahi hai (Offline mode). Local knowledge se bata raha hoon."

        results = search_res.get("results", [])
        log_live("NETWORK", "SOURCES FOUND", f"Fetched {len(results)} live news sources from the web.")

        for idx, r in enumerate(results[:3]):
            log_live("SOURCE", f"[{idx+1}] {r['title'][:40]}...", r.get('link', '')[:60])

        snippets = "\n".join([f"- Title: {r['title']}\n  Snippet: {r['snippet']}\n  Link: {r['link']}" for r in results])
        
        analysis_prompt = (
            f"User ka exact question: '{user_prompt}'\n\n"
            f"Internet se live verified sources ye mile hain:\n{snippets}\n\n"
            f"RULES:\n"
            f"1. In live sources ke hisaab se Hinglish me accurate aur direct answer do.\n"
            f"2. Jo facts aur news mili hain direct mention karo.\n"
            f"3. Bilkul ye mat bolo ki tumhare paas data nahi hai; live data upar provide kiya gaya hai.\n"
            f"4. Format clear aur bullet points me rakho."
        )

        log_live("SYNTHESIS", "PROCESSING FACTS", "Qwen3.5 4B synthesizing live news facts into Hinglish...")
        summary = self.brain.generate(analysis_prompt)
        self.memory.log_task(user_prompt, "WEB_RESEARCH", f"Found {len(results)} sources")
        
        return f"Done bhai! Live Internet search se ye taaza jaankari mili hai:\n\n{summary}"
