"""
Synthetic Radio Host Generator - Core Functions

Note: Import warnings in IDE are expected if dependencies aren't installed locally.
Install dependencies with: pip install -r requirements.txt
"""
__version__ = "1.0.0"

import os
import re
import io
import logging
import warnings
from functools import reduce
from operator import add
from typing import Optional, TYPE_CHECKING

warnings.filterwarnings("ignore", category=UserWarning, module="elevenlabs")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")

if TYPE_CHECKING:
    from openai import OpenAI
    from elevenlabs import Client as ElevenLabs
    from pydub import AudioSegment

try:
    from openai import OpenAI
    from elevenlabs import Client as ElevenLabs
    from pydub import AudioSegment
    import wikipediaapi
except ImportError as e:
    import sys
    error_msg = f"Required dependencies not installed: {e}\n"
    error_msg += "Install with: pip install -r requirements.txt\n"
    if sys.version_info >= (3, 13) and "pydub" in str(e).lower():
        error_msg += "\nNote: For Python 3.13+, also install: pip install audioop-lts"
    raise ImportError(error_msg) from e

CONFIG = {
    "WIKIPEDIA_MAX_CHARS": 2500,
    "SCRIPT_TARGET_WORDS": (260, 300),
    "SCRIPT_TARGET_TURNS": (16, 18),
    "OPENAI_MODEL": "gpt-4o-mini",
    "OPENAI_TEMPERATURE": 0.9,
    "ELEVENLABS_MODEL": "eleven_multilingual_v2",
    "VOICE_A_ID": "pNInz6obpgDQGcFmaJgB",
    "VOICE_B_ID": "21m00Tcm4TlvDq8ikWAM",
    "OUTPUT_FILENAME": "synthetic_radio_host.mp3"
}

logger = logging.getLogger(__name__)


def fetch_wikipedia_article(title: str, max_chars: int = CONFIG["WIKIPEDIA_MAX_CHARS"]) -> str:
    try:
        logger.info(f"Fetching Wikipedia article: {title}")
        wiki = wikipediaapi.Wikipedia(
            user_agent="SyntheticRadioHost/1.0",
            language="en"
        )
        page = wiki.page(title.strip())
        
        if not page.exists():
            raise ValueError(f"Wikipedia page not found: {title}")
        
        text = page.text[:max_chars]
        if len(text) < 100:
            raise ValueError(f"Article too short: {len(text)} characters")
        
        logger.info(f"Successfully fetched article: {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"Error fetching Wikipedia article: {e}")
        raise


def generate_script_prompt(wiki_text: str, config: dict = CONFIG) -> str:
    min_words, max_words = config["SCRIPT_TARGET_WORDS"]
    min_turns, max_turns = config["SCRIPT_TARGET_TURNS"]
    
    return f"""You are a creative Indian radio show script writer.

TASK:
Generate a natural-sounding Hinglish (Hindi + English mix) conversation
between two radio hosts (A and B) based on the topic below.

HARD CONSTRAINTS (VERY IMPORTANT):
- Total length: {min_words}–{max_words} words (≈2 minutes of speech)
- Exactly {min_turns}–{max_turns} dialogue turns total (A + B combined)
- Each line should sound spoken, not written

STYLE RULES:
- Use casual Hinglish, not pure Hindi or English
- Frequently use fillers like: "achcha", "umm", "arre", "haan", "yaar", "matlab"
- Add light interruptions, incomplete sentences, and informal reactions
- Add occasional laughter cues like "(laughs)" or "(chuckles)"
- Avoid formal explanations or Wikipedia-style narration
- Keep sentences short and conversational

FORMAT (STRICT):
A: ...
B: ...
A: ...
B: ...

TOPIC:
{wiki_text}
"""


def generate_script(prompt: str, openai_client: OpenAI) -> str:
    try:
        logger.info("Generating radio script using OpenAI...")
        response = openai_client.chat.completions.create(
            model=CONFIG["OPENAI_MODEL"],
            messages=[
                {
                    "role": "system",
                    "content": "You write conversational Indian Hinglish radio scripts."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=CONFIG["OPENAI_TEMPERATURE"],
            max_tokens=1000
        )
        
        script = response.choices[0].message.content.strip()
        
        if not script:
            raise ValueError("Generated script is empty")
        
        lines = [l for l in script.splitlines() if l.strip()]
        logger.info(f"Script generated successfully: {len(lines)} lines")
        
        return script
    except Exception as e:
        logger.error(f"Error generating script: {e}")
        raise


def clean_for_tts(line: str) -> str:
    if not line:
        return ""
    
    line = line.strip()
    line = re.sub(r"^[AB]:\s*", "", line)
    line = re.sub(r"\(laughs?\)|\(chuckles?\)", " haha ", line, flags=re.I)
    line = line.replace("…", ", ")
    line = re.sub(r"[!?]{2,}", "!", line)
    
    return line.strip()


def generate_audio_segments(script: str, eleven_client: ElevenLabs, config: dict = CONFIG) -> list:
    audio_segments = []
    lines = [l.strip() for l in script.splitlines() if l.strip()]
    total_lines = len(lines)
    
    logger.info(f"Generating audio for {total_lines} lines...")
    
    for idx, line in enumerate(lines, 1):
        try:
            if line.startswith("A:"):
                voice_id = config["VOICE_A_ID"]
            elif line.startswith("B:"):
                voice_id = config["VOICE_B_ID"]
            else:
                voice_id = config["VOICE_A_ID"]
            
            text = clean_for_tts(line)
            
            if not text:
                logger.warning(f"Skipping empty line {idx}")
                continue
            
            logger.info(f"Processing line {idx}/{total_lines}: {text[:50]}...")
            
            audio_stream = eleven_client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id=config["ELEVENLABS_MODEL"]
            )
            
            audio_bytes = b"".join(audio_stream)
            
            if not audio_bytes:
                raise ValueError(f"No audio data received for line {idx}")
            
            segment = AudioSegment.from_file(
                io.BytesIO(audio_bytes),
                format="mp3"
            )
            
            audio_segments.append(segment)
            
        except Exception as e:
            logger.error(f"Error processing line {idx}: {e}")
            raise
    
    logger.info(f"Successfully generated {len(audio_segments)} audio segments")
    return audio_segments


def combine_and_export_audio(audio_segments: list, output_file: str, files_download=None) -> None:
    try:
        if not audio_segments:
            raise ValueError("No audio segments to combine")
        
        logger.info(f"Combining {len(audio_segments)} audio segments...")
        final_audio = reduce(add, audio_segments) if len(audio_segments) > 1 else audio_segments[0]
        
        duration_seconds = len(final_audio) / 1000.0
        logger.info(f"Final audio duration: {duration_seconds:.2f} seconds")
        
        logger.info(f"Exporting to {output_file}...")
        final_audio.export(output_file, format="mp3", bitrate="192k")
        
        file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
        logger.info(f"Audio file generated successfully: {output_file} ({file_size_mb:.2f} MB)")
        
        if files_download:
            files_download(output_file)
            logger.info("Download initiated")
        
    except Exception as e:
        logger.error(f"Error exporting audio: {e}")
        raise

