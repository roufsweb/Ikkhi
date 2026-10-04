"""
Deterministic Action Registry for Ikkhi.
Enforces type safety and eliminates arbitrary code execution or AI hallucinations.
"""

from typing import Callable, Dict, Any, Optional
from pydantic import BaseModel
import inspect
from ikkhi.core.exceptions import ActionExecutionError


class ActionMetadata(BaseModel):
    name: str
    description: str
    parameter_model: Optional[type[BaseModel]] = None


class ActionRegistry:
    """Central repository storing verified executable Python automation functions."""

    def __init__(self) -> None:
        self._actions: Dict[str, Callable[..., Any]] = {}
        self._metadata: Dict[str, ActionMetadata] = {}

    def register(
        self,
        name: str,
        description: str,
        param_model: Optional[type[BaseModel]] = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a validated action."""
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self._actions[name] = func
            self._metadata[name] = ActionMetadata(
                name=name,
                description=description,
                parameter_model=param_model
            )
            return func
        return decorator

    def execute(self, name: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a registered action with validated arguments."""
        if name not in self._actions:
            raise ActionExecutionError(f"Action '{name}' is not registered in the system.")

        func = self._actions[name]
        meta = self._metadata[name]
        params = params or {}

        try:
            if meta.parameter_model:
                validated_params = meta.parameter_model(**params)
                return func(validated_params)
            
            # Check if function takes kwargs or zero parameters
            sig = inspect.signature(func)
            if len(sig.parameters) == 0:
                return func()
            return func(**params)
        except Exception as exc:
            raise ActionExecutionError(f"Failed to execute action '{name}': {exc}") from exc

    def list_actions(self) -> Dict[str, ActionMetadata]:
        return self._metadata.copy()


# Global action registry singleton
registry = ActionRegistry()
