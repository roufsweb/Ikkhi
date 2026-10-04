"""
Universal Application Automation Engine.
Executes actions across any application through adaptive profile learning and UI Automation.
"""

import logging
from typing import Optional, Tuple
import pyautogui
from ikkhi.core.config import UniversalAutomationSettings
from ikkhi.automation.inspector import UniversalUIInspector, WindowContext
from ikkhi.automation.profiles import ProfileManager, AppProfile, IndexedControl, LearnedInteraction
from ikkhi.vision.pointer import CursorPointer

logger = logging.getLogger(__name__)


class UniversalAutomationEngine:
    """Orchestrates dynamic, app-agnostic automation with persistent user-learning."""

    def __init__(self, settings: UniversalAutomationSettings, pointer: CursorPointer) -> None:
        self.settings = settings
        self.pointer = pointer
        self.inspector = UniversalUIInspector()
        self.profile_mgr = ProfileManager(settings.profiles_directory)

    def execute_for_active_app(self, user_command: str) -> Tuple[bool, str]:
        """
        Attempts to resolve and execute user_command on the current foreground application.
        Returns: (success_status, feedback_message)
        """
        context = self.inspector.get_foreground_context()
        if not context:
            return False, "No active foreground window detected."

        app_id = context.process_name.lower().replace(".exe", "")
        profile = self.profile_mgr.get_or_create_profile(app_id, context.process_name)
        cmd_clean = user_command.strip().lower()

        # Step 1: Check learned interactions memory (Fastest Tier)
        if cmd_clean in profile.learned_interactions:
            learned = profile.learned_interactions[cmd_clean]
            logger.info("Executing learned interaction for [%s]: %s", app_id, cmd_clean)
            if learned.hotkey:
                pyautogui.hotkey(*learned.hotkey.split("+"))
                self.profile_mgr.record_interaction(app_id, cmd_clean, hotkey=learned.hotkey)
                return True, f"Triggered learned hotkey '{learned.hotkey}' for {app_id}."
            if learned.relative_coords:
                norm_x, norm_y = learned.relative_coords
                left, top, right, bottom = context.bounding_box
                target_x = int(left + norm_x * (right - left))
                target_y = int(top + norm_y * (bottom - top))
                self.pointer.point_to(target_x, target_y)
                pyautogui.click()
                self.profile_mgr.record_interaction(app_id, cmd_clean, relative_coords=learned.relative_coords)
                return True, f"Clicked learned target at ({target_x}, {target_y}) in {app_id}."

        # Step 2: Check cached controls in this application's profile
        for ctrl_name, ctrl in profile.controls.items():
            if ctrl_name in cmd_clean or cmd_clean in ctrl_name:
                logger.info("Found cached control '%s' in profile for [%s]", ctrl.name, app_id)
                return self._invoke_control(ctrl, context, app_id, cmd_clean)

        # Step 3: Live accessibility inspection of the current window
        live_controls = self.inspector.inspect_controls(context.hwnd, self.settings.uia_search_depth)
        # Update app profile with newly discovered controls
        for k, v in live_controls.items():
            if k not in profile.controls:
                profile.controls[k] = v
        self.profile_mgr.save_profile(profile)

        for ctrl_name, ctrl in live_controls.items():
            if ctrl_name in cmd_clean or cmd_clean in ctrl_name:
                logger.info("Discovered live control '%s' in [%s]", ctrl.name, app_id)
                return self._invoke_control(ctrl, context, app_id, cmd_clean)

        return False, f"Could not locate matching control for '{user_command}' in {app_id}."

    def _invoke_control(
        self,
        ctrl: IndexedControl,
        context: WindowContext,
        app_id: str,
        trigger_phrase: str
    ) -> Tuple[bool, str]:
        """Interacts with an identified control and commits the learning to the app profile."""
        if ctrl.bounding_box:
            left, top, right, bottom = ctrl.bounding_box
            cx = (left + right) // 2
            cy = (top + bottom) // 2
            self.pointer.point_to(cx, cy)
            pyautogui.click()
            
            # Commit learning into persistent profile
            if ctrl.relative_center:
                self.profile_mgr.record_interaction(
                    app_id=app_id,
                    trigger_phrase=trigger_phrase,
                    target_name=ctrl.name,
                    relative_coords=ctrl.relative_center
                )
            return True, f"Activated '{ctrl.name}' in {app_id}."
        return False, f"Control '{ctrl.name}' found but missing valid screen bounds."
