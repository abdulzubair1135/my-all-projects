"""
AI Provider abstraction layer for StickForge AI.
Supports visible DeepSeek browser automation, direct API, and deterministic mock modes.
"""

from __future__ import annotations
import abc
import json
import uuid
from typing import Dict, Any, Optional, Callable

from app.core.config import get_config
from app.core.logging_manager import get_logger
from app.ai.prompt_templates import (
    STORY_PROMPT_TEMPLATE,
    STORYBOARD_PROMPT_TEMPLATE,
    SUPPORTED_ACTIONS,
    SUPPORTED_BACKGROUNDS,
)
from app.ai.schema_validator import GeneratedScript, GeneratedStoryboard, CharacterDef, StoryBeat, SceneSpec, ActionSpec, CameraSpec
from app.ai.output_parser import parse_and_validate

logger = get_logger("ai_provider")


class BaseAIProvider(abc.ABC):
    """Abstract interface for Story and Storyboard generation."""

    @abc.abstractmethod
    def generate_story(
        self,
        topic: str,
        genre: str,
        language: str,
        duration_target: float,
        character_count: int = 1,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> GeneratedScript:
        pass

    @abc.abstractmethod
    def generate_storyboard(
        self,
        project_id: str,
        script: GeneratedScript,
        aspect_ratio: str = "9:16",
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> GeneratedStoryboard:
        pass


class MockAIProvider(BaseAIProvider):
    """Smart offline AI provider that dynamically creates topic-relevant scripts and storyboards."""

    def generate_story(
        self,
        topic: str,
        genre: str,
        language: str,
        duration_target: float,
        character_count: int = 1,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> GeneratedScript:
        if progress_callback:
            progress_callback(50.0, "Crafting topic-specific story beats...")

        clean_topic = topic.strip() or "The Mystery of Life"
        t_lower = clean_topic.lower()
        lang_lower = language.lower()
        is_hindi_hinglish = "hing" in lang_lower or "hi" in lang_lower

        beat_dur = round(duration_target / 4.0, 1)

        # 1. Topic-aware matching
        if any(w in t_lower for w in ["dream", "sleep", "sapna", "neend", "so", "sote"]):
            if is_hindi_hinglish:
                title = f"Sapne Kyu Aate Hain? — The Mystery of {clean_topic.title()}"
                premise = f"Har raat jab hum sote hain, hamara dimaag ajeeb aur rochak sapne dikhata hai. Lekin iske peeche ka asli scientific reason kya hai?"
                beats = [
                    StoryBeat(
                        beat_name="beginning",
                        summary="Sleeping and brain activity",
                        narration="Jab hum raat ko bistar par so jaate hain, hamara sharir relax karta hai lekin hamara dimaag bilkul active ho jata hai!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="conflict",
                        summary="The bizarre dream world",
                        narration="Achanak sapno ki ajeeb duniya shuru hoti hai—kabhi hum badalon mein udne lagte hain, toh kabhi ajeeb raston par daudte rehte hain!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="climax",
                        summary="REM stage and memory sorting",
                        narration="Science kehti hai ki neend ke REM stage mein hamara brain din bhar ki memories aur emotions ko sort aur store karta hai.",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="ending",
                        summary="Mind refresh conclusion",
                        narration="Toh agli baar jab koi ajeeb sapna aaye, samajh lijiye ki aapka super-brain aapke dimaag ko refresh kar raha hai!",
                        estimated_duration=beat_dur,
                    ),
                ]
            else:
                title = f"Why Do We Dream? — The Science of Dreams"
                premise = f"Every night as we sleep, our brain creates vivid adventures. What is the real science behind dreams?"
                beats = [
                    StoryBeat(
                        beat_name="beginning",
                        summary="Sleep and active brain",
                        narration="When our head hits the pillow and the body rests, our brain actually shifts into high-gear activity!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="conflict",
                        summary="Entering bizarre dreamscapes",
                        narration="Suddenly, bizarre dream worlds emerge—flying through clouds or running through impossible gravity-defying mazes!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="climax",
                        summary="The neuroscience of REM sleep",
                        narration="Neuroscientists discovered that during REM sleep, the brain actively organizes memories and processes daily emotions.",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="ending",
                        summary="The morning cognitive reboot",
                        narration="So whenever you wake from an unusual dream, remember: your super-brain was just performing its nightly system reboot!",
                        estimated_duration=beat_dur,
                    ),
                ]

        elif any(w in t_lower for w in ["money", "paisa", "rich", "business", "crorepati", "ameer"]):
            if is_hindi_hinglish:
                title = f"Paisa Kaise Banayein? — The Wealth Formula"
                premise = f"Har koi chahta hai ki uski jeb hamesha bhari rahe, lekin wealth banane ka asli tarika kya hai?"
                beats = [
                    StoryBeat(
                        beat_name="beginning",
                        summary="The ambition to earn",
                        narration="Har koi chahta hai ki uski jeb hamesha bhari rahe aur paise ki kabhi kami na ho!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="conflict",
                        summary="High expenses vs low savings",
                        narration="Lekin bina planning ke har roz kharche badhte jaate hain aur mahine ke aakhir mein wallet bilkul khali reh jata hai!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="climax",
                        summary="Smart investing and consistency",
                        narration="Kamyab log kehte hain ki sirf mehnat se nahi, balki smart skills aur consistent savings se wealth banti hai.",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="ending",
                        summary="Financial independence",
                        narration="Chhoti-chhoti bachat aur sahi decisions ek din bada financial freedom le kar aate hain!",
                        estimated_duration=beat_dur,
                    ),
                ]
            else:
                title = f"How Wealth Is Built — The Money Mindset"
                premise = f"Everyone dreams of financial freedom, but what actually separates big earners from the rest?"
                beats = [
                    StoryBeat(
                        beat_name="beginning",
                        summary="The desire for financial growth",
                        narration="Everyone dreams of having total financial independence and living life on their own terms.",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="conflict",
                        summary="Unplanned spending trap",
                        narration="Yet without a clear financial plan, rising expenses quickly drain monthly savings down to zero.",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="climax",
                        summary="Smart compounding and high-value skills",
                        narration="Wealth experts prove that real success comes from mastering high-value skills and the power of compounding.",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="ending",
                        summary="Lasting financial freedom",
                        narration="Small daily disciplines and smart investments compound into lifelong financial freedom!",
                        estimated_duration=beat_dur,
                    ),
                ]

        elif any(w in t_lower for w in ["exam", "study", "padh", "school", "college", "test"]):
            if is_hindi_hinglish:
                title = f"Exam Ki Tension Aur Jeet"
                premise = f"Exam se ek raat pehle ki tension ko kaise smartly handle karein?"
                beats = [
                    StoryBeat(
                        beat_name="beginning",
                        summary="Stickman blank at exam desk staring at question paper",
                        narration="Exam hall me ghuste hi dimaag ka saara syllabus achanak format ho gaya aur question paper blank dikhne laga!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="conflict",
                        summary="Whispering to topper friend for help",
                        narration="Tabhi aage baithe topper dost se umeed ki kiran dikhi aur chupke se ishara kiya—bhai teesra bata de!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="climax",
                        summary="Fierce invigilator staring with eagle eye",
                        narration="Lekin tabhi khadoos invigilator ki eagle eye hamari taraf ghoom gayi aur dimaag ki batti gul ho gayi!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="ending",
                        summary="Submitting paper with cool swagger pose",
                        narration="Aakhir me paper par roll number aur jai mata di likh kar pure swag ke saath submit kar diya!",
                        estimated_duration=beat_dur,
                    ),
                ]
            else:
                title = f"Beating Exam Anxiety — The Smart Strategy"
                premise = f"How to turn late-night study panic into calm, winning exam performance."
                beats = [
                    StoryBeat(
                        beat_name="beginning",
                        summary="Mounting study pressure",
                        narration="The night before the final exam, piles of textbooks and rising panic can feel overwhelming.",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="conflict",
                        summary="Running out of time",
                        narration="The syllabus looks like an ocean, and the ticking clock feels like a racing bullet train!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="climax",
                        summary="Calm prioritized focus",
                        narration="Taking a deep breath and focusing strictly on high-yield concepts restores clarity and confidence.",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="ending",
                        summary="Triumph through composure",
                        narration="Walking into the exam hall with a calm and prepared mind always delivers the best score!",
                        estimated_duration=beat_dur,
                    ),
                ]

        elif any(w in t_lower for w in ["ghost", "bhoot", "horror", "aatma", "haunted", "dar"]):
            if is_hindi_hinglish:
                title = f"Purani Haveli Ka Raaz"
                premise = f"Raat ke andhere mein purane kamre ka ajeeb saaya aur uska unexpected twist."
                beats = [
                    StoryBeat(
                        beat_name="beginning",
                        summary="Dark hallway",
                        narration="Raat ke 12 baje hostel ke purane corridor mein achanak ek ajeeb sa saya dikhai diya!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="conflict",
                        summary="Creepy sounds and racing heartbeat",
                        narration="Har kadam par dil ki dhadkan tez ho rahi thi aur piche se hawa ke jhonke se darwaza band ho gaya!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="climax",
                        summary="Turning on the flashlight",
                        narration="Rahul ne himmat juta kar flashlight on ki aur pure zor se saamne dekha!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="ending",
                        summary="Hilarious twist",
                        narration="Saamne koi bhoot nahi, balki uska dost chadar lapet kar midnight snack chori kar raha tha!",
                        estimated_duration=beat_dur,
                    ),
                ]
            else:
                title = f"The Midnight Mystery of the Haunted Hall"
                premise = f"A spooky hallway encounter turns into an unforgettable and funny twist."
                beats = [
                    StoryBeat(
                        beat_name="beginning",
                        summary="Midnight hallway",
                        narration="At the stroke of midnight, a strange flickering shadow appeared in the empty hallway!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="conflict",
                        summary="Sudden creepy noises",
                        narration="Footsteps echoed down the cold floorboards as the wooden door slammed shut on its own!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="climax",
                        summary="Flipping on the flashlight",
                        narration="Gathering courage, our hero switched on the flashlight and aimed straight ahead!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="ending",
                        summary="The comic reveal",
                        narration="It wasn't a phantom at all—just his friend draped in a blanket raiding the midnight snacks!",
                        estimated_duration=beat_dur,
                    ),
                ]

        elif any(w in t_lower for w in ["mom", "maa", "mummy", "mother", "angry", "gussa"]):
            if is_hindi_hinglish:
                title = f"Mummy Ka Gussa — Why Mom Is Angry"
                premise = f"Ghar par aaram se baithe stickman par Mummy ke gusse ki aafat kaise aayi."
                beats = [
                    StoryBeat(
                        beat_name="beginning",
                        summary="Stickman relaxing peacefully on sofa",
                        narration="Ghar me sab mast chill chal raha tha, phone haath me aur dimaag bilkul shaant... tabhi Mummy ke aane ki aahat hui!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="conflict",
                        summary="Angry Mom spots messy room",
                        narration="Mummy ne dekha kamra kachra petti bana hua hai, geela tauliya bistar par aur subah ke bartan waise hi pade hain!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="climax",
                        summary="Flying chappal activated",
                        narration="Mummy ka laser-guided missile weapon—flying chappal—activate ho chuka tha aur target 100% lock ho gaya!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="ending",
                        summary="Stickman cleaning fast to save life",
                        narration="Isliye bhai, Mummy se panga mat lo, chup-chap jhadu-pocha lagao aur safe raho!",
                        estimated_duration=beat_dur,
                    ),
                ]
            else:
                title = f"Why Mom Is Angry — The Flying Slipper"
                premise = f"A peaceful afternoon turns into extreme survival when mom spots a messy room."
                beats = [
                    StoryBeat(
                        beat_name="beginning",
                        summary="Relaxing on the couch",
                        narration="Everything was super chill on the couch with the phone... until footsteps echoed down the hallway!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="conflict",
                        summary="The messy room disaster",
                        narration="Mom spotted dirty laundry on the floor and unwashed dishes piled up in the sink!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="climax",
                        summary="The airborne slipper",
                        narration="Her legendary precision weapon—the flying slipper—was locked onto its target!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="ending",
                        summary="Instant survival cleaning",
                        narration="Lesson learned: grab the broom immediately and pretend you were cleaning all along!",
                        estimated_duration=beat_dur,
                    ),
                ]

        else:
            # Universal Dynamic Story Builder (NO BORING GENERIC JARGON)
            if is_hindi_hinglish:
                title = f"{clean_topic.title()} Ka Dhamaka"
                premise = f"Ek mazedaar kahani {clean_topic} ke baare mein."
                beats = [
                    StoryBeat(
                        beat_name="beginning",
                        summary=f"Start of {clean_topic}",
                        narration=f"Aapne kabhi socha hai ki {clean_topic} ka chakkar aakhir shuru kahan se hota hai? Kahani shuru hoti hai ek aam din se!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="conflict",
                        summary=f"Funny problem with {clean_topic}",
                        narration=f"Tabhi achanak sab kuch ulta-pulta ho gaya aur situation dimaag se bahar nikal gayi!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="climax",
                        summary=f"Desi Jugaad for {clean_topic}",
                        narration=f"Lekin phir lagaya gaya ek zabardast desi jugaad aur full confidence ke saath mamla sambhala gaya!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="ending",
                        summary=f"Hilarious ending of {clean_topic}",
                        narration=f"Toh dosto, {clean_topic} se seekho aur agli baar ke liye hamesha taiyyar raho!",
                        estimated_duration=beat_dur,
                    ),
                ]
            else:
                title = f"The Story of {clean_topic.title()}"
                premise = f"An engaging narrative exploring the challenges and ultimate truth of {clean_topic}."
                beats = [
                    StoryBeat(
                        beat_name="beginning",
                        summary=f"Introducing {clean_topic}",
                        narration=f"Today we dive straight into a fascinating and critical topic — {clean_topic}!",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="conflict",
                        summary=f"The friction around {clean_topic}",
                        narration=f"Misunderstandings often cloud the truth, leading to unexpected challenges and tricky hurdles along the way.",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="climax",
                        summary=f"The breakthrough for {clean_topic}",
                        narration=f"With clear insight and dedicated focus, the crucial breakthrough finally reveals the real secret.",
                        estimated_duration=beat_dur,
                    ),
                    StoryBeat(
                        beat_name="ending",
                        summary="The lasting takeaway",
                        narration=f"Mastering {clean_topic} empowers us with the wisdom and confidence to move forward successfully!",
                        estimated_duration=beat_dur,
                    ),
                ]

        full_narr = " ".join(b.narration for b in beats)
        chars = [CharacterDef(id="char_1", name="Hero", role="protagonist", color="#38BDF8")]
        if character_count > 1:
            chars.append(CharacterDef(id="char_2", name="Buddy", role="friend", color="#F59E0B"))

        if progress_callback:
            progress_callback(100.0, "Story created successfully.")

        return GeneratedScript(
            title=title,
            premise=premise,
            language=language,
            genre=genre,
            estimated_duration_seconds=duration_target,
            characters=chars,
            beats=beats,
            full_narration=full_narr,
        )

    def generate_storyboard(
        self,
        project_id: str,
        script: GeneratedScript,
        aspect_ratio: str = "9:16",
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> GeneratedStoryboard:
        if progress_callback:
            progress_callback(40.0, "Decomposing story into timed stickman scenes...")

        scenes = []
        action_sequence = ["walk", "run", "jump", "happy"]
        backgrounds = ["classroom", "street", "forest", "plain_white"]
        t_lower = (script.title + " " + script.premise).lower()

        for idx, beat in enumerate(script.beats):
            b_low = beat.narration.lower()
            if any(w in b_low for w in ["so ", "sote", "bistar", "bed", "sleep", "rest", "night"]):
                bg_name = "room"
                act_name = "sit"
            elif any(w in b_low for w in ["udne", "fly", "jump", "badal", "cloud", "chasing", "bhaag"]):
                bg_name = "plain_dark"
                act_name = "jump"
            elif any(w in b_low for w in ["science", "brain", "rem", "study", "exam", "school", "concept"]):
                bg_name = "classroom"
                act_name = "point"
            elif any(w in b_low for w in ["ghost", "bhoot", "dar", "shadow", "corridor", "aatma"]):
                bg_name = "plain_dark"
                act_name = "react"
            elif any(w in b_low for w in ["fresh", "smile", "morning", "subah", "victory", "freedom", "super"]):
                bg_name = "room" if "dream" in t_lower or "sleep" in t_lower else "street"
                act_name = "happy"
            else:
                act_name = action_sequence[idx % len(action_sequence)]
                bg_name = backgrounds[idx % len(backgrounds)]

            scenes.append(
                SceneSpec(
                    id=f"scene_{idx+1:03d}",
                    sequence_order=idx + 1,
                    duration=beat.estimated_duration,
                    background=bg_name,
                    narration=beat.narration,
                    actions=[ActionSpec(character_id="char_1", action=act_name)],
                    camera=CameraSpec(shot="medium", movement="static"),
                    sound_effects=["swoosh" if act_name == "jump" else "footsteps"],
                    transition="fade" if idx > 0 else "none",
                )
            )

        if progress_callback:
            progress_callback(100.0, "Storyboard created.")

        return GeneratedStoryboard(
            schema_version=1,
            project_id=project_id,
            title=script.title,
            language=script.language,
            aspect_ratio=aspect_ratio,
            characters=script.characters,
            scenes=scenes,
        )


class BrowserDeepSeekProvider(BaseAIProvider):
    """Integrates with visible Chromium DeepSeek automation."""

    def __init__(self):
        from app.ai.deepseek_controller import get_deepseek_controller
        self.controller = get_deepseek_controller()

    def generate_story(
        self,
        topic: str,
        genre: str,
        language: str,
        duration_target: float,
        character_count: int = 1,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> GeneratedScript:
        prompt = STORY_PROMPT_TEMPLATE.format(
            topic=topic,
            genre=genre,
            language=language,
            duration_target=duration_target,
            character_count=character_count,
        )
        job_id = f"ai_story_{uuid.uuid4().hex[:6]}"
        raw_output = self.controller.submit_prompt(
            job_id=job_id,
            project_id="active",
            task_type="story_generation",
            prompt=prompt,
            progress_callback=progress_callback,
        )
        return parse_and_validate(raw_output, GeneratedScript)

    def generate_storyboard(
        self,
        project_id: str,
        script: GeneratedScript,
        aspect_ratio: str = "9:16",
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> GeneratedStoryboard:
        prompt = STORYBOARD_PROMPT_TEMPLATE.format(
            project_id=project_id,
            title=script.title,
            language=script.language,
            aspect_ratio=aspect_ratio,
            beats_json=json.dumps([b.model_dump() for b in script.beats], indent=2),
            characters_json=json.dumps([c.model_dump() for c in script.characters], indent=2),
            supported_actions=", ".join(SUPPORTED_ACTIONS),
            supported_backgrounds=", ".join(SUPPORTED_BACKGROUNDS),
        )
        job_id = f"ai_sb_{uuid.uuid4().hex[:6]}"
        raw_output = self.controller.submit_prompt(
            job_id=job_id,
            project_id=project_id,
            task_type="storyboard_generation",
            prompt=prompt,
            progress_callback=progress_callback,
        )
        return parse_and_validate(raw_output, GeneratedStoryboard)


def get_ai_provider(provider_type: Optional[str] = None) -> BaseAIProvider:
    """Factory for configured AI provider."""
    ptype = provider_type or get_config().ai.provider
    if ptype == "deepseek_browser":
        return BrowserDeepSeekProvider()
    elif ptype == "mock":
        return MockAIProvider()
    else:
        # Fallback to Mock if unrecognized or unconfigured
        return MockAIProvider()
