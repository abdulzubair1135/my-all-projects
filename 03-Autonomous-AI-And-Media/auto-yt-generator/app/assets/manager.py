"""
AUTO YT GENERATOR — Central Asset Manager.

Handles cataloging, procedural generation, duplicate detection, content-hashing,
and caching for all 2D visual assets (Characters, Backgrounds, Props).
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image

from app.constants import AssetType
from app.config import settings
from app.models.asset import AssetModel, AssetMetadata
from app.models.scene import SceneModel, ScenePlan
from app.assets.character import CharacterGenerator
from app.assets.background import BackgroundGenerator
from app.assets.props import PropGenerator
from app.database import db
from app.logger import logger


class AssetManager:
    """Central manager for visual and audio assets."""

    def __init__(self, assets_dir: Optional[str] = None):
        self.assets_dir = Path(assets_dir or settings.paths.assets_dir)
        self.char_gen = CharacterGenerator()
        self.bg_gen = BackgroundGenerator()
        self.prop_gen = PropGenerator()

        # Ensure base asset directory structure
        for sub in ["characters", "backgrounds", "props", "sprites", "audio", "fonts"]:
            (self.assets_dir / sub).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        """Computes SHA-256 hash of a file for duplicate detection."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get_or_create_background(self, background_id: str, project_dir: Optional[str] = None) -> str:
        """Retrieves background image path or generates it procedurally."""
        safe_id = background_id.lower().replace(" ", "_").replace("/", "_")
        file_name = f"bg_{safe_id}.png"

        # Check in project directory or global assets
        target_dir = Path(project_dir) / "assets" if project_dir else self.assets_dir / "backgrounds"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / file_name

        if not target_path.exists():
            logger.info(f"Generating procedural background: '{safe_id}'")
            img = self.bg_gen.generate_background(safe_id)
            img.save(target_path, "PNG")

        return str(target_path)

    def get_or_create_character_pose(
        self,
        character_id: str,
        action: str = "idle",
        expression: str = "neutral",
        mouth_state: str = "idle",
        project_dir: Optional[str] = None,
    ) -> str:
        """Retrieves character sprite path or generates specific pose procedurally."""
        safe_id = character_id.lower().replace(" ", "_")
        file_name = f"char_{safe_id}_{action}_{expression}_{mouth_state}.png"

        target_dir = Path(project_dir) / "assets" if project_dir else self.assets_dir / "characters"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / file_name

        if not target_path.exists():
            logger.info(f"Generating character sprite: '{safe_id}' (Pose: {action}, Exp: {expression}, Mouth: {mouth_state})")
            img = self.char_gen.generate_character(action=action, expression=expression, mouth_state=mouth_state)
            img.save(target_path, "PNG")

        return str(target_path)

    def get_or_create_prop(self, prop_id: str, project_dir: Optional[str] = None) -> str:
        """Retrieves prop image path or generates it procedurally."""
        safe_id = prop_id.lower().replace(" ", "_")
        file_name = f"prop_{safe_id}.png"

        target_dir = Path(project_dir) / "assets" if project_dir else self.assets_dir / "props"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / file_name

        if not target_path.exists():
            logger.info(f"Generating procedural prop: '{safe_id}'")
            img = self.prop_gen.generate_prop(safe_id)
            img.save(target_path, "PNG")

        return str(target_path)

    def generate_all_scene_assets(self, scene_plan: ScenePlan, project_dir: Optional[str] = None) -> Dict[str, List[str]]:
        """Scans the entire scene plan and generates all required backgrounds, characters, and props."""
        generated: Dict[str, List[str]] = {
            "backgrounds": [],
            "characters": [],
            "props": [],
        }

        for scene in scene_plan.scenes:
            # 1. Background
            bg_path = self.get_or_create_background(scene.background_id, project_dir=project_dir)
            if bg_path not in generated["backgrounds"]:
                generated["backgrounds"].append(bg_path)

            # 2. Characters & Actions
            for action in scene.actions:
                char_path = self.get_or_create_character_pose(
                    character_id=action.entity_id,
                    action=action.action,
                    expression=action.expression,
                    mouth_state="open" if "talk" in action.action else "idle",
                    project_dir=project_dir,
                )
                if char_path not in generated["characters"]:
                    generated["characters"].append(char_path)

            # 3. Props
            for prop in scene.props:
                prop_path = self.get_or_create_prop(prop, project_dir=project_dir)
                if prop_path not in generated["props"]:
                    generated["props"].append(prop_path)

        logger.info(
            f"Asset generation complete: {len(generated['backgrounds'])} backgrounds, "
            f"{len(generated['characters'])} character poses, {len(generated['props'])} props."
        )
        return generated


# Default asset manager instance
asset_manager = AssetManager()
