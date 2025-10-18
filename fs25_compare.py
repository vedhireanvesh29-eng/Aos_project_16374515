"""Aggregate comparison table generation."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from fs25_models import AlgorithmResult


def write_comparison_csv(results: Iterable[AlgorithmResult], output_path: Path) -> None:
    """Write comparison metrics for a set of algorithm results."""
    fieldnames = [
        "algorithm",
        "avg_waiting",
        "avg_turnaround",
        "avg_response",
        "throughput",
        "context_switches",
        "cpu_utilization",
        "makespan",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "algorithm": result.algorithm,
                    "avg_waiting": result.averages["waiting"],
                    "avg_turnaround": result.averages["turnaround"],
                    "avg_response": result.averages["response"],
                    "throughput": result.throughput,
                    "context_switches": result.context_switches,
                    "cpu_utilization": result.cpu_utilization,
                    "makespan": result.makespan,
                }
            )

