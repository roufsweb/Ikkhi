---
name: ikkhi-automation
description: Instructions for extending Ikkhi automation actions, registering new voice commands, and utilizing the hybrid Windows UI / visual automation stack.
---

# Ikkhi Automation Extension Skill

Use this skill when adding new voice commands, macros, or application integrations to the Ikkhi project.

## 1. Action Function Signature
Every action must be an isolated, deterministic Python function registered in the action registry:

```python
from pydantic import BaseModel, Field

class CutClipArgs(BaseModel):
    ripple_delete: bool = Field(default=False, description="Whether to ripple delete the cut portion")

def cut_timeline_clip(args: CutClipArgs) -> bool:
    """Action implementation with error handling."""
    # 1. Check if DaVinci Resolve is active
    # 2. Execute keyboard shortcut or DaVinci API
    ...
```

## 2. Choosing the Right Automation Tier
When automating a feature:
1. **Tier 1 (Application API):** Does the app have a Python or CLI API? (e.g. DaVinci Resolve has `DaVinciResolveScript`). Always prefer this.
2. **Tier 2 (Windows UIA via `pywinauto`):** Can the button or menu be located via accessibility tree? Use this over pixel clicks.
3. **Tier 3 (Shortcuts):** Can standard keyboard shortcuts (`Ctrl+B`, `Ctrl+S`) achieve the result? This is instant and 100% reliable.
4. **Tier 4 (Visual / Template Matching):** Only use `pyautogui` + `cv2.matchTemplate` when the target is a custom-rendered canvas or icon with no UIA handle. Always verify screen resolution and match confidence >= 0.85.
