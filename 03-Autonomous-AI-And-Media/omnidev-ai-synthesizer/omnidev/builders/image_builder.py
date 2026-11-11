import os
import re
import time
import requests
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional
from config import console

class ImageBuilder:
    """
    Generates high-resolution images from text prompts using AI image engines
    (Pollinations AI API, zero key required) and saves them locally.
    """
    def __init__(self, brain, output_dir: Path):
        self.brain = brain
        self.output_dir = Path(output_dir) / "images"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_image(
        self,
        prompt: str,
        filename: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        enhance_prompt: bool = True
    ) -> Dict[str, Any]:
        """
        Generates and saves image, then automatically opens preview.
        """
        console.print(f"[bold cyan]🎨 Generating AI image for:[/bold cyan] '{prompt}'")

        # Apply rich photographic enhancement keywords locally for instant 2-second generation
        if enhance_prompt and not any(k in prompt.lower() for k in ["8k", "photorealistic", "cinematic"]):
            final_prompt = f"{prompt}, photorealistic, 8k resolution, cinematic lighting, masterpiece, highly detailed"
        else:
            final_prompt = prompt

        # Use Pollinations AI API
        encoded_prompt = urllib.parse.quote(final_prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed=42"

        console.print("[magenta]Downloading generated AI image...[/magenta]")
        resp = requests.get(image_url, timeout=40)
        resp.raise_for_status()

        clean_slug = re.sub(r'[^a-zA-Z0-9]', '_', prompt.lower())[:25].strip('_') or 'art'
        safe_name = filename or f"img_{clean_slug}_{int(time.time())}.jpg"
        if not safe_name.endswith((".jpg", ".png")):
            safe_name += ".jpg"

        dest_file = self.output_dir / safe_name
        dest_file.write_bytes(resp.content)

        console.print(f"[bold green]✅ Image generated and saved at: {dest_file}[/bold green]")
        
        # Auto-open generated image for user in Windows default photo viewer
        try:
            os.startfile(str(dest_file))
            console.print(f"[cyan]🖼️ Opened image preview: {dest_file.name}[/cyan]")
        except Exception:
            pass

        return {
            "success": True,
            "filepath": str(dest_file),
            "url": image_url,
            "prompt_used": final_prompt
        }
