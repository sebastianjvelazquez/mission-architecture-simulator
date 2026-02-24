"""
app/services/simulator.py

Re-exports the simulator classes from app.core.simulator for convenience.
This allows importing as `from app.services.simulator import MissionArchitectureSimulator`
which matches the expected import path in tests and documentation.
"""

from app.core.simulator import (
    SUPPORTED_SCENARIOS,
    MissionArchitectureSimulator,
    SimulatorError,
)

__all__ = [
    "MissionArchitectureSimulator",
    "SimulatorError",
    "SUPPORTED_SCENARIOS",
]
