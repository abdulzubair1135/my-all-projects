"""
Tests for Phase 3 & 4: AI Script Generation, Storyboard Decomposition, and Continuity Checker.
"""

import pytest
from app.ai.output_parser import extract_json_str, clean_and_repair_json, parse_and_validate
from app.ai.schema_validator import GeneratedScript, GeneratedStoryboard, SceneSpec, ActionSpec, CharacterDef
from app.ai.ai_provider import MockAIProvider
from app.story.continuity_checker import check_continuity


def test_output_parser_markdown_fence():
    raw = """
    Here is the story script for your project:
    ```json
    {
      "title": "The Golden Stick",
      "premise": "A stickman finds a magic staff.",
      "language": "hinglish",
      "genre": "comedy",
      "estimated_duration_seconds": 20.0,
      "characters": [],
      "beats": [],
      "full_narration": "Intro narration"
    }
    ```
    Hope you like it!
    """
    parsed = parse_and_validate(raw, GeneratedScript)
    assert parsed.title == "The Golden Stick"
    assert parsed.language == "hinglish"


def test_output_parser_trailing_comma_repair():
    raw_bad = '{"title": "Test", "premise": "Hook", "beats": [],}'
    repaired = clean_and_repair_json(raw_bad)
    assert repaired == '{"title": "Test", "premise": "Hook", "beats": []}'


def test_mock_ai_provider_story_and_storyboard():
    provider = MockAIProvider()
    
    # 1. Generate story
    script = provider.generate_story(
        topic="Cricket Match",
        genre="comedy",
        language="hinglish",
        duration_target=24.0,
        character_count=2,
    )
    assert "Cricket Match" in script.title
    assert len(script.characters) == 2
    assert len(script.beats) == 4
    assert script.estimated_duration_seconds == 24.0

    # 2. Generate storyboard
    storyboard = provider.generate_storyboard(
        project_id="proj_test_123",
        script=script,
        aspect_ratio="9:16",
    )
    assert storyboard.project_id == "proj_test_123"
    assert len(storyboard.scenes) == 4
    assert storyboard.scenes[0].actions[0].action in ["walk", "run", "jump", "happy"]


def test_continuity_checker():
    # Valid storyboard
    sb = GeneratedStoryboard(
        project_id="p1",
        title="Valid Story",
        characters=[CharacterDef(id="hero", name="Hero")],
        scenes=[
            SceneSpec(
                id="s1",
                sequence_order=1,
                duration=5.0,
                background="classroom",
                actions=[ActionSpec(character_id="hero", action="walk")],
            )
        ]
    )
    report = check_continuity(sb, target_duration=5.0)
    assert report.is_valid is True
    assert len(report.errors) == 0

    # Invalid storyboard: missing character and illegal action
    bad_sb = GeneratedStoryboard(
        project_id="p2",
        title="Bad Story",
        characters=[CharacterDef(id="hero", name="Hero")],
        scenes=[
            SceneSpec(
                id="s1",
                sequence_order=1,
                duration=5.0,
                background="classroom",
                actions=[
                    ActionSpec(character_id="ghost", action="walk"),
                    ActionSpec(character_id="hero", action="fly_like_a_superhero_unknown"),
                ],
            )
        ]
    )
    bad_report = check_continuity(bad_sb, target_duration=5.0)
    assert bad_report.is_valid is False
    assert any("ghost" in err for err in bad_report.errors)
    assert any("fly_like_a_superhero_unknown" in err for err in bad_report.errors)
