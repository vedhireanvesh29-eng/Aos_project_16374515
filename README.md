# FS-25 CPU Scheduling Simulator

**Student ID:** 16374515

This project simulates and compares five classical CPU scheduling algorithms:
- First-Come-First-Served (FCFS)
- Shortest Job First (SJF, non-preemptive)
- Shortest Remaining Time First (SRTF, preemptive)
- Priority (non-preemptive; lower number = higher priority)
- Round Robin (preemptive; default quantum = 4)

The simulator generates deterministic workloads (seeded with the student ID), runs the algorithms **with and without** a transient emergency process, produces per-algorithm metrics and Gantt charts, and generates a final Markdown report.

## Quick Start

```bash
# Optional: create & activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install deps
pip install -r requirements.txt

# Run (defaults: seed=16374515, n=15, quantum=4)
python fs25_main_16374515.py

More runs
# Change RR quantum and transient injection time
python fs25_main_16374515.py --quantum 5 --t_transient 12

# Disable transient event
python fs25_main_16374515.py --transient false

# Load custom processes from JSON
python fs25_main_16374515.py --input_json custom_processes.json

Outputs

All artifacts are written to FS25_Output_16374515/ (or the directory set with --outdir):

Per-algorithm metrics (CSV) for baseline and transient runs

Gantt charts (PNG) for each algorithm, both runs

Aggregated comparison tables

Final report: FS25_Report_16374515.md

Development
pytest -q


Feature branches are recommended:

git checkout -b feat/<short-name>
# ...
git commit -m "feat: <message>"
git push -u origin feat/<short-name>


Tag a release:

git tag v0.1.0
git push origin v0.1.0

Continuous Integration

A GitHub Actions workflow at .github/workflows/ci.yaml installs dependencies and runs tests on every push and pull request.
