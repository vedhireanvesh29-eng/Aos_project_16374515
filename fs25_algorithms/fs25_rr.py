"""Round Robin scheduling implementation."""
from __future__ import annotations

from collections import deque
from typing import Deque, Dict, List, Tuple

from fs25_models import Process, ScheduleSlice
from .common import append_slice, pid_numeric, sort_by_arrival_then_pid


def run_rr(processes: List[Process], quantum: int = 4) -> List[ScheduleSlice]:
    """Simulate Round Robin scheduling with a configurable quantum."""
    quantum = max(1, int(quantum))
    ordered = sort_by_arrival_then_pid(processes)
    timeline: List[ScheduleSlice] = []
    queue: Deque[Tuple[Process, int]] = deque()
    index = 0
    time = ordered[0].arrival if ordered else 0

    while index < len(ordered) or queue:
        while index < len(ordered) and ordered[index].arrival <= time:
            proc = ordered[index]
            if proc.burst > 0:
                queue.append((proc, proc.burst))
            index += 1

        if not queue:
            time = max(time, ordered[index].arrival)
            continue

        proc, remaining = queue.popleft()
        run_duration = min(quantum, remaining)
        start = time
        end = start + run_duration
        append_slice(timeline, proc.pid, start, end)
        time = end
        remaining -= run_duration

        arrivals_to_enqueue: List[Tuple[int, Process, int]] = []
        while index < len(ordered) and ordered[index].arrival <= time:
            incoming = ordered[index]
            if incoming.burst > 0:
                arrivals_to_enqueue.append((incoming.arrival, incoming, pid_numeric(incoming.pid)))
            index += 1
        for _, incoming_proc, _ in sorted(arrivals_to_enqueue, key=lambda item: (item[0], item[2])):
            queue.append((incoming_proc, incoming_proc.burst))

        if remaining > 0:
            queue.append((proc, remaining))

    return timeline

