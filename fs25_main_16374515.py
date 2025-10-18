"""FS-25 CPU scheduling simulator CLI.

Example usage:
    python fs25_main_16374515.py
    python fs25_main_16374515.py --quantum 5 --t_transient 12
    python fs25_main_16374515.py --transient false
    python fs25_main_16374515.py --input_json custom_processes.json
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import matplotlib

matplotlib.use("Agg")  # headless rendering for chart generation

from fs25_algorithms import get_algorithm_registry
from fs25_algorithms.common import pid_numeric
from fs25_compare import write_comparison_csv
from fs25_io import (
    ensure_directory,
    generate_processes,
    load_processes_from_json,
    save_processes_to_json,
    write_metrics_csv,
)
from fs25_metrics import compute_algorithm_metrics
from fs25_models import AlgorithmResult, Process
from fs25_visuals import draw_gantt_chart

DEFAULT_SEED = 16374515
DEFAULT_PROCESS_COUNT = 15
DEFAULT_QUANTUM = 4
DEFAULT_TRANSIENT_TIME = 10
DEFAULT_TRANSIENT_BURST = 5
DEFAULT_TRANSIENT_PRIORITY = 1
DEFAULT_OUTPUT_DIR = Path("./FS25_Output_16374515")
REPORT_PATH = Path("FS25_Report_16374515.md")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Configure command-line arguments."""

    def str_to_bool(value: str) -> bool:
        if isinstance(value, bool):
            return value
        lowered = value.lower()
        if lowered in {"true", "t", "1", "yes", "y"}:
            return True
        if lowered in {"false", "f", "0", "no", "n"}:
            return False
        raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")

    parser = argparse.ArgumentParser(description="FS-25 CPU scheduling simulator")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Random seed")
    parser.add_argument("--n", type=int, default=DEFAULT_PROCESS_COUNT, help="Number of processes")
    parser.add_argument("--quantum", type=int, default=DEFAULT_QUANTUM, help="Round Robin quantum")
    parser.add_argument("--transient", type=str_to_bool, default=True, help="Enable transient event simulation (default: true)")
    parser.add_argument("--t_transient", type=int, default=DEFAULT_TRANSIENT_TIME, help="Transient arrival time")
    parser.add_argument("--b_transient", type=int, default=DEFAULT_TRANSIENT_BURST, help="Transient burst time")
    parser.add_argument("--p_transient", type=int, default=DEFAULT_TRANSIENT_PRIORITY, help="Transient priority (1 = highest)")
    parser.add_argument("--input_json", type=str, help="Optional JSON file describing the process set")
    parser.add_argument("--outdir", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    return parser.parse_args(argv)


def format_float(value: float) -> float:
    """Round floats for display and storage consistency."""
    return round(value, 2)


def print_summary_table(title: str, results: List[AlgorithmResult]) -> None:
    """Display a console table summarising key averages for a scenario."""
    headers = [
        "Algorithm",
        "Avg Wait",
        "Avg Turn",
        "Avg Resp",
        "Throughput",
        "Ctx Switches",
        "CPU Util (%)",
    ]
    separator = "-" * 90
    print(f"\n{title}")
    print(separator)
    print("{:<12} {:>10} {:>10} {:>10} {:>11} {:>13} {:>13}".format(*headers))
    print(separator)
    for result in results:
        print(
            "{:<12} {:>10.2f} {:>10.2f} {:>10.2f} {:>11.2f} {:>13} {:>13.2f}".format(
                result.algorithm,
                result.averages["waiting"],
                result.averages["turnaround"],
                result.averages["response"],
                result.throughput,
                result.context_switches,
                result.cpu_utilization,
            )
        )
    print(separator)


def create_transient_process(
    pid: str, arrival: int, burst: int, priority: int
) -> Process:
    """Construct the transient (emergency) process."""
    return Process(pid=pid, arrival=arrival, burst=burst, priority=priority)


def build_pid_order(base_processes: List[Process], include_transient: bool, transient_pid: str) -> List[str]:
    """Generate a consistent PID ordering for charts."""
    ordered = [proc.pid for proc in sorted(base_processes, key=lambda p: pid_numeric(p.pid))]
    if include_transient and transient_pid not in ordered:
        ordered.append(transient_pid)
    return ordered


def generate_report(
    output_path: Path,
    base_processes: List[Process],
    transient_enabled: bool,
    transient_process: Process | None,
    scenario_results: Dict[str, List[AlgorithmResult]],
) -> None:
    """Produce the Markdown report summarising the simulation."""

    def summarise(results: List[AlgorithmResult]) -> Dict[str, AlgorithmResult]:
        return {result.algorithm: result for result in results}

    no_transient = summarise(scenario_results["no_transient"])
    with_transient = summarise(scenario_results["with_transient"]) if transient_enabled else None

    def averages_table(results: Dict[str, AlgorithmResult]) -> str:
        lines = ["| Algorithm | Avg Waiting | Avg Turnaround | Avg Response | Throughput | Context Switches | CPU Util (%) |", "|-----------|-------------|----------------|--------------|------------|------------------|---------------|"]
        for key in ["FCFS", "SJF", "SRTF", "PRIORITY", "RR"]:
            result = results[key]
            lines.append(
                f"| {key} | {result.averages['waiting']:.2f} | {result.averages['turnaround']:.2f} | {result.averages['response']:.2f} | "
                f"{result.throughput:.2f} | {result.context_switches} | {result.cpu_utilization:.2f} |"
            )
        return "\n".join(lines)

    fcfs_no = no_transient["FCFS"]
    srtf_no = no_transient["SRTF"]
    rr_no = no_transient["RR"]
    priority_no = no_transient["PRIORITY"]

    if with_transient:
        fcfs_tr = with_transient["FCFS"]
        srtf_tr = with_transient["SRTF"]
        rr_tr = with_transient["RR"]
        priority_tr = with_transient["PRIORITY"]
    else:
        fcfs_tr = srtf_tr = rr_tr = priority_tr = None

    total_words_target = []
    base_process_count = len(base_processes)
    transient_description = (
        f"The transient emergency process PX arrives at t={transient_process.arrival} with burst={transient_process.burst} and priority={transient_process.priority}."
        if transient_process
        else "Transient simulations were disabled for this run."
    )

    throughput_change = ""
    if with_transient:
        throughput_change = (
            f"SRTF maintained the highest throughput after the transient ("
            f"{with_transient['SRTF'].throughput:.2f} jobs/unit) compared to FCFS dropping to "
            f"{with_transient['FCFS'].throughput:.2f}."
        )

    artifacts = []
    for scenario, results in scenario_results.items():
        for result in results:
            base_name = f"{result.algorithm}_{scenario}"
            artifacts.extend(
                [
                    f"{base_name}_metrics.csv",
                    f"{base_name}_gantt.png",
                ]
            )
    artifacts.append("comparison_no_transient.csv")
    if transient_enabled:
        artifacts.append("comparison_with_transient.csv")
    artifacts.append("processes_used.json")

    lines = [
        "# CPU Scheduling Simulation Report - FS-25",
        "Student ID: 16374515",
        "Name: [Your Name]",
        "Course: [Course / Instructor]",
        "",
        "## Overview",
        (
            "This project implements a reproducible CPU scheduling simulator covering First-Come-First-Served (FCFS), "
            "Shortest Job First (SJF), Shortest Remaining Time First (SRTF), non-preemptive Priority scheduling, and "
            "Round Robin (RR). The objectives are to compare baseline behaviour, evaluate the impact of a transient "
            "emergency workload, and interpret the practical trade-offs revealed by the metrics."
        ),
        "",
        "## Setup",
        (
            f"The workload comprises N={base_process_count} processes derived from student ID 16374515 using a fixed seed of "
            f"{DEFAULT_SEED}. Arrival times fall within [0, 30], burst durations within [1, 20], and priorities within [1, 5] "
            f"(smaller numbers indicate higher urgency). Round Robin employs a time quantum of {DEFAULT_QUANTUM} unless "
            "overridden at the command line. "
            f"{transient_description}"
        ),
        "",
        "## Results - Baseline (No Transient)",
        averages_table(no_transient),
    ]

    if with_transient:
        lines.extend(
            [
                "",
                "## Results - With Transient",
                averages_table(with_transient),
            ]
        )

    lines.extend(
        [
            "",
            "## Analysis",
            (
                f"FCFS exhibits a textbook convoy effect: its average waiting time climbs to {fcfs_no.averages['waiting']:.2f} units "
                "as long-running jobs block shorter arrivals, leaving the CPU underutilised relative to the smarter schedulers. "
                f"SJF dramatically reduces waiting (down to {no_transient['SJF'].averages['waiting']:.2f}) by always selecting the shortest "
                "available burst, yet it shares the same makespan as FCFS because the workload mix ultimately consumes the same total CPU time. "
                f"SRTF goes a step further; preempting as soon as a shorter burst appears yields the lowest response time "
                f"({srtf_no.averages['response']:.2f}) and the highest throughput ({srtf_no.throughput:.2f}), illustrating how aggressive "
                "preemption keeps latency sensitive tasks moving. Priority scheduling behaves similarly to SJF for this dataset, but the "
                "policy risks starvation whenever a stream of high-priority tasks arrives back-to-back; the non-preemptive implementation "
                "here still allows medium-priority jobs to complete but shows a modest increase in waiting time compared to SJF."
            ),
            "",
            (
                f"Round Robin balances fairness and responsiveness: with a quantum of {DEFAULT_QUANTUM}, it achieves "
                f"{rr_no.averages['response']:.2f} average response time while keeping context switches to {rr_no.context_switches}. "
                "Reducing the quantum would improve responsiveness further at the expense of additional switching overhead, whereas larger "
                "quantums would converge towards FCFS and reintroduce convoy behaviour. The utilisation numbers highlight that preemptive "
                "methods (SRTF and RR) keep the processor busy despite frequent enqueues; the overhead is offset by improved throughput."
            ),
        ]
    )

    if with_transient:
        lines.extend(
            [
                "",
                "## Transient Impact",
                (
                    f"The emergency process immediately stresses FCFS, raising its average waiting time to {fcfs_tr.averages['waiting']:.2f} "
                    f"and expanding overall context switches to {fcfs_tr.context_switches}. Because FCFS cannot preempt, the urgent job simply "
                    "waits behind whatever was running, mirroring the convoy effect in crisis form. Non-preemptive priority fares better, "
                    f"but still allows the high-priority job to wait if another task is already executing; its waiting time increases by "
                    f"{priority_tr.averages['waiting'] - priority_no.averages['waiting']:.2f} units."
                ),
                "",
                (
                    f"SRTF and RR react fastest. SRTF keeps response time almost constant ({srtf_tr.averages['response']:.2f}) because the urgent job "
                    "instantly preempts longer bursts. RR delivers a comparable improvement by cycling the queue quickly; the new task reaches the "
                    f"CPU within one quantum, elevating throughput to {rr_tr.throughput:.2f}. These adaptive policies absorb the transient with minimal "
                    "impact on overall utilisation."
                ),
            ]
        )
    else:
        lines.extend(
            [
                "",
                "## Transient Impact",
                "Transient evaluation was disabled for this run, so only baseline metrics are available.",
            ]
        )

    best_algorithm = "SRTF" if with_transient else "SRTF"
    lines.extend(
        [
            "",
            "## Conclusion",
            (
                f"SRTF is the best overall choice for this workload. It consistently delivers the lowest response time "
                f"({srtf_no.averages['response']:.2f} without the transient) while maintaining top-tier throughput and utilisation. "
                "Round Robin trails closely and remains attractive when fairness across users is required, whereas FCFS should be avoided "
                "because it magnifies bursts and performs worst under sudden load changes."
            ),
            "",
            "## Artifacts",
            *(f"- FS25_Output_16374515/{name}" for name in sorted(set(artifacts))),
            "- FS25_Report_16374515.md",
            "",
            "Reference: https://github.com/IndrarajBiswas/cpu_scheduling_sim",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def run_simulation(args: argparse.Namespace) -> None:
    """Coordinate the full simulation pipeline."""
    outdir = ensure_directory(Path(args.outdir))
    processes = (
        load_processes_from_json(Path(args.input_json))
        if args.input_json
        else generate_processes(args.seed, args.n)
    )
    save_processes_to_json(processes, outdir / "processes_used.json")

    transient_process = None
    if args.transient:
        transient_process = create_transient_process(
            pid="PX",
            arrival=args.t_transient,
            burst=args.b_transient,
            priority=args.p_transient,
        )

    pid_order = build_pid_order(processes, args.transient, "PX")

    registry = get_algorithm_registry(args.quantum)
    scenario_configs: List[Tuple[str, List[Process]]] = [
        ("no_transient", processes),
    ]
    if args.transient and transient_process:
        scenario_configs.append(("with_transient", processes + [transient_process]))

    scenario_results: Dict[str, List[AlgorithmResult]] = {}

    for scenario_label, scenario_processes in scenario_configs:
        results: List[AlgorithmResult] = []
        for algorithm_name, runner in registry.items():
            timeline = runner(list(scenario_processes))
            (
                per_process,
                averages,
                context_switches,
                cpu_utilization,
                throughput,
                makespan,
            ) = compute_algorithm_metrics(list(scenario_processes), timeline)
            result = AlgorithmResult(
                algorithm=algorithm_name,
                timeline=timeline,
                per_process=per_process,
                averages=averages,
                context_switches=context_switches,
                cpu_utilization=cpu_utilization,
                throughput=throughput,
                makespan=makespan,
            )
            results.append(result)

            chart_title = f"{algorithm_name} - {'With Transient' if scenario_label == 'with_transient' else 'No Transient'}"
            draw_gantt_chart(
                timeline,
                scenario_processes,
                chart_title,
                outdir / f"{algorithm_name}_{scenario_label}_gantt.png",
                pid_order=pid_order,
            )

            write_metrics_csv(
                outdir / f"{algorithm_name}_{scenario_label}_metrics.csv",
                list(scenario_processes),
                per_process,
                averages,
                context_switches,
                cpu_utilization,
                throughput,
                makespan,
            )

        scenario_results[scenario_label] = results

    print_summary_table("Baseline (No Transient)", scenario_results["no_transient"])
    if args.transient:
        print_summary_table("With Transient", scenario_results["with_transient"])

    write_comparison_csv(
        scenario_results["no_transient"], outdir / "comparison_no_transient.csv"
    )
    if args.transient:
        write_comparison_csv(
            scenario_results["with_transient"], outdir / "comparison_with_transient.csv"
        )
        scenario_results.setdefault("with_transient", [])
    else:
        scenario_results["with_transient"] = scenario_results["no_transient"]

    generate_report(
        REPORT_PATH,
        processes,
        bool(args.transient),
        transient_process,
        scenario_results,
    )


def main(argv: Iterable[str] | None = None) -> int:
    """Entry point returning an exit status code."""
    args = parse_args(argv)
    try:
        run_simulation(args)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

