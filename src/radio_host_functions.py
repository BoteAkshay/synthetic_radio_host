"""
Synthetic Radio Host Generator - Core Functions
"""
__version__ = "1.1.0"

import os
import re
import io
import logging
import warnings
from functools import reduce
from operator import add
from typing import List

warnings.filterwarnings("ignore", category=UserWarning, module="elevenlabs")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")

try:
    from openai import OpenAI
    from elevenlabs import generate, set_api_key
    from pydub import AudioSegment
    import wikipediaapi
except ImportError as e:
    raise ImportError(
        f"Required dependencies not installed: {e}\n"
        "Install with: pip install wikipedia-api openai elevenlabs pydub"
    ) from e


# ======================
# Configuration
# ======================

CONFIG = {
    "WIKIPEDIA_MAX_CHARS": 2500,
    "SCRIPT_TARGET_WORDS": (260, 300),
    "SCRIPT_TARGET_TURNS": (16, 18),

    "OPENAI_MODEL": "gpt-4o-mini",
    "OPENAI_TEMPERATURE": 0.9,

    "ELEVENLABS_MODEL": "eleven_multilingual_v2",

    # 🎙️ Speaker configuration
    "SPEAKER_A_NAME": "Vijay",
    "SPEAKER_B_NAME": "Neha",
    "VOICE_A": "pNInz6obpgDQGcFmaJgB",
    "VOICE_B": "21m00Tcm4TlvDq8ikWAM",

    "OUTPUT_FILENAME": "synthetic_radio_host.mp3",
}

logger = logging.getLogger(__name__)


# ======================
# Wikipedia
# ======================

def fetch_wikipedia_article(title: str, max_chars: int = CONFIG["WIKIPEDIA_MAX_CHARS"]) -> str:
    logger.info(f"Fetching Wikipedia article: {title}")

    wiki = wikipediaapi.Wikipedia(
        user_agent="SyntheticRadioHost/1.1",
        language="en",
    )

    page = wiki.page(title.strip())
    if not page.exists():
        raise ValueError(f"Wikipedia page not found: {title}")

    text = page.text[:max_chars]
    if len(text) < 200:
        raise ValueError("Wikipedia article too short to generate script")

    logger.info(f"Wikipedia content loaded ({len(text)} chars)")
    return text


# ======================
# Prompt + Script
# ======================

def generate_script_prompt(wiki_text: str) -> str:
    min_words, max_words = CONFIG["SCRIPT_TARGET_WORDS"]
    min_turns, max_turns = CONFIG["SCRIPT_TARGET_TURNS"]

    speaker_a = CONFIG["SPEAKER_A_NAME"]
    speaker_b = CONFIG["SPEAKER_B_NAME"]

    return f"""
You are a creative Indian radio show script writer.

TASK:
Generate a natural-sounding Hinglish conversation
between two radio hosts named {speaker_a} and {speaker_b}.

HARD CONSTRAINTS:
- {min_words}–{max_words} words total
- {min_turns}–{max_turns} dialogue turns
- Conversational, spoken style only

STYLE (VERY IMPORTANT):
- Casual Hinglish
- Natural pauses
- Fillers like: achcha, yaar, haan, matlab
- Light laughter like "haha"
- No formal language
- Short spoken sentences

FORMAT (STRICT):
{speaker_a}: ...
{speaker_b}: ...

TOPIC:
{wiki_text}
""".strip()


def generate_script(prompt: str, client: OpenAI) -> str:
    logger.info("Generating script with OpenAI")

    response = client.chat.completions.create(
        model=CONFIG["OPENAI_MODEL"],
        messages=[
            {"role": "system", "content": "You write conversational Hinglish radio scripts."},
            {"role": "user", "content": prompt},
        ],
        temperature=CONFIG["OPENAI_TEMPERATURE"],
        max_tokens=1000,
    )

    script = response.choices[0].message.content.strip()
    if not script:
        raise ValueError("Empty script generated")

    logger.info(f"Script generated ({len(script.splitlines())} lines)")
    return script


# ======================
# TTS Helpers
# ======================

def clean_for_tts(line: str) -> str:
    speaker_a = CONFIG["SPEAKER_A_NAME"]
    speaker_b = CONFIG["SPEAKER_B_NAME"]

    line = re.sub(rf"^({speaker_a}|{speaker_b}):\s*", "", line)
    line = re.sub(r"\(laughs?\)|\(chuckles?\)", " haha ", line, flags=re.I)
    line = line.replace("…", ", ")
    line = re.sub(r"[!?]{2,}", "!", line)
    line = re.sub(r"\s+", " ", line)

    return line.strip()


def configure_elevenlabs(api_key: str) -> None:
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY missing")
    set_api_key(api_key)
    logger.info("ElevenLabs API configured")


# ======================
# Audio Generation
# ======================

def generate_audio_segments(script: str) -> List[AudioSegment]:
    speaker_a = CONFIG["SPEAKER_A_NAME"]
    speaker_b = CONFIG["SPEAKER_B_NAME"]

    lines = [l for l in script.splitlines() if l.strip()]
    audio_segments: List[AudioSegment] = []

    logger.info(f"Generating audio for {len(lines)} lines")

    for idx, line in enumerate(lines, start=1):

        if line.startswith(f"{speaker_a}:"):
            voice = CONFIG["VOICE_A"]
        elif line.startswith(f"{speaker_b}:"):
            voice = CONFIG["VOICE_B"]
        else:
            continue

        text = clean_for_tts(line)
        if not text:
            continue

        logger.info(f"TTS {idx}/{len(lines)} | voice={voice}")

        audio_bytes = generate(
            text=text,
            voice=voice,
            model=CONFIG["ELEVENLABS_MODEL"],
            voice_settings={
                "stability": 0.35,
                "similarity_boost": 0.75,
                "style": 0.45,
                "use_speaker_boost": True
            }
        )

        segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")

        # 🎧 Natural pause between turns
        pause = AudioSegment.silent(duration=250)
        audio_segments.append(segment + pause)

    if not audio_segments:
        raise RuntimeError("No audio generated")

    logger.info("Audio generation completed")
    return audio_segments


# ======================
# Export
# ======================

def combine_and_export_audio(audio_segments: List[AudioSegment], output_file: str) -> None:
    logger.info("Combining audio segments")

    final_audio = reduce(add, audio_segments)

    # 🎚️ Light normalization for radio feel
    final_audio = final_audio.normalize(headroom=2.0)

    duration = len(final_audio) / 1000
    final_audio.export(output_file, format="mp3", bitrate="192k")

    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    logger.info(f"Exported {output_file} | {duration:.1f}s | {size_mb:.2f}MB")