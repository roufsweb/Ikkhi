---
name: ikkhi-files
description: File system governance, directory taxonomy, artifact archiving, clutter prevention, and naming conventions for the Ikkhi codebase.
---

# Ikkhi File Management & Workspace Organizing Protocol

This skill dictates the file system standards, directory boundaries, naming rules, and clutter-prevention procedures across the **Ikkhi** repository.

---

## 1. Canonical Directory Taxonomy

Every file in the repository must reside strictly in its designated architectural partition:

| Directory | Mandatory Contents | Prohibited Contents |
| :--- | :--- | :--- |
| **`src/ikkhi/`** | Production PEP 517/621 application source code (`core/`, `audio/`, `vision/`, `automation/`, `ai/`, `ui/`). | Scratch scripts, test files, temporary data, hardcoded secrets. |
| **`tests/`** | Automated pytest suites (`unit/`, `integration/`) mirroring `src/ikkhi/` structure. | Production runtime logic, large binary dumps (>1MB). |
| **`scripts/`** | Maintenance tools, build pipelines, hardware diagnostics, and launchers. | Core business logic that should be packaged inside `src/`. |
| **`docs/`** | Architectural plans, comparative analyses, research deconstructions. | Ephemeral code snippets or scratch notes. |
| **`.agents/skills/`** | Reusable agent workflow skills containing valid `SKILL.md` files. | Unrelated configuration files or temporary logs. |
| **`storage/`** | Persistent runtime state (`profiles/` JSON maps, session logs). **100% Git-ignored.** | Source code, tracked configuration files. |
| **`dist/` & `build/`** | Compiled binary distributions (`Ikkhi.exe`) and PyInstaller build artifacts. | Source files, untracked development notes. |

---

## 2. Naming Conventions & Casing Standards

All files and directories must adhere to standardized casing schemes:

1. **Python Modules & Packages:** Lowercase snake_case (`whisper_stt.py`, `screen_indexer.py`).
2. **Class Names:** UpperCamelCase (`AudioCaptureEngine`, `UniversalUIInspector`).
3. **Root Markdown Documents:** UPPERCASE_SNAKE_CASE with `.md` (`PROJECT_MAP.md`, `BOUNDARIES.md`, `CONTEXT.md`).
4. **Agent Skill Directories:** Kebab-case prefixed with `ikkhi-` (`ikkhi-ui`, `ikkhi-automation`, `ikkhi-product`, `ikkhi-files`).
5. **Configuration Files:** Lowercase with extension (`config.yaml`, `pyproject.toml`, `.env.example`).

---

## 3. Path Resolution Invariants (Dev vs. Frozen Binary)

Code in `src/ikkhi/` must **never** assume a fixed relative path from the current working directory or `__file__`. Always route asset and storage lookups through [`src/ikkhi/core/paths.py`](file:///e:/rouf/software-project/Ikkhi/src/ikkhi/core/paths.py):

```python
# CORRECT: Works in both .venv and PyInstaller Ikkhi.exe
from ikkhi.core.paths import get_storage_dir, get_profiles_dir, resolve_config_path

storage_path = get_storage_dir()
config_file = resolve_config_path("config.yaml")

# INCORRECT: Breaks when running standalone executable (Ikkhi.exe)
path = Path("storage/profiles")
```

---

## 4. Anti-Clutter & Workspace Hygiene Routine

Before ending any task or committing changes:

1. **Purge Ephemeral Artifacts:** Remove any `.tmp`, `temp_*`, `.dump`, or debug audio WAV/MP3 files created during ad-hoc testing.
2. **Storage Cleanliness:** Verify that files written to `storage/` are strictly ignored by `.gitignore`.
3. **No Root Pollution:** Never leave scratch scripts or experiment files in the root folder. Move temporary scripts into `scripts/` or delete them.
4. **Master Map Verification:** Run the [`ikkhi-map`](file:///e:/rouf/software-project/Ikkhi/.agents/skills/ikkhi-map/SKILL.md) update routine to ensure all new or modified files are cataloged with their inbound and outbound connections.
