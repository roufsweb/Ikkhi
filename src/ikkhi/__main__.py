"""
CLI entry point for the Ikkhi desktop assistant.
"""

import sys
import logging
from ikkhi.core.config import AppConfig
from ikkhi.core.orchestrator import IkkhiOrchestrator


def main() -> None:
    """Initialize system configuration and launch orchestrator daemon."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    logging.info("Starting Ikkhi Desktop Assistant...")

    config = AppConfig.load_from_yaml("config.yaml")
    orchestrator = IkkhiOrchestrator(config)

    # If run in test mode via argument:
    if len(sys.argv) > 1:
        test_command = " ".join(sys.argv[1:])
        logging.info("Executing test command: '%s'", test_command)
        result = orchestrator.process_transcript(test_command)
        print(f"\nResult: {result}")
        return

    print("Ikkhi Desktop Assistant initialized successfully.")
    print("Run with a command argument to simulate input, e.g.:")
    print("  python -m ikkhi cut clip")
    print("  python -m ikkhi where is the export button")


if __name__ == "__main__":
    main()
