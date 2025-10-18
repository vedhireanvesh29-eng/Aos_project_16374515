"""Shortest Job First (non-preemptive) scheduling implementation."""
from __future__ import annotations

from typing import List, Optional

from fs25_models import Process, ScheduleSlice
from .common import append_slice, pid_numeric, sort_by_arrival_then_pid


def run_sjf(processes: List[Process]) -> List[ScheduleSlice]:
    """Simulate non-preemptive SJF scheduling."""
    pending = sort_by_arrival_then_pid(processes)
    timeline: List[ScheduleSlice] = []
    ready: List[Process] = []
    index = 0
    time = pending[0].arrival if pending else 0

    def pop_next_job(current_time: int) -> Optional[Process]:
        if not ready:
            return None
        ready.sort(key=lambda p: (p.burst, p.arrival, pid_numeric(p.pid)))
        return ready.pop(0)

    while index < len(pending) or ready:
        while index < len(pending) and pending[index].arrival <= time:
            ready.append(pending[index])
            index += 1

        job = pop_next_job(time)
        if job is None:
            # CPU idle until next arrival
            time = pending[index].arrival
            continue

        if job.burst <= 0:
            continue

        start = max(time, job.arrival)
        end = start + job.burst
        append_slice(timeline, job.pid, start, end)
        time = end

    return timeline

