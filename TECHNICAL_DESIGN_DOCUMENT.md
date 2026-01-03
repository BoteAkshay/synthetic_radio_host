# Technical Design Document
## Synthetic Radio Host Generator

---

## Table of Contents

1. [Project Overview](#1-project-overview)
   - [Track Selected](#track-selected)
   - [Purpose](#purpose)
   - [Key Features](#key-features)
2. [System Architecture](#2-system-architecture)
   - [High-Level Flow Diagram](#high-level-flow-diagram)
   - [Component Architecture](#component-architecture)
   - [Data Flow](#data-flow)
3. [Setup and Running Instructions (Google Colab)](#3-setup-and-running-instructions-google-colab)
   - [Prerequisites](#prerequisites)
   - [Step-by-Step Setup](#step-by-step-setup)
   - [Quick Start Command](#quick-start-command)
   - [Expected Output](#expected-output)
   - [Troubleshooting](#troubleshooting)
4. [Code Explanations and Assumptions](#4-code-explanations-and-assumptions)
   - [Core Functions](#core-functions)
   - [Configuration Constants](#configuration-constants)
   - [Key Assumptions](#key-assumptions)
   - [Error Handling](#error-handling)
   - [Limitations](#limitations)
5. [Summary](#summary)

---

## 1. Project Overview

### Track Selected
**AI/ML - Text-to-Speech & Natural Language Generation**

This project generates synthetic radio host conversations by combining:
- **Wikipedia API** for content sourcing
- **OpenAI GPT-4o-mini** for Hinglish script generation
- **ElevenLabs TTS** for multi-voice audio synthesis
- **Audio processing** for seamless segment combination

### Purpose
Automatically create engaging Hinglish (Hindi-English) radio conversations between two hosts (Vijay and Neha) discussing any Wikipedia topic, producing a natural-sounding MP3 audio file suitable for radio broadcasting or content creation.

### Key Features
- Automated content fetching from Wikipedia
- AI-generated conversational scripts in Hinglish
- Dual-voice TTS with natural pauses
- High-quality MP3 audio output (192kbps)

---

## 2. System Architecture

### High-Level Flow Diagram

```
┌─────────────────┐
│  User Input     │
│  (Topic Name)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Wikipedia API          │
│  - Fetch article        │
│  - Extract text         │
│  - Limit to 2500 chars  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  OpenAI GPT-4o-mini     │
│  - Generate prompt      │
│  - Create Hinglish      │
│    conversation script  │
│  - 260-300 words        │
│  - 16-18 dialogue turns │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Script Parser          │
│  - Split by speaker     │
│  - Clean text           │
│  - Remove labels        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  ElevenLabs TTS         │
│  - Voice A (Vijay)      │
│  - Voice B (Neha)       │
│  - Generate segments    │
│  - Add 220ms pauses     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Audio Processing       │
│  - Combine segments     │
│  - Normalize audio      │
│  - Export MP3 (192kbps) │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Output File            │
│  synthetic_radio_host.mp3│
└─────────────────────────┘
```

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Colab Environment                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  Repository      │    │  Dependencies    │              │
│  │  Setup           │───▶│  Installation    │              │
│  └──────────────────┘    └──────────────────┘              │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           radio_host_functions.py                    │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  • fetch_wikipedia_article()                         │   │
│  │  • generate_script_prompt()                          │   │
│  │  • generate_script()                                 │   │
│  │  • clean_for_tts()                                   │   │
│  │  • generate_audio_segments()                         │   │
│  │  • combine_and_export_audio()                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   OpenAI     │  │  ElevenLabs  │  │  Wikipedia   │      │
│  │   API        │  │     API      │  │     API      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Wikipedia Text (2500 chars)
    │
    ├─▶ Prompt Generation
    │   └─▶ Hinglish conversation template
    │
    ├─▶ OpenAI API Call
    │   └─▶ Script (260-300 words, 16-18 turns)
    │
    ├─▶ Script Parsing
    │   ├─▶ Vijay lines → Voice A
    │   └─▶ Neha lines → Voice B
    │
    ├─▶ ElevenLabs TTS (per line)
    │   ├─▶ Audio Segment 1 (Vijay)
    │   ├─▶ Audio Segment 2 (Neha)
    │   └─▶ ... (with 220ms pauses)
    │
    └─▶ Audio Combination
        └─▶ Final MP3 (normalized, 192kbps)
```

---

## 3. Setup and Running Instructions (Google Colab)

### Prerequisites
1. **Google Colab Account** (free tier sufficient)
2. **API Keys** (stored in Colab Secrets):
   - OpenAI API Key
   - ElevenLabs API Key

### Step-by-Step Setup

#### Step 1: Configure API Keys
1. Open Google Colab: https://colab.research.google.com/
2. Click **🔑 Secrets** (key icon in left sidebar)
3. Add two secrets:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ELEVENLABS_API_KEY`: Your ElevenLabs API key

#### Step 2: Upload Notebook
1. Upload `synthetic_radio_host_main.ipynb` to Colab
2. Or clone from repository:
   ```python
   !git clone https://github.com/BoteAkshay/synthetic_radio_host.git
   ```

#### Step 3: Run Notebook Cells
Execute cells sequentially:

**Cell 1-2: Repository Setup**
- Clones/updates repository from GitHub
- Adds source directory to Python path

**Cell 3-4: Dependency Installation**
- Installs packages from `requirements.txt`:
  - `wikipedia-api==0.6.0`
  - `openai==1.3.9`
  - `elevenlabs>=1.0.0`
  - `pydub==0.25.1`
- Uses marker file to avoid re-installation

**Cell 5-6: Initialize API Clients**
- Loads API keys from Colab secrets
- Initializes OpenAI and ElevenLabs clients
- Validates keys are present

**Cell 7-8: Fetch Wikipedia Article**
- Change `WIKIPEDIA_TOPIC` variable (default: "MS Dhoni")
- Fetches article text (max 2500 characters)

**Cell 9-10: Generate Script**
- Creates Hinglish conversation prompt
- Calls OpenAI API with retry logic (max 2 attempts)
- Validates script length (minimum 600 characters)

**Cell 11-12: Generate Audio Segments**
- Splits script by speaker (Vijay/Neha)
- Generates TTS audio for each line
- Adds 220ms pauses between segments

**Cell 13-14: Export Audio**
- Combines all audio segments
- Normalizes audio levels
- Exports as MP3 (192kbps)
- Downloads file automatically

### Quick Start Command
```python
# Change topic here (Cell 8)
WIKIPEDIA_TOPIC = "Your Topic Here"
```

### Expected Output
- **File**: `synthetic_radio_host.mp3`
- **Duration**: ~30-60 seconds (depending on script length)
- **Size**: ~1-2 MB
- **Format**: MP3, 192kbps, 44.1kHz

### Troubleshooting
- **API Key Errors**: Verify keys in Colab Secrets
- **Wikipedia Not Found**: Check topic spelling/capitalization
- **Short Script**: Increase `MIN_SCRIPT_CHARS` or adjust prompt
- **Audio Generation Fails**: Check ElevenLabs API quota/credits

---

## 4. Code Explanations and Assumptions

### Core Functions

#### `fetch_wikipedia_article(title: str) -> str`
**Purpose**: Retrieves Wikipedia article text for a given topic.

**Process**:
1. Creates Wikipedia API client with user agent
2. Fetches page by title
3. Validates page exists
4. Truncates to 2500 characters (configurable)
5. Ensures minimum 300 characters

**Assumptions**:
- Wikipedia article exists for the topic
- English Wikipedia is used
- Article contains sufficient content (>300 chars)

#### `generate_script_prompt(wiki_text: str) -> str`
**Purpose**: Creates a structured prompt for OpenAI to generate Hinglish radio conversation.

**Key Elements**:
- Speaker names: Vijay (A) and Neha (B)
- Target: 260-300 words, 16-18 dialogue turns
- Format: Strict speaker-label format (`Vijay: ...`, `Neha: ...`)
- Style: Natural Hinglish (Hindi-English mix)

**Assumptions**:
- OpenAI model understands Hinglish
- Prompt format ensures consistent output structure

#### `generate_script(prompt: str, client: OpenAI) -> str`
**Purpose**: Calls OpenAI API to generate the conversation script.

**Configuration**:
- Model: `gpt-4o-mini` (cost-effective)
- Temperature: `0.9` (creative, natural conversation)
- Max tokens: `1200` (sufficient for target length)

**Assumptions**:
- API key is valid and has credits
- Model generates properly formatted script
- Retry logic handles transient failures

#### `clean_for_tts(line: str) -> str`
**Purpose**: Removes speaker labels and formatting for TTS input.

**Process**:
1. Removes speaker prefixes (`Vijay:`, `Neha:`)
2. Removes parenthetical notes `(laughs)`
3. Normalizes whitespace

**Assumptions**:
- Script follows strict format
- Parentheticals are not needed for TTS

#### `generate_audio_segments(script: str) -> List[AudioSegment]`
**Purpose**: Converts script lines to audio segments using ElevenLabs TTS.

**Process**:
1. Splits script by lines
2. Identifies speaker (Vijay → Voice A, Neha → Voice B)
3. Cleans text for TTS
4. Calls ElevenLabs API per line
5. Converts streaming response to AudioSegment
6. Adds 220ms silence between segments

**Voice Configuration**:
- Voice A (Vijay): `pNInz6obpgDQGcFmaJgB`
- Voice B (Neha): `21m00Tcm4TlvDq8ikWAM`
- Model: `eleven_multilingual_v2` (supports Hinglish)
- Settings: Stability 0.30, Similarity 0.80, Style 0.55

**Assumptions**:
- ElevenLabs API key is valid
- Voices support Hinglish pronunciation
- Streaming audio chunks can be combined
- 220ms pause creates natural conversation flow

#### `combine_and_export_audio(segments: List[AudioSegment], output_file: str) -> None`
**Purpose**: Combines audio segments into final MP3 file.

**Process**:
1. Concatenates all segments using `reduce(add, segments)`
2. Normalizes audio (headroom: 1.5dB)
3. Exports as MP3 (192kbps)

**Assumptions**:
- All segments are compatible formats
- Normalization prevents clipping
- 192kbps provides good quality/size balance

### Configuration Constants

```python
CONFIG = {
    "WIKIPEDIA_MAX_CHARS": 2500,      # Article text limit
    "SCRIPT_TARGET_WORDS": (260, 300), # Target script length
    "SCRIPT_TARGET_TURNS": (16, 18),   # Dialogue turns
    "OPENAI_MODEL": "gpt-4o-mini",     # Cost-effective model
    "OPENAI_TEMPERATURE": 0.9,         # Creative output
    "ELEVENLABS_MODEL": "eleven_multilingual_v2",
    "SPEAKER_A_NAME": "Vijay",
    "SPEAKER_B_NAME": "Neha",
    "VOICE_A": "pNInz6obpgDQGcFmaJgB", # Vijay voice ID
    "VOICE_B": "21m00Tcm4TlvDq8ikWAM", # Neha voice ID
    "OUTPUT_FILENAME": "synthetic_radio_host.mp3"
}
```

### Key Assumptions

1. **API Availability**: OpenAI and ElevenLabs APIs are accessible and have sufficient credits
2. **Language Support**: Models support Hinglish (Hindi-English mix)
3. **Voice Quality**: Pre-selected voices produce natural-sounding Hinglish
4. **Script Format**: OpenAI generates scripts in strict `Speaker: text` format
5. **Audio Compatibility**: All segments can be combined without format issues
6. **Colab Environment**: Google Colab provides necessary system dependencies (ffmpeg for pydub)
7. **Network Stability**: Stable internet connection for API calls
8. **Topic Validity**: Wikipedia topics are spelled correctly and exist

### Error Handling

- **Wikipedia**: Raises `ValueError` if page not found or too short
- **OpenAI**: Retry logic (2 attempts) for transient failures
- **Script Validation**: Checks minimum length (600 chars)
- **API Keys**: Validates presence before execution
- **Audio Generation**: Raises `RuntimeError` if no segments created

### Limitations

1. **Wikipedia Dependency**: Requires valid Wikipedia article
2. **API Costs**: Uses paid APIs (OpenAI, ElevenLabs)
3. **Language**: Optimized for Hinglish, may not work well for other languages
4. **Voice Selection**: Fixed voices, not customizable in current version
5. **Script Quality**: Depends on OpenAI model performance
6. **Audio Length**: Limited by script generation (typically 30-60 seconds)

---

## Summary

This project automates the creation of synthetic radio host conversations by combining Wikipedia content, AI-generated Hinglish scripts, and multi-voice TTS. The system is designed for Google Colab with minimal setup, producing broadcast-quality audio files suitable for content creation or radio production.

**Technology Stack**: Python, OpenAI API, ElevenLabs API, Wikipedia API, pydub
**Output**: MP3 audio file with natural Hinglish conversation
**Use Cases**: Content creation, radio production, educational demonstrations, AI/ML showcases
