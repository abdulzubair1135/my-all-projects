"""
browser_bridge.py - Chromium Connection & DeepSeek Extraction

Connects to persistent Chromium instance over Chrome DevTools Protocol (CDP port 9222)
or persistent profile, submits topic prompt with strict JSON schema enforcement,
extracts and parses scene-by-scene storyboard, and provides local offline fallback.
"""

from __future__ import annotations
import json
import re
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.core.logging_manager import get_logger

logger = get_logger("browser_bridge")

STRICT_DEEPSEEK_PROMPT = """You are an expert animated stickman video director and scriptwriter.
Topic: "{topic}"
Language: {language} (conversational and engaging)
Target Duration: {duration} seconds

Create an entertaining, scene-by-scene stickman story storyboard.
You MUST output ONLY a valid raw JSON array conforming strictly to this schema:
[
  {{
    "scene_id": 1,
    "visual_prompt": "stickman standing confused looking at a broken screen, minimalist line art, clean vector, pure white background",
    "voiceover": "Kya aapka computer bhi aise hi crash hota hai?",
    "estimated_seconds": 4
  }}
]

Rules:
1. Generate between 3 to 6 progressive scenes (Beginning, Conflict, Climax, Ending).
2. "visual_prompt" must describe stickman action and simple props on pure white background.
3. "voiceover" must be in {language}.
4. Return ONLY the raw JSON array. Do not include markdown codeblocks or conversational text.
"""


class SceneItem(BaseModel):
    scene_id: int
    visual_prompt: str
    voiceover: str
    estimated_seconds: float = Field(default=4.0, ge=1.0, le=60.0)


def extract_json_array(text: str) -> Optional[List[Dict[str, Any]]]:
    """Extract and parse a JSON array from raw model text."""
    clean = text.strip()
    # Remove markdown code fences if present
    fence_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", clean, re.DOTALL)
    if fence_match:
        clean = fence_match.group(1).strip()
    else:
        bracket_match = re.search(r"(\[.*\])", clean, re.DOTALL)
        if bracket_match:
            clean = bracket_match.group(1).strip()

    # Attempt standard parse
    try:
        data = json.loads(clean)
        if isinstance(data, list) and len(data) > 0:
            return data
    except Exception:
        # Trailing comma cleanup
        repaired = re.sub(r",\s*([\]\}])", r"\1", clean)
        try:
            data = json.loads(repaired)
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception:
            pass
    return None


