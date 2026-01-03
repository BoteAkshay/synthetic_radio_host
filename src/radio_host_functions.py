"""
Synthetic Radio Host Generator - Core Functions
"""
__version__ = "2.0.1"

import os
import re
import io
import logging
from functools import reduce
from operator import add
from typing import List

from openai import OpenAI
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
import wikipediaapi

logger = logging.getLogger(__name__)

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

    "SPEAKER_A_NAME": "Vijay",
    "SPEAKER_B_NAME": "Neha",

    "VOICE_A": "pNInz6obpgDQGcFmaJgB",
    "VOICE_B": "21m00Tcm4TlvDq8ikWAM",

    "OUTPUT_FILENAME": "synthetic_radio_host.mp3",
}

# ======================
# Wikipedia
# ======================

def fetch_wikipedia_article(title: str) -> str:
    wiki = wikipediaapi.Wikipedia(
        user_agent="SyntheticRadioHost/2.0.1",
        language="en",
    )

    page = wiki.page(title.strip())
    if not page.exists():
        raise ValueError("Wikipedia page not found")

    text = page.text[:CONFIG["WIKIPEDIA_MAX_CHARS"]]
    if len(text) < 300:
        raise ValueError("Wikipedia article too short")

    return text


# ======================
# Prompt + Script
# ======================

def generate_script_prompt(wiki_text: str) -> str:
    a = CONFIG["SPEAKER_A_NAME"]
    b = CONFIG["SPEAKER_B_NAME"]
    wmin, wmax = CONFIG["SCRIPT_TARGET_WORDS"]
    tmin, tmax = CONFIG["SCRIPT_TARGET_TURNS"]

    return f"""
You are a professional Indian FM radio script writer.

Generate a natural Hinglish conversation
between two radio hosts: {a} and {b}.

MANDATORY:
- Start with: "{a}: Hi hello dosto, main {a} hoon..."
- End with friendly goodbyes from both hosts
- {wmin}-{wmax} words
- {tmin}-{tmax} turns
- Spoken Hinglish only

STYLE RULES: 
- Use casual Hinglish, not pure Hindi or English
- Frequently use fillers like: "achcha", "umm", "arre", "haan", "yaar", "matlab"
- Add light interruptions, incomplete sentences, and informal reactions 
- Add occasional laughter cues like "(laughs)" or "(chuckles)" 
- Avoid formal explanations or Wikipedia-style narration 
- Keep sentences short and conversational

FORMAT (STRICT):
{a}: ...
{b}: ...

TOPIC:
{wiki_text}
""".strip()


def generate_script(prompt: str, client: OpenAI) -> str:
    response = client.chat.completions.create(
        model=CONFIG["OPENAI_MODEL"],
        messages=[
            {"role": "system", "content": "You write natural Hinglish radio conversations."},
            {"role": "user", "content": prompt},
        ],
        temperature=CONFIG["OPENAI_TEMPERATURE"],
        max_tokens=1200,
    )

    script = response.choices[0].message.content.strip()
    if not script:
        raise RuntimeError("Empty script")

    return script


# ======================
# TTS Helpers
# ======================

def clean_for_tts(line: str) -> str:
    a = CONFIG["SPEAKER_A_NAME"]
    b = CONFIG["SPEAKER_B_NAME"]

    line = re.sub(rf"^({a}|{b}):\s*", "", line)
    line = re.sub(r"\(.*?\)", "", line)
    line = re.sub(r"\s+", " ", line)
    line = re.sub(r"\(laughs?\)|\(chuckles?\)", " haha ", line, flags=re.I)

    return line.strip()


# ======================
# Audio Generation (SMOOTH)
# ======================

def generate_audio_segments(script: str) -> List[AudioSegment]:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY not set in environment")

    client = ElevenLabs(api_key=api_key)

    a = CONFIG["SPEAKER_A_NAME"]
    b = CONFIG["SPEAKER_B_NAME"]

    segments: List[AudioSegment] = []

    for line in script.splitlines():
        if line.startswith(f"{a}:"):
            voice = CONFIG["VOICE_A"]
        elif line.startswith(f"{b}:"):
            voice = CONFIG["VOICE_B"]
        else:
            continue

        text = clean_for_tts(line)
        if not text:
            continue

        audio_stream = client.text_to_speech.convert(
            text=text,
            voice_id=voice,
            model_id=CONFIG["ELEVENLABS_MODEL"],
            output_format="mp3_44100_128",
            voice_settings={
                "stability": 0.30,
                "similarity_boost": 0.80,
                "style": 0.55,
                "use_speaker_boost": True
            }
        )

        # consume streaming generator → bytes
        audio_bytes = b"".join(chunk for chunk in audio_stream)

        segment = AudioSegment.from_file(
            io.BytesIO(audio_bytes),
            format="mp3"
        )

        segments.append(segment + AudioSegment.silent(220))

    if not segments:
        raise RuntimeError("No audio generated")

    return segments


# ======================
# Export
# ======================

def combine_and_export_audio(audio_segments: List[AudioSegment], output_file: str) -> None:
    final_audio = reduce(add, audio_segments)
    final_audio = final_audio.normalize(headroom=1.5)

    final_audio.export(output_file, format="mp3", bitrate="192k")

    logger.info(
        f"Exported {output_file} | "
        f"{len(final_audio) / 1000:.1f}s | "
        f"{os.path.getsize(output_file) / (1024 * 1024):.2f} MB"
    )