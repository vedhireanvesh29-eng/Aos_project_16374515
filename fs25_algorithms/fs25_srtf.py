"""Shortest Remaining Time First (preemptive SJF) implementation."""
from __future__ import annotations

import heapq
from typing import Dict, List, Optional, Tuple

from fs25_models import Process, ScheduleSlice
from .common import append_slice, pid_numeric, sort_by_arrival_then_pid


def run_srtf(processes: List[Process]) -> List[ScheduleSlice]:
    """Simulate preemptive SRTF scheduling."""
    ordered = sort_by_arrival_then_pid(processes)
    timeline: List[ScheduleSlice] = []
    ready: List[Tuple[int, int, int, int, Dict[str, object]]] = []
    index = 0
    time = ordered[0].arrival if ordered else 0
    sequence = 0

    while index < len(ordered) or ready:
        while index < len(ordered) and ordered[index].arrival <= time:
            proc = ordered[index]
            if proc.burst > 0:
                state = {"process": proc, "remaining": proc.burst}
                entry = (proc.burst, proc.arrival, pid_numeric(proc.pid), sequence, state)
                heapq.heappush(ready, entry)
                sequence += 1
            index += 1

        if not ready:
            next_arrival = ordered[index].arrival
            time = max(time, next_arrival)
            continue

        remaining, arrival, pid_order, _, state = heapq.heappop(ready)
        proc: Process = state["process"]  # type: ignore[assignment]
        rem: int = state["remaining"]  # type: ignore[assignment]
        next_arrival: Optional[int] = ordered[index].arrival if index < len(ordered) else None

        run_duration = rem
        if next_arrival is not None and time + rem > next_arrival:
            run_duration = next_arrival - time

        # Protect against pathological input where next arrival equals current time.
        if run_duration <= 0:
            time = next_arrival if next_arrival is not None else time
            state["remaining"] = rem
            entry = (state["remaining"], arrival, pid_order, sequence, state)
            heapq.heappush(ready, entry)
            sequence += 1
            continue

        start = time
        end = start + run_duration
        append_slice(timeline, proc.pid, start, end)
        time = end
        rem -= run_duration

        if rem > 0:
            state["remaining"] = rem
            entry = (rem, arrival, pid_order, sequence, state)
            heapq.heappush(ready, entry)
            sequence += 1

    return timeline

