import pyautogui
from ikkhi.automation.registry import registry

# Allow macro hotkeys to dispatch even if cursor rests at physical corner
pyautogui.FAILSAFE = False


@registry.register("davinci_blade_cut", "Split the clip at the current playhead position in DaVinci Resolve (Ctrl+B)")
def davinci_blade_cut() -> bool:
    pyautogui.hotkey("ctrl", "b")
    return True


@registry.register("davinci_ripple_delete", "Ripple delete selected clip or gap (Shift+Backspace)")
def davinci_ripple_delete() -> bool:
    pyautogui.hotkey("shift", "backspace")
    return True


@registry.register("davinci_add_marker", "Add an edit marker at the current playhead position (M)")
def davinci_add_marker() -> bool:
    pyautogui.press("m")
    return True
