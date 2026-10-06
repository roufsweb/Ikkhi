"""
Unit tests for the Screen Text-to-Speech reading subsystem and its routing.
"""

from unittest.mock import MagicMock, patch
from ikkhi.automation.reader import ScreenTextReader, get_screen_reader
from ikkhi.automation.registry import registry
from ikkhi.core.router import IntentRouter, RouteTarget


def test_router_screen_reading_fast_path():
    router = IntentRouter()
    
    queries = [
        "read text",
        "read selected",
        "read screen",
        "read this",
        "read out loud",
        "speak text",
    ]
    for q in queries:
        route = router.route(q)
        assert route.target == RouteTarget.LOCAL_ACTION, f"Failed for {q}"
        assert route.action_name == "screen_read_text", f"Failed for {q}"
        assert route.is_cloud_request is False


def test_reader_get_selected_text_mocked():
    mock_speech = MagicMock()
    reader = ScreenTextReader(speech_engine=mock_speech)

    with patch("pyperclip.paste", side_effect=["", "Hello world from selection"]), \
         patch("pyperclip.copy"), \
         patch("pyautogui.hotkey"):
        text = reader.get_selected_text(timeout_seconds=0.01)
        assert text == "Hello world from selection"


def test_reader_read_aloud_with_speech_engine():
    mock_speech = MagicMock()
    reader = ScreenTextReader(speech_engine=mock_speech)

    with patch.object(reader, "get_selected_text", return_value="Selected sample line"):
        res = reader.read_aloud(prefer_selected=True)
        assert res == "Selected sample line"
        mock_speech.speak.assert_called_once_with("Selected sample line")


def test_reader_fallback_to_active_window():
    mock_speech = MagicMock()
    reader = ScreenTextReader(speech_engine=mock_speech)

    with patch.object(reader, "get_selected_text", return_value=""), \
         patch.object(reader, "get_active_window_text", return_value="Active window title and controls"):
        res = reader.read_aloud(prefer_selected=True)
        assert res == "Active window title and controls"
        mock_speech.speak.assert_called_once_with("Active window title and controls")


def test_reader_registry_action_invocation():
    mock_speech = MagicMock()
    reader = get_screen_reader(speech_engine=mock_speech)

    with patch.object(reader, "read_aloud", return_value="Spoken successfully"):
        result = registry.execute("screen_read_text")
        assert result == "Spoken successfully"
