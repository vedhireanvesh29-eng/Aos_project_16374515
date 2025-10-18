"""Shared helpers for scheduling algorithms."""
from __future__ import annotations

from typing import Iterable, List

from fs25_models import Process, ScheduleSlice


def pid_numeric(pid: str) -> int:
    """Extract the numeric suffix of a PID (e.g., P10 -> 10) for tie-breaking."""
    digits = "".join(ch for ch in pid if ch.isdigit())
    return int(digits) if digits else 0


def sort_by_arrival_then_pid(processes: Iterable[Process]) -> List[Process]:
    """Return processes ordered by arrival time, breaking ties by PID suffix."""
    return sorted(processes, key=lambda p: (p.arrival, pid_numeric(p.pid)))


def append_slice(timeline: List[ScheduleSlice], pid: str, start: int, end: int) -> None:
    """Append a schedule slice, merging contiguous slices for the same PID."""
    if start == end:
        return
    if timeline and timeline[-1].pid == pid and timeline[-1].end == start:
        timeline[-1] = ScheduleSlice(pid=pid, start=timeline[-1].start, end=end)
    else:
        timeline.append(ScheduleSlice(pid=pid, start=start, end=end))
