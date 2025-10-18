"""Visualisation utilities for the FS-25 simulator."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from fs25_models import Process, ScheduleSlice
from fs25_algorithms.common import pid_numeric


def draw_gantt_chart(
    timeline: List[ScheduleSlice],
    processes: Iterable[Process],
    title: str,
    output_path: Path,
    pid_order: Optional[List[str]] = None,
) -> None:
    """Render a horizontal Gantt chart."""
    processes = list(processes)
    if pid_order is None:
        pid_order = [proc.pid for proc in sorted(processes, key=lambda p: pid_numeric(p.pid))]

    pid_to_index = {pid: idx for idx, pid in enumerate(pid_order)}
    cmap = plt.get_cmap("tab20")

    height = max(4, len(pid_order) * 0.45 + 1)
    fig, ax = plt.subplots(figsize=(12, height))

    if not timeline:
        ax.set_title(f"{title}\n(No execution slices recorded)")
        ax.set_xlabel("Time")
        ax.set_ylabel("Process")
        ax.set_yticks(range(len(pid_order)))
        ax.set_yticklabels(pid_order)
    else:
        colors = {}
        for idx, pid in enumerate(pid_order):
            colors[pid] = cmap(idx % cmap.N)
        for slice_ in timeline:
            color = colors.get(slice_.pid, cmap(0))
            y = pid_to_index.get(slice_.pid)
            if y is None:
                continue  # skip processes not requested for the chart
            ax.barh(
                y=y,
                width=slice_.end - slice_.start,
                left=slice_.start,
                height=0.4,
                align="center",
                color=color,
                edgecolor="black",
            )
            ax.text(
                x=(slice_.start + slice_.end) / 2,
                y=y,
                s=slice_.pid,
                va="center",
                ha="center",
                color="white",
                fontsize=8,
                fontweight="bold",
            )

        ax.set_title(title)
        ax.set_xlabel("Time")
        ax.set_ylabel("Process")
        ax.set_yticks(range(len(pid_order)))
        ax.set_yticklabels(pid_order)
        ax.grid(axis="x", linestyle="--", alpha=0.4)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)

