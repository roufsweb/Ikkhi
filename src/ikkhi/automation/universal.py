"""
Universal Creative Application Automation & Experiential Learning Engine.
Executes actions across any application through adaptive profile learning,
creative app catalogs, UI Automation, and empirical mistake feedback loops.
"""

import time
import logging
from typing import Optional, Tuple
import pyautogui

from ikkhi.core.config import UniversalAutomationSettings
from ikkhi.automation.inspector import UniversalUIInspector, WindowContext
from ikkhi.automation.profiles import ProfileManager, AppProfile, IndexedControl, LearnedInteraction
from ikkhi.automation.experience import ExperientialMemory, ActionOutcome
from ikkhi.automation.creative.catalog import CreativeAppCatalog
from ikkhi.vision.pointer import CursorPointer

logger = logging.getLogger(__name__)


class UniversalAutomationEngine:
    """
    Orchestrates application-agnostic automation across all creative software suites.
    Utilizes Bayesian experiential memory to learn from runtime mistakes and user feedback.
    """

    def __init__(self, settings: UniversalAutomationSettings, pointer: CursorPointer) -> None:
        self.settings = settings
        self.pointer = pointer
        self.inspector = UniversalUIInspector()
        self.profile_mgr = ProfileManager(settings.profiles_directory)
        self.experience = ExperientialMemory()
        self.catalog = CreativeAppCatalog()

    def execute_for_active_app(self, user_command: str) -> Tuple[bool, str]:
        """
        Attempts to resolve and execute user_command on the current foreground application.
        Learns from successes and mistakes to refine future execution confidence.
        Returns: (success_status, feedback_message)
        """
        cmd_clean = user_command.strip().lower()

        # Step 0: Autonomous Mistake Feedback & Correction Detection
        if self.experience.is_user_correction(cmd_clean):
            corrected_outcome = self.experience.handle_user_correction(cmd_clean)
            if corrected_outcome:
                logger.warning(
                    "User corrected previous action on [%s]: %s (Penalized strategy '%s')",
                    corrected_outcome.app_id, corrected_outcome.intent, corrected_outcome.strategy
                )
                # Dispatch universal undo shortcut if applicable
                pyautogui.hotkey("ctrl", "z")
                return True, (
                    f"Acknowledged correction for '{corrected_outcome.intent}' in {corrected_outcome.app_id}. "
                    f"Reverted action and penalized flawed strategy."
                )

        context = self.inspector.get_foreground_context()
        if not context:
            return False, "No active foreground window detected."

        # Detect active creative application identity
        creative_app = self.catalog.identify_app(context.process_name, context.title)
        app_id = creative_app.app_id if creative_app else context.process_name.lower().replace(".exe", "")

        profile = self.profile_mgr.get_or_create_profile(app_id, context.process_name)
        start_time = time.time()

        # Strategy Tier 1: Check Experiential Memory for proven, high-confidence strategy (>= 0.70)
        best_strat = self.experience.get_best_strategy(app_id, cmd_clean, min_confidence=0.70)
        if best_strat:
            logger.info(
                "Executing proven experiential strategy for [%s:%s] (Confidence: %.2f)",
                app_id, cmd_clean, best_strat.confidence_score
            )
            success, msg = self._dispatch_strategy(best_strat.strategy, best_strat.payload, context)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            if success:
                self.experience.record_success(app_id, cmd_clean, best_strat.strategy, best_strat.payload, duration_ms)
                return True, f"[Experiential Memory] {msg}"
            else:
                self.experience.record_failure(app_id, cmd_clean, best_strat.strategy, best_strat.payload, msg, duration_ms)
                logger.warning("Experiential strategy failed, falling through to alternative tiers...")

        # Strategy Tier 2: Check Creative App Catalog (Standardized Cross-App Shortcuts)
        shortcut = self.catalog.resolve_shortcut(app_id, cmd_clean)
        if shortcut:
            logger.info("Executing creative catalog shortcut for [%s]: %s -> %s", app_id, cmd_clean, shortcut)
            try:
                pyautogui.hotkey(*shortcut.split("+"))
                duration_ms = round((time.time() - start_time) * 1000, 2)
                self.experience.record_success(app_id, cmd_clean, "hotkey", shortcut, duration_ms)
                self.profile_mgr.record_interaction(app_id, cmd_clean, hotkey=shortcut)
                return True, f"Triggered {creative_app.display_name if creative_app else app_id} shortcut '{shortcut}'."
            except Exception as exc:
                duration_ms = round((time.time() - start_time) * 1000, 2)
                self.experience.record_failure(app_id, cmd_clean, "hotkey", shortcut, str(exc), duration_ms)

        # Strategy Tier 3: Check Learned App Profiles (User-Trained Interactions)
        if cmd_clean in profile.learned_interactions:
            learned = profile.learned_interactions[cmd_clean]
            logger.info("Executing learned interaction for [%s]: %s", app_id, cmd_clean)
            if learned.hotkey:
                try:
                    pyautogui.hotkey(*learned.hotkey.split("+"))
                    duration_ms = round((time.time() - start_time) * 1000, 2)
                    self.experience.record_success(app_id, cmd_clean, "hotkey", learned.hotkey, duration_ms)
                    self.profile_mgr.record_interaction(app_id, cmd_clean, hotkey=learned.hotkey)
                    return True, f"Triggered learned hotkey '{learned.hotkey}' for {app_id}."
                except Exception as exc:
                    duration_ms = round((time.time() - start_time) * 1000, 2)
                    self.experience.record_failure(app_id, cmd_clean, "hotkey", learned.hotkey, str(exc), duration_ms)

            if learned.relative_coords:
                norm_x, norm_y = learned.relative_coords
                left, top, right, bottom = context.bounding_box
                target_x = int(left + norm_x * (right - left))
                target_y = int(top + norm_y * (bottom - top))
                try:
                    self.pointer.point_to(target_x, target_y)
                    pyautogui.click()
                    duration_ms = round((time.time() - start_time) * 1000, 2)
                    coord_str = f"({norm_x:.3f}, {norm_y:.3f})"
                    self.experience.record_success(app_id, cmd_clean, "visual_coordinate", coord_str, duration_ms)
                    self.profile_mgr.record_interaction(app_id, cmd_clean, relative_coords=learned.relative_coords)
                    return True, f"Clicked learned target at ({target_x}, {target_y}) in {app_id}."
                except Exception as exc:
                    duration_ms = round((time.time() - start_time) * 1000, 2)
                    self.experience.record_failure(app_id, cmd_clean, "visual_coordinate", str(learned.relative_coords), str(exc), duration_ms)

        # Strategy Tier 4: Check Cached UI Controls in Profile
        for ctrl_name, ctrl in profile.controls.items():
            if ctrl_name in cmd_clean or cmd_clean in ctrl_name:
                logger.info("Found cached control '%s' in profile for [%s]", ctrl.name, app_id)
                success, msg = self._invoke_control(ctrl, context, app_id, cmd_clean)
                duration_ms = round((time.time() - start_time) * 1000, 2)
                if success:
                    self.experience.record_success(app_id, cmd_clean, "uia_control", ctrl.name, duration_ms)
                else:
                    self.experience.record_failure(app_id, cmd_clean, "uia_control", ctrl.name, msg, duration_ms)
                return success, msg

        # Strategy Tier 5: Live Accessibility Inspection (Windows UIA Tree)
        live_controls = self.inspector.inspect_controls(context.hwnd, self.settings.uia_search_depth)
        for k, v in live_controls.items():
            if k not in profile.controls:
                profile.controls[k] = v
        self.profile_mgr.save_profile(profile)

        for ctrl_name, ctrl in live_controls.items():
            if ctrl_name in cmd_clean or cmd_clean in ctrl_name:
                logger.info("Discovered live control '%s' in [%s]", ctrl.name, app_id)
                success, msg = self._invoke_control(ctrl, context, app_id, cmd_clean)
                duration_ms = round((time.time() - start_time) * 1000, 2)
                if success:
                    self.experience.record_success(app_id, cmd_clean, "uia_control", ctrl.name, duration_ms)
                else:
                    self.experience.record_failure(app_id, cmd_clean, "uia_control", ctrl.name, msg, duration_ms)
                return success, msg

        return False, f"Could not locate matching control for '{user_command}' in {app_id}."

    def _dispatch_strategy(self, strategy: str, payload: str, context: WindowContext) -> Tuple[bool, str]:
        """Dispatch a known strategy directly."""
        try:
            if strategy == "hotkey":
                pyautogui.hotkey(*payload.split("+"))
                return True, f"Dispatched hotkey '{payload}'"
            elif strategy in ("visual_coordinate", "coordinate"):
                # Parse normalized coordinates e.g. "(0.450, 0.320)"
                parts = payload.strip("()[]").split(",")
                norm_x, norm_y = float(parts[0].strip()), float(parts[1].strip())
                left, top, right, bottom = context.bounding_box
                target_x = int(left + norm_x * (right - left))
                target_y = int(top + norm_y * (bottom - top))
                self.pointer.point_to(target_x, target_y)
                pyautogui.click()
                return True, f"Clicked coordinate ({target_x}, {target_y})"
            return False, f"Unknown strategy type: {strategy}"
        except Exception as exc:
            return False, f"Strategy execution error: {exc}"

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

            if ctrl.relative_center:
                self.profile_mgr.record_interaction(
                    app_id=app_id,
                    trigger_phrase=trigger_phrase,
                    target_name=ctrl.name,
                    relative_coords=ctrl.relative_center
                )
            return True, f"Activated '{ctrl.name}' in {app_id}."
        return False, f"Control '{ctrl.name}' found but missing valid screen bounds."
