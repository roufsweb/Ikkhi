"""
Automated validation of the Ultra-Compact Context Snapshot (CONTEXT.md).
Ensures documentation remains high-density, concise, and strictly bounded in length.
"""

from pathlib import Path


def test_compact_context_snapshot_exists_and_bounded():
    """Verify that CONTEXT.md exists, stays concise (<120 lines), and covers core essentials."""
    project_root = Path(__file__).resolve().parent.parent.parent
    context_file = project_root / "CONTEXT.md"

    assert context_file.is_file(), "CONTEXT.md must exist in repository root."

    lines = context_file.read_text(encoding="utf-8").splitlines()
    line_count = len(lines)

    # Hard boundary to guarantee it never bloats beyond ~800 tokens
    assert line_count <= 120, f"CONTEXT.md exceeds line budget ({line_count} > 120 lines)."
    assert line_count >= 30, f"CONTEXT.md is suspiciously sparse ({line_count} lines)."

    content = context_file.read_text(encoding="utf-8")
    assert "Ikkhi" in content
    assert "dist/Ikkhi.exe" in content
    assert "pytest" in content
    assert "-m ikkhi" in content
    assert "PROJECT_MAP.md" in content


def test_compact_context_plan_exists():
    """Verify that the implementation plan for the compact context engine exists."""
    project_root = Path(__file__).resolve().parent.parent.parent
    plan_file = project_root / "docs" / "COMPACT_CONTEXT_PLAN.md"
    assert plan_file.is_file()
