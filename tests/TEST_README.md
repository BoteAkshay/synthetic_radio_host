# Unit Tests for Synthetic Radio Host Generator

## Overview

This test suite provides comprehensive unit tests for all functions in the Synthetic Radio Host Generator. The tests use pytest with mocking to test functionality without requiring actual API calls or external dependencies.

## Test Coverage

The test suite covers:

1. **`clean_for_tts`** - Text cleaning function
   - Speaker label removal
   - Laughter/chuckle replacement
   - Punctuation normalization
   - Edge cases (empty strings, whitespace)

2. **`generate_script_prompt`** - Prompt generation
   - Wiki text inclusion
   - Configuration parameter usage
   - Format validation

3. **`fetch_wikipedia_article`** - Wikipedia article fetching
   - Successful article retrieval
   - Character limit enforcement
   - Error handling (page not found, short articles)
   - Title whitespace handling

4. **`generate_script`** - OpenAI script generation
   - Successful script generation
   - Empty script detection
   - API parameter validation
   - Error handling

5. **`generate_audio_segments`** - Audio segment generation
   - Voice selection (A vs B)
   - Text cleaning application
   - Empty line handling
   - Audio data validation
   - Error handling

6. **`combine_and_export_audio`** - Audio combination and export
   - Segment combination
   - File export
   - Duration calculation
   - File size logging
   - Error handling

## Installation

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

Or install manually:

```bash
pip install pytest pytest-cov pytest-mock
```

## Running Tests

### Run all tests:

```bash
pytest test_radio_host.py -v
```

### Run with coverage:

```bash
pytest test_radio_host.py --cov=radio_host_functions --cov-report=term-missing
```

### Run specific test class:

```bash
pytest test_radio_host.py::TestCleanForTTS -v
```

### Run specific test:

```bash
pytest test_radio_host.py::TestCleanForTTS::test_remove_speaker_label_a -v
```

### Using the test runner:

```bash
python run_tests.py
```

This will run tests with coverage and generate an HTML coverage report in `htmlcov/`.

## Test Structure

Tests are organized into classes by function:

- `TestCleanForTTS` - Tests for text-to-speech cleaning
- `TestGenerateScriptPrompt` - Tests for prompt generation
- `TestFetchWikipediaArticle` - Tests for Wikipedia fetching
- `TestGenerateScript` - Tests for script generation
- `TestGenerateAudioSegments` - Tests for audio generation
- `TestCombineAndExportAudio` - Tests for audio export

## Mocking Strategy

The tests use `unittest.mock` to mock external dependencies:

- **Wikipedia API**: Mocked to avoid actual API calls
- **OpenAI API**: Mocked to avoid API costs and network calls
- **ElevenLabs API**: Mocked to avoid API costs and network calls
- **File operations**: Mocked where appropriate
- **AudioSegment**: Mocked for audio processing tests

## Expected Test Results

All tests should pass. The test suite includes:

- **Positive test cases**: Valid inputs and expected outputs
- **Negative test cases**: Error conditions and edge cases
- **Boundary tests**: Limits and constraints
- **Integration-style tests**: Function interactions

## Continuous Integration

These tests are designed to run in CI/CD pipelines. They:

- Have no external dependencies (all APIs are mocked)
- Run quickly (no network calls)
- Provide clear error messages
- Include comprehensive coverage reporting

## Notes

- Tests do not require API keys or Colab environment
- All external services are mocked
- Tests can run locally or in CI/CD environments
- The `radio_host_functions.py` module contains the testable functions

