# Quality Intelligence Platform

**Self-Healing Quality Intelligence Platform** for modern engineering teams.

This project goes beyond traditional pass/fail test automation. It helps teams understand:

- **What** broke
- **Why** it broke
- **How risky** the change is
- **Whether** a release should proceed

---

## Key Capabilities

| Capability                    | Description                                                                 |
|------------------------------|-----------------------------------------------------------------------------|
| Risk-based Test Selection    | Selects the most relevant tests using changed files, historical failures, and criticality |
| Flaky Test Intelligence      | Detects intermittent failures and tracks failure rates                      |
| Failure Evidence Engine      | Collects screenshots, logs, stack traces, and API responses into one report |
| Root-cause Suggestions       | Rule-based explanations with optional LLM grounding                         |
| Release Quality Gate         | Blocks releases when critical tests fail or quality thresholds are violated |
| Self-Healing with Guardrails | Suggests locator repairs but **never** auto-applies them                    |

---

## Controlled Experiment Results

We ran a controlled comparison between full regression and risk-based selection:

| Metric                      | Result      |
|----------------------------|-------------|
| Average test reduction     | **28.6%**   |
| Failure detection rate     | **100%**    |
| Missed failures            | **0**       |

Raw experiment data is available in `experiments/results/`.

---

## Tech Stack

- **Python 3.12** + pytest
- **Playwright** for UI testing
- **SQLAlchemy** + PostgreSQL (optional) for history
- **GitHub Actions** for CI
- Structured evidence reports (JSON + HTML)

---

## Quick Start

```bash
# Clone
git clone https://github.com/dhyaneshwarimasram23-eng/quality-intelligence-platform.git
cd quality-intelligence-platform

# Setup
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
playwright install chromium

# Run unit tests
set PYTHONPATH=.
pytest tests/ -v

# Run UI tests
pytest tests/ui/ -v

# Run the controlled experiment
python experiments/risk_selection_experiment.py