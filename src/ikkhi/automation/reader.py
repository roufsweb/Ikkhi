"""
Screen Text-to-Speech & Accessibility Reading Subsystem.
Extracts selected or active window text natively and articulates it through
the local zero-token speech engine without external API calls.
"""

import time
import logging
from typing import Optional
import pyautogui
import pyperclip

from ikkhi.automation.inspector import UniversalUIInspector
from ikkhi.audio.tts import LocalSpeechEngine

logger = logging.getLogger(__name__)


class ScreenTextReader:
    """
    Extracts text from active user selections, documents, or UI elements
    and pipes it directly into the local voice synthesis engine.
    """

    def __init__(self, speech_engine: Optional[LocalSpeechEngine] = None) -> None:
        self.speech_engine = speech_engine
        self.inspector = UniversalUIInspector()

    def get_selected_text(self, timeout_seconds: float = 0.3) -> str:
        """
        Extract text currently highlighted/selected by the user across any application
        via non-destructive clipboard interaction.
        """
        # Save previous clipboard state
        try:
            previous_clip = pyperclip.paste()
        except Exception:
            previous_clip = ""

        # Clear clipboard temporarily to detect fresh copy
        try:
            pyperclip.copy("")
        except Exception:
            pass

        # Simulate Copy command (Ctrl+C)
        pyautogui.hotkey("ctrl", "c")
        time.sleep(timeout_seconds)

        try:
            copied_text = pyperclip.paste().strip()
        except Exception:
            copied_text = ""

        # If nothing was selected, restore previous clipboard
        if not copied_text and previous_clip:
            try:
                pyperclip.copy(previous_clip)
            except Exception:
                pass

        return copied_text

    def get_active_window_text(self, max_length: int = 1200) -> str:
        """
        Extract visible text contents from the active window's UI Automation tree.
        Traverses edit controls, document bodies, and text labels.
        """
        context = self.inspector.get_foreground_context()
        if not context:
            return ""

        controls = self.inspector.inspect_controls(context.hwnd, max_depth=3)
        text_fragments = []

        for ctrl in controls.values():
            if ctrl.control_type in ("Text", "Edit", "Document", "DataItem", "ListItem"):
                name = ctrl.name.strip()
                if name and len(name) > 1 and name not in text_fragments:
                    text_fragments.append(name)

        combined = " ".join(text_fragments)
        if len(combined) > max_length:
            combined = combined[:max_length] + "..."
        return combined

    def read_aloud(self, prefer_selected: bool = True) -> str:
        """
        Acquire text from screen (prioritizing selection, then active window)
        and articulate it via the local voice synthesis engine.
        Returns the spoken text.
        """
        text_to_read = ""
        if prefer_selected:
            text_to_read = self.get_selected_text()

        if not text_to_read:
            text_to_read = self.get_active_window_text()

        if not text_to_read:
            msg = "No selectable or readable text was detected on the active window."
            if self.speech_engine:
                self.speech_engine.speak(msg)
            return msg

        logger.info("Articulating screen text aloud (%d characters)...", len(text_to_read))
        if self.speech_engine:
            self.speech_engine.speak(text_to_read)

        return text_to_read


# Global singleton instance and action registration
_global_reader: Optional[ScreenTextReader] = None

def get_screen_reader(speech_engine: Optional[LocalSpeechEngine] = None) -> ScreenTextReader:
    global _global_reader
    if _global_reader is None:
        _global_reader = ScreenTextReader(speech_engine)
    elif speech_engine and not _global_reader.speech_engine:
        _global_reader.speech_engine = speech_engine
    return _global_reader


from ikkhi.automation.registry import registry

@registry.register("screen_read_text", "Read aloud the selected text or active window text using local TTS")
def screen_read_text_action() -> str:
    reader = get_screen_reader()
    return reader.read_aloud()
