"""
engine.py - Voiceover, Stickman Visual Generation & Headless FFmpeg Assembly

Modules:
1. Audio Engine: Synthesizes narration via edge-tts (or Windows SAPI5 offline fallback),
   measures exact duration using mutagen.
2. Visual Engine: Queries local Stable Diffusion WebUI API (127.0.0.1:7860/sdapi/v1/txt2img)
   with stickman negative/positive prompts; provides intelligent procedural vector renderer fallback.
3. Video Assembly: Headless FFmpeg stitching that synchronizes frame duration to audio duration
   and outputs final_stickman_story.mp4.
"""

from __future__ import annotations
import base64
import json
import math
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import requests
from PIL import Image, ImageDraw, ImageFont

from app.core.logging_manager import get_logger
from app.video.ffmpeg_manager import get_ffmpeg_binary, run_ffmpeg_command, probe_media

logger = get_logger("engine")


# =====================================================================
# 1. AUDIO ENGINE (TTS & Duration Inspection)
# =====================================================================

class AudioEngine:
    """Handles speech synthesis and exact audio duration measurement."""

    def __init__(self, voice_hi: str = "hi-IN-MadhurNeural", voice_en: str = "en-US-ChristopherNeural"):
        self.voice_hi = voice_hi
        self.voice_en = voice_en

    def synthesize_scene_audio(self, text: str, output_path: Path, language: str = "hinglish") -> float:
        """
        Synthesize text to output_path (.mp3) using edge-tts or offline fallback.
        Returns the exact audio duration in seconds.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        chosen_voice = self.voice_hi if ("hi" in language.lower() or "hing" in language.lower()) else self.voice_en

        success = False
        try:
            import asyncio
            import edge_tts

            async def _run():
                communicate = edge_tts.Communicate(text=text, voice=chosen_voice)
                await communicate.save(str(output_path))

            asyncio.run(_run())
            if output_path.exists() and output_path.stat().st_size > 500:
                success = True
        except Exception as e:
            logger.info(f"Edge-TTS synthesis unavailable ({e}). Using local offline speech engine...")

        if not success:
            # Fallback to local Windows SAPI5 via pyttsx3 or wave
            self._offline_sapi5_synthesize(text, output_path)

        duration = self.get_audio_duration(output_path)
        logger.info(f"Synthesized audio for: '{text[:30]}...' -> {duration:.2f}s ({output_path.name})")
        return duration

    def _offline_sapi5_synthesize(self, text: str, output_path: Path) -> None:
        """Synthesize WAV locally and transcode to MP3 using FFmpeg."""
        wav_temp = output_path.with_suffix(".tmp.wav")
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.save_to_file(text, str(wav_temp))
            engine.runAndWait()
        except Exception as e:
            logger.warning(f"pyttsx3 fallback exception: {e}")

        if wav_temp.exists() and wav_temp.stat().st_size > 100:
            run_ffmpeg_command(["-i", str(wav_temp), "-c:a", "libmp3lame", "-b:a", "192k", str(output_path)])
            wav_temp.unlink(missing_ok=True)
        else:
            # Generate clean synthetic silent/tone file of reasonable duration
            self._generate_synthetic_tone(text, output_path)

    def _generate_synthetic_tone(self, text: str, output_path: Path) -> None:
        import struct, wave
        est_dur = max(2.5, len(text.split()) / 2.8 + 0.5)
        wav_temp = output_path.with_suffix(".tone.wav")
        sample_rate = 22050
        num_samples = int(est_dur * sample_rate)

        with wave.open(str(wav_temp), "w") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sample_rate)
            data = bytearray()
            for i in range(num_samples):
                val = int(800.0 * (1.0 if (i // 50) % 2 == 0 else -1.0))
                data.extend(struct.pack("<h", val))
            f.writeframes(data)

        run_ffmpeg_command(["-i", str(wav_temp), "-c:a", "libmp3lame", "-b:a", "192k", str(output_path)])
        wav_temp.unlink(missing_ok=True)

    @staticmethod
    def get_audio_duration(file_path: Path) -> float:
        """Read exact audio duration using mutagen with probe fallback."""
        if not file_path.exists():
            return 3.0

        try:
            from mutagen.mp3 import MP3
            audio = MP3(str(file_path))
            if audio.info and audio.info.length > 0:
                return round(float(audio.info.length), 2)
        except Exception:
            pass

        try:
            from mutagen import File
            f = File(str(file_path))
            if f and f.info and getattr(f.info, "length", 0) > 0:
                return round(float(f.info.length), 2)
        except Exception:
            pass

        # Probe fallback
        info = probe_media(file_path)
        return max(1.0, info.get("duration", 3.0))


# =====================================================================
# 2. VISUAL ENGINE (SD WebUI API & Procedural Stickman Fallback)
# =====================================================================

class VisualEngine:
    """Generates minimalist stickman frames via ComfyUI, SD WebUI, or procedural vector renderer."""

    def __init__(
        self,
        sd_api_url: str = "http://127.0.0.1:7860/sdapi/v1/txt2img",
        comfyui_url: str = "http://127.0.0.1:8188",
        width: int = 1080,
        height: int = 1920,
    ):
        self.sd_api_url = sd_api_url
        self.comfyui_url = comfyui_url
        self.width = width
        self.height = height

    def generate_scene_frame(self, visual_prompt: str, output_path: Path) -> Path:
        """Generate scene visual using ComfyUI, SD WebUI API, or procedural vector stickman."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Attempt ComfyUI API (Port 8188)
        if self._try_comfyui(visual_prompt, output_path):
            logger.info(f"Rendered stickman visual via ComfyUI API: {output_path.name}")
            return output_path

        # 2. Attempt Stable Diffusion WebUI / Forge API (Port 7860)
        if self._try_sd_webui(visual_prompt, output_path):
            logger.info(f"Rendered stickman visual via SD WebUI API: {output_path.name}")
            return output_path

        # 3. Procedural Clean Vector Stickman Fallback
        logger.info(f"AI image generator (ComfyUI:8188 / SD-WebUI:7860) not active. Using clean comic vector stickman: {output_path.name}")
        self._procedural_vector_stickman(visual_prompt, output_path)
        return output_path

    def _try_comfyui(self, visual_prompt: str, output_path: Path) -> bool:
        """Call ComfyUI API on http://127.0.0.1:8188 if running."""
        try:
            chk = requests.get(f"{self.comfyui_url}/system_stats", timeout=1.0)
            if chk.status_code != 200:
                return False
        except Exception:
            return False

        logger.info("ComfyUI server detected on 127.0.0.1:8188. Sending prompt...")
        positive = f"{visual_prompt}, minimalist stick figure, clean black ink lines on solid white canvas, 2d vector doodle"
        negative = "colors, shading, 3d, realistic, gradients, complex background, text, watermark"

        workflow = {
            "3": {
                "inputs": {
                    "seed": int(time.time()),
                    "steps": 20,
                    "cfg": 7.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                },
                "class_type": "KSampler",
            },
            "4": {"inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"}, "class_type": "CheckpointLoaderSimple"},
            "5": {"inputs": {"width": 540, "height": 960, "batch_size": 1}, "class_type": "EmptyLatentImage"},
            "6": {"inputs": {"text": positive, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
            "7": {"inputs": {"text": negative, "clip": ["4", 1]}, "class_type": "CLIPTextEncode"},
            "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
            "9": {"inputs": {"filename_prefix": "stickforge", "images": ["8", 0]}, "class_type": "SaveImage"},
        }

        try:
            p_resp = requests.post(f"{self.comfyui_url}/prompt", json={"prompt": workflow}, timeout=5.0)
            if p_resp.status_code == 200:
                prompt_id = p_resp.json().get("prompt_id")
                for _ in range(40):
                    time.sleep(1.0)
                    h_resp = requests.get(f"{self.comfyui_url}/history/{prompt_id}", timeout=2.0)
                    if h_resp.status_code == 200:
                        h_data = h_resp.json().get(prompt_id, {})
                        outputs = h_data.get("outputs", {}).get("9", {}).get("images", [])
                        if outputs:
                            fname = outputs[0]["filename"]
                            subfolder = outputs[0].get("subfolder", "")
                            img_resp = requests.get(f"{self.comfyui_url}/view?filename={fname}&subfolder={subfolder}", timeout=10.0)
                            if img_resp.status_code == 200:
                                with open(output_path, "wb") as f:
                                    f.write(img_resp.content)
                                with Image.open(output_path) as im:
                                    resized = im.resize((self.width, self.height), Image.Resampling.LANCZOS)
                                    resized.save(output_path, format="PNG")
                                return True
        except Exception as e:
            logger.warning(f"ComfyUI generation note: {e}")
        return False

    def _try_sd_webui(self, visual_prompt: str, output_path: Path) -> bool:
        """Call txt2img on Automatic1111/Forge WebUI."""
        positive_prompt = f"{visual_prompt}, minimalist stick figure, clean black ink lines on solid white canvas, 2d vector doodle"
        negative_prompt = "colors, shading, 3d, realistic, gradients, complex background, text, watermark, signature, grey"

        payload = {
            "prompt": positive_prompt,
            "negative_prompt": negative_prompt,
            "steps": 20,
            "width": 540 if self.width <= 720 else 768,
            "height": 960 if self.height <= 1280 else 1344,
            "cfg_scale": 7.0,
            "sampler_name": "Euler a",
        }

        try:
            resp = requests.post(self.sd_api_url, json=payload, timeout=6.0)
            if resp.status_code == 200:
                data = resp.json()
                images = data.get("images", [])
                if images:
                    img_bytes = base64.b64decode(images[0])
                    with open(output_path, "wb") as f:
                        f.write(img_bytes)
                    # Resize to target canvas size
                    with Image.open(output_path) as im:
                        resized = im.resize((self.width, self.height), Image.Resampling.LANCZOS)
                        resized.save(output_path, format="PNG")
                    return True
        except Exception:
            pass
        return False

    def _procedural_vector_stickman(self, visual_prompt: str, output_path: Path) -> None:
        """Draws expressive, high-resolution comic-style stickman art with faces, props, and scene context."""
        w, h = self.width, self.height
        img = Image.new("RGB", (w, h), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        ink = (20, 24, 33)           # Deep comic ink
        line_w = max(10, int(w * 0.011))  # Bold expressive lines
        accent_red = (239, 68, 68)   # Alert red
        accent_blue = (59, 130, 246) # Electric blue
        accent_gold = (245, 158, 11) # Glowing gold
        accent_green = (16, 185, 129)# Victory green
        ground_gray = (226, 232, 240)

        # Baseline ground positioning
        ground_y = int(h * 0.74)
        draw.line([(int(w * 0.08), ground_y), (int(w * 0.92), ground_y)], fill=(203, 213, 225), width=max(4, line_w // 2))

        # Default centers
        cx = int(w * 0.5)
        cy = int(h * 0.50)
        hr = int(w * 0.085)  # Head radius

        v_lower = visual_prompt.lower()

        # Try to load Windows standard clean fonts (Arial/Calibri/Segoe UI)
        font_title = None
        font_sub = None
        try:
            font_title = ImageFont.truetype("segoeui.ttf", int(w * 0.042))
            font_sub = ImageFont.truetype("segoeuib.ttf", int(w * 0.032))
        except Exception:
            try:
                font_title = ImageFont.truetype("arial.ttf", int(w * 0.042))
                font_sub = ImageFont.truetype("arialbd.ttf", int(w * 0.032))
            except Exception:
                font_title = font_sub = ImageFont.load_default()

        # -------------------------------------------------------------
        # POSE 1: RUNNING / PANIC / FAST
        # -------------------------------------------------------------
        if any(k in v_lower for k in ["run", "bhaag", "panic", "rush", "fast", "danger", "bhago"]):
            # Ground shadow
            draw.ellipse([cx - 160, ground_y - 8, cx + 80, ground_y + 16], fill=ground_gray)

            # Head (tilted forward in sprint)
            hx, hy = cx - 30, cy - 180
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255), outline=ink, width=line_w)

            # Expressive Panic Face: Wide shock eyes & open screaming mouth
            draw.ellipse([hx - 24, hy - 18, hx - 8, hy + 2], fill=ink)
            draw.ellipse([hx + 8, hy - 18, hx + 24, hy + 2], fill=ink)
            draw.ellipse([hx - 14, hy + 12, hx + 14, hy + 38], fill=accent_red, outline=ink, width=max(3, line_w // 3))

            # Panic Sweat drops flying off forehead
            for sw_x, sw_y in [(hx - 45, hy - 40), (hx - 70, hy - 20), (hx - 55, hy + 10)]:
                draw.ellipse([sw_x, sw_y, sw_x + 14, sw_y + 22], fill=accent_blue)

            # Leaning torso
            hip = (cx + 20, cy + 90)
            draw.line([(hx, hy + hr), hip], fill=ink, width=line_w)

            # Sprinting arms (flailing backwards & forwards)
            draw.line([(cx - 10, cy - 60), (cx + 110, cy - 10)], fill=ink, width=line_w)
            draw.line([(cx - 10, cy - 60), (cx - 120, cy - 20), (cx - 170, cy + 30)], fill=ink, width=line_w)

            # Sprinting legs
            draw.line([hip, (cx + 120, cy + 180), (cx + 170, ground_y)], fill=ink, width=line_w)
            draw.line([hip, (cx - 100, cy + 150), (cx - 160, cy + 220)], fill=ink, width=line_w)

            # Speed dust clouds / motion dash lines
            for off in [-240, -200, -160]:
                draw.line([(cx + off, ground_y - 25), (cx + off + 35, ground_y - 25)], fill=(148, 163, 184), width=max(4, line_w // 2))
                draw.arc([cx + off, ground_y - 45, cx + off + 40, ground_y - 5], start=45, end=270, fill=(148, 163, 184), width=max(3, line_w // 3))

        # -------------------------------------------------------------
        # POSE 2: CELEBRATION / JUMPING / HAPPY / SUCCESS
        # -------------------------------------------------------------
        elif any(k in v_lower for k in ["jump", "udne", "celebrat", "happy", "success", "joy", "kamyabi"]):
            # Ground shadow (smaller because airborne)
            draw.ellipse([cx - 80, ground_y - 4, cx + 80, ground_y + 12], fill=ground_gray)

            # Head high in the air
            hx, hy = cx, cy - 240
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255), outline=ink, width=line_w)

            # Happy smiling face: Joyful curved eyes (^ ^) & broad grin
            draw.arc([hx - 28, hy - 22, hx - 6, hy], start=200, end=340, fill=ink, width=max(4, line_w // 2))
            draw.arc([hx + 6, hy - 22, hx + 28, hy], start=200, end=340, fill=ink, width=max(4, line_w // 2))
            draw.arc([hx - 22, hy - 5, hx + 22, hy + 35], start=10, end=170, fill=ink, width=max(4, line_w // 2))

            # Torso airborne
            hip = (cx, cy)
            draw.line([(hx, hy + hr), hip], fill=ink, width=line_w)

            # Victorious V-shaped arms raised high
            draw.line([(cx, cy - 130), (cx - 120, cy - 260), (cx - 160, cy - 310)], fill=ink, width=line_w)
            draw.line([(cx, cy - 130), (cx + 120, cy - 260), (cx + 160, cy - 310)], fill=ink, width=line_w)

            # Tucked legs mid-jump
            draw.line([hip, (cx - 70, cy + 90), (cx - 50, cy + 170)], fill=ink, width=line_w)
            draw.line([hip, (cx + 70, cy + 90), (cx + 50, cy + 170)], fill=ink, width=line_w)

            # Confetti & Celebration Stars
            confetti_colors = [accent_gold, accent_red, accent_blue, accent_green]
            for i, (cf_x, cf_y) in enumerate([
                (cx - 240, cy - 280), (cx + 250, cy - 290),
                (cx - 180, cy - 150), (cx + 200, cy - 130),
                (cx - 100, cy - 360), (cx + 110, cy - 370)
            ]):
                c_col = confetti_colors[i % len(confetti_colors)]
                draw.rectangle([cf_x, cf_y, cf_x + 18, cf_y + 18], fill=c_col)
                draw.line([(cf_x - 10, cf_y + 9), (cf_x + 28, cf_y + 9)], fill=c_col, width=3)

        # -------------------------------------------------------------
        # POSE 3: IDEA / SOLUTION / POINTING / LIGHTBULB
        # -------------------------------------------------------------
        elif any(k in v_lower for k in ["idea", "lightbulb", "brain", "think", "solution", "point", "samadhan"]):
            draw.ellipse([cx - 100, ground_y - 8, cx + 100, ground_y + 14], fill=ground_gray)

            hx, hy = cx, cy - 140
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255), outline=ink, width=line_w)

            # Confident smiling face with alert eyes
            draw.ellipse([hx - 22, hy - 14, hx - 8, hy], fill=ink)
            draw.ellipse([hx + 8, hy - 14, hx + 22, hy], fill=ink)
            draw.arc([hx - 18, hy, hx + 18, hy + 28], start=20, end=160, fill=ink, width=max(4, line_w // 2))

            hip = (cx, cy + 120)
            draw.line([(hx, hy + hr), hip], fill=ink, width=line_w)

            # Arm pointing straight up to lightbulb
            draw.line([(cx, cy - 50), (cx + 90, cy - 110), (cx + 100, cy - 230)], fill=ink, width=line_w)
            # Arm resting proudly on hip
            draw.line([(cx, cy - 50), (cx - 80, cy + 10), (cx - 40, cy + 50)], fill=ink, width=line_w)

            # Standing confident legs
            draw.line([hip, (cx - 65, ground_y)], fill=ink, width=line_w)
            draw.line([hip, (cx + 65, ground_y)], fill=ink, width=line_w)

            # Glowing Radiant Lightbulb
            lb_x, lb_y = cx + 110, cy - 300
            # Bulb body
            draw.ellipse([lb_x - 36, lb_y - 36, lb_x + 36, lb_y + 36], fill=accent_gold, outline=ink, width=line_w)
            draw.rectangle([lb_x - 16, lb_y + 32, lb_x + 16, lb_y + 54], fill=(100, 116, 139), outline=ink, width=max(3, line_w // 3))
            # Glowing rays
            for deg_dx, deg_dy in [(-55, 0), (55, 0), (0, -55), (-40, -40), (40, -40)]:
                draw.line([(lb_x + deg_dx // 2, lb_y + deg_dy // 2), (lb_x + deg_dx, lb_y + deg_dy)], fill=accent_gold, width=max(5, line_w // 2))

        # -------------------------------------------------------------
        # POSE 4: CONFUSED / COMPUTER CRASH / BROKEN SCREEN
        # -------------------------------------------------------------
        elif any(k in v_lower for k in ["confus", "broken", "screen", "crash", "shock", "computer", "problem"]):
            # Ground shadow under stickman and desk
            draw.ellipse([cx - 240, ground_y - 8, cx - 40, ground_y + 14], fill=ground_gray)
            draw.ellipse([cx + 60, ground_y - 8, cx + 320, ground_y + 14], fill=ground_gray)

            # Stickman standing on the left
            hx, hy = cx - 140, cy - 130
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255), outline=ink, width=line_w)

            # Confused / Shocked Face: Uneven eyes & wavy mouth
            draw.ellipse([hx - 24, hy - 16, hx - 10, hy - 2], fill=ink)
            draw.ellipse([hx + 8, hy - 22, hx + 26, hy - 4], fill=ink)
            # Wavy confused mouth
            draw.line([(hx - 20, hy + 20), (hx - 8, hy + 14), (hx + 4, hy + 24), (hx + 18, hy + 16)], fill=ink, width=max(4, line_w // 2))
            # Question marks near head
            draw.arc([hx - hr - 40, hy - 50, hx - hr - 10, hy - 20], start=180, end=360, fill=accent_red, width=max(4, line_w // 2))
            draw.line([(hx - hr - 10, hy - 35), (hx - hr - 25, hy - 15)], fill=accent_red, width=max(4, line_w // 2))
            draw.ellipse([hx - hr - 28, hy - 6, hx - hr - 22, hy], fill=accent_red)

            hip = (cx - 140, cy + 120)
            draw.line([(hx, hy + hr), hip], fill=ink, width=line_w)

            # Hands: one scratching head in disbelief, one pointing at screen
            draw.line([(cx - 140, cy - 40), (cx - 220, cy - 90), (hx - hr + 10, hy - 10)], fill=ink, width=line_w)
            draw.line([(cx - 140, cy - 40), (cx - 20, cy - 30)], fill=ink, width=line_w)

            # Legs
            draw.line([hip, (cx - 180, ground_y)], fill=ink, width=line_w)
            draw.line([hip, (cx - 100, ground_y)], fill=ink, width=line_w)

            # Desk & Broken Computer Monitor on the right
            desk_x = cx + 80
            # Monitor screen
            draw.rectangle([desk_x, cy - 140, desk_x + 220, cy + 30], fill=(241, 245, 249), outline=ink, width=line_w)
            # Monitor stand & base
            draw.line([desk_x + 110, cy + 30, desk_x + 110, cy + 90], fill=ink, width=line_w)
            draw.line([desk_x + 60, cy + 90, desk_x + 160, cy + 90], fill=ink, width=line_w)
            # Desk table
            draw.line([desk_x - 30, cy + 90, desk_x + 260, cy + 90], fill=ink, width=line_w)
            draw.line([desk_x, cy + 90, desk_x, ground_y], fill=ink, width=max(5, line_w // 2))
            draw.line([desk_x + 230, cy + 90, desk_x + 230, ground_y], fill=ink, width=max(5, line_w // 2))

            # Red Jagged Crack on Monitor Screen
            draw.line([desk_x + 40, cy - 120, desk_x + 110, cy - 60, desk_x + 80, cy - 10, desk_x + 170, cy + 15], fill=accent_red, width=max(5, line_w // 2))
            draw.line([desk_x + 110, cy - 60, desk_x + 160, cy - 80], fill=accent_red, width=max(4, line_w // 2))

            # Electric spark sparks flying out
            for sp_x, sp_y in [(desk_x + 120, cy - 170), (desk_x + 200, cy - 150)]:
                draw.line([(sp_x, sp_y), (sp_x + 10, sp_y + 15), (sp_x + 5, sp_y + 20), (sp_x + 20, sp_y + 35)], fill=accent_gold, width=4)

        # -------------------------------------------------------------
        # POSE: FLYING CHAPPAL / PANIC ESCAPE
        # -------------------------------------------------------------
        elif any(k in v_lower for k in ["chappal", "slipper", "flying"]):
            draw.ellipse([cx - 180, ground_y - 8, cx + 60, ground_y + 16], fill=ground_gray)
            hx, hy = cx - 40, cy - 180
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255), outline=ink, width=line_w)
            # Screaming panic face
            draw.ellipse([hx - 24, hy - 18, hx - 8, hy + 2], fill=ink)
            draw.ellipse([hx + 8, hy - 18, hx + 24, hy + 2], fill=ink)
            draw.ellipse([hx - 16, hy + 10, hx + 16, hy + 38], fill=accent_red, outline=ink, width=3)
            # Torso & running limbs
            hip = (cx + 20, cy + 90)
            draw.line([(hx, hy + hr), hip], fill=ink, width=line_w)
            draw.line([(cx - 10, cy - 60), (cx - 130, cy - 140)], fill=ink, width=line_w)
            draw.line([(cx - 10, cy - 60), (cx + 100, cy - 10)], fill=ink, width=line_w)
            draw.line([hip, (cx + 120, cy + 180), (cx + 170, ground_y)], fill=ink, width=line_w)
            draw.line([hip, (cx - 100, cy + 150), (cx - 160, cy + 220)], fill=ink, width=line_w)
            # Flying Chappal/Slipper in the air!
            ch_x, ch_y = cx + 180, cy - 240
            draw.ellipse([ch_x - 45, ch_y - 20, ch_x + 45, ch_y + 20], fill=accent_red, outline=ink, width=line_w)
            draw.line([(ch_x - 15, ch_y - 12), (ch_x + 15, ch_y + 12)], fill=ink, width=max(4, line_w // 2))
            for sw_off in [50, 90, 130]:
                draw.line([(ch_x + sw_off, ch_y - 10), (ch_x + sw_off + 35, ch_y - 10)], fill=(160, 160, 160), width=4)

        # -------------------------------------------------------------
        # POSE: BROOM / SWEEPING / CLEANING
        # -------------------------------------------------------------
        elif any(k in v_lower for k in ["broom", "sweep", "pocha", "jhadu", "clean"]):
            draw.ellipse([cx - 100, ground_y - 8, cx + 100, ground_y + 14], fill=ground_gray)
            hx, hy = cx - 20, cy - 140
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255), outline=ink, width=line_w)
            # Nervous smiling face
            draw.ellipse([hx - 20, hy - 14, hx - 8, hy], fill=ink)
            draw.ellipse([hx + 8, hy - 14, hx + 20, hy], fill=ink)
            draw.arc([hx - 16, hy + 4, hx + 16, hy + 26], start=20, end=160, fill=ink, width=max(4, line_w // 2))
            hip = (cx - 20, cy + 120)
            draw.line([(hx, hy + hr), hip], fill=ink, width=line_w)
            draw.line([hip, (cx - 70, ground_y)], fill=ink, width=line_w)
            draw.line([hip, (cx + 30, ground_y)], fill=ink, width=line_w)
            # Arms holding broom handle
            draw.line([(cx - 20, cy - 50), (cx + 50, cy + 10)], fill=ink, width=line_w)
            draw.line([(cx - 20, cy - 50), (cx + 70, cy + 30)], fill=ink, width=line_w)
            # Long broom stick down to ground
            draw.line([(cx + 40, cy - 80), (cx + 100, ground_y)], fill=(120, 53, 15), width=line_w)
            # Broom bristles
            draw.polygon([(cx + 80, ground_y), (cx + 140, ground_y), (cx + 110, ground_y - 35)], fill=accent_gold, outline=ink)

        # -------------------------------------------------------------
        # POSE: SOFA / CHILL / PHONE
        # -------------------------------------------------------------
        elif any(k in v_lower for k in ["sofa", "phone", "chill", "relax", "bed"]):
            # Sofa base
            draw.rectangle([cx - 220, cy + 30, cx + 220, cy + 150], fill=(226, 232, 240), outline=ink, width=line_w)
            draw.rectangle([cx - 220, cy - 60, cx - 160, cy + 30], fill=(203, 213, 225), outline=ink, width=line_w)
            draw.rectangle([cx + 160, cy - 60, cx + 220, cy + 30], fill=(203, 213, 225), outline=ink, width=line_w)
            hx, hy = cx - 40, cy - 80
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255), outline=ink, width=line_w)
            draw.ellipse([hx - 20, hy - 10, hx - 8, hy + 2], fill=ink)
            draw.ellipse([hx + 8, hy - 10, hx + 20, hy + 2], fill=ink)
            draw.arc([hx - 14, hy + 6, hx + 14, hy + 24], start=10, end=170, fill=ink, width=4)
            hip = (cx - 20, cy + 70)
            draw.line([(hx, hy + hr), hip], fill=ink, width=line_w)
            # Legs relaxed on sofa
            draw.line([hip, (cx + 100, cy + 70), (cx + 120, cy + 120)], fill=ink, width=line_w)
            # Hands holding mobile phone
            draw.line([(cx - 30, cy - 10), (cx + 20, cy + 10)], fill=ink, width=line_w)
            # Smartphone
            draw.rectangle([cx + 18, cy - 15, cx + 38, cy + 25], fill=accent_blue, outline=ink, width=max(3, line_w // 3))

        # -------------------------------------------------------------
        # POSE: EXAM / DESK / PAPER / BLANK / SYLLABUS
        # -------------------------------------------------------------
        elif any(k in v_lower for k in ["exam", "desk", "paper", "blank", "syllabus", "test"]):
            # Ground shadow
            draw.ellipse([cx - 200, ground_y - 8, cx + 200, ground_y + 14], fill=ground_gray)
            # School Wooden Desk
            desk_l, desk_r = cx - 180, cx + 180
            desk_t = cy + 40
            draw.rectangle([desk_l, desk_t, desk_r, desk_t + 25], fill=(217, 119, 6), outline=ink, width=line_w)
            draw.line([(desk_l + 30, desk_t + 25), (desk_l + 30, ground_y)], fill=ink, width=line_w)
            draw.line([(desk_r - 30, desk_t + 25), (desk_r - 30, ground_y)], fill=ink, width=line_w)
            # Question paper on desk with big '?'
            draw.rectangle([cx - 50, desk_t - 45, cx + 50, desk_t], fill=(255, 255, 255), outline=ink, width=max(3, line_w // 3))
            draw.arc([cx - 15, desk_t - 40, cx + 15, desk_t - 20], start=180, end=360, fill=accent_red, width=max(3, line_w // 3))
            draw.line([(cx + 15, desk_t - 30), (cx, desk_t - 15)], fill=accent_red, width=max(3, line_w // 3))
            draw.ellipse([cx - 4, desk_t - 10, cx + 4, desk_t - 2], fill=accent_red)

            # Stickman Head seated behind desk in pure panic
            hx, hy = cx - 20, cy - 140
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255), outline=ink, width=line_w)
            # Shocked wide blank spiral eyes
            draw.ellipse([hx - 24, hy - 16, hx - 8, hy + 2], fill=ink)
            draw.ellipse([hx + 8, hy - 16, hx + 24, hy + 2], fill=ink)
            # Wavy trembling mouth
            draw.line([(hx - 18, hy + 22), (hx - 6, hy + 14), (hx + 6, hy + 24), (hx + 18, hy + 16)], fill=ink, width=max(4, line_w // 2))
            # Giant panic sweat drops flying
            for sw_x, sw_y in [(hx + hr + 10, hy - 20), (hx + hr + 25, hy + 10), (hx - hr - 20, hy - 10)]:
                draw.ellipse([sw_x, sw_y, sw_x + 16, sw_y + 24], fill=accent_blue)
            # Torso behind desk
            hip = (cx - 20, desk_t + 10)
            draw.line([(hx, hy + hr), (cx - 20, desk_t)], fill=ink, width=line_w)
            # Hands clutching head in desperation
            draw.line([(cx - 20, cy - 40), (hx - hr - 20, cy - 50), (hx - hr + 10, hy - 10)], fill=ink, width=line_w)
            draw.line([(cx - 20, cy - 40), (hx + hr + 20, cy - 50), (hx + hr - 10, hy - 10)], fill=ink, width=line_w)

        # -------------------------------------------------------------
        # POSE: WHISPER / TOPPER / FRIEND / ISHARA / CHEAT
        # -------------------------------------------------------------
        elif any(k in v_lower for k in ["whisper", "topper", "friend", "ishara", "cheat", "help", "dost"]):
            draw.ellipse([cx - 220, ground_y - 8, cx + 180, ground_y + 14], fill=ground_gray)
            # Stickman on left stretching ridiculously far to right
            hx, hy = cx + 40, cy - 110
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255), outline=ink, width=line_w)
            # Shifty sideways glancing eyes
            draw.ellipse([hx + 2, hy - 12, hx + 16, hy + 2], fill=ink)
            draw.ellipse([hx + 24, hy - 12, hx + 38, hy + 2], fill=ink)
            # Whispering small open mouth
            draw.ellipse([hx + 20, hy + 14, hx + 34, hy + 26], fill=ink)
            # Cupped hand over mouth
            draw.arc([hx + 36, hy + 6, hx + 60, hy + 34], start=90, end=270, fill=ink, width=line_w)
            # Comic dotted whisper lines
            for dot_x in [hx + 70, hx + 100, hx + 130]:
                draw.ellipse([dot_x, hy + 18, dot_x + 8, hy + 26], fill=accent_red)

            hip = (cx - 160, cy + 120)
            # Ridiculously elongated stretchy neck from torso to head
            draw.line([(cx - 160, cy - 40), (cx - 40, cy - 70), (hx, hy + hr)], fill=ink, width=line_w)
            draw.line([(cx - 160, cy - 40), hip], fill=ink, width=line_w)
            draw.line([hip, (cx - 210, ground_y)], fill=ink, width=line_w)
            draw.line([hip, (cx - 120, ground_y)], fill=ink, width=line_w)

        # -------------------------------------------------------------
        # POSE: STRICT INVIGILATOR / TEACHER / EAGLE EYE / STARE
        # -------------------------------------------------------------
        elif any(k in v_lower for k in ["invigilator", "teacher", "eagle", "stare", "strict", "khadoos", "sir"]):
            draw.ellipse([cx - 110, ground_y - 8, cx + 110, ground_y + 14], fill=ground_gray)
            # Tall menacing teacher
            hx, hy = cx, cy - 180
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255), outline=ink, width=line_w)
            # Strict horned glasses / stern angled eyebrows
            draw.line([(hx - 36, hy - 25), (hx - 4, hy - 10)], fill=ink, width=line_w)
            draw.line([(hx + 4, hy - 10), (hx + 36, hy - 25)], fill=ink, width=line_w)
            # Red glowing laser stare eyes
            draw.ellipse([hx - 28, hy - 14, hx - 8, hy + 4], fill=accent_red, outline=ink, width=3)
            draw.ellipse([hx + 8, hy - 14, hx + 28, hy + 4], fill=accent_red, outline=ink, width=3)
            # Red laser sight beams beaming down
            draw.line([(hx - 18, hy - 5), (hx - 160, cy + 200)], fill=accent_red, width=max(3, line_w // 3))
            draw.line([(hx + 18, hy - 5), (hx + 160, cy + 200)], fill=accent_red, width=max(3, line_w // 3))
            # Stern straight frowning mouth
            draw.line([(hx - 22, hy + 22), (hx + 22, hy + 22)], fill=ink, width=line_w)

            hip = (cx, cy + 90)
            draw.line([(hx, hy + hr), hip], fill=ink, width=line_w)
            # Authoritative folded arms across chest
            draw.line([(cx - 70, cy - 60), (cx + 70, cy - 60)], fill=ink, width=int(line_w * 1.5))
            draw.line([(cx, cy - 90), (cx - 70, cy - 60)], fill=ink, width=line_w)
            draw.line([(cx, cy - 90), (cx + 70, cy - 60)], fill=ink, width=line_w)
            # Standing firm wide legs
            draw.line([hip, (cx - 70, ground_y)], fill=ink, width=line_w)
            draw.line([hip, (cx + 70, ground_y)], fill=ink, width=line_w)

        # -------------------------------------------------------------
        # POSE: SWAG / COOL / SUBMIT / SUNGLASSES / VICTORY
        # -------------------------------------------------------------
        elif any(k in v_lower for k in ["swag", "cool", "submit", "sunglass", "boss", "hero", "roll number"]):
            draw.ellipse([cx - 130, ground_y - 8, cx + 130, ground_y + 14], fill=ground_gray)
            hx, hy = cx - 20, cy - 150
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255), outline=ink, width=line_w)

            # Cool Black Sunglasses (Thug Life style)
            sg_w, sg_h = 32, 18
            draw.rectangle([hx - sg_w - 6, hy - 14, hx - 6, hy + sg_h - 14], fill=ink)
            draw.rectangle([hx + 6, hy - 14, hx + sg_w + 6, hy + sg_h - 14], fill=ink)
            draw.line([(hx - 6, hy - 6), (hx + 6, hy - 6)], fill=ink, width=max(4, line_w // 2))
            # Sunglasses shine white slash
            draw.line([(hx - sg_w, hy + sg_h - 18), (hx - 12, hy - 10)], fill=(255, 255, 255), width=3)
            draw.line([(hx + 12, hy + sg_h - 18), (hx + sg_w, hy - 10)], fill=(255, 255, 255), width=3)
            # Confident smirk
            draw.arc([hx - 10, hy + 4, hx + 22, hy + 26], start=20, end=140, fill=ink, width=max(4, line_w // 2))

            hip = (cx - 10, cy + 110)
            draw.line([(hx, hy + hr), hip], fill=ink, width=line_w)
            # One hand holding submitted exam paper like a boss trophy
            draw.line([(cx - 20, cy - 50), (cx + 90, cy - 90), (cx + 130, cy - 140)], fill=ink, width=line_w)
            # Paper in hand with "100" or checkmark
            draw.rectangle([cx + 120, cy - 200, cx + 200, cy - 120], fill=(255, 255, 255), outline=ink, width=max(3, line_w // 3))
            draw.line([(cx + 135, cy - 160), (cx + 150, cy - 145), (cx + 185, cy - 185)], fill=accent_green, width=max(4, line_w // 2))
            # Other hand coolly in pocket
            draw.line([(cx - 20, cy - 50), (cx - 80, cy + 30), (cx - 40, cy + 80)], fill=ink, width=line_w)
            # Swag walking stride legs
            draw.line([hip, (cx + 80, ground_y)], fill=ink, width=line_w)
            draw.line([hip, (cx - 100, ground_y - 20), (cx - 120, ground_y)], fill=ink, width=line_w)
            # Sparkle shine stars around head
            for st_x, st_y in [(hx + hr + 30, hy - 50), (hx - hr - 40, hy - 30)]:
                draw.line([(st_x - 18, st_y), (st_x + 18, st_y)], fill=accent_gold, width=4)
                draw.line([(st_x, st_y - 18), (st_x, st_y + 18)], fill=accent_gold, width=4)

        # -------------------------------------------------------------
        # DEFAULT: WELCOMING / INTRO STICKMAN
        # -------------------------------------------------------------
        else:
            draw.ellipse([cx - 100, ground_y - 8, cx + 100, ground_y + 14], fill=ground_gray)

            hx, hy = cx, cy - 140
            draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255), outline=ink, width=line_w)

            # Friendly cheerful face
            draw.ellipse([hx - 20, hy - 14, hx - 8, hy], fill=ink)
            draw.ellipse([hx + 8, hy - 14, hx + 20, hy], fill=ink)
            draw.arc([hx - 18, hy + 2, hx + 18, hy + 28], start=20, end=160, fill=ink, width=max(4, line_w // 2))

            hip = (cx, cy + 120)
            draw.line([(hx, hy + hr), hip], fill=ink, width=line_w)

            # Welcoming waving hand on right
            draw.line([(cx, cy - 50), (cx + 80, cy - 100), (cx + 120, cy - 170)], fill=ink, width=line_w)
            # Friendly hand on hip on left
            draw.line([(cx, cy - 50), (cx - 70, cy), (cx - 30, cy + 40)], fill=ink, width=line_w)

            # Standing legs
            draw.line([hip, (cx - 60, ground_y)], fill=ink, width=line_w)
            draw.line([hip, (cx + 60, ground_y)], fill=ink, width=line_w)

        # -------------------------------------------------------------
        # TOP BANNER / STORYBOARD BADGE (YouTube Shorts / Reel Style)
        # -------------------------------------------------------------
        banner_w, banner_h = int(w * 0.84), int(h * 0.08)
        bx1 = (w - banner_w) // 2
        by1 = int(h * 0.07)
        bx2, by2 = bx1 + banner_w, by1 + banner_h

        # Rounded badge background
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=24, fill=(248, 250, 252), outline=ink, width=max(4, line_w // 2))

        # Channel / Title Header
        title_text = "STICKFORGE AI ANIMATION"
        draw.text((w // 2, by1 + int(banner_h * 0.28)), title_text, fill=(30, 41, 59), font=font_title, anchor="mm")

        img.save(output_path, format="PNG")


# =====================================================================
# 3. VIDEO STITCHING & ASSEMBLY ENGINE (FFmpeg Headless)
# =====================================================================

class VideoAssembler:
    """Stitches scene frames and audio into final MP4 strictly in FCFS order."""

    def __init__(self, fps: int = 24, width: int = 1080, height: int = 1920):
        self.fps = fps
        self.width = width
        self.height = height

    def render_scene_clip(
        self,
        image_path: Path,
        audio_path: Path,
        duration: float,
        output_clip_path: Path,
        voiceover: str = "",
        camera_action: str = "zoom_in",
        cue_word: str = "",
    ) -> Path:
        """Renders an individual scene clip with AI-directed camera actions and word subtitles."""
        output_clip_path.parent.mkdir(parents=True, exist_ok=True)
        img_clean = str(image_path.resolve()).replace("\\", "/")
        audio_clean = str(audio_path.resolve()).replace("\\", "/")

        # 1. AI-Directed Camera Action Filter
        if camera_action == "zoom_in":
            vf_parts = [f"zoompan=z='min(zoom+0.0006,1.08)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={self.width}x{self.height}:fps={self.fps}"]
        elif camera_action == "shake":
            vf_parts = [f"zoompan=z='1.05':d=1:x='iw/2-(iw/zoom/2)+sin(in*1.5)*12':y='ih/2-(ih/zoom/2)+cos(in*1.5)*12':s={self.width}x{self.height}:fps={self.fps}"]
        else:
            vf_parts = [f"scale={self.width}:{self.height}", "format=yuv420p"]

        # 2. Dynamic Subtitle Overlay Filter
        if voiceover:
            clean_text = voiceover.replace("'", "\\'").replace(":", "\\:").replace("%", "%%").replace("\n", " ")
            if len(clean_text) > 42:
                words = clean_text.split()
                mid = len(words) // 2
                clean_text = " ".join(words[:mid]) + " - " + " ".join(words[mid:])

            drawtext_str = (
                f"drawtext=text='{clean_text}':fontcolor=white:fontsize=46:"
                f"x=(w-text_w)/2:y=h*0.82:box=1:boxcolor=black@0.75:boxborderw=16"
            )
            vf_parts.append(drawtext_str)

        filter_complex = ",".join(vf_parts)

        args = [
            "-loop", "1",
            "-framerate", str(self.fps),
            "-i", img_clean,
            "-i", audio_clean,
            "-vf", filter_complex,
            "-c:v", "libx264",
            "-b:v", "2000k",
            "-minrate", "2000k",
            "-maxrate", "2000k",
            "-bufsize", "4000k",
            "-x264-params", "nal-hrd=cbr",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", f"{duration:.3f}",
            "-shortest",
            str(output_clip_path.resolve()),
        ]
        run_ffmpeg_command(args, total_duration_seconds=duration)
        return output_clip_path

    def concatenate_scene_clips(self, clip_paths: List[Path], final_output_path: Path) -> Path:
        """Concatenates all scene clips into a single unified MP4 video."""
        final_output_path.parent.mkdir(parents=True, exist_ok=True)
        if not clip_paths:
            raise ValueError("No scene clips provided to concatenate.")

        if len(clip_paths) == 1:
            shutil.copyfile(clip_paths[0], final_output_path)
            return final_output_path

        concat_list_file = final_output_path.with_suffix(".concat_list.txt")
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for clip in clip_paths:
                clean_p = str(clip.resolve()).replace("\\", "/")
                f.write(f"file '{clean_p}'\n")

        args = [
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file.resolve()),
            "-c", "copy",
            str(final_output_path.resolve()),
        ]
        run_ffmpeg_command(args)
        concat_list_file.unlink(missing_ok=True)
        return final_output_path
