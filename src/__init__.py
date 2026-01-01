"""
Synthetic Radio Host Generator Package
"""

from .radio_host_functions import (
    __version__,
    CONFIG,
    fetch_wikipedia_article,
    generate_script_prompt,
    generate_script,
    clean_for_tts,
    generate_audio_segments,
    combine_and_export_audio
)

__all__ = [
    "__version__",
    "CONFIG",
    "fetch_wikipedia_article",
    "generate_script_prompt",
    "generate_script",
    "clean_for_tts",
    "generate_audio_segments",
    "combine_and_export_audio",
]

