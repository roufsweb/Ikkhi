"""
Unit test suite for CreativeAppCatalog across video editors, 3D suites, DAWs, and IDEs.
"""

from ikkhi.automation.creative.catalog import CreativeAppCatalog, CreativeAppDefinition


def test_creative_app_identification():
    """Verify process name and window title detection for major creative applications."""
    catalog = CreativeAppCatalog()

    # DaVinci Resolve
    app_davinci = catalog.identify_app("Resolve.exe", "DaVinci Resolve - Project 1")
    assert app_davinci is not None
    assert app_davinci.app_id == "resolve"

    # Adobe Premiere Pro
    app_prem = catalog.identify_app("Adobe Premiere Pro.exe")
    assert app_prem is not None
    assert app_prem.app_id == "premiere"

    # Blender 3D
    app_blender = catalog.identify_app("blender.exe", "Blender [E:\\scene.blend]")
    assert app_blender is not None
    assert app_blender.app_id == "blender"

    # Photoshop
    app_ps = catalog.identify_app("Photoshop.exe")
    assert app_ps is not None
    assert app_ps.app_id == "photoshop"

    # Ableton Live
    app_live = catalog.identify_app("Live.exe", "Ableton Live 11 Suite")
    assert app_live is not None
    assert app_live.app_id == "ableton"

    # VS Code
    app_code = catalog.identify_app("Code.exe", "Ikkhi - Visual Studio Code")
    assert app_code is not None
    assert app_code.app_id == "code"


def test_cross_app_semantic_intent_resolution():
    """Verify that generic creative commands resolve to app-specific native shortcuts."""
    catalog = CreativeAppCatalog()

    # Split clip across different suites
    assert catalog.resolve_shortcut("resolve", "split_clip") == "ctrl+b"
    assert catalog.resolve_shortcut("premiere", "split_clip") == "ctrl+k"
    assert catalog.resolve_shortcut("blender", "split_clip") == "k"
    assert catalog.resolve_shortcut("ableton", "split_clip") == "ctrl+e"

    # Render / Export
    assert catalog.resolve_shortcut("premiere", "render_export") == "ctrl+m"
    assert catalog.resolve_shortcut("blender", "render_image") == "f12"
    assert catalog.resolve_shortcut("afterfx", "render_export") == "ctrl+m"
    assert catalog.resolve_shortcut("code", "toggle_terminal") == "ctrl+`"


def test_custom_app_registration():
    """Verify dynamic extension of catalog with novel user applications."""
    catalog = CreativeAppCatalog()
    custom_app = CreativeAppDefinition(
        app_id="reaper",
        display_name="Reaper DAW",
        category="audio_daw",
        process_names=["reaper.exe"],
        window_title_keywords=["reaper v"],
        default_shortcuts={"split_clip": "s", "save": "ctrl+s"}
    )
    catalog.register_app(custom_app)

    matched = catalog.identify_app("reaper.exe")
    assert matched is not None
    assert matched.app_id == "reaper"
    assert catalog.resolve_shortcut("reaper", "split_clip") == "s"
