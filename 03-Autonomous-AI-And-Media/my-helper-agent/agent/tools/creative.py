import os
import subprocess
import shutil

class CreativeTools:
    """
    Modular bridges for Creative Pipelines:
    - Blender (3D modeling & render automation)
    - FFmpeg (Video/Audio processing & encoding)
    - Audio TTS (Edge-TTS / Piper)
    - Image (Local ComfyUI / SD pipeline trigger)
    """
    def __init__(self, output_dir="storage/outputs"):
        self.output_dir = os.path.abspath(output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
        self.blender_path = self._find_blender()

    def _find_blender(self):
        cmd_path = shutil.which("blender")
        if cmd_path:
            return cmd_path
        default_dir = r"C:\Program Files\Blender Foundation"
        if os.path.exists(default_dir):
            for folder in os.listdir(default_dir):
                candidate = os.path.join(default_dir, folder, "blender.exe")
                if os.path.exists(candidate):
                    return candidate
        return None

    def run_blender_script(self, python_script_path: str, output_file: str = None) -> dict:
        """Executes a Blender automation script in background mode."""
        if not self.blender_path:
            return {"success": False, "error": "Blender executable not found on system."}
        
        cmd = [self.blender_path, "-b", "--python", python_script_path]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout[-1000:],
                "output_file": output_file,
                "error": res.stderr if res.returncode != 0 else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_ffmpeg(self, args_list: list) -> dict:
        """Runs FFmpeg for video/audio processing."""
        cmd = ["ffmpeg", "-y"] + args_list
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout,
                "stderr": res.stderr[-500:],
                "error": None if res.returncode == 0 else res.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def text_to_speech_edge(self, text: str, output_filename: str = "speech.mp3", voice="hi-IN-MadhurNeural") -> dict:
        """Generates high quality natural Hindi/Hinglish speech using Edge-TTS."""
        out_path = os.path.join(self.output_dir, output_filename)
        cmd = ["edge-tts", "--voice", voice, "--text", text, "--write-media", out_path]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and os.path.exists(out_path):
                return {"success": True, "output_path": out_path, "error": None}
            return {"success": False, "output_path": None, "error": res.stderr}
        except Exception as e:
            return {"success": False, "output_path": None, "error": str(e)}
