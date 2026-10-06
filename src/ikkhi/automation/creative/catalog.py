"""
Universal Creative Application Catalog and Semantic Action Normalizer.
Maps cross-app creative intentions (video editing, 3D CG, digital audio, graphic design)
to application-specific hotkey macros and control pathways.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CreativeAppDefinition(BaseModel):
    """Specification of a creative application with its process signatures and hotkey map."""
    app_id: str
    display_name: str
    category: str  # "video_editing", "vfx_3d", "audio_daw", "graphic_design", "code_ide"
    process_names: List[str]
    window_title_keywords: List[str]
    default_shortcuts: Dict[str, str] = Field(default_factory=dict)


class CreativeAppCatalog:
    """
    Catalog of major professional creative software suites with semantic intent resolution.
    Permits Ikkhi to operate as a universal creative assistant rather than a single-app tool.
    """

    def __init__(self) -> None:
        self._apps: Dict[str, CreativeAppDefinition] = {}
        self._register_default_creative_suites()

    def register_app(self, definition: CreativeAppDefinition) -> None:
        """Register or extend a creative application definition."""
        self._apps[definition.app_id.lower()] = definition

    def _register_default_creative_suites(self) -> None:
        """Populate initial canonical shortcut tables for major creative tools."""
        # 1. DaVinci Resolve
        self.register_app(CreativeAppDefinition(
            app_id="resolve",
            display_name="DaVinci Resolve",
            category="video_editing",
            process_names=["resolve.exe", "resolve"],
            window_title_keywords=["davinci resolve"],
            default_shortcuts={
                "split_clip": "ctrl+b",
                "cut": "ctrl+b",
                "blade": "ctrl+b",
                "ripple_delete": "shift+backspace",
                "add_marker": "m",
                "toggle_snapping": "n",
                "fit_to_screen": "shift+z",
                "save": "ctrl+s",
                "undo": "ctrl+z",
                "redo": "ctrl+shift+z",
            }
        ))

        # 2. Adobe Premiere Pro
        self.register_app(CreativeAppDefinition(
            app_id="premiere",
            display_name="Adobe Premiere Pro",
            category="video_editing",
            process_names=["premiere.exe", "adobe premiere pro.exe"],
            window_title_keywords=["premiere pro", "adobe premiere"],
            default_shortcuts={
                "split_clip": "ctrl+k",
                "cut": "ctrl+k",
                "blade": "c",
                "ripple_delete": "shift+delete",
                "add_marker": "m",
                "toggle_snapping": "s",
                "render_export": "ctrl+m",
                "save": "ctrl+s",
                "undo": "ctrl+z",
                "redo": "ctrl+shift+z",
            }
        ))

        # 3. Blender 3D
        self.register_app(CreativeAppDefinition(
            app_id="blender",
            display_name="Blender",
            category="vfx_3d",
            process_names=["blender.exe", "blender"],
            window_title_keywords=["blender"],
            default_shortcuts={
                "split_clip": "k",
                "cut": "k",
                "render_image": "f12",
                "render_animation": "ctrl+f12",
                "toggle_snapping": "shift+tab",
                "search_menu": "f3",
                "fit_to_screen": "home",
                "delete": "x",
                "save": "ctrl+s",
                "undo": "ctrl+z",
                "redo": "ctrl+shift+z",
            }
        ))

        # 4. Adobe After Effects
        self.register_app(CreativeAppDefinition(
            app_id="afterfx",
            display_name="Adobe After Effects",
            category="vfx_3d",
            process_names=["afterfx.exe", "adobe after effects.exe"],
            window_title_keywords=["after effects"],
            default_shortcuts={
                "split_layer": "ctrl+shift+d",
                "cut": "ctrl+shift+d",
                "render_export": "ctrl+m",
                "add_marker": "*",
                "fit_to_screen": "shift+/",
                "save": "ctrl+s",
                "undo": "ctrl+z",
                "redo": "ctrl+shift+z",
            }
        ))

        # 5. Adobe Photoshop
        self.register_app(CreativeAppDefinition(
            app_id="photoshop",
            display_name="Adobe Photoshop",
            category="graphic_design",
            process_names=["photoshop.exe", "adobe photoshop.exe"],
            window_title_keywords=["photoshop"],
            default_shortcuts={
                "new_layer": "ctrl+shift+n",
                "duplicate_layer": "ctrl+j",
                "fit_to_screen": "ctrl+0",
                "actual_pixels": "ctrl+1",
                "deselect": "ctrl+d",
                "save": "ctrl+s",
                "export": "ctrl+shift+alt+w",
                "undo": "ctrl+z",
                "redo": "ctrl+shift+z",
            }
        ))

        # 6. Figma Desktop
        self.register_app(CreativeAppDefinition(
            app_id="figma",
            display_name="Figma",
            category="graphic_design",
            process_names=["figma.exe"],
            window_title_keywords=["figma"],
            default_shortcuts={
                "zoom_to_fit": "shift+1",
                "zoom_to_selection": "shift+2",
                "create_component": "ctrl+alt+k",
                "detach_instance": "ctrl+alt+b",
                "group_selection": "ctrl+g",
                "ungroup": "ctrl+shift+g",
                "undo": "ctrl+z",
                "redo": "ctrl+y",
            }
        ))

        # 7. Ableton Live (DAW)
        self.register_app(CreativeAppDefinition(
            app_id="ableton",
            display_name="Ableton Live",
            category="audio_daw",
            process_names=["ableton live", "live.exe"],
            window_title_keywords=["ableton live"],
            default_shortcuts={
                "split_clip": "ctrl+e",
                "cut": "ctrl+e",
                "consolidate": "ctrl+j",
                "quantize": "ctrl+u",
                "export_audio": "ctrl+shift+r",
                "save": "ctrl+s",
                "undo": "ctrl+z",
                "redo": "ctrl+y",
            }
        ))

        # 8. Visual Studio Code
        self.register_app(CreativeAppDefinition(
            app_id="code",
            display_name="Visual Studio Code",
            category="code_ide",
            process_names=["code.exe"],
            window_title_keywords=["visual studio code"],
            default_shortcuts={
                "command_palette": "ctrl+shift+p",
                "quick_open": "ctrl+p",
                "toggle_terminal": "ctrl+`",
                "format_document": "shift+alt+f",
                "split_editor": "ctrl+\\",
                "save": "ctrl+s",
                "undo": "ctrl+z",
                "redo": "ctrl+y",
            }
        ))

    def identify_app(self, process_name: str, window_title: str = "") -> Optional[CreativeAppDefinition]:
        """Match foreground window context to a registered creative application."""
        proc_lower = process_name.lower()
        title_lower = window_title.lower()

        for app in self._apps.values():
            if any(p in proc_lower for p in app.process_names):
                return app
            if any(k in title_lower for k in app.window_title_keywords):
                return app

        return None

    def resolve_shortcut(self, app_id: str, semantic_intent: str) -> Optional[str]:
        """Lookup canonical shortcut for a normalized creative intent in an application."""
        app = self._apps.get(app_id.lower())
        if not app:
            return None

        clean_intent = semantic_intent.strip().lower()
        return app.default_shortcuts.get(clean_intent)
