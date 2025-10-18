"""Core data models for the FS-25 CPU scheduling simulator."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True, order=True)
class Process:
    """Represents a single process in the scheduling workload."""

    pid: str
    arrival: int
    burst: int
    priority: int


@dataclass(frozen=True)
class ScheduleSlice:
    """One uninterrupted execution segment for a process."""

    pid: str
    start: int
    end: int


@dataclass
class AlgorithmResult:
    """Aggregated result produced by running a scheduling algorithm."""

    algorithm: str
    timeline: List[ScheduleSlice]
    per_process: Dict[str, Dict[str, float]]
    averages: Dict[str, float]
    context_switches: int
    cpu_utilization: float
    throughput: float
    makespan: int

