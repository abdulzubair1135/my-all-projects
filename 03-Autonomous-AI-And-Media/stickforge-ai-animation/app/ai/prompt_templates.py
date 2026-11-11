"""
Prompt Templates for StickForge AI Director.
Structured prompts for story creation, storyboard decomposition, and metadata generation.
"""

from __future__ import annotations

SUPPORTED_ACTIONS = [
    "stand", "walk", "run", "jump", "fall", "sit", "crouch",
    "wave", "point", "explain", "shrug", "raise_hands",
    "happy", "sad", "angry", "shocked", "confused", "scared",
    "handshake", "hug", "push", "dodge", "fight_punch", "fight_kick"
]

SUPPORTED_BACKGROUNDS = [
    "classroom", "street", "room", "office", "forest", "plain_white", "plain_dark"
]


STORY_PROMPT_TEMPLATE = """You are the Lead Story Director for StickForge AI, specializing in short-form animated stickman storytelling.
Create a compelling short story formatted as strict JSON based on the user's parameters.

Parameters:
- Topic: {topic}
- Genre: {genre}
- Language: {language} (English, Hindi, or conversational Hinglish)
- Target Duration: {duration_target} seconds
- Audience: General / Social Media Shorts & Reels
- Number of Characters: {character_count}

Output JSON Schema:
```json
{{
  "title": "Catchy Story Title",
  "premise": "1-sentence hook",
  "language": "{language}",
  "genre": "{genre}",
  "estimated_duration_seconds": {duration_target},
  "characters": [
    {{
      "id": "char_1",
      "name": "Character Name",
      "role": "protagonist",
      "style": "classic_stickman",
      "color": "#FFFFFF",
      "description": "Short bio"
    }}
  ],
  "beats": [
    {{
      "beat_name": "beginning",
      "summary": "Scene summary",
      "narration": "Voiceover lines in {language}",
      "estimated_duration": 6.0
    }},
    {{
      "beat_name": "conflict",
      "summary": "The dilemma arises",
      "narration": "Voiceover lines",
      "estimated_duration": 8.0
    }},
    {{
      "beat_name": "escalation",
      "summary": "Stakes get higher",
      "narration": "Voiceover lines",
      "estimated_duration": 8.0
    }},
    {{
      "beat_name": "climax",
      "summary": "Turning point",
      "narration": "Voiceover lines",
      "estimated_duration": 8.0
    }},
    {{
      "beat_name": "ending",
      "summary": "Resolution or punchline",
      "narration": "Voiceover lines",
      "estimated_duration": 6.0
    }}
  ],
  "full_narration": "Complete narration text for voiceover..."
}}
```

Requirements:
1. ONLY return the valid JSON object. No intro, no conversational text.
2. In Hinglish mode, use relatable everyday Romanized Hindi (e.g., "Rahul ke paas paise nahi the, lekin uske sapne bahut bade the.").
3. Keep the narration pacing tight and energetic.
"""


STORYBOARD_PROMPT_TEMPLATE = """You are the Animation Choreographer for StickForge AI.
Convert the provided script into timed storyboard scenes for a stickman animation video.

Project ID: {project_id}
Script Title: {title}
Target Aspect Ratio: {aspect_ratio} (9:16 vertical or 16:9 horizontal)
Story Beats & Narration:
{beats_json}

Supported Actions: {supported_actions}
Supported Backgrounds: {supported_backgrounds}

Output JSON Schema:
```json
{{
  "schema_version": 1,
  "project_id": "{project_id}",
  "title": "{title}",
  "language": "{language}",
  "aspect_ratio": "{aspect_ratio}",
  "characters": {characters_json},
  "scenes": [
    {{
      "id": "scene_001",
      "sequence_order": 1,
      "duration": 6.0,
      "background": "classroom",
      "actions": [
        {{
          "character_id": "char_1",
          "action": "walk",
          "parameters": {{"direction": "right", "speed": 1.0}}
        }}
      ],
      "narration": "Voiceover narration for this scene",
      "dialogue": "",
      "camera": {{
        "shot": "medium",
        "movement": "static",
        "speed": 1.0
      }},
      "sound_effects": ["footsteps"],
      "transition": "fade"
    }}
  ]
}}
```

Strict Rules:
1. Every scene's `action` MUST be chosen from the Supported Actions list.
2. DO NOT invent arbitrary function calls or Python code.
3. Total duration of scenes should closely match the script duration.
4. ONLY return valid JSON.
"""
