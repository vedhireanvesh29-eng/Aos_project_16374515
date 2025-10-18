"""Algorithm registry for the FS-25 CPU scheduling simulator."""
from __future__ import annotations

from typing import Callable, Dict, List

from fs25_models import Process, ScheduleSlice

from .fs25_fcfs import run_fcfs
from .fs25_priority import run_priority
from .fs25_rr import run_rr
from .fs25_sjf import run_sjf
from .fs25_srtf import run_srtf

AlgorithmFunc = Callable[[List[Process]], List[ScheduleSlice]]


def get_algorithm_registry(quantum: int) -> Dict[str, AlgorithmFunc]:
    """Return a mapping of algorithm names to callable simulators."""

    def rr_runner(procs: List[Process]) -> List[ScheduleSlice]:
        return run_rr(procs, quantum=quantum)

    return {
        "FCFS": run_fcfs,
        "SJF": run_sjf,
        "SRTF": run_srtf,
        "PRIORITY": run_priority,
        "RR": rr_runner,
    }


__all__ = [
    "get_algorithm_registry",
]

