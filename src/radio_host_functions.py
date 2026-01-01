"""
Synthetic Radio Host Generator - Core Functions
"""
__version__ = "1.0.1"

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
    "VOICE_A": "Adam",
    "VOICE_B": "Rachel",
    "OUTPUT_FILENAME": "synthetic_radio_host.mp3",
}

logger = logging.getLogger(__name__)


# ======================
# Wikipedia
# ======================

def fetch_wikipedia_article(title: str, max_chars: int = CONFIG["WIKIPEDIA_MAX_CHARS"]) -> str:
    logger.info(f"Fetching Wikipedia article: {title}")

    wiki = wikipediaapi.Wikipedia(
        user_agent="SyntheticRadioHost/1.0",
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

    return f"""
You are a creative Indian radio show script writer.

TASK:
Generate a natural-sounding Hinglish conversation
between two radio hosts (A and B).

HARD CONSTRAINTS:
- {min_words}–{max_words} words total
- {min_turns}–{max_turns} dialogue turns
- Conversational, spoken style only

STYLE:
- Casual Hinglish
- Fillers: achcha, yaar, haan, matlab
- Light laughter like "haha"
- Short sentences

FORMAT:
A: ...
B: ...

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
    line = re.sub(r"^[AB]:\s*", "", line)
    line = re.sub(r"\(laughs?\)|\(chuckles?\)", " haha ", line, flags=re.I)
    line = line.replace("…", ", ")
    line = re.sub(r"[!?]{2,}", "!", line)
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
    lines = [l for l in script.splitlines() if l.strip()]
    audio_segments: List[AudioSegment] = []

    logger.info(f"Generating audio for {len(lines)} lines")

    for idx, line in enumerate(lines, start=1):
        voice = CONFIG["VOICE_A"] if line.startswith("A:") else CONFIG["VOICE_B"]
        text = clean_for_tts(line)

        if not text:
            continue

        logger.info(f"TTS line {idx}/{len(lines)} | voice={voice}")

        audio_bytes = generate(
            text=text,
            voice=voice,
            model=CONFIG["ELEVENLABS_MODEL"],
        )

        segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
        audio_segments.append(segment)

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
    duration = len(final_audio) / 1000

    final_audio.export(output_file, format="mp3", bitrate="192k")
    size_mb = os.path.getsize(output_file) / (1024 * 1024)

    logger.info(f"Exported {output_file} | {duration:.1f}s | {size_mb:.2f}MB")
