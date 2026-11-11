import re
import sys
from typing import Dict, Any, Optional
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from config import console

class InteractiveWizard:
    """
    Intelligent Preference & Requirement Clarifier:
    Prompts the user interactively (in CLI) or parses blueprints for tech stack,
    engine choices (Godot 4 3D/2D, C++, Pygame), dimension (3D Voxel/First-Person vs 2D),
    visual art styles, era/time, and custom story lines.
    """

    @staticmethod
    def prompt_game_preferences_interactive(user_prompt: str, is_interactive: Optional[bool] = None) -> Dict[str, Any]:
        """
        Interactively asks the user for Game Engine, Dimension, Art Style, Era,
        and custom Story Lore before generation begins.
        """
        # Determine if interactive prompt is possible
        if is_interactive is None:
            is_interactive = sys.stdin.isatty()

        detected = InteractiveWizard.parse_game_preferences(user_prompt)

        if not is_interactive:
            return detected

        try:
            console.print()
            table = Table(title="🎮 Game Design & Architecture Wizard", border_style="bold magenta")
            table.add_column("Category", style="bold cyan")
            table.add_column("Options", style="white")
            table.add_column("Default Selection", style="bold green")

            table.add_row("1. Engine", "[1] Godot 4 (GDScript 4.x)  [2] C++ (Raylib)  [3] Python Pygame", "Godot 4 Engine")
            table.add_row("2. Dimension", "[1] 3D Third-Person RPG  [2] 3D Voxel / FPS  [3] 2D Action Platformer  [4] 2D Top-Down", detected.get("dimension", "3d_voxel"))
            table.add_row("3. Art Style", "[1] Voxel Blocky 3D  [2] Low-Poly 3D  [3] Dark Fantasy Medieval  [4] Cyberpunk Neon  [5] Retro Pixel", detected.get("art_style", "voxel_blocky_3d"))
            table.add_row("4. Time Era", "[1] Medieval Fantasy  [2] Cyberpunk 2099  [3] Post-Apocalyptic  [4] Modern Day", detected.get("era", "medieval_fantasy"))
            console.print(table)
            console.print("[dim]Press Enter to accept default or type number/text:[/dim]\n")

            # 1. Engine
            engine_choice = Prompt.ask("[bold cyan]Choose Engine[/bold cyan] (1: Godot 4, 2: C++, 3: Pygame)", default="1").strip()
            if engine_choice == "2" or "c++" in engine_choice.lower():
                engine = "cpp_raylib"
            elif engine_choice == "3" or "pygame" in engine_choice.lower():
                engine = "python_pygame"
            else:
                engine = "godot_engine"

            # 2. Dimension
            dim_choice = Prompt.ask("[bold cyan]Choose Dimension/Camera[/bold cyan] (1: 3D RPG/Third-Person, 2: 3D Voxel/FPS, 3: 2D Platformer, 4: 2D Top-Down)", default="1" if "rpg" in user_prompt.lower() else "2").strip()
            if dim_choice == "1" or "rpg" in dim_choice.lower() or "third" in dim_choice.lower():
                dimension = "3d_third_person"
            elif dim_choice == "2" or "voxel" in dim_choice.lower() or "fps" in dim_choice.lower():
                dimension = "3d_voxel"
            elif dim_choice == "3" or "platformer" in dim_choice.lower():
                dimension = "2d_action"
            elif dim_choice == "4" or "top" in dim_choice.lower():
                dimension = "2d_top_down"
            else:
                dimension = detected.get("dimension", "3d_voxel")

            # 3. Art Style
            style_choice = Prompt.ask("[bold cyan]Choose Art Style[/bold cyan] (1: Voxel, 2: Low-Poly 3D, 3: Dark Fantasy, 4: Cyberpunk Neon, 5: Retro Pixel)", default="3" if "rpg" in user_prompt.lower() else "1").strip()
            style_map = {
                "1": "voxel_blocky_3d",
                "2": "lowpoly_3d",
                "3": "dark_fantasy_medieval",
                "4": "cyberpunk_neon",
                "5": "retro_pixel_art"
            }
            art_style = style_map.get(style_choice, detected.get("art_style", "voxel_blocky_3d"))

            # 4. Era
            era_choice = Prompt.ask("[bold cyan]Choose Time/Era[/bold cyan] (1: Medieval Fantasy, 2: Cyberpunk 2099, 3: Post-Apocalyptic, 4: Modern Day)", default="1").strip()
            era_map = {
                "1": "medieval_fantasy",
                "2": "cyberpunk_2099",
                "3": "post_apocalyptic",
                "4": "modern_day"
            }
            era = era_map.get(era_choice, detected.get("era", "medieval_fantasy"))

            # 5. Story Lore
            console.print("[bold yellow]📜 Custom Story Lore / Kahani (Apni custom story likhein ya auto-generate ke liye Enter dabayein):[/bold yellow]")
            custom_story = Prompt.ask("[bold green]Story Narrative[/bold green]", default=detected.get("story", "")).strip()

            final_prefs = {
                "engine": engine,
                "dimension": dimension,
                "art_style": art_style,
                "era": era,
                "story": custom_story or detected.get("story", ""),
                "generate_custom_assets": True,
                "procedural_textures": True,
                "procedural_audio": True,
                "high_fps_loop": True,
                "raw_prompt": user_prompt
            }

            console.print(Panel(
                f"[bold green]✓ Configuration Locked:[/bold green]\n"
                f"• Engine: [bold cyan]{final_prefs['engine']}[/bold cyan]\n"
                f"• Dimension: [bold cyan]{final_prefs['dimension']}[/bold cyan]\n"
                f"• Art Style: [bold cyan]{final_prefs['art_style']}[/bold cyan]\n"
                f"• Era: [bold cyan]{final_prefs['era']}[/bold cyan]\n"
                f"• Story: [italic]{final_prefs['story'][:100]}...[/italic]",
                title="🚀 Launching Godot 4 Game Pipeline",
                border_style="green"
            ))
            return final_prefs

        except Exception as e:
            console.print(f"[yellow]Wizard prompt fallback to defaults: {e}[/yellow]")
            return detected

    @staticmethod
    def parse_game_preferences(user_prompt: str, story_input: Optional[str] = None) -> Dict[str, Any]:
        """Detects or assigns high-quality Godot specifications."""
        prompt_lower = user_prompt.lower()

        # 1. Engine: Sovereign Default is GODOT 4 ENGINE for ALL games
        engine = "godot_engine"
        if "c++" in prompt_lower or "raylib" in prompt_lower:
            engine = "cpp_raylib"
        elif "pygame" in prompt_lower:
            engine = "python_pygame"

        # 2. Dimension (3D Voxel / 3D FPS / 2D)
        dimension = "3d_voxel"
        if "2d" in prompt_lower or "arcade" in prompt_lower or "platformer" in prompt_lower or "flappy" in prompt_lower or "snake" in prompt_lower:
            dimension = "2d_action"
        elif "3d" in prompt_lower or "minecraft" in prompt_lower or "voxel" in prompt_lower or "open world" in prompt_lower or "fps" in prompt_lower:
            dimension = "3d_voxel"
        elif "third person" in prompt_lower or "rpg" in prompt_lower:
            dimension = "3d_third_person"

        # 3. Art / Visual Style
        art_style = "voxel_blocky_3d"
        if "pixel" in prompt_lower or "retro" in prompt_lower or "8bit" in prompt_lower:
            art_style = "retro_pixel_art"
        elif "cyberpunk" in prompt_lower or "neon" in prompt_lower or "scifi" in prompt_lower:
            art_style = "cyberpunk_neon"
        elif "lowpoly" in prompt_lower or "low poly" in prompt_lower:
            art_style = "lowpoly_3d"
        elif "fantasy" in prompt_lower or "medieval" in prompt_lower:
            art_style = "dark_fantasy_medieval"

        # 4. Time Period / Era
        era = "medieval_fantasy"
        if "cyberpunk" in prompt_lower or "2099" in prompt_lower or "future" in prompt_lower or "space" in prompt_lower:
            era = "cyberpunk_2099"
        elif "post apocalyptic" in prompt_lower or "wasteland" in prompt_lower:
            era = "post_apocalyptic"
        elif "modern" in prompt_lower or "city" in prompt_lower:
            era = "modern_day"

        # 5. Story / Lore Narrative
        story = story_input or ""
        if not story:
            if "minecraft" in prompt_lower or "voxel" in prompt_lower:
                story = "You awake in an infinite procedural voxel frontier. Gather resources, sculpt the landscape, build sovereign fortresses, and survive against nocturnal beasts."
            elif era == "cyberpunk_2099":
                story = "In the neon-lit megalopolis of Sector 7, rogue AI syndicates rule the underworld. Hack data cores and neutralize mercenary drones."
            else:
                story = f"Embark on an epic journey in the world of {user_prompt.title()}. Overcome hostile forces, build structures, and create your sovereign legacy."

        return {
            "engine": engine,
            "dimension": dimension,
            "art_style": art_style,
            "era": era,
            "story": story,
            "generate_custom_assets": True,
            "procedural_textures": True,
            "procedural_audio": True,
            "high_fps_loop": True,
            "raw_prompt": user_prompt
        }

    @staticmethod
    def parse_web_preferences(user_prompt: str) -> Dict[str, Any]:
        """Detects or assigns high-quality website & UI specifications."""
        prompt_lower = user_prompt.lower()

        style = "glassmorphism_saas"
        if "dark" in prompt_lower or "cyber" in prompt_lower:
            style = "dark_cyberpunk"
        elif "minimal" in prompt_lower or "clean" in prompt_lower or "white" in prompt_lower:
            style = "minimal_executive"
        elif "dashboard" in prompt_lower or "analytics" in prompt_lower:
            style = "fintech_dashboard"
        elif "portfolio" in prompt_lower:
            style = "creative_portfolio"

        return {
            "style": style,
            "framework": "tailwind_css",
            "interactive_js": True,
            "theme_toggle": True,
            "responsive": True,
            "raw_prompt": user_prompt
        }

    @staticmethod
    def parse_ppt_preferences(user_prompt: str) -> Dict[str, Any]:
        """Detects or assigns high-quality presentation specifications."""
        prompt_lower = user_prompt.lower()

        theme = "mckinsey_executive"
        if "dark" in prompt_lower or "tech" in prompt_lower:
            theme = "modern_dark_tech"
        elif "creative" in prompt_lower or "startup" in prompt_lower or "pitch" in prompt_lower:
            theme = "creative_pitch"

        num_slides = 6
        slide_match = re.search(r"(\d+)\s*(?:slides?|pages?)", prompt_lower)
        if slide_match:
            num_slides = max(3, min(20, int(slide_match.group(1))))

        return {
            "theme": theme,
            "num_slides": num_slides,
            "aspect_ratio": "16:9",
            "card_containers": True,
            "raw_prompt": user_prompt
        }

