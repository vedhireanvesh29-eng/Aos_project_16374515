from __future__ import annotations

from fs25_algorithms.fs25_fcfs import run_fcfs
from fs25_algorithms.fs25_priority import run_priority
from fs25_algorithms.fs25_rr import run_rr
from fs25_algorithms.fs25_sjf import run_sjf
from fs25_algorithms.fs25_srtf import run_srtf
from fs25_models import Process


def extract_pid_sequence(timeline):
    return [slice_.pid for slice_ in timeline]


def test_fcfs_tie_breaks_by_pid_suffix() -> None:
    processes = [
        Process("P10", arrival=0, burst=2, priority=1),
        Process("P2", arrival=0, burst=1, priority=1),
        Process("P1", arrival=0, burst=1, priority=1),
    ]
    order = extract_pid_sequence(run_fcfs(processes))
    assert order == ["P1", "P2", "P10"]


def test_sjf_prefers_shortest_then_pid() -> None:
    processes = [
        Process("P1", arrival=0, burst=4, priority=1),
        Process("P2", arrival=1, burst=2, priority=1),
        Process("P3", arrival=1, burst=2, priority=1),
        Process("P4", arrival=1, burst=3, priority=1),
    ]
    order = extract_pid_sequence(run_sjf(processes))
    # After the initial P1, SJF should choose P2 then P3 (same burst, pid order), then P4.
    assert order == ["P1", "P2", "P3", "P4"]


def test_srtf_preempts_and_uses_pid_tie_breaker() -> None:
    processes = [
        Process("P1", arrival=0, burst=10, priority=1),
        Process("P2", arrival=1, burst=3, priority=1),
        Process("P3", arrival=1, burst=3, priority=1),
    ]
    order = extract_pid_sequence(run_srtf(processes))
    assert order[:3] == ["P1", "P2", "P3"]


def test_priority_non_preemptive_ties() -> None:
    processes = [
        Process("P1", arrival=0, burst=3, priority=2),
        Process("P2", arrival=0, burst=2, priority=2),
        Process("P3", arrival=1, burst=1, priority=1),
    ]
    order = extract_pid_sequence(run_priority(processes))
    assert order == ["P1", "P3", "P2"]


def test_round_robin_queue_order() -> None:
    processes = [
        Process("P1", arrival=0, burst=5, priority=1),
        Process("P2", arrival=0, burst=5, priority=1),
        Process("P3", arrival=0, burst=5, priority=1),
    ]
    timeline = run_rr(processes, quantum=2)
    assert extract_pid_sequence(timeline)[:3] == ["P1", "P2", "P3"]
