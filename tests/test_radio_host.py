import pytest
import re
import io
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from pydub import AudioSegment

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import radio_host_functions as rhf

CONFIG = rhf.CONFIG


class TestCleanForTTS:
    
    def test_remove_speaker_label_a(self):
        assert rhf.clean_for_tts("A: Hello world") == "Hello world"
    
    def test_remove_speaker_label_b(self):
        assert rhf.clean_for_tts("B: Test message") == "Test message"
    
    def test_remove_speaker_label_with_spaces(self):
        assert rhf.clean_for_tts("A:   Multiple spaces") == "Multiple spaces"
    
    def test_replace_laughs(self):
        result = rhf.clean_for_tts("A: That's funny (laughs)")
        assert "haha" in result
        assert "A:" not in result
    
    def test_replace_chuckles(self):
        result = rhf.clean_for_tts("B: Interesting (chuckles)")
        assert "haha" in result
        assert "B:" not in result
    
    def test_replace_laugh_case_insensitive(self):
        assert "haha" in rhf.clean_for_tts("A: Funny (LAUGHS)")
        assert "haha" in rhf.clean_for_tts("B: Hilarious (Chuckles)")
    
    def test_replace_ellipsis(self):
        assert rhf.clean_for_tts("A: Wait… what?") == "Wait,  what?"
    
    def test_normalize_multiple_exclamation(self):
        assert rhf.clean_for_tts("A: Wow!!!") == "Wow!"
        assert rhf.clean_for_tts("B: Really??") == "Really!"
    
    def test_empty_string(self):
        assert rhf.clean_for_tts("") == ""
    
    def test_whitespace_only(self):
        assert rhf.clean_for_tts("   ") == ""
    
    def test_complex_line(self):
        result = rhf.clean_for_tts("A: Arre yaar (laughs)… that's amazing!!!")
        assert "A:" not in result
        assert "haha" in result
        assert "!!!" not in result
        assert "…" not in result
    
    def test_strip_whitespace(self):
        assert rhf.clean_for_tts("  A:  Test  ") == "Test"
    
    def test_multiple_laughs(self):
        result = rhf.clean_for_tts("A: (laughs) test (chuckles) more")
        assert result.count("haha") == 2
    
    def test_no_speaker_label(self):
        assert rhf.clean_for_tts("Just a regular line") == "Just a regular line"


class TestGenerateScriptPrompt:
    
    def test_prompt_contains_wiki_text(self):
        wiki_text = "Test article content about cricket"
        prompt = rhf.generate_script_prompt(wiki_text)
        assert wiki_text in prompt
    
    def test_prompt_contains_word_constraints(self):
        wiki_text = "Test"
        prompt = rhf.generate_script_prompt(wiki_text)
        assert "260" in prompt
        assert "300" in prompt
    
    def test_prompt_contains_turn_constraints(self):
        wiki_text = "Test"
        prompt = rhf.generate_script_prompt(wiki_text)
        assert "16" in prompt
        assert "18" in prompt
    
    def test_prompt_contains_hinglish_instructions(self):
        wiki_text = "Test"
        prompt = rhf.generate_script_prompt(wiki_text)
        assert "Hinglish" in prompt
        assert "radio hosts" in prompt
    
    def test_prompt_format_section(self):
        wiki_text = "Test"
        prompt = rhf.generate_script_prompt(wiki_text)
        assert "A: ..." in prompt
        assert "B: ..." in prompt
    
    def test_custom_config(self):
        custom_config = {
            **CONFIG,
            "SCRIPT_TARGET_WORDS": (200, 250),
            "SCRIPT_TARGET_TURNS": (10, 12),
        }
        wiki_text = "Test"
        prompt = rhf.generate_script_prompt(wiki_text, custom_config)
        assert "200" in prompt
        assert "250" in prompt
        assert "10" in prompt
        assert "12" in prompt
    
    def test_prompt_contains_style_rules(self):
        wiki_text = "Test"
        prompt = rhf.generate_script_prompt(wiki_text)
        assert "achcha" in prompt
        assert "yaar" in prompt
        assert "matlab" in prompt