class BrowserBridge:
    """Manages CDP connection to running Chromium and extracts DeepSeek responses."""

    def __init__(self, cdp_url: str = "http://127.0.0.1:9222"):
        self.cdp_url = cdp_url

    def is_cdp_available(self) -> bool:
        """Check if remote debugging port 9222 is responding."""
        import urllib.request
        try:
            with urllib.request.urlopen(f"{self.cdp_url}/json/version", timeout=1.5) as response:
                return response.status == 200
        except Exception:
            return False

    def query_deepseek(
        self,
        topic: str,
        language: str = "hinglish",
        duration: int = 20,
        timeout_seconds: int = 90,
    ) -> Optional[List[Dict[str, Any]]]:
        """Query DeepSeek via CDP (port 9222) if available, or direct Chromium browser."""
        if self.is_cdp_available():
            res = self.query_deepseek_cdp(topic=topic, language=language, duration=duration, timeout_seconds=timeout_seconds)
            if res:
                return res

        return self.query_deepseek_direct_chromium(topic=topic, language=language, duration=duration, timeout_seconds=timeout_seconds)

    def query_deepseek_direct_chromium(
        self,
        topic: str,
        language: str = "hinglish",
        duration: int = 20,
        timeout_seconds: int = 90,
    ) -> Optional[List[Dict[str, Any]]]:
        """Launch Chromium with persistent profile to query DeepSeek directly."""
        import os
        from playwright.sync_api import sync_playwright

        profile_dir = os.path.expandvars(r"%LOCALAPPDATA%\StickForgeAI\deepseek_profile")
        os.makedirs(profile_dir, exist_ok=True)
        prompt = STRICT_DEEPSEEK_PROMPT.format(topic=topic, language=language, duration=duration)

        try:
            with sync_playwright() as p:
                logger.info("Opening Chromium for DeepSeek AI...")
                context = p.chromium.launch_persistent_context(
                    user_data_dir=profile_dir,
                    headless=False,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = context.pages[0] if context.pages else context.new_page()
                page.goto("https://chat.deepseek.com", timeout=30000)
                time.sleep(2.0)

                # Check if login is required
                if "sign_in" in page.url or "login" in page.url:
                    logger.info("DeepSeek sign-in detected. Please log in on the browser window (waiting 15s)...")
                    logged_in = False
                    for _ in range(15):
                        time.sleep(1.0)
                        if "sign_in" not in page.url and "login" not in page.url:
                            logged_in = True
                            break
                    if not logged_in:
                        logger.info("DeepSeek login pending. Handing off to fast local AI (Qwen)...")
                        context.close()
                        return None

                # Locate chat input
                input_selectors = [
                    "textarea#chat-input",
                    "textarea[placeholder*='DeepSeek']",
                    "textarea[placeholder*='Send a message']",
                    "div[contenteditable='true']",
                    "textarea",
                ]
                chat_box = None
                for sel in input_selectors:
                    loc = page.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        chat_box = loc.first
                        break

                if not chat_box:
                    logger.info("DeepSeek input not accessible. Handing off to fast local AI (Qwen)...")
                    context.close()
                    return None

                logger.info(f"Submitting '{topic}' to DeepSeek...")
                chat_box.click()
                chat_box.fill(prompt)
                time.sleep(0.5)
                page.keyboard.press("Enter")

                # Monitor generation
                logger.info("Awaiting DeepSeek response completion...")
                start_time = time.time()
                last_text = ""
                stable_cycles = 0

                while time.time() - start_time < timeout_seconds:
                    time.sleep(2.0)

                    # Extract current message bubbles
                    bubbles = page.locator(".markdown, .ds-markdown, div[class*='message-content']")
                    if bubbles.count() > 0:
                        current_text = bubbles.last.inner_text().strip()
                        if current_text and current_text == last_text:
                            stable_cycles += 1
                            if stable_cycles >= 2:
                                parsed = extract_json_array(current_text)
                                if parsed:
                                    logger.info(f"Extracted {len(parsed)} scenes from DeepSeek response.")
                                    context.close()
                                    return parsed
                        else:
                            last_text = current_text
                            stable_cycles = 0

                    stop_btn = page.locator("button[aria-label*='Stop'], div[class*='stop']")
                    if stop_btn.count() == 0 and last_text:
                        parsed = extract_json_array(last_text)
                        if parsed:
                            context.close()
                            return parsed

                context.close()
        except Exception as e:
            logger.info(f"DeepSeek browser notice: {e}")
        return None

    def query_deepseek_cdp(
        self,
        topic: str,
        language: str = "hinglish",
        duration: int = 20,
        timeout_seconds: int = 90,
    ) -> Optional[List[Dict[str, Any]]]:
        """Connect to Chrome via CDP, submit prompt, and extract JSON array."""
        from playwright.sync_api import sync_playwright

        if not self.is_cdp_available():
            logger.info("CDP endpoint (127.0.0.1:9222) not detected.")
            return None

        prompt = STRICT_DEEPSEEK_PROMPT.format(topic=topic, language=language, duration=duration)

        try:
            with sync_playwright() as p:
                logger.info(f"Connecting to Chrome over CDP at {self.cdp_url}...")
                browser = p.chromium.connect_over_cdp(self.cdp_url)
                context = browser.contexts[0] if browser.contexts else browser.new_context()

                # Find DeepSeek page or create one
                target_page = None
                for page in context.pages:
                    if "deepseek.com" in page.url:
                        target_page = page
                        break

                if not target_page:
                    target_page = context.new_page()
                    target_page.goto("https://chat.deepseek.com", wait_until="domcontentloaded", timeout=30000)
                    time.sleep(2.0)

                # Locate chat input
                input_selectors = [
                    "textarea#chat-input",
                    "textarea[placeholder*='DeepSeek']",
                    "textarea[placeholder*='Send a message']",
                    "div[contenteditable='true']",
                    "textarea",
                ]

                chat_box = None
                for sel in input_selectors:
                    loc = target_page.locator(sel)
                    if loc.count() > 0 and loc.first.is_visible():
                        chat_box = loc.first
                        break

                if not chat_box:
                    logger.warning("DeepSeek chat input not found (login or challenge page may be active).")
                    return None

                # Focus and fill prompt
                logger.info("Injecting prompt into DeepSeek chat input...")
                chat_box.click()
                chat_box.fill(prompt)
                time.sleep(0.5)
                target_page.keyboard.press("Enter")

                # Monitor generation
                logger.info("Awaiting DeepSeek response completion...")
                start_time = time.time()
                last_text = ""
                stable_cycles = 0

                while time.time() - start_time < timeout_seconds:
                    time.sleep(2.0)

                    # Check for Continue button if long generation
                    continue_btn = target_page.locator("button:has-text('Continue'), div[role='button']:has-text('Continue')")
                    if continue_btn.count() > 0 and continue_btn.first.is_visible():
                        logger.info("Clicking DeepSeek 'Continue' button...")
                        continue_btn.first.click()
                        time.sleep(1.0)

                    # Extract current message bubbles
                    bubbles = target_page.locator(".markdown, .ds-markdown, div[class*='message-content']")
                    if bubbles.count() > 0:
                        current_text = bubbles.last.inner_text().strip()
                        if current_text and current_text == last_text:
                            stable_cycles += 1
                            if stable_cycles >= 2:  # 4 seconds without text change
                                parsed = extract_json_array(current_text)
                                if parsed:
                                    logger.info(f"Extracted {len(parsed)} scenes from DeepSeek response.")
                                    return parsed
                        else:
                            last_text = current_text
                            stable_cycles = 0

                    # Check if stop button disappeared
                    stop_btn = target_page.locator("button[aria-label*='Stop'], div[class*='stop']")
                    if stop_btn.count() == 0 and last_text:
                        parsed = extract_json_array(last_text)
                        if parsed:
                            return parsed

        except Exception as e:
            logger.warning(f"DeepSeek CDP automation notice: {e}")

        return None

    def query_ollama(
        self,
        topic: str,
        language: str = "hinglish",
        duration: int = 20,
        timeout_seconds: int = 60,
    ) -> Optional[List[Dict[str, Any]]]:
        """Query local Ollama instance running Qwen with thinking mode disabled for instant response."""
        import urllib.request
        try:
            req_check = urllib.request.Request("http://127.0.0.1:11434/api/tags")
            with urllib.request.urlopen(req_check, timeout=2.0) as r:
                if r.status != 200:
                    return None
        except Exception:
            return None

        logger.info("Local Ollama service detected. Querying Qwen model for story...")
        prompt = (
            f"You are a viral comedy stickman animator. Write a hilarious 4-scene stickman story about '{topic}' in natural {language}.\n"
            f"Output strictly a JSON array containing 4 scene objects.\n"
            f"Format:\n"
            f"[\n"
            f'  {{"scene_id": 1, "visual_prompt": "stickman blank at exam desk staring at question paper in panic", "voiceover": "Exam hall me ghuste hi dimaag ka sara syllabus format ho gaya!", "camera_action": "zoom_in", "cue_word": "format", "estimated_seconds": 6.0}},\n'
            f'  {{"scene_id": 2, "visual_prompt": "stickman stretching neck whispering to topper friend for help", "voiceover": "Aage baithe topper dost se umeed ki kiran dikhi—bhai teesra bata de!", "camera_action": "pan_right", "cue_word": "topper", "estimated_seconds": 6.0}},\n'
            f'  {{"scene_id": 3, "visual_prompt": "strict eagle eye invigilator teacher staring with fiery glare", "voiceover": "Tabhi khadoos invigilator ki eagle eye hamari taraf ghoom gayi!", "camera_action": "shake", "cue_word": "eagle", "estimated_seconds": 6.0}},\n'
            f'  {{"scene_id": 4, "visual_prompt": "stickman wearing cool black sunglasses walking with pure swag", "voiceover": "Aakhir me roll number likh kar pure swag ke saath paper submit kar diya!", "camera_action": "zoom_out", "cue_word": "swag", "estimated_seconds": 6.0}}\n'
            f"]"
        )
        payload = {
            "model": "qwen3.5:4b",
            "prompt": prompt,
            "think": False,
            "format": "json",
            "stream": False,
            "options": {"num_predict": 750, "temperature": 0.75},
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:11434/api/generate",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=timeout_seconds) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                response_text = result.get("response", "")
                parsed = extract_json_array(response_text)
                if parsed:
                    logger.info(f"Successfully generated {len(parsed)} scenes via Ollama Qwen.")
                    return parsed
        except Exception as e:
            logger.warning(f"Ollama generation fallback note: {e}")
        return None

    def generate_storyboard(
        self,
        topic: str,
        language: str = "hinglish",
        duration: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Primary entry point: Attempts DeepSeek CDP extraction first;
        then queries local Ollama Qwen;
        falls back to rich topic-specific humor generator.
        """
        # 1. Try DeepSeek (Port 9222 CDP or Direct Chromium Playwright)
        deepseek_result = self.query_deepseek(topic=topic, language=language, duration=duration)
        if deepseek_result:
            return self._validate_and_format(deepseek_result)

        # 2. Try Ollama Qwen
        ollama_result = self.query_ollama(topic=topic, language=language, duration=duration)
        if ollama_result:
            return self._validate_and_format(ollama_result)

        # 3. Rich Topic-Specific Dynamic Script Generator (NO GENERIC PLACEHOLDERS)
        logger.info(f"Generating rich topic-specific stickman script for: '{topic}'...")
        return self._local_dynamic_fallback(topic=topic, language=language, duration=duration)

    def _local_dynamic_fallback(
        self,
        topic: str,
        language: str = "hinglish",
        duration: int = 20,
    ) -> List[Dict[str, Any]]:
        """Procedurally crafts context-aware scenes adhering strictly to the required schema."""
        from app.ai.ai_provider import MockAIProvider

        mock_provider = MockAIProvider()
        script = mock_provider.generate_story(
            topic=topic,
            genre="comedy",
            language=language,
            duration_target=float(duration),
        )

        import re
        t_lower = topic.lower()
        is_mom_topic = bool(re.search(r'\b(mom|mummy|maa|mother)\b', t_lower))
        scenes: List[Dict[str, Any]] = []

        for idx, beat in enumerate(script.beats):
            # Generate custom visual prompts matching the actual beat summary and topic
            b_name = beat.beat_name.lower()
            summary = beat.summary

            if is_mom_topic:
                if "beginning" in b_name or idx == 0:
                    vis = "stickman relaxing chill on sofa looking at phone, minimalist line art on pure white canvas"
                    action, cue = "zoom_in", "sofa"
                elif "conflict" in b_name or idx == 1:
                    vis = "angry mom stickman pointing angrily with hands on hips at messy room, clean line art on white background"
                    action, cue = "shake", "gussa"
                elif "climax" in b_name or idx == 2:
                    vis = "stickman running in panic dodging a flying chappal slipper in the air, dynamic motion lines on white canvas"
                    action, cue = "shake", "chappal"
                else:
                    vis = "stickman holding broom and sweeping floor with an innocent nervous smile, clean vector stick figure"
                    action, cue = "zoom_out", "jhadu"
            else:
                vis = f"stickman {summary}, clean minimalist black ink vector art on solid white canvas"
                action = "shake" if idx == 2 else ("zoom_in" if idx == 0 else "static")
                cue = ""

            scenes.append(
                {
                    "scene_id": idx + 1,
                    "visual_prompt": vis,
                    "voiceover": beat.narration,
                    "camera_action": action,
                    "cue_word": cue,
                    "estimated_seconds": round(beat.estimated_duration, 1),
                }
            )

        return scenes

    def _validate_and_format(self, raw_scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure all required keys exist and types conform to SceneItem."""
        validated = []
        for idx, item in enumerate(raw_scenes):
            validated.append(
                {
                    "scene_id": int(item.get("scene_id", idx + 1)),
                    "visual_prompt": str(item.get("visual_prompt", "stickman standing on white background")),
                    "voiceover": str(item.get("voiceover", "...")),
                    "camera_action": str(item.get("camera_action", "static")),
                    "cue_word": str(item.get("cue_word", "")),
                    "estimated_seconds": float(item.get("estimated_seconds", 4.0)),
                }
            )
        return validated
