"""
AUTO YT GENERATOR — Asset Data Models.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from app.constants import AssetType


class AssetMetadata(BaseModel):
    """Metadata describing dimensions, parameters, or tags of an asset."""

    width: Optional[int] = None
    height: Optional[int] = None
    format: str = "png"
    tags: list[str] = Field(default_factory=list)
    generator: str = "procedural"
    custom_props: Dict[str, Any] = Field(default_factory=dict)


class AssetModel(BaseModel):
    """Catalog entry for an asset (character, background, prop, audio, etc.)."""

    id: str = Field(..., description="Unique asset identifier")
    name: str
    asset_type: str = Field(..., description="AssetType enum value")
    file_path: str
    content_hash: str
    is_procedural: bool = True
    metadata: AssetMetadata = Field(default_factory=AssetMetadata)
    created_at: datetime = Field(default_factory=datetime.utcnow)