class TestFetchWikipediaArticle:
    
    @patch('radio_host_functions.wikipediaapi.Wikipedia')
    def test_successful_fetch(self, mock_wikipedia):
        mock_page = Mock()
        mock_page.exists.return_value = True
        mock_page.text = "A" * 500
        
        mock_wiki = Mock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia.return_value = mock_wiki
        
        result = rhf.fetch_wikipedia_article("Test Topic")
        assert len(result) == 500
        assert result == "A" * 500
        mock_wiki.page.assert_called_once_with("Test Topic")
    
    @patch('radio_host_functions.wikipediaapi.Wikipedia')
    def test_respects_max_chars(self, mock_wikipedia):
        mock_page = Mock()
        mock_page.exists.return_value = True
        mock_page.text = "A" * 5000
        
        mock_wiki = Mock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia.return_value = mock_wiki
        
        result = rhf.fetch_wikipedia_article("Test Topic", max_chars=1000)
        assert len(result) == 1000
    
    @patch('radio_host_functions.wikipediaapi.Wikipedia')
    def test_strips_title_whitespace(self, mock_wikipedia):
        mock_page = Mock()
        mock_page.exists.return_value = True
        mock_page.text = "A" * 500
        
        mock_wiki = Mock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia.return_value = mock_wiki
        
        rhf.fetch_wikipedia_article("  Test Topic  ")
        mock_wiki.page.assert_called_once_with("Test Topic")
    
    @patch('radio_host_functions.wikipediaapi.Wikipedia')
    def test_page_not_found_error(self, mock_wikipedia):
        mock_page = Mock()
        mock_page.exists.return_value = False
        
        mock_wiki = Mock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia.return_value = mock_wiki
        
        with pytest.raises(ValueError, match="Wikipedia page not found"):
            rhf.fetch_wikipedia_article("NonExistent")
    
    @patch('radio_host_functions.wikipediaapi.Wikipedia')
    def test_article_too_short_error(self, mock_wikipedia):
        mock_page = Mock()
        mock_page.exists.return_value = True
        mock_page.text = "A" * 50
        
        mock_wiki = Mock()
        mock_wiki.page.return_value = mock_page
        mock_wikipedia.return_value = mock_wiki
        
        with pytest.raises(ValueError, match="Article too short"):
            rhf.fetch_wikipedia_article("Short Article")
    
    @patch('radio_host_functions.wikipediaapi.Wikipedia')
    def test_wikipedia_api_error_handling(self, mock_wikipedia):
        mock_wikipedia.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            rhf.fetch_wikipedia_article("Test")


class TestGenerateScript:
    
    def test_successful_script_generation(self):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "A: Hello\nB: Hi there\n"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        result = rhf.generate_script("Test prompt", mock_client)
        assert result == "A: Hello\nB: Hi there"
        assert mock_client.chat.completions.create.called
    
    def test_empty_script_error(self):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = ""
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with pytest.raises(ValueError, match="Generated script is empty"):
            rhf.generate_script("Test prompt", mock_client)
    
    def test_whitespace_only_script_error(self):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "   \n\t  "
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        with pytest.raises(ValueError, match="Generated script is empty"):
            rhf.generate_script("Test prompt", mock_client)
    
    def test_api_call_parameters(self):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "A: Test\n"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        rhf.generate_script("Test prompt", mock_client)
        
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs["model"] == CONFIG["OPENAI_MODEL"]
        assert call_args.kwargs["temperature"] == CONFIG["OPENAI_TEMPERATURE"]
        assert call_args.kwargs["max_tokens"] == 1000
        assert len(call_args.kwargs["messages"]) == 2
        assert call_args.kwargs["messages"][0]["role"] == "system"
        assert call_args.kwargs["messages"][1]["role"] == "user"
    
    def test_api_error_handling(self):
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with pytest.raises(Exception):
            rhf.generate_script("Test prompt", mock_client)
    
    def test_script_with_multiple_lines(self):
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "A: Line 1\nB: Line 2\nA: Line 3\n"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        
        result = rhf.generate_script("Test prompt", mock_client)
        lines = [l for l in result.splitlines() if l.strip()]
        assert len(lines) == 3


