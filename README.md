# FS-25 CPU Scheduling Simulator

**Student ID:** 16374515

## Overview
This project simulates and compares five classical CPU scheduling algorithms: First-Come-First-Served (FCFS), Shortest Job First (SJF), Shortest Remaining Time First (SRTF), non-preemptive Priority (lower value = higher priority), and Round Robin (RR) with a default quantum of 4. The simulator generates deterministic workloads, evaluates metrics (waiting, turnaround, response, throughput, context switches, CPU utilisation), and produces Gantt charts plus aggregated reports.

## Quick Start

`ash
# Optional: create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the simulator (default settings)
python fs25_main_16374515.py

# Alternate examples
python fs25_main_16374515.py --quantum 5 --t_transient 12
python fs25_main_16374515.py --transient false
python fs25_main_16374515.py --input_json custom_processes.json

# Run unit tests
pytest -q
`

## Generated Outputs
Results are written to FS25_Output_16374515/ (or another directory supplied via --outdir). Expect:

- Per-algorithm metrics CSVs and Gantt charts for both baseline and transient scenarios.
- Comparison tables summarising average metrics across algorithms.
- FS25_Report_16374515.md — 600–900 word Markdown report describing setup, results, analysis, transient impact, and conclusions.

## Algorithms Implemented
- **FCFS:** Non-preemptive, arrival-order scheduling.
- **SJF:** Non-preemptive, shortest burst first with deterministic tie-breaking.
- **SRTF:** Preemptive SJF, using remaining burst time for priority.
- **Priority (NP):** Non-preemptive scheduling by priority value.
- **Round Robin:** Preemptive with fixed quantum (default 4).

## Branching, Tags, and Workflow
Use feature branches to isolate work:

`ash
git checkout -b feat/<short-description>
# make changes
git commit -am "Describe your change"
git push -u origin feat/<short-description>
`

Tag releases after merging:

`ash
git tag v0.1.0
git push origin v0.1.0
`

(Optional) Install pre-commit hooks to enforce formatting or linting:

`ash
pip install pre-commit
pre-commit install
`

## Continuous Integration
A GitHub Actions workflow in .github/workflows/ci.yaml installs dependencies and runs the pytest suite on every push and pull request.

## Optional Large File Support
If you plan to retain large Gantt images or other binaries in version control:

`ash
git lfs install
git lfs track "FS25_Output_16374515/**/*.png"
git add .gitattributes
git commit -m "Configure Git LFS for scheduler artifacts"
`

## Reference
Inspired by: [https://github.com/IndrarajBiswas/cpu_scheduling_sim](https://github.com/IndrarajBiswas/cpu_scheduling_sim)
