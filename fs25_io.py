"""Input/output helpers for the FS-25 CPU scheduling simulator."""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, Iterable, List

from fs25_models import Process


def ensure_directory(path: Path) -> Path:
    """Create an output directory if it does not already exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def generate_processes(seed: int, count: int) -> List[Process]:
    """Generate a deterministic set of processes."""
    rng = random.Random(seed)
    arrivals = [rng.randint(0, 30) for _ in range(count)]
    if len(set(arrivals)) == count and count >= 2:
        i1, i2 = rng.sample(range(count), 2)
        arrivals[i2] = arrivals[i1]

    processes = []
    for index in range(count):
        pid = f"P{index + 1}"
        arrival = arrivals[index]
        burst = rng.randint(1, 20)
        priority = rng.randint(1, 5)
        processes.append(Process(pid=pid, arrival=arrival, burst=burst, priority=priority))
    return processes


def load_processes_from_json(path: Path) -> List[Process]:
    """Load process definitions from a JSON file adhering to the required schema."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON format in {path}") from exc

    if not isinstance(data, list):
        raise ValueError("Process JSON must be a list of objects")

    processes: List[Process] = []
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError("Process entries must be objects")
        required_keys = {"pid", "arrival", "burst", "priority"}
        missing = required_keys - entry.keys()
        if missing:
            raise ValueError(f"Process entry missing fields: {missing}")
        pid = str(entry["pid"])
        try:
            arrival = int(entry["arrival"])
            burst = int(entry["burst"])
            priority = int(entry["priority"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Process entry has non-integer values: {entry}") from exc
        processes.append(Process(pid=pid, arrival=arrival, burst=burst, priority=priority))

    return processes


def save_processes_to_json(processes: Iterable[Process], path: Path) -> None:
    """Persist the processes used for a simulation run."""
    serialisable = [
        {
            "pid": proc.pid,
            "arrival": proc.arrival,
            "burst": proc.burst,
            "priority": proc.priority,
        }
        for proc in processes
    ]
    path.write_text(json.dumps(serialisable, indent=2), encoding="utf-8")


def write_metrics_csv(
    path: Path,
    processes: List[Process],
    per_process: Dict[str, Dict[str, float]],
    averages: Dict[str, float],
    context_switches: int,
    cpu_utilization: float,
    throughput: float,
    makespan: int,
) -> None:
    """Write the per-process metrics table with an appended averages row."""
    import csv

    fieldnames = [
        "pid",
        "arrival",
        "burst",
        "priority",
        "waiting",
        "turnaround",
        "response",
        "completion",
        "first_start",
    ]

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames + ["throughput", "context_switches", "cpu_utilization", "makespan"])
        writer.writeheader()
        for proc in processes:
            metrics = per_process[proc.pid]
            row = {key: metrics[key] for key in fieldnames if key != "pid"}
            row["pid"] = proc.pid
            writer.writerow(
                {
                    **row,
                    "throughput": "",
                    "context_switches": "",
                    "cpu_utilization": "",
                    "makespan": "",
                }
            )

        writer.writerow(
            {
                "pid": "AVERAGES",
                "arrival": "",
                "burst": "",
                "priority": "",
                "waiting": averages["waiting"],
                "turnaround": averages["turnaround"],
                "response": averages["response"],
                "completion": "",
                "first_start": "",
                "throughput": throughput,
                "context_switches": context_switches,
                "cpu_utilization": cpu_utilization,
                "makespan": makespan,
            }
        )

