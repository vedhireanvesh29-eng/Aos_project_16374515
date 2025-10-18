"""First-Come, First-Served (FCFS) scheduling implementation."""
from __future__ import annotations

from typing import List

from fs25_models import Process, ScheduleSlice
from .common import append_slice, pid_numeric, sort_by_arrival_then_pid


def run_fcfs(processes: List[Process]) -> List[ScheduleSlice]:
    """Simulate FCFS scheduling and return the executed timeline."""
    timeline: List[ScheduleSlice] = []
    time = 0

    for process in sort_by_arrival_then_pid(processes):
        if process.burst <= 0:
            continue  # zero-length jobs never occupy the CPU

        time = max(time, process.arrival)
        start = time
        end = start + process.burst
        append_slice(timeline, process.pid, start, end)
        time = end

    return timeline

