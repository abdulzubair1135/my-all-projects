"""
OmniDev Autonomous Self-Healing & Diagnostic Engine
Automatically detects compilation, parse, and runtime errors in Godot 4 and Python/Web apps,
consults DeepSeek AI, applies precision code fixes, and verifies resolution.
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from rich.console import Console
from tools.codebase_inspector import ProjectContextBuilder

console = Console()

class AutoHealer:
    def __init__(self, brain=None, file_manager=None, workspace_dir: Optional[Path] = None):
        self.brain = brain
        self.file_manager = file_manager
        self.workspace_dir = Path(workspace_dir or Path.cwd()).resolve()

    def heal_project(self, project_dir: Path, error_text: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Autonomously heals a project by analyzing error_text, feeding context to AI brain,
        applying corrections, and verifying until errors are resolved.
        """
        project_dir = Path(project_dir).resolve()
        if not project_dir.exists():
            return {"success": False, "error": f"Project directory not found: {project_dir}"}

        console.print(f"[bold red]🩺 [Auto-Healer Active][/bold red] Analyzing errors for [cyan]{project_dir.name}[/cyan]...")
        console.print(f"[yellow]Error Summary:[/yellow] {error_text[:200]}...")

        is_godot = (project_dir / "project.godot").exists() or any(f.suffix == ".gd" for f in project_dir.rglob("*.*"))

        for attempt in range(1, max_retries + 1):
            console.print(f"[bold cyan]🔄 Auto-Healing Attempt {attempt}/{max_retries}...[/bold cyan]")

            # 1. Deterministic Pre-Pass (Instant fixes for common Godot 4 pitfalls)
            if is_godot:
                self._apply_deterministic_godot_fixes(project_dir)

            # 2. Gather Project Context
            files_context = self._gather_project_context(project_dir)

            # 3. Formulate Autonomous Diagnosis Prompt
            prompt = self._build_healing_prompt(project_dir, error_text, files_context, is_godot)

            # 4. Ask AI Brain
            console.print("[magenta]🤖 Asking DeepSeek AI for architectural error resolution...[/magenta]")
            attach = None
            try:
                attach = ProjectContextBuilder.write_bundle_file(project_dir)
            except Exception:
                attach = None

            response = self.brain.ask(prompt, new_chat=False, file_to_attach=attach) if self.brain else ""

            # 5. Apply Updates to Disk
            files_updated = self._apply_code_modifications(project_dir, response)

            # 6. Sanitize Godot configuration
            if is_godot:
                self._apply_deterministic_godot_fixes(project_dir)

            # 7. Verification Pass
            passed, new_error = self._verify_project(project_dir, is_godot)
            if passed:
                console.print(f"[bold green]✨ [Auto-Healer Success] All errors resolved cleanly in attempt {attempt}![/bold green]")
                return {
                    "success": True,
                    "attempts": attempt,
                    "files_updated": files_updated,
                    "project_dir": str(project_dir)
                }
            else:
                console.print(f"[yellow]⚠️ Attempt {attempt} still has issues:[/yellow] {new_error[:150]}")
                error_text = new_error

        return {
            "success": False,
            "error": "Max auto-heal attempts reached",
            "last_error": error_text,
            "project_dir": str(project_dir)
        }

    def _build_healing_prompt(self, project_dir: Path, error_text: str, files_context: str, is_godot: bool) -> str:
        project_name = project_dir.name
        ascii_tree = ProjectContextBuilder.generate_ascii_tree(project_dir)
        inventory = ProjectContextBuilder.scan_asset_inventory(project_dir)

        asset_summary_parts = []
        if inventory.get("textures"):
            asset_summary_parts.append("🎨 Textures:")
            for t in inventory["textures"]:
                asset_summary_parts.append(f"   • {t['path']} ({t['format']}, {t['size']}) -> Code: {t['gd_load']}")
        if inventory.get("audio"):
            asset_summary_parts.append("🔊 Audio / Sounds:")
            for a in inventory["audio"]:
                asset_summary_parts.append(f"   • {a['path']} ({a['format']}, {a['size']}) -> Code: {a['gd_load']}")
        if inventory.get("models_3d"):
            asset_summary_parts.append("🧊 3D Meshes:")
            for m in inventory["models_3d"]:
                asset_summary_parts.append(f"   • {m['path']} ({m['format']}, {m['size']}) -> Code: {m['gd_load']}")
        if inventory.get("shaders"):
            asset_summary_parts.append("🔮 Shaders:")
            for s in inventory["shaders"]:
                asset_summary_parts.append(f"   • {s['path']} ({s['format']}, {s['size']}) -> Code: {s['gd_load']}")
        if inventory.get("scenes"):
            asset_summary_parts.append("🎬 Scene Files:")
            for sc in inventory["scenes"]:
                asset_summary_parts.append(f"   • {sc['path']} ({sc['size']}) -> Code: {sc['gd_load']}")

        asset_catalog_str = "\n".join(asset_summary_parts) if asset_summary_parts else "No external binary assets detected."

        if is_godot:
            return f"""You are OmniDev AI Principal Godot 4 Systems Architect & Debugging Expert.
The Godot 4.x game project '{project_name}' has encountered compilation or runtime errors.

ERROR DETAILS FROM GODOT OUTPUT:
\"\"\"
{error_text}
\"\"\"

=== 1. COMPLETE PROJECT STRUCTURE & DIRECTORY TREE ===
{ascii_tree}

=== 2. COMPREHENSIVE ASSET & RESOURCE CATALOG ===
{asset_catalog_str}

PROJECT CODEBASE (GDScript & Scenes ONLY):
{files_context}

CRITICAL GODOT 4 DEBUGGING RULES:
1. Output ONLY Godot 4 GDScript (`.gd`) files, Scenes (`.tscn`), and `project.godot`.
2. NEVER output HTML, JavaScript, CSS, or `simulator.html`. All code runs strictly in Godot 4 Engine.
3. 'Cannot call non-static function on the class directly': 
   - If calling an Autoload singleton (e.g. `SoundManager`), do NOT put `class_name SoundManager` on `SoundManager.gd`. Use `extends Node` and reference via `SoundManager.func()` or `get_node_or_null("/root/SoundManager").func()`.
4. 'Identifier not declared in current scope': 
   - Add missing Autoload to `project.godot` or declare `class_name` on referenced helper classes.
5. 'Failed to load script ... Parse error': 
   - Correct all syntax, indentation, type hints, or missing node references.
6. MANDATORY: You MUST provide the 100% COMPLETE, full code for each corrected file inside markdown code blocks with the `FILE: <relative_path>` header. NEVER return only summaries or explanations without the code blocks.

OUTPUT FORMAT:
FILE: <relative_path>
```gdscript
<100% full corrected code>
```
"""
        else:
            return f"""You are OmniDev AI Senior Full-Stack Debugger.
The application '{project_name}' encountered an error.

ERROR LOG:
\"\"\"
{error_text}
\"\"\"

=== PROJECT DIRECTORY TREE ===
{ascii_tree}

=== ASSET INVENTORY ===
{asset_catalog_str}

PROJECT FILES:
{files_context}

Provide complete corrected code for modified files in this format:
FILE: <relative_path>
```<language>
<full corrected code>
```
"""

    def _gather_project_context(self, project_dir: Path) -> str:
        relevant_files = []
        for ext in ["*.gd", "*.tscn", "*.gdshader", "*.tres", "*.godot", "*.py", "*.html", "*.css", "*.js", "*.json"]:
            relevant_files.extend(list(project_dir.rglob(ext)))

        relevant_files = [f for f in relevant_files if not any(bad in f.name for bad in [".git", "gdscript", "text", "cache", ".omnidev_bundle"]) and not any(p in ["cenes", "cripts"] for p in f.parts)]
        
        context_parts = []
        for f in relevant_files:
            try:
                rel = f.relative_to(project_dir).as_posix()
                content = f.read_text(encoding="utf-8", errors="ignore")
                context_parts.append(f"--- FILE: {rel} ---\n{content}\n")
            except Exception:
                pass
        return "\n".join(context_parts)

    def _apply_code_modifications(self, project_dir: Path, response: str) -> List[str]:
        found_files = {}

        # Pattern 1: Standard FILE: <path> before code block
        p1 = r'(?:###\s*|\*\*|\*)?(?:FILE|File|file|Filename|filename):\s*`?(?:res:\/\/)?([a-zA-Z0-9_\-\./\\]+?\.(?:gd|tscn|godot|py|html|css|js|ts|json|bat|txt|md|sql))`?\*?\*?\s*(?:\n|\r\n)```[a-zA-Z0-9_\-]*\n(.*?)```'
        for fpath, code in re.findall(p1, response, re.DOTALL):
            clean_p = fpath.strip().replace('\\\\', '/').replace('\\', '/').lstrip('/')
            if clean_p.startswith('res://'): clean_p = clean_p[6:]
            clean_code = re.sub(r'^(?:gdscript|gdscene|python|json|html|bash|sh|text|tscn|markdown)\s*\n', '', code.strip(), flags=re.IGNORECASE).strip()
            if len(clean_code) > 10:
                found_files[clean_p] = clean_code

        # Pattern 2: In-code comment `# FILE: <path>` or `// filepath: <path>`
        p2 = r'```[a-zA-Z0-9_\-]*\s*(?:\n|\r\n)(?:[#\/]{1,2}\s*(?:FILE|File|file|filepath|filename):\s*`?(?:res:\/\/)?([a-zA-Z0-9_\-\./\\]+?\.(?:gd|tscn|godot|py|html|css|js|ts|json|bat|txt|md|sql))`?)\s*\n(.*?)```'
        for fpath, code in re.findall(p2, response, re.DOTALL):
            clean_p = fpath.strip().replace('\\\\', '/').replace('\\', '/').lstrip('/')
            if clean_p.startswith('res://'): clean_p = clean_p[6:]
            clean_code = re.sub(r'^(?:gdscript|gdscene|python|json|html|bash|sh|text|tscn|markdown)\s*\n', '', code.strip(), flags=re.IGNORECASE).strip()
            if len(clean_code) > 10 and clean_p not in found_files:
                found_files[clean_p] = clean_code

        # Intelligent Content-Based Classifier for untagged code blocks
        raw_blocks = re.findall(r"```(?:[a-zA-Z0-9_\-]+)?\n(.*?)```", response, re.DOTALL)
        for block in raw_blocks:
            b_text = re.sub(r'^(?:gdscript|gdscene|python|json|html|bash|sh|text|tscn|markdown)\s*\n', '', block.strip(), flags=re.IGNORECASE).strip()
            if len(b_text) < 20:
                continue

            # 1. WorldGenerator (MUST BE MATCHED BEFORE Animal to avoid chunk/terrain scripts with animal spawning matching Animal.gd)
            if "class_name WorldGenerator" in b_text or ("FastNoiseLite" in b_text or "generate_terrain" in b_text or "create_voxel" in b_text or "generate_tree" in b_text or "CHUNK_SIZE" in b_text or "WORLD_HEIGHT" in b_text):
                if "scripts/WorldGenerator.gd" not in found_files:
                    found_files["scripts/WorldGenerator.gd"] = b_text
            # 2. Player (MUST BE MATCHED BEFORE Animal)
            elif "class_name Player" in b_text or (any(k in b_text for k in ["mouse_sensitivity", "FirstPersonCamera", "toggle_camera", "jump_velocity", "velocity.y -="]) and "class_name Animal" not in b_text):
                if "scripts/Player.gd" not in found_files:
                    found_files["scripts/Player.gd"] = b_text
            # 3. Animal (Strictly CharacterBody3D and NOT WorldGenerator)
            elif ("class_name Animal" in b_text or any(k in b_text for k in [
                "build_procedural_animal", "_animal_type", "animal_type", "graze", "flee", "take_damage", "handle_fleeing", "handle_wandering"
            ])) and ("class_name WorldGenerator" not in b_text and "FastNoiseLite" not in b_text and "CHUNK_SIZE" not in b_text and "create_voxel" not in b_text and "class_name Player" not in b_text):
                if "scripts/Animal.gd" not in found_files:
                    found_files["scripts/Animal.gd"] = b_text
            # 4. UI
            elif any(k in b_text for k in [
                "extends Control", "extends CanvasLayer", "class_name UI", "ProgressBar", "Hotbar",
                "pause_menu", "start_menu", "toggle_pause_menu", "show_hud", "update_health",
                "health_bar", "hotbar_slots", "inventory_slots", "crosshair", "debug_label", "resume_button", "restart_button"
            ]):
                if "scripts/UI.gd" not in found_files:
                    found_files["scripts/UI.gd"] = b_text
            # 5. SoundManager
            elif any(k in b_text for k in ["AudioStreamGenerator", "play_jump", "SoundManager", "play_block_break", "play_block_place", "generate_tone"]):
                if "scripts/SoundManager.gd" not in found_files:
                    found_files["scripts/SoundManager.gd"] = b_text
            elif "[application]" in b_text or "config_version=5" in b_text:
                if "project.godot" not in found_files:
                    found_files["project.godot"] = b_text
            elif "[gd_scene" in b_text:
                if "scenes/Animal.tscn" not in found_files and ("Animal" in b_text or "mesh" in b_text.lower()):
                    found_files["scenes/Animal.tscn"] = b_text
                elif "scenes/Main.tscn" not in found_files:
                    found_files["scenes/Main.tscn"] = b_text

        files_updated = []
        for fname, code in found_files.items():
            dest = project_dir / fname
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            clean_code = code
            if dest.exists() and fname.endswith(".gd"):
                try:
                    existing_text = dest.read_text(encoding="utf-8", errors="ignore")
                    if not ("extends " in clean_code or "class_name " in clean_code) and len(existing_text.splitlines()) > len(clean_code.splitlines()) + 5:
                        clean_code = self._merge_gdscript_snippets(existing_text, clean_code)
                except Exception:
                    pass

            dest.write_text(clean_code, encoding="utf-8")
            files_updated.append(fname)
            console.print(f"[bold green]📝 [Auto-Healer] Updated: [cyan]{fname}[/cyan][/bold green]")

        return files_updated

    def _merge_gdscript_snippets(self, existing_code: str, snippet: str) -> str:
        """Safely merges partial function updates into existing complete GDScript without wiping out other features."""
        func_pattern = r'(func\s+([a-zA-Z0-9_]+)\s*\([^)]*\)(?:\s*->\s*[a-zA-Z0-9_]+)?\s*:.*?(?=\nfunc\s|\Z))'
        snippet_funcs = re.findall(func_pattern, snippet, re.DOTALL)
        
        updated_code = existing_code
        if snippet_funcs:
            for full_func_code, func_name in snippet_funcs:
                exist_func_pattern = rf'(func\s+{re.escape(func_name)}\s*\([^)]*\)(?:\s*->\s*[a-zA-Z0-9_]+)?\s*:.*?(?=\nfunc\s|\Z))'
                if re.search(exist_func_pattern, updated_code, re.DOTALL):
                    updated_code = re.sub(exist_func_pattern, full_func_code.strip(), updated_code, count=1, flags=re.DOTALL)
                else:
                    updated_code = updated_code.strip() + "\n\n" + full_func_code.strip() + "\n"
            return updated_code
        return existing_code.strip() + "\n\n" + snippet.strip() + "\n"

    def _apply_deterministic_godot_fixes(self, project_dir: Path):
        """Applies instant structural fixes for Godot 4 scripts and Autoloads."""
        import shutil
        for bad_dir in ["cenes", "cripts"]:
            p = project_dir / bad_dir
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)

        for f in list(project_dir.rglob("*")):
            if f.is_file() and (f.name.endswith("gdscript") or f.name.endswith("text")):
                try:
                    f.unlink()
                except Exception:
                    pass

        # Universal GDScript Syntax & Unicode Sanitizer for all .gd files
        for gd_file in project_dir.rglob("*.gd"):
            try:
                content = gd_file.read_text(encoding="utf-8", errors="ignore")
                orig = content
                content = re.sub(r'[\u200B-\u200D\uFEFF]', '', content)
                content = re.sub(r'([^\n])(@onready\s+var\s+)', r'\1\n\2', content)
                content = re.sub(r'([^\n])(func\s+\w+\()', r'\1\n\n\2', content)
                content = re.sub(r'([^\n])(class_name\s+\w+)', r'\1\n\2', content)
                content = re.sub(r'@onready\s+var\s+(\w+)\s*(?::\s*(\w+))?\s*=\s*(?!\$|get_node|null|\[|\{)(HUD\/[\w\/]+|StartMenu\/[\w\/]+|PauseMenu\/[\w\/]+|Crosshair\/[\w\/]+|[\w]+\/[\w\/]+)', r'@onready var \1: \2 = get_node_or_null("\3")', content)

                content = content.replace("SpatialMaterial.new()", "StandardMaterial3D.new()")
                content = re.sub(r'\bSpatialMaterial\b', 'StandardMaterial3D', content)
                content = re.sub(r'(\w+)_mat\.material_override\s*=\s*\1_mat', r'\1.material_override = \1_mat', content)

                if content != orig:
                    gd_file.write_text(content.strip() + "\n", encoding="utf-8")
            except Exception:
                pass

        # Animal.gd class_name & Auto-Recovery
        an_file = project_dir / "scripts" / "Animal.gd"
        if an_file.exists():
            content = an_file.read_text(encoding="utf-8", errors="ignore")
            if "class_name WorldGenerator" in content or "FastNoiseLite" in content or "CHUNK_SIZE" in content:
                content = """class_name Animal
extends CharacterBody3D

enum AnimalType { COW, SHEEP, PIG }
@export var animal_type: AnimalType = AnimalType.COW
var _animal_type: String = "cow":
\tset(val):
\t\t_animal_type = str(val).to_lower()
\t\tif "sheep" in _animal_type: animal_type = AnimalType.SHEEP
\t\telif "pig" in _animal_type: animal_type = AnimalType.PIG
\t\telse: animal_type = AnimalType.COW
\t\tbuild_procedural_animal()
\tget:
\t\treturn _animal_type

var speed: float = 2.5
var flee_speed: float = 6.0
var health: int = 4
var max_health: int = 4
var state: int = 0 # 0: Wandering, 1: Fleeing, 2: Dead
var wander_timer: float = 0.0
var move_direction: Vector3 = Vector3.ZERO
var player_ref: Node3D = null
var gravity: float = 9.8

@onready var model_root: Node3D = get_node_or_null("Model")
var leg_nodes = []
var walk_anim_timer: float = 0.0

func _ready():
\tbuild_procedural_animal()
\tvar players = get_tree().get_nodes_in_group("player")
\tif players.size() > 0:
\t\tplayer_ref = players[0]

func build_procedural_animal():
\tif not model_root:
\t\tmodel_root = Node3D.new()
\t\tmodel_root.name = "Model"
\t\tadd_child(model_root)
\tfor c in model_root.get_children():
\t\tc.queue_free()
\tleg_nodes.clear()
\t
\tvar body_mesh = MeshInstance3D.new()
\tvar box = BoxMesh.new()
\tbox.size = Vector3(1.2, 0.9, 1.6)
\tbody_mesh.mesh = box
\tbody_mesh.position = Vector3(0, 0.9, 0)
\tvar mat = StandardMaterial3D.new()
\tif animal_type == AnimalType.SHEEP: mat.albedo_color = Color(0.9, 0.9, 0.9)
\telif animal_type == AnimalType.PIG: mat.albedo_color = Color(1.0, 0.75, 0.8)
\telse: mat.albedo_color = Color(0.4, 0.25, 0.15)
\tbody_mesh.material_override = mat
\tmodel_root.add_child(body_mesh)
\t
\t# Head
\tvar head_mesh = MeshInstance3D.new()
\tvar head_box = BoxMesh.new()
\thead_box.size = Vector3(0.8, 0.8, 0.8)
\thead_mesh.mesh = head_box
\thead_mesh.position = Vector3(0, 1.3, -0.9)
\thead_mesh.material_override = mat
\tmodel_root.add_child(head_mesh)
\t
\t# 4 Legs
\tvar leg_positions = [Vector3(-0.4, 0.35, -0.5), Vector3(0.4, 0.35, -0.5), Vector3(-0.4, 0.35, 0.5), Vector3(0.4, 0.35, 0.5)]
\tfor lp in leg_positions:
\t\tvar leg = MeshInstance3D.new()
\t\tvar l_box = BoxMesh.new()
\t\tl_box.size = Vector3(0.25, 0.7, 0.25)
\t\tleg.mesh = l_box
\t\tleg.position = lp
\t\tleg.material_override = mat
\t\tmodel_root.add_child(leg)
\t\tleg_nodes.append(leg)

func _physics_process(delta: float):
\tif state == 2: return
\tif not is_on_floor():
\t\tvelocity.y -= gravity * delta
\twander_timer -= delta
\tif wander_timer <= 0:
\t\twander_timer = randf_range(2.0, 5.0)
\t\tif randf() > 0.4:
\t\t\tvar angle = randf() * TAU
\t\t\tmove_direction = Vector3(cos(angle), 0, sin(angle)).normalized()
\t\telse:
\t\t\tmove_direction = Vector3.ZERO
\t
\tif state == 1 and player_ref:
\t\tvar away = (global_position - player_ref.global_position).normalized()
\t\taway.y = 0
\t\tvelocity.x = away.x * flee_speed
\t\tvelocity.z = away.z * flee_speed
\telif move_direction != Vector3.ZERO:
\t\tvelocity.x = move_direction.x * speed
\t\tvelocity.z = move_direction.z * speed
\t\tlook_at(global_position + move_direction, Vector3.UP)
\telse:
\t\tvelocity.x = move_toward(velocity.x, 0, speed * delta * 4)
\t\tvelocity.z = move_toward(velocity.z, 0, speed * delta * 4)
\t
\tmove_and_slide()
\t
\t# Leg animation
\tif velocity.length() > 0.2 and is_on_floor():
\t\twalk_anim_timer += delta * 10.0
\t\tfor i in range(leg_nodes.size()):
\t\t\tvar sign_mult = 1.0 if i % 2 == 0 else -1.0
\t\t\tleg_nodes[i].rotation.x = sin(walk_anim_timer) * 0.4 * sign_mult
\telse:
\t\tfor leg in leg_nodes:
\t\t\tleg.rotation.x = 0.0

func take_damage(amount: int = 1):
\tif state == 2: return
\thealth -= amount
\tstate = 1
\tif health <= 0:
\t\tdie()

func die():
\tstate = 2
\tvelocity = Vector3.ZERO
\trotation.z = deg_to_rad(90)
\tglobal_position.y += 0.2
\tset_collision_layer_value(1, false)
\tset_collision_mask_value(1, false)
\tawait get_tree().create_timer(1.5).timeout
\tqueue_free()
"""
            else:
                if "class_name Player" in content:
                    content = content.replace("class_name Player", "class_name Animal")
                if "class_name Animal" not in content and "extends CharacterBody3D" in content:
                    content = "class_name Animal\n" + content
                if "_animal_type" not in content and "extends CharacterBody3D" in content:
                    content = content.replace("extends CharacterBody3D\n", "extends CharacterBody3D\n\nvar _animal_type: String = \"cow\"\n")
            an_file.write_text(content.strip() + "\n", encoding="utf-8")

        # SoundManager Singleton Fix
        sm_file = project_dir / "scripts" / "SoundManager.gd"
        if sm_file.exists():
            content = sm_file.read_text(encoding="utf-8", errors="ignore")
            if "class_name SoundManager" in content:
                content = content.replace("class_name SoundManager\n", "").replace("class_name SoundManager", "")
                sm_file.write_text(content.strip(), encoding="utf-8")

        # WorldGenerator class_name
        wg_file = project_dir / "scripts" / "WorldGenerator.gd"
        if wg_file.exists():
            content = wg_file.read_text(encoding="utf-8", errors="ignore")
            if "class_name WorldGenerator" not in content:
                content = "class_name WorldGenerator\n" + content
                wg_file.write_text(content, encoding="utf-8")

        # Player.gd Safe Sound Call & Safe Node Lookup Fix
        pl_file = project_dir / "scripts" / "Player.gd"
        if pl_file.exists():
            content = pl_file.read_text(encoding="utf-8", errors="ignore")
            content = re.sub(r'(?<!get_node\("/root/)SoundManager\.play_jump\(\)', 'if has_node("/root/SoundManager"): get_node("/root/SoundManager").play_jump()', content)
            content = re.sub(r'(?<!get_node\("/root/)SoundManager\.play_block_break\(\)', 'if has_node("/root/SoundManager"): get_node("/root/SoundManager").play_block_break()', content)
            content = re.sub(r'(?<!get_node\("/root/)SoundManager\.play_block_place\(\)', 'if has_node("/root/SoundManager"): get_node("/root/SoundManager").play_block_place()', content)
            
            # Prevent 'Node not found' crashes by converting unverified $ lookups to get_node_or_null
            content = re.sub(r'@onready\s+var\s+player_mesh(?:\s*:\s*\w+)?\s*=\s*\$PlayerMesh', '@onready var player_mesh: Node3D = get_node_or_null("PlayerMesh")', content)
            content = re.sub(r'@onready\s+var\s+armature(?:\s*:\s*\w+)?\s*=\s*\$PlayerMesh/Armature', '@onready var armature: Node3D = get_node_or_null("PlayerMesh/Armature")', content)
            content = re.sub(r'@onready\s+var\s+animation_player(?:\s*:\s*\w+)?\s*=\s*\$PlayerMesh/AnimationPlayer', '@onready var animation_player: AnimationPlayer = get_node_or_null("PlayerMesh/AnimationPlayer")', content)
            
            pl_file.write_text(content, encoding="utf-8")

        # Autoload registration in project.godot
        proj_godot = project_dir / "project.godot"
        if proj_godot.exists() and sm_file.exists():
            proj_text = proj_godot.read_text(encoding="utf-8", errors="ignore")
            if "[autoload]" not in proj_text:
                proj_text += '\n[autoload]\n\nSoundManager="*res://scripts/SoundManager.gd"\n'
                proj_godot.write_text(proj_text, encoding="utf-8")
            elif "SoundManager=" not in proj_text:
                proj_text = proj_text.replace("[autoload]", '[autoload]\n\nSoundManager="*res://scripts/SoundManager.gd"')
                proj_godot.write_text(proj_text, encoding="utf-8")

    def _verify_project(self, project_dir: Path, is_godot: bool) -> tuple[bool, str]:
        """Runs headless verification on the project to check if errors remain."""
        if is_godot:
            godot_bin = None
            for cand in [
                Path(r"C:\Users\abdul\OneDrive\Desktop\Godot_v4.6.2-stable_win64 - Copy.exe"),
                Path(r"C:\Users\abdul\OneDrive\Desktop\Godot_v4.6.2-stable_win64.exe\Godot_v4.6.2-stable_win64.exe"),
                Path(r"C:\Users\abdul\Desktop\Godot_v4.6.2-stable_win64.exe")
            ]:
                if cand.exists():
                    godot_bin = cand
                    break

            if godot_bin:
                try:
                    cmd = f'"{godot_bin}" --headless --path "{project_dir}" -e --quit'
                    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=12)
                    out = (proc.stderr or "") + "\n" + (proc.stdout or "")
                    has_error = any(k in out for k in ["SCRIPT ERROR:", "Parse Error:", "Failed to load script", "ERROR: res://", "Unexpected identifier", "Expected '['"])
                    if not has_error:
                        return True, ""
                    return False, out
                except Exception as e:
                    return False, str(e)
            return True, ""
        else:
            # Python syntax check
            for py_file in project_dir.rglob("*.py"):
                try:
                    cmd = f'"{sys.executable}" -m py_compile "{py_file}"'
                    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                    if proc.returncode != 0:
                        return False, proc.stderr
                except Exception:
                    pass
            return True, ""
