"""
Unit test suite for Experiential Memory, Mistake Learning, and Bayesian confidence scoring.
"""

import shutil
from pathlib import Path
import pytest
from ikkhi.automation.experience import ExperientialMemory, ActionOutcome, StrategyStats


@pytest.fixture
def temp_memory_dir(tmp_path: Path):
    """Provide isolated temporary directory for experiential memory storage."""
    mem_dir = tmp_path / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)
    yield mem_dir
    shutil.rmtree(tmp_path, ignore_errors=True)


def test_strategy_stats_bayesian_confidence():
    """Verify Laplace smoothing in confidence calculation."""
    stats = StrategyStats(app_id="blender", intent="cut", strategy="hotkey", payload="k")
    # Initial: (0 + 1) / (0 + 0 + 2) = 0.50
    assert stats.update_confidence() == 0.50

    stats.success_count = 3
    # (3 + 1) / (3 + 0 + 2) = 4 / 5 = 0.80
    assert stats.update_confidence() == 0.80

    stats.failure_count = 2
    # (3 + 1) / (3 + 2 + 2) = 4 / 7 = 0.571
    assert stats.update_confidence() == 0.571


def test_experiential_memory_lifecycle(temp_memory_dir: Path):
    """Verify outcome recording, confidence updates, and persistence."""
    mem = ExperientialMemory(memory_dir=temp_memory_dir)

    # 1. Record successes for Blender knife tool
    mem.record_success(app_id="blender", intent="cut", strategy="hotkey", payload="k", duration_ms=12.5)
    mem.record_success(app_id="blender", intent="cut", strategy="hotkey", payload="k", duration_ms=10.0)

    best = mem.get_best_strategy("blender", "cut")
    assert best is not None
    assert best.strategy == "hotkey"
    assert best.payload == "k"
    assert best.success_count == 2
    assert best.confidence_score > 0.70

    # 2. Record inferior strategy that failed
    mem.record_failure(app_id="blender", intent="cut", strategy="hotkey", payload="shift+k", error_reason="No split")
    inferior = mem.get_best_strategy("blender", "cut")
    # Top strategy should still be "k"
    assert inferior.payload == "k"


def test_mistake_learning_and_user_correction(temp_memory_dir: Path):
    """Verify that human corrections strongly penalize the preceding flawed strategy."""
    mem = ExperientialMemory(memory_dir=temp_memory_dir)

    # Agent performs an action in Premiere
    mem.record_success(app_id="premiere", intent="split", strategy="hotkey", payload="ctrl+b")
    strat_before = mem.get_best_strategy("premiere", "split")
    assert strat_before is not None
    conf_before = strat_before.confidence_score

    # User says "no, that's wrong"
    assert mem.is_user_correction("no")
    assert mem.is_user_correction("undo")
    assert mem.is_user_correction("wrong")

    corrected = mem.handle_user_correction("undo that")
    assert corrected is not None
    assert corrected.user_corrected is True

    # Flawed strategy should now fall below production confidence threshold (0.5)
    assert mem.get_best_strategy("premiere", "split", min_confidence=0.5) is None

    # Inspect the penalised stats
    strat_after = mem.get_best_strategy("premiere", "split", min_confidence=0.0)
    assert strat_after is not None
    assert strat_after.confidence_score < conf_before
    assert strat_after.failure_count >= 2


def test_app_stats_summary(temp_memory_dir: Path):
    """Verify aggregated application accuracy metric computation."""
    mem = ExperientialMemory(memory_dir=temp_memory_dir)
    mem.record_success("resolve", "cut", "hotkey", "ctrl+b")
    mem.record_success("resolve", "ripple", "hotkey", "shift+backspace")
    mem.record_failure("resolve", "export", "hotkey", "ctrl+e", "Shortcut unmapped")

    summary = mem.get_app_stats_summary("resolve")
    assert summary["app_id"] == "resolve"
    assert summary["distinct_intents"] == 3
    assert summary["total_successes"] == 2
    assert summary["total_failures"] == 1
    assert summary["empirical_accuracy"] == round(2 / 3, 3)