class TestGenerateAudioSegments:
    
    @patch('radio_host_functions.AudioSegment.from_file')
    @patch('radio_host_functions.io.BytesIO')
    def test_successful_audio_generation(self, mock_bytesio, mock_audio_segment):
        mock_segment = Mock()
        mock_audio_segment.return_value = mock_segment
        
        mock_eleven_client = Mock()
        mock_stream = [b"audio", b"data"]
        mock_eleven_client.text_to_speech.convert.return_value = mock_stream
        
        script = "A: Hello world\nB: Hi there\n"
        result = rhf.generate_audio_segments(script, mock_eleven_client)
        
        assert len(result) == 2
        assert mock_eleven_client.text_to_speech.convert.call_count == 2
    
    @patch('radio_host_functions.AudioSegment.from_file')
    @patch('radio_host_functions.io.BytesIO')
    def test_voice_selection_a(self, mock_bytesio, mock_audio_segment):
        mock_segment = Mock()
        mock_audio_segment.return_value = mock_segment
        
        mock_eleven_client = Mock()
        mock_stream = [b"audio"]
        mock_eleven_client.text_to_speech.convert.return_value = mock_stream
        
        script = "A: Test line\n"
        rhf.generate_audio_segments(script, mock_eleven_client)
        
        call_args = mock_eleven_client.text_to_speech.convert.call_args
        assert call_args.kwargs["voice_id"] == CONFIG["VOICE_A_ID"]
    
    @patch('radio_host_functions.AudioSegment.from_file')
    @patch('radio_host_functions.io.BytesIO')
    def test_voice_selection_b(self, mock_bytesio, mock_audio_segment):
        mock_segment = Mock()
        mock_audio_segment.return_value = mock_segment
        
        mock_eleven_client = Mock()
        mock_stream = [b"audio"]
        mock_eleven_client.text_to_speech.convert.return_value = mock_stream
        
        script = "B: Test line\n"
        rhf.generate_audio_segments(script, mock_eleven_client)
        
        call_args = mock_eleven_client.text_to_speech.convert.call_args
        assert call_args.kwargs["voice_id"] == CONFIG["VOICE_B_ID"]
    
    @patch('radio_host_functions.AudioSegment.from_file')
    @patch('radio_host_functions.io.BytesIO')
    def test_default_voice_for_no_label(self, mock_bytesio, mock_audio_segment):
        mock_segment = Mock()
        mock_audio_segment.return_value = mock_segment
        
        mock_eleven_client = Mock()
        mock_stream = [b"audio"]
        mock_eleven_client.text_to_speech.convert.return_value = mock_stream
        
        script = "No label line\n"
        rhf.generate_audio_segments(script, mock_eleven_client)
        
        call_args = mock_eleven_client.text_to_speech.convert.call_args
        assert call_args.kwargs["voice_id"] == CONFIG["VOICE_A_ID"]
    
    @patch('radio_host_functions.AudioSegment.from_file')
    @patch('radio_host_functions.io.BytesIO')
    def test_skips_empty_lines(self, mock_bytesio, mock_audio_segment):
        mock_segment = Mock()
        mock_audio_segment.return_value = mock_segment
        
        mock_eleven_client = Mock()
        mock_stream = [b"audio"]
        mock_eleven_client.text_to_speech.convert.return_value = mock_stream
        
        script = "A: Valid line\n\nB: Another line\n   \n"
        result = rhf.generate_audio_segments(script, mock_eleven_client)
        
        assert len(result) == 2
        assert mock_eleven_client.text_to_speech.convert.call_count == 2
    
    @patch('radio_host_functions.AudioSegment.from_file')
    @patch('radio_host_functions.io.BytesIO')
    def test_empty_audio_bytes_error(self, mock_bytesio, mock_audio_segment):
        mock_eleven_client = Mock()
        mock_stream = [b""]
        mock_eleven_client.text_to_speech.convert.return_value = mock_stream
        
        script = "A: Test line\n"
        
        with pytest.raises(ValueError, match="No audio data received"):
            rhf.generate_audio_segments(script, mock_eleven_client)
    
    @patch('radio_host_functions.AudioSegment.from_file')
    @patch('radio_host_functions.io.BytesIO')
    def test_text_cleaning_applied(self, mock_bytesio, mock_audio_segment):
        mock_segment = Mock()
        mock_audio_segment.return_value = mock_segment
        
        mock_eleven_client = Mock()
        mock_stream = [b"audio"]
        mock_eleven_client.text_to_speech.convert.return_value = mock_stream
        
        script = "A: Test (laughs)!!!\n"
        rhf.generate_audio_segments(script, mock_eleven_client)
        
        call_args = mock_eleven_client.text_to_speech.convert.call_args
        assert "A:" not in call_args.kwargs["text"]
        assert "haha" in call_args.kwargs["text"]
    
    @patch('radio_host_functions.AudioSegment.from_file')
    @patch('radio_host_functions.io.BytesIO')
    def test_elevenlabs_model_used(self, mock_bytesio, mock_audio_segment):
        mock_segment = Mock()
        mock_audio_segment.return_value = mock_segment
        
        mock_eleven_client = Mock()
        mock_stream = [b"audio"]
        mock_eleven_client.text_to_speech.convert.return_value = mock_stream
        
        script = "A: Test\n"
        rhf.generate_audio_segments(script, mock_eleven_client)
        
        call_args = mock_eleven_client.text_to_speech.convert.call_args
        assert call_args.kwargs["model_id"] == CONFIG["ELEVENLABS_MODEL"]
    
    @patch('radio_host_functions.AudioSegment.from_file')
    @patch('radio_host_functions.io.BytesIO')
    def test_api_error_handling(self, mock_bytesio, mock_audio_segment):
        mock_eleven_client = Mock()
        mock_eleven_client.text_to_speech.convert.side_effect = Exception("API Error")
        
        script = "A: Test\n"
        
        with pytest.raises(Exception):
            rhf.generate_audio_segments(script, mock_eleven_client)


