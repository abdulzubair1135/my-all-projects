from typing import Optional, Any
from rich.console import Console
from .base_brain import BaseBrain
from .chrome_deepseek import ChromeDeepSeekBrain
from .chrome_gemini import ChromeGeminiBrain
from .api_fallback import ApiFallbackBrain

import config
from config import console

class BrainRouter(BaseBrain):
    """
    Intelligent router that chooses the best available intelligence source:
    1. Direct API (if user set API key)
    2. Chrome Gemini (ultra-fast Google AI Web Chat automation)
    3. Chrome DeepSeek (zero-cost Web Chat automation)
    """
    def __init__(self, preferred: Optional[str] = None):
        self.preferred = preferred or getattr(config, "DEFAULT_BRAIN", "deepseek")
        self.api_brain = ApiFallbackBrain()
        self.chrome_deepseek = ChromeDeepSeekBrain()
        self.chrome_gemini = ChromeGeminiBrain()
        self.active_brain: Optional[BaseBrain] = None

    def get_active_brain(self) -> BaseBrain:
        if self.active_brain:
            return self.active_brain

        # 1. Check if user configured direct API
        if self.preferred == "api" or (self.preferred == "auto" and self.api_brain.is_available()):
            console.print("[cyan]Using Direct API Engine[/cyan]")
            self.active_brain = self.api_brain
            return self.active_brain

        # 2. Try Chrome DeepSeek (Preferred Primary Engine)
        if self.preferred in ["deepseek", "auto"]:
            try:
                if self.chrome_deepseek.is_available():
                    console.print("[bold cyan]⚡ Active Intelligence Brain: DeepSeek Web (chat.deepseek.com)[/bold cyan]")
                    self.active_brain = self.chrome_deepseek
                    return self.active_brain
            except Exception as e:
                console.print(f"[yellow]DeepSeek Web connection failed: {e}[/yellow]")

        # 3. Try Chrome Gemini (Fallback / Fast Alternative)
        if self.preferred in ["gemini", "auto", "deepseek"]:
            try:
                if self.chrome_gemini.is_available():
                    console.print("[bold green]Active Intelligence Brain: Google Gemini Web[/bold green]")
                    self.active_brain = self.chrome_gemini
                    return self.active_brain
            except Exception as e:
                console.print(f"[yellow]Gemini Web connection failed: {e}[/yellow]")

        # Default fallback
        self.active_brain = self.chrome_deepseek if self.preferred == "deepseek" else self.chrome_gemini
        return self.active_brain

    def ask(self, prompt: str, new_chat: bool = False, file_to_attach: Optional[Any] = None, image_to_attach: Optional[Any] = None) -> str:
        brain = self.get_active_brain()
        try:
            # Check if brain supports new_chat/file_to_attach/image_to_attach arguments
            import inspect
            sig = inspect.signature(brain.ask)
            kwargs = {}
            if "new_chat" in sig.parameters:
                kwargs["new_chat"] = new_chat
            if "file_to_attach" in sig.parameters:
                kwargs["file_to_attach"] = file_to_attach
            if "image_to_attach" in sig.parameters:
                kwargs["image_to_attach"] = image_to_attach
            return brain.ask(prompt, **kwargs)
        except Exception as e:
            console.print(f"[yellow]Primary brain failed ({e}). Attempting fallback...[/yellow]")
            # Attempt fallback to Gemini or API
            if brain != self.api_brain and self.api_brain.is_available():
                return self.api_brain.ask(prompt)
            raise e

    def is_available(self) -> bool:
        try:
            b = self.get_active_brain()
            return b.is_available()
        except Exception:
            return False
