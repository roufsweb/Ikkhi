"""
Experiential Memory & Autonomous Mistake Learning Subsystem.
Maintains a compact, resource-conscious feedback ledger tracking action reliability,
mistake penalties, and user corrections across all applications.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field

from ikkhi.core.paths import get_storage_dir


class ActionOutcome(BaseModel):
    """Encapsulates the discrete runtime execution result of an automation strategy."""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    app_id: str
    intent: str
    strategy: str  # "hotkey", "uia_control", "visual_coordinate", "macro"
    payload: str   # e.g., "ctrl+b", "Timeline->Split", "(450, 320)"
    success: bool
    duration_ms: float = 0.0
    error_reason: Optional[str] = None
    user_corrected: bool = False


class StrategyStats(BaseModel):
    """Aggregated empirical reliability statistics for a specific app intent strategy."""
    app_id: str
    intent: str
    strategy: str
    payload: str
    success_count: int = 0
    failure_count: int = 0
    confidence_score: float = 0.5
    last_used: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_error: Optional[str] = None

    def update_confidence(self) -> float:
        """
        Compute Laplace-smoothed Bayesian confidence estimate:
        P(Success) = (Successes + 1) / (Successes + Failures + 2)
        """
        total = self.success_count + self.failure_count
        self.confidence_score = round((self.success_count + 1.0) / (total + 2.0), 3)
        return self.confidence_score


class ExperientialMemory:
    """
    Ultra-lightweight experiential ledger and mistake tracking coordinator.
    Persists bounded JSONL logs under storage/memory/ and maintains an in-memory
    cache for O(1) strategy ranking without CPU or disk bottlenecks.
    """

    CORRECTION_TRIGGERS = {
        "no", "wrong", "undo", "undo that", "cancel", "not that",
        "mistake", "stop", "go back", "incorrect"
    }

    def __init__(self, memory_dir: Optional[Path | str] = None) -> None:
        if memory_dir:
            self.memory_dir = Path(memory_dir).resolve()
        else:
            self.memory_dir = get_storage_dir() / "memory"

        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.memory_dir / "experience.jsonl"

        # In-memory index: (app_id, clean_intent) -> List[StrategyStats]
        self._strategy_cache: Dict[Tuple[str, str], List[StrategyStats]] = {}
        self._last_outcome: Optional[ActionOutcome] = None

        self._load_existing_stats()

    def _load_existing_stats(self) -> None:
        """Hydrate in-memory strategy cache from historical log on startup."""
        if not self.log_file.is_file():
            return

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line_str = line.strip()
                    if not line_str:
                        continue
                    try:
                        record = json.loads(line_str)
                        outcome = ActionOutcome(**record)
                        self._apply_outcome_to_cache(outcome, persist_log=False)
                    except Exception:
                        continue
        except Exception:
            pass

    def _apply_outcome_to_cache(self, outcome: ActionOutcome, persist_log: bool = True) -> None:
        """Update in-memory stats cache and optionally append to JSONL log."""
        app_clean = outcome.app_id.lower()
        intent_clean = outcome.intent.lower().strip()
        key = (app_clean, intent_clean)

        if key not in self._strategy_cache:
            self._strategy_cache[key] = []

        strategies = self._strategy_cache[key]
        matching = next(
            (s for s in strategies if s.strategy == outcome.strategy and s.payload == outcome.payload),
            None
        )

        if not matching:
            matching = StrategyStats(
                app_id=app_clean,
                intent=intent_clean,
                strategy=outcome.strategy,
                payload=outcome.payload
            )
            strategies.append(matching)

        if outcome.user_corrected:
            matching.failure_count += 2  # Double penalty for explicit human correction
            matching.last_error = "User corrected previous action"
        elif outcome.success:
            matching.success_count += 1
        else:
            matching.failure_count += 1
            matching.last_error = outcome.error_reason

        matching.last_used = outcome.timestamp
        matching.update_confidence()

        self._last_outcome = outcome

        if persist_log:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(outcome.model_dump()) + "\n")
            except Exception:
                pass

    def record_success(
        self,
        app_id: str,
        intent: str,
        strategy: str,
        payload: str,
        duration_ms: float = 0.0
    ) -> ActionOutcome:
        """Record a successful action execution, boosting strategy confidence."""
        outcome = ActionOutcome(
            app_id=app_id,
            intent=intent,
            strategy=strategy,
            payload=payload,
            success=True,
            duration_ms=duration_ms
        )
        self._apply_outcome_to_cache(outcome, persist_log=True)
        return outcome

    def record_failure(
        self,
        app_id: str,
        intent: str,
        strategy: str,
        payload: str,
        error_reason: str,
        duration_ms: float = 0.0
    ) -> ActionOutcome:
        """Record an execution failure, penalizing strategy confidence."""
        outcome = ActionOutcome(
            app_id=app_id,
            intent=intent,
            strategy=strategy,
            payload=payload,
            success=False,
            error_reason=error_reason,
            duration_ms=duration_ms
        )
        self._apply_outcome_to_cache(outcome, persist_log=True)
        return outcome

    def is_user_correction(self, phrase: str) -> bool:
        """Determine whether the user utterance signifies an explicit error correction."""
        clean = phrase.strip().lower()
        return clean in self.CORRECTION_TRIGGERS or any(clean.startswith(trig) for trig in self.CORRECTION_TRIGGERS)

    def handle_user_correction(self, phrase: str) -> Optional[ActionOutcome]:
        """
        If the user uttered a correction, penalize the preceding action's strategy
        and return the updated negative outcome.
        """
        if not self.is_user_correction(phrase) or not self._last_outcome:
            return None

        # Re-apply negative penalty to last action
        corrected_outcome = ActionOutcome(
            app_id=self._last_outcome.app_id,
            intent=self._last_outcome.intent,
            strategy=self._last_outcome.strategy,
            payload=self._last_outcome.payload,
            success=False,
            error_reason=f"Human user negative feedback: '{phrase}'",
            user_corrected=True
        )
        self._apply_outcome_to_cache(corrected_outcome, persist_log=True)
        return corrected_outcome

    def get_best_strategy(
        self,
        app_id: str,
        intent: str,
        min_confidence: float = 0.5
    ) -> Optional[StrategyStats]:
        """
        Select the empirical optimal strategy with highest proven confidence for an app intent.
        Returns None if no strategies meet min_confidence or if untested.
        """
        app_clean = app_id.lower()
        intent_clean = intent.lower().strip()
        key = (app_clean, intent_clean)

        strategies = self._strategy_cache.get(key, [])
        if not strategies:
            return None

        # Sort descending by Bayesian confidence score, break ties by success count
        sorted_strats = sorted(strategies, key=lambda s: (s.confidence_score, s.success_count), reverse=True)
        top = sorted_strats[0]
        return top if top.confidence_score >= min_confidence else None

    def get_app_stats_summary(self, app_id: str) -> Dict[str, Any]:
        """Produce an aggregated efficiency summary for an individual application."""
        app_clean = app_id.lower()
        matching_keys = [k for k in self._strategy_cache if k[0] == app_clean]
        
        total_strategies = 0
        total_successes = 0
        total_failures = 0

        for k in matching_keys:
            for s in self._strategy_cache[k]:
                total_strategies += 1
                total_successes += s.success_count
                total_failures += s.failure_count

        total_actions = total_successes + total_failures
        accuracy = round(total_successes / total_actions, 3) if total_actions > 0 else 1.0

        return {
            "app_id": app_clean,
            "distinct_intents": len(matching_keys),
            "total_strategies": total_strategies,
            "total_successes": total_successes,
            "total_failures": total_failures,
            "empirical_accuracy": accuracy
        }
