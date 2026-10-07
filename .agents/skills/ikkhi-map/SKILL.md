---
name: ikkhi-map
description: Governance protocol, schema standards, and autonomous maintenance procedures for continuously maintaining and structuring the Ikkhi Master Project Map and component connection matrices.
---

# Ikkhi Master Project Map Governance & Maintenance Protocol

This skill dictates the mandatory formatting standards, structural schema, and autonomous update triggers for the **Ikkhi Master Project Map** ([`PROJECT_MAP.md`](file:///e:/rouf/software-project/Ikkhi/PROJECT_MAP.md)).

---

## 1. Core Purpose & Philosophy

The Master Project Map is the single source of truth for the codebase topology of **Ikkhi**. Every AI agent, incoming developer, and model reading the repository relies on it to:
1. Understand the exact job and primary duty of every directory, subdirectory, and file.
2. Trace bidirectional connectivity: **Inbound Connections** (who calls/imports this file) and **Outbound Connections** (what this file calls/imports).
3. Identify operational boundaries, resource consumption budgets, and execution tiers (Tier 0 Deterministic vs Tier 1 Cloud Fallback).

---

## 2. Standardized Naming Schemes

To maintain flawless architectural clarity, all maps, files, and modules must adhere to the standardized naming conventions:

| Entity Type | Naming Convention Scheme | Example |
| :--- | :--- | :--- |
| **Master Map** | `PROJECT_MAP.md` (Root directory) | [`PROJECT_MAP.md`](file:///e:/rouf/software-project/Ikkhi/PROJECT_MAP.md) |
| **Subsystem Dossiers** | `docs/maps/<subsystem>_MAP.md` (Optional deep dives) | `docs/maps/AUDIO_MAP.md` |
| **Python Packages / Dirs** | Snake_case, semantic noun phrases | `src/ikkhi/automation/creative/` |
| **Python Source Files** | Snake_case, descriptive duty | `src/ikkhi/audio/wakeword.py` |
| **Test Files** | `test_<module_name>.py` mirroring source path | `tests/unit/test_experience.py` |
| **Diagnostic Scripts** | `test_live_<feature>.py` or `build_<target>.py` | `scripts/test_live_gui.py` |
| **Documentation Files** | UPPERCASE_SNAKE_CASE with `.md` extension | `BOUNDARIES.md`, `PROGRESS.md` |

---

## 3. Mandatory File & Folder Dossier Schema

Every file and directory documented in [`PROJECT_MAP.md`](file:///e:/rouf/software-project/Ikkhi/PROJECT_MAP.md) MUST adhere to this strict schema template:

### 3.1 Directory / Subfolder Template
```markdown
### 📁 `<relative/directory/path>`
- **Domain / Job:** Brief 1-2 sentence description of the subsystem's architectural responsibility.
- **Parent / Inbound Callers:** Subsystems that orchestrate or invoke modules in this directory.
- **Submodules & Children:** List of files and nested subdirectories contained within.
```

### 3.2 Individual File Template
```markdown
#### 📄 [`<filename>`](file:///<absolute_or_relative_path>)
- **Job / Core Duty:** Explicit statement of the file's primary job in the application.
- **Inbound Connections (Who calls this?):** List of modules, scripts, or tests that import or invoke this file.
- **Outbound Connections (What does this call?):** List of internal and external libraries this file imports or writes to.
- **Key Interfaces / Exports:** Primary classes, functions, signals, or constants provided.
- **Resource & Token Profile:** Execution tier (Tier 0 vs Tier 1), hardware footprint (CPU/GPU/VRAM), token cost ($0.00 vs API).
```

---

## 4. Autonomous Update Trigger Cadence

Any AI agent working on Ikkhi MUST execute the Project Map synchronization routine under the following triggers:

1. **File Creation:** When a new file is created, immediately:
   - Insert it into the Directory Tree in Section 1.
   - Author a complete Dossier Card in Section 2 with Inbound/Outbound connections.
   - Update the Mermaid Dependency Graph in Section 3 if data flow is affected.
2. **File Refactoring / Renaming:** When an existing file changes responsibilities or imports:
   - Update its Inbound/Outbound connection entries.
   - Update the Inbound entries of any files it now imports.
3. **File Retirement / Deletion:** When a file is removed:
   - Remove its card from Section 2.
   - Remove references from other files' Inbound/Outbound lists.
   - Update the Directory Tree.
4. **Batch Update Cadence:** After every completed milestone or batch of $\ge 3$ file modifications, the agent must inspect [`PROJECT_MAP.md`](file:///e:/rouf/software-project/Ikkhi/PROJECT_MAP.md) and verify that all connections reflect the active state on disk.

---

## 5. Verification Checklist for `ikkhi-map`

Before closing any session or task that touches project files, verify:
- [ ] Are all new or modified files cataloged in [`PROJECT_MAP.md`](file:///e:/rouf/software-project/Ikkhi/PROJECT_MAP.md)?
- [ ] Are Inbound and Outbound connections verified against actual `import` statements?
- [ ] Does the Mermaid architecture diagram accurately reflect active modules (no legacy filenames)?
- [ ] Are all file links formatted with valid markdown links?
- [ ] Is [`CONTEXT.md`](file:///e:/rouf/software-project/Ikkhi/CONTEXT.md) synchronized with any high-level structural shifts?
