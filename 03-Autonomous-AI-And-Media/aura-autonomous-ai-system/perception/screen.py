"""
AURA Screen Perception Module.
Captures desktop screenshots and monitors screen changes with delta detection.
"""

import hashlib
from typing import Dict, Any, Optional
from pathlib import Path
from config import config
from core.logger import setup_logger

logger = setup_logger("ScreenCapturer")

class ScreenCapturer:
    def __init__(self):
        self.last_hash: Optional[str] = None
        self.screenshot_dir = config.storage.storage_dir if hasattr(config.storage, "storage_dir") else config.storage.logs_dir

    def capture_screen(self, filename: str = "current_screen.png") -> Dict[str, Any]:
        """
        Captures screen, calculates hash, and determines if screen meaningfully changed.
        """
        save_path = config.storage.logs_dir / filename
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            img.save(save_path)
            
            # Calculate fast pixel hash for change detection
            img_bytes = img.tobytes()
            curr_hash = hashlib.md5(img_bytes).hexdigest()
            changed = (self.last_hash != curr_hash)
            self.last_hash = curr_hash

            logger.info(f"Captured screenshot: {save_path.name} (changed: {changed})")
            return {
                "status": "success",
                "path": str(save_path),
                "changed": changed,
                "width": img.width,
                "height": img.height,
                "hash": curr_hash
            }
        except Exception as e:
            logger.warning(f"PIL ImageGrab not available or headless mode: {e}")
            return {
                "status": "fallback",
                "path": "",
                "changed": False,
                "width": 1920,
                "height": 1080,
                "hash": "mock_hash"
            }

screen_capturer = ScreenCapturer()
