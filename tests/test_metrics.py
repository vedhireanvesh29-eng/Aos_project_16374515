from __future__ import annotations

import math

from fs25_metrics import compute_algorithm_metrics
from fs25_models import Process, ScheduleSlice


def test_basic_metrics_and_context_switches() -> None:
    processes = [
        Process("P1", arrival=0, burst=3, priority=1),
        Process("P2", arrival=1, burst=2, priority=1),
    ]
    timeline = [
        ScheduleSlice("P1", 0, 3),
        ScheduleSlice("P2", 3, 5),
    ]

    per_process, averages, context_switches, cpu_util, throughput, makespan = compute_algorithm_metrics(
        processes, timeline
    )

    assert per_process["P1"]["waiting"] == 0
    assert math.isclose(per_process["P2"]["waiting"], 2.0)
    assert math.isclose(averages["waiting"], 1.0)
    assert context_switches == 1
    assert math.isclose(cpu_util, 100.0)
    assert math.isclose(throughput, 0.4)
    assert makespan == 5


def test_utilisation_with_idle_gap() -> None:
    processes = [
        Process("P1", arrival=0, burst=2, priority=1),
        Process("P2", arrival=5, burst=3, priority=1),
    ]
    timeline = [
        ScheduleSlice("P1", 0, 2),
        ScheduleSlice("P2", 5, 8),
    ]

    _, averages, context_switches, cpu_util, throughput, makespan = compute_algorithm_metrics(processes, timeline)

    assert context_switches == 1
    assert math.isclose(cpu_util, 62.5)
    assert math.isclose(averages["response"], 0.0)
    assert math.isclose(throughput, 5 / 8, rel_tol=1e-3)
    assert makespan == 8


def test_preemptive_context_switch_count() -> None:
    processes = [
        Process("P1", arrival=0, burst=2, priority=1),
        Process("P2", arrival=0, burst=1, priority=1),
    ]
    timeline = [
        ScheduleSlice("P1", 0, 1),
        ScheduleSlice("P2", 1, 2),
        ScheduleSlice("P1", 2, 3),
    ]
    _, _, context_switches, _, _, _ = compute_algorithm_metrics(processes, timeline)
    assert context_switches == 2

