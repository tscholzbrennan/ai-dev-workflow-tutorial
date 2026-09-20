# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A tutorial project (see `README.md`) that teaches an AI-assisted development workflow — PRD → `TASKS.md` milestones → brainstorming → writing-plans → executing-plans → commit → push → review → deploy — by having the student build a real Streamlit sales dashboard. The dashboard itself (KPI cards, a monthly trend chart, category/region breakdowns reading from `data/sales-data.csv`) is intentionally simple; the point of the repo is the traceable workflow, not the app.

The requirements live in `prd/ecommerce-analytics.md`. Work is tracked milestone-by-milestone in `TASKS.md` (`TASK-1` through `TASK-7`), each with a Definition of Done: acceptance criteria met, `streamlit run app.py` works locally, and the commit message includes the milestone ID. The active implementation plan and design doc are under `docs/superpowers/plans/` and `docs/superpowers/specs/`.

## Commands

Activate the virtual environment before running `pytest` or `streamlit` — there is no other setup step:

```bash
source venv/bin/activate       # macOS/Linux
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Run the app:
```bash
streamlit run app.py
```

Run tests:
```bash
pytest                                    # full suite
pytest tests/test_calculations.py -v      # one file, verbose
pytest tests/test_calculations.py::test_compute_total_sales   # one test
```

There is no linter, formatter, or build step configured in this repo.

## Architecture

The codebase enforces a hard split between computation and rendering, and it matters for where new code goes:

- **`calculations.py`** — pure pandas, zero Streamlit imports. `load_data(path)` reads and validates `data/sales-data.csv` (existence, required columns, parseable date/numeric types), raising `ValueError` with a plain-language message on failure rather than crashing. The rest are pure aggregation functions (`compute_total_sales`, `compute_total_orders`, `sales_by_month`, `sales_by_category`, `sales_by_region`) that take a validated DataFrame and return small, chart-ready DataFrames — `sales_by_category`/`sales_by_region` pre-sort descending so chart code never sorts itself. Because this module never imports `streamlit`, it's fully covered by plain `pytest` in `tests/test_calculations.py` against small hand-built fixture DataFrames, not the full 482-row CSV.
- **`app.py`** — Streamlit rendering only: page config, layout (`st.columns`), formatting (`f"${total_sales:,.0f}"`), and Plotly chart construction. It imports from `calculations.py` and never computes anything itself. It wraps `load_data(...)` in `try/except ValueError` and calls `st.error(...)` + `st.stop()` on failure instead of letting a raw traceback reach the page.

This split is why there are no tests for `app.py` — Streamlit UI isn't meaningfully unit-testable, so TDD is applied to `calculations.py`'s functions only (write the failing test, then the implementation).

## Workflow conventions specific to this repo

- Work happens on `feature/sales-dashboard`; no git worktree is used for this project.
- Every commit that touches milestone work includes that milestone's ID (e.g. `TASK-3: ...`) per `TASKS.md`'s Definition of Done — this is what makes `git log` traceable back to a requirement.
- Milestone board moves (`To Do` → `In Progress` → `Done` in `TASKS.md`) are typically their own commits, separate from the implementation commit for that milestone.
- `TASK-7` (deployment to Streamlit Community Cloud) is developer-executed: it runs from `main` after `feature/sales-dashboard` is reviewed and merged, and is not something to run automatically as part of implementing the other milestones.

## Lessons

Distilled from `TASKS.md`'s per-milestone Notes lines:

- A bare `pytest` run from the repo root can't resolve the top-level `calculations` module without discovery help — that's why an empty `conftest.py` exists at the project root. Don't delete it as dead weight; it's load-bearing for imports.
- If `streamlit run` is launched non-interactively (e.g. in a background process), Streamlit's first-run onboarding can block waiting for an email prompt on stdin. Fix it with a local `~/.streamlit/credentials.toml` (a machine-level config, not a project file) rather than treating the process as hung.
- A `urllib3`/OpenSSL `NotOpenSSLWarning` on `streamlit run` startup is a pre-existing environment quirk (LibreSSL vs OpenSSL), not an app regression — don't chase it as part of a task's "no errors or warnings" check.
- `plotly.express` infers axis labels from raw DataFrame column names by default (e.g. `total_amount`, `month`). Always pass an explicit `labels=` mapping to `px.line`/`px.bar` calls — this was a real gap caught during TASK-6's acceptance-criteria pass, not a hypothetical.
- Streamlit apps can't be verified with `curl`/non-JS fetches: the page is a client-side JS shell that decides at runtime whether to render the app or an auth wall, so a 200 response proves nothing about what a real viewer sees. When no browser automation tool is available, verify data correctness by computing expected values directly against the real CSV via `calculations.py` and checking the server log for errors — but say plainly that visual rendering, tooltips, and cross-browser behavior are unverified rather than implying they were checked.
- Deployment/cross-browser verification (TASK-7-style acceptance criteria) is a human step, not something an agent can complete from the CLI — hand it back to the developer rather than approximating it with `curl`.