class TestCombineAndExportAudio:
    
    @patch('radio_host_functions.os.path.getsize')
    def test_successful_export(self, mock_getsize):
        mock_segment1 = Mock()
        mock_segment1.__len__ = Mock(return_value=1000)
        mock_segment2 = Mock()
        mock_segment2.__len__ = Mock(return_value=2000)
        
        mock_final = Mock()
        mock_final.__len__ = Mock(return_value=3000)
        mock_final.export = Mock()
        
        def add_segments(seg1, seg2):
            return mock_final
        
        mock_segment1.__add__ = add_segments
        mock_segment2.__add__ = add_segments
        mock_getsize.return_value = 1024 * 1024
        
        segments = [mock_segment1, mock_segment2]
        rhf.combine_and_export_audio(segments, "test.mp3", files_download=None)
        
        mock_final.export.assert_called_once_with("test.mp3", format="mp3", bitrate="192k")
    
    def test_empty_segments_error(self):
        with pytest.raises(ValueError, match="No audio segments to combine"):
            rhf.combine_and_export_audio([], "test.mp3", files_download=None)
    
    @patch('radio_host_functions.os.path.getsize')
    def test_duration_calculation(self, mock_getsize):
        mock_segment = Mock()
        mock_segment.__len__ = Mock(return_value=5000)
        mock_segment.export = Mock()
        mock_getsize.return_value = 1024 * 1024
        
        segments = [mock_segment]
        rhf.combine_and_export_audio(segments, "test.mp3", files_download=None)
        
        mock_segment.export.assert_called_once_with("test.mp3", format="mp3", bitrate="192k")
    
    @patch('radio_host_functions.os.path.getsize')
    def test_file_size_logging(self, mock_getsize):
        mock_segment = Mock()
        mock_segment.__len__ = Mock(return_value=1000)
        mock_segment.export = Mock()
        mock_getsize.return_value = 2 * 1024 * 1024
        
        segments = [mock_segment]
        rhf.combine_and_export_audio(segments, "test.mp3", files_download=None)
        
        mock_getsize.assert_called_once_with("test.mp3")
    
    @patch('radio_host_functions.os.path.getsize')
    def test_files_download_called(self, mock_getsize):
        mock_segment = Mock()
        mock_segment.__len__ = Mock(return_value=1000)
        mock_segment.export = Mock()
        mock_getsize.return_value = 1024 * 1024
        mock_download = Mock()
        
        segments = [mock_segment]
        rhf.combine_and_export_audio(segments, "test.mp3", files_download=mock_download)
        
        mock_download.assert_called_once_with("test.mp3")
    
    @patch('radio_host_functions.os.path.getsize')
    def test_export_error_handling(self, mock_getsize):
        mock_segment = Mock()
        mock_segment.__len__ = Mock(return_value=1000)
        mock_segment.export.side_effect = Exception("Export failed")
        
        segments = [mock_segment]
        
        with pytest.raises(Exception):
            rhf.combine_and_export_audio(segments, "test.mp3", files_download=None)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
