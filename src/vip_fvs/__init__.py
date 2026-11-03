"""Public API for the local functional vertical slice.

The package deliberately exposes one small synchronous entry point.  Runtime
components are registered by the coordinator integration lane; keeping that
boundary explicit prevents the command surface from growing accidental
provider- or scheduler-specific behaviour.
"""

from .coordinator import CoordinatorNotConfigured, run_vertical_slice

__all__ = ["CoordinatorNotConfigured", "run_vertical_slice"]
__version__ = "0.1.0"
