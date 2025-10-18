"""Metric calculations for the FS-25 CPU scheduling simulator."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

from fs25_models import Process, ScheduleSlice


def compute_algorithm_metrics(
    processes: List[Process], timeline: List[ScheduleSlice]
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, float], int, float, float, int]:
    """Compute per-process metrics and aggregates for a completed simulation.

    Returns:
        per_process: metrics keyed by PID.
        averages: mean waiting/turnaround/response times.
        context_switches: total number of context switches.
        cpu_utilization: percentage of busy time across the makespan.
        throughput: completed processes per unit time.
        makespan: total elapsed simulated time.
    """

    processes_by_pid: Dict[str, Process] = {proc.pid: proc for proc in processes}
    runtime_info: Dict[str, Dict[str, float]] = defaultdict(
        lambda: {"first_start": None, "completion": 0.0, "runtime": 0.0}
    )

    sorted_timeline = sorted(timeline, key=lambda sl: (sl.start, sl.end))
    busy_time = 0.0
    context_switches = 0
    previous_pid = None

    for slice_ in sorted_timeline:
        busy_time += slice_.end - slice_.start
        info = runtime_info[slice_.pid]
        if info["first_start"] is None:
            info["first_start"] = float(slice_.start)
        info["completion"] = float(slice_.end)
        info["runtime"] += slice_.end - slice_.start

        if previous_pid is not None and previous_pid != slice_.pid:
            context_switches += 1
        previous_pid = slice_.pid

    if processes:
        earliest_arrival = min(proc.arrival for proc in processes)
    else:
        earliest_arrival = 0

    last_completion = max((slice_.end for slice_ in sorted_timeline), default=earliest_arrival)
    makespan = max(0, int(last_completion - earliest_arrival))
    makespan_duration = max(last_completion - earliest_arrival, 0.0)

    per_process: Dict[str, Dict[str, float]] = {}
    waiting_times: List[float] = []
    turnaround_times: List[float] = []
    response_times: List[float] = []

    for proc in processes:
        info = runtime_info.get(proc.pid)
        if info and info["runtime"] > 0:
            completion = info["completion"]
            first_start = info["first_start"]
            runtime = info["runtime"]
        else:
            completion = float(proc.arrival)
            first_start = float(proc.arrival)
            runtime = 0.0

        turnaround = completion - proc.arrival
        waiting = turnaround - proc.burst
        response = first_start - proc.arrival if first_start is not None else 0.0

        waiting = max(waiting, 0.0)
        turnaround = max(turnaround, 0.0)
        response = max(response, 0.0)

        per_process[proc.pid] = {
            "arrival": float(proc.arrival),
            "burst": float(proc.burst),
            "priority": float(proc.priority),
            "waiting": waiting,
            "turnaround": turnaround,
            "response": response,
            "completion": completion,
            "first_start": float(first_start) if first_start is not None else float(proc.arrival),
        }

        waiting_times.append(waiting)
        turnaround_times.append(turnaround)
        response_times.append(response)

    averages = {
        "waiting": sum(waiting_times) / len(waiting_times) if waiting_times else 0.0,
        "turnaround": sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0.0,
        "response": sum(response_times) / len(response_times) if response_times else 0.0,
    }

    completed = len([proc for proc in processes if proc.burst > 0])
    throughput = completed / makespan_duration if makespan_duration > 0 else 0.0
    cpu_utilization = (busy_time / makespan_duration * 100.0) if makespan_duration > 0 else 0.0

    return per_process, averages, context_switches, cpu_utilization, throughput, makespan


def build_summary_row(result: Dict[str, float]) -> Dict[str, float]:
    """Utility to normalise rounded summary metrics for tabular output."""
    return {key: round(value, 2) for key, value in result.items()}

