# Synthetic Radio Host Generator

A production-grade system for generating synthetic radio show content using AI, featuring Hinglish (Hindi-English) conversation generation and text-to-speech conversion.

## Features

- 📚 Wikipedia article fetching
- 🤖 AI-powered script generation (OpenAI GPT)
- 🎙️ Multi-voice text-to-speech (ElevenLabs)
- 🎵 Audio composition and export
- ✅ Comprehensive unit test coverage (92%)
- 📊 Production-ready logging
- 🔄 CI/CD pipeline with GitHub Actions
- 📦 Versioned and pinned dependencies

## Project Structure

```
synthetic_radio_host/
├── src/
│   └── radio_host_functions.py  # Core business logic
├── tests/
│   ├── test_radio_host.py        # Unit tests
│   ├── run_tests.py              # Test runner
│   └── TEST_README.md            # Test documentation
├── notebooks/
│   └── synthetic_radio_host_main.ipynb  # Colab notebook
├── .github/
│   └── workflows/
│       └── ci.yml                # CI/CD pipeline
├── requirements.txt              # Production dependencies (pinned)
├── requirements-test.txt         # Test dependencies
├── env.example                   # Environment variables template
├── LICENSE                       # MIT License
└── README.md                     # This file
```

## Quick Start

### In Google Colab

1. Open `notebooks/synthetic_radio_host_main.ipynb` in Google Colab
2. The notebook will automatically:
   - Clone the repository from GitHub
   - Install dependencies from `requirements.txt`
   - Import functions from the module (no code duplication!)
3. Set up API keys in Colab Secrets:
   - `OPENAI_API_KEY`
   - `ELEVENLABS_API_KEY`
4. Run the notebook cells sequentially

### Local Development

```bash
# Clone repository
git clone https://github.com/Procrastinator02/synthetic_radio_host.git
cd synthetic_radio_host

# Install dependencies
pip install -r requirements.txt

# Install test dependencies
pip install -r requirements-test.txt

# Run tests
cd tests
python run_tests.py

# Or use pytest directly
pytest tests/test_radio_host.py -v --cov=src/radio_host_functions
```

## Configuration

Edit `CONFIG` dictionary in `src/radio_host_functions.py`:

- `WIKIPEDIA_MAX_CHARS`: Maximum characters from Wikipedia (default: 2500)
- `SCRIPT_TARGET_WORDS`: Target word count range (default: 260-300)
- `SCRIPT_TARGET_TURNS`: Target dialogue turns (default: 16-18)
- `VOICE_A_ID` / `VOICE_B_ID`: ElevenLabs voice IDs
- `OUTPUT_FILENAME`: Output audio filename

## Usage

```python
from src.radio_host_functions import (
    fetch_wikipedia_article,
    generate_script_prompt,
    generate_script,
    generate_audio_segments,
    combine_and_export_audio
)
from openai import OpenAI
from elevenlabs import ElevenLabs

# Initialize clients
openai_client = OpenAI(api_key="your-key")
eleven_client = ElevenLabs(api_key="your-key")

# Fetch Wikipedia content
wiki_text = fetch_wikipedia_article("MS Dhoni")

# Generate script
prompt = generate_script_prompt(wiki_text)
script = generate_script(prompt, openai_client)

# Generate audio
segments = generate_audio_segments(script, eleven_client)

# Export
combine_and_export_audio(segments, "output.mp3")
```

## Testing

Comprehensive unit test suite with 48+ test cases covering:

- Text processing functions
- API integrations (mocked)
- Error handling
- Edge cases

**Test Coverage: 92%**

Run tests:
```bash
# From project root
cd tests
python run_tests.py

# Or with pytest
pytest tests/test_radio_host.py -v --cov=src/radio_host_functions
```

See [tests/TEST_README.md](tests/TEST_README.md) for detailed testing documentation.

## Requirements

### Production
- `wikipedia-api==0.6.0`
- `openai==1.12.0`
- `elevenlabs==0.2.27`
- `pydub==0.25.1`
- `audioop-lts` (Python 3.13+)

### Testing
- `pytest>=7.4.0`
- `pytest-cov>=4.1.0`
- `pytest-mock>=3.11.1`

## Environment Variables

Copy `env.example` to `.env` and fill in your API keys:

```bash
cp env.example .env
# Edit .env with your actual API keys
```

Required:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key

## Production Deployment

This codebase is structured for production use:

- ✅ Modular architecture (`src/` directory)
- ✅ Comprehensive error handling
- ✅ Structured logging
- ✅ Unit test coverage (92%)
- ✅ Version control ready
- ✅ CI/CD compatible (GitHub Actions)
- ✅ Pinned dependency versions
- ✅ Versioned module (`__version__ = "1.0.0"`)
- ✅ MIT License

## CI/CD

GitHub Actions automatically runs:
- Tests on Python 3.9, 3.10, 3.11, 3.12
- Code coverage reporting
- Linting (flake8, black, isort)

See `.github/workflows/ci.yml` for details.

## Version

Current version: **1.0.0**

Check version:
```python
from src.radio_host_functions import __version__
print(__version__)
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new features
4. Ensure all tests pass (`python tests/run_tests.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Acknowledgments

- OpenAI for GPT API
- ElevenLabs for text-to-speech API
- Wikipedia API for content fetching
