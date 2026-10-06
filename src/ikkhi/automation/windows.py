import ctypes
import pyautogui
from ikkhi.automation.registry import registry

# Allow macro hotkeys to dispatch even if cursor rests at physical corner
pyautogui.FAILSAFE = False

# Windows Virtual-Key Codes for Media
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3


def _send_vk(vk_code: int) -> None:
    """Send a hardware-level virtual key event."""
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0) # KEYEVENTF_KEYUP


@registry.register("media_play_pause", "Toggle media playback state (Play/Pause)")
def media_play_pause() -> bool:
    _send_vk(VK_MEDIA_PLAY_PAUSE)
    return True


@registry.register("media_stop", "Stop active media playback")
def media_stop() -> bool:
    _send_vk(VK_MEDIA_STOP)
    return True


@registry.register("audio_toggle_mute", "Toggle system audio mute")
def audio_toggle_mute() -> bool:
    _send_vk(VK_VOLUME_MUTE)
    return True


@registry.register("audio_volume_up", "Increase system master volume")
def audio_volume_up(step: int = 5) -> bool:
    for _ in range(max(1, step // 2)):
        _send_vk(VK_VOLUME_UP)
    return True


@registry.register("audio_volume_down", "Decrease system master volume")
def audio_volume_down(step: int = 5) -> bool:
    for _ in range(max(1, step // 2)):
        _send_vk(VK_VOLUME_DOWN)
    return True


@registry.register("window_minimize", "Minimize the currently active foreground window")
def window_minimize() -> bool:
    pyautogui.hotkey("win", "down")
    return True


@registry.register("window_maximize", "Maximize the currently active foreground window")
def window_maximize() -> bool:
    pyautogui.hotkey("win", "up")
    return True


@registry.register("app_save", "Trigger standard file/project save (Ctrl+S)")
def app_save() -> bool:
    pyautogui.hotkey("ctrl", "s")
    return True
