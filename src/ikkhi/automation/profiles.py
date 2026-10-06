"""
Adaptive Application Profile Management Subsystem.
Persists per-app knowledge, UI control maps, and user-learned interactions.
"""

import re
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Optional, List, Tuple
from pydantic import BaseModel, Field
from ikkhi.core.exceptions import IkkhiError


class SecurityValidationError(IkkhiError):
    """Raised when an untrusted input fails strict security validation."""
    pass


class IndexedControl(BaseModel):
    name: str
    control_type: str
    automation_id: Optional[str] = None
    bounding_box: Optional[Tuple[int, int, int, int]] = None # (left, top, right, bottom)
    relative_center: Optional[Tuple[float, float]] = None    # (norm_x, norm_y) within window
    keyboard_shortcut: Optional[str] = None
    frequency: int = 1


class LearnedInteraction(BaseModel):
    trigger_phrase: str
    target_control_name: Optional[str] = None
    action_type: str = "click" # "click", "hotkey", "double_click"
    hotkey: Optional[str] = None
    relative_coords: Optional[Tuple[float, float]] = None
    last_invoked: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    success_count: int = 1


class AppProfile(BaseModel):
    app_identifier: str
    process_names: List[str] = Field(default_factory=list)
    window_title_patterns: List[str] = Field(default_factory=list)
    controls: Dict[str, IndexedControl] = Field(default_factory=dict)
    learned_interactions: Dict[str, LearnedInteraction] = Field(default_factory=dict)
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProfileManager:
    """Manages persistent JSON profiles for individual applications used by the user."""

    def __init__(self, profiles_dir: str | Path = "storage/profiles") -> None:
        self.profiles_dir = Path(profiles_dir).resolve()
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, AppProfile] = {}

    def _sanitize_path(self, app_identifier: str) -> Tuple[str, Path]:
        """Sanitizes application identifiers to prevent directory traversal attacks."""
        clean_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", app_identifier.lower().replace(".exe", ""))
        clean_name = clean_name.strip("_") or "unknown_app"
        file_path = (self.profiles_dir / f"{clean_name}.json").resolve()
        
        # Enforce path containment within profiles_dir
        if not file_path.is_relative_to(self.profiles_dir):
            raise SecurityValidationError(f"Path traversal attempt detected: '{app_identifier}'")
        return clean_name, file_path

    def get_or_create_profile(self, app_identifier: str, process_name: Optional[str] = None) -> AppProfile:
        """Retrieve existing profile from memory/disk or create a new one."""
        app_id_clean, file_path = self._sanitize_path(app_identifier)
        if app_id_clean in self._cache:
            return self._cache[app_id_clean]

        if file_path.is_file():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                profile = AppProfile(**data)
                self._cache[app_id_clean] = profile
                return profile
            except Exception:
                pass

        # Create fresh profile for this application
        profile = AppProfile(
            app_identifier=app_id_clean,
            process_names=[process_name] if process_name else []
        )
        self._cache[app_id_clean] = profile
        self.save_profile(profile)
        return profile

    def save_profile(self, profile: AppProfile) -> None:
        """Persist profile state to disk safely."""
        _, file_path = self._sanitize_path(profile.app_identifier)
        profile.last_updated = datetime.now(timezone.utc).isoformat()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(profile.model_dump(), f, indent=2)


    def record_interaction(
        self,
        app_identifier: str,
        trigger_phrase: str,
        target_name: Optional[str] = None,
        relative_coords: Optional[Tuple[float, float]] = None,
        hotkey: Optional[str] = None
    ) -> None:
        """Record or update a learned interaction for an individual user app."""
        profile = self.get_or_create_profile(app_identifier)
        clean_phrase = trigger_phrase.strip().lower()

        if clean_phrase in profile.learned_interactions:
            existing = profile.learned_interactions[clean_phrase]
            existing.success_count += 1
            existing.last_invoked = datetime.now(timezone.utc).isoformat()
            if relative_coords:
                existing.relative_coords = relative_coords
            if hotkey:
                existing.hotkey = hotkey
        else:
            profile.learned_interactions[clean_phrase] = LearnedInteraction(
                trigger_phrase=clean_phrase,
                target_control_name=target_name,
                relative_coords=relative_coords,
                hotkey=hotkey,
                action_type="hotkey" if hotkey else "click"
            )

        self.save_profile(profile)
