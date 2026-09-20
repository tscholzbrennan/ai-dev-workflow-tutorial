# Design: E-Commerce Sales Dashboard

**Source:** `prd/ecommerce-analytics.md`
**Milestones tracked in:** `TASKS.md` (TASK-1 through TASK-7)
**Branch:** `feature/sales-dashboard`

## Purpose

Build the Phase 1 sales dashboard described in the PRD: a Streamlit app showing Total Sales and Total Orders as KPI cards, a monthly sales trend line chart, and bar charts breaking down sales by category and by region — all reading from `data/sales-data.csv`.

## Constraints (set by the developer, not defaults)

- Work on the existing `feature/sales-dashboard` branch. No git worktree.
- Plain `venv/` virtual environment with a `requirements.txt` (no uv/conda). `venv/` is already covered by `.gitignore`.
- Data calculations live in their own module with pytest tests, separate from the Streamlit UI code.
- Code stays simple and readable — no abstractions beyond what this scope needs.
- Deployment is the plan's final step, executed by the developer from `main` after merge — not part of this build.

## File structure

```
app.py                  # Streamlit UI only: page config, KPI cards, charts, layout
calculations.py         # Pure functions: load + validate CSV, aggregations
tests/
  test_calculations.py  # pytest tests for calculations.py
data/sales-data.csv     # existing sample data (482 rows)
requirements.txt        # streamlit, pandas, plotly, pytest
venv/                   # gitignored
```

`calculations.py` has no Streamlit dependency — it's plain pandas — so it's testable with pytest alone. `app.py` imports from it and never computes anything itself; it only formats and renders what `calculations.py` returns.

## Data loading and calculations (`calculations.py`)

```python
def load_data(path: str) -> pd.DataFrame:
    """Read and validate the sales CSV; raises ValueError on missing/malformed file."""

def compute_total_sales(df: pd.DataFrame) -> float
def compute_total_orders(df: pd.DataFrame) -> int
def sales_by_month(df: pd.DataFrame) -> pd.DataFrame     # columns: month, total_amount
def sales_by_category(df: pd.DataFrame) -> pd.DataFrame  # columns: category, total_amount — sorted desc
def sales_by_region(df: pd.DataFrame) -> pd.DataFrame    # columns: region, total_amount — sorted desc
```

- `load_data` validates that the file exists and that the required columns (`date`, `order_id`, `product`, `category`, `region`, `quantity`, `unit_price`, `total_amount`) are present and parse cleanly (dates as dates, numeric columns as numbers). On failure it raises `ValueError` with a plain-language message — it does not touch Streamlit or print tracebacks itself.
- The aggregation functions assume a validated DataFrame and return small, chart-ready DataFrames. `sales_by_category` and `sales_by_region` pre-sort descending by `total_amount`, so chart code never needs its own sort step.
- Monthly granularity for the trend chart (not daily): aggregate the 12 months of daily transactions into one point per calendar month, matching the PRD's mockup and avoiding a noisy 365-point axis.

## Rendering (`app.py`)

- **Error handling**: wraps `load_data(...)` in `try/except ValueError` and renders `st.error(message)` in the page if it fails, instead of crashing with a raw traceback. This satisfies TASK-1's "handles a missing file cleanly" criterion and NFR-2 (clear labels, no training required).
- **KPI cards**: `st.columns(2)` with `st.metric("Total Sales", f"${total_sales:,.0f}")` and `st.metric("Total Orders", f"{total_orders:,}")` — whole-dollar currency with comma separators, matching the PRD's `$X,XXX,XXX` format and its Expected Output table (no cents).
- **Trend chart**: `plotly.express.line` over `sales_by_month()`, with Plotly's built-in hover tooltips showing exact values (FR-2).
- **Category / region charts**: two `plotly.express.bar` charts side by side via `st.columns(2)`, each fed by its already-sorted DataFrame, with hover tooltips (FR-3, FR-4).
- **Layout**: title → KPI row → trend chart → category/region row, matching the PRD's mockup.

## Testing strategy

- `tests/test_calculations.py` covers every function in `calculations.py`, using a small hand-built fixture DataFrame (not the full 482-row CSV) so expected totals are easy to verify by inspection.
- Includes a test for `load_data` raising on a missing file, and one for a malformed CSV (e.g., a missing required column).
- No tests for `app.py` — Streamlit UI code isn't meaningfully testable with pytest; this matches the tutorial's convention of TDD on data transforms and skipping it on chart/layout rendering.
- `calculations.py`'s functions are the natural target for the plan's TDD-flagged steps: a failing test is written first for each, then the implementation.

## Milestone mapping (for the implementation plan)

| TASKS.md milestone | Covers |
|---|---|
| TASK-1: Environment setup and project initialization | venv, requirements.txt, `app.py` skeleton, project structure |
| TASK-2: Data loading and basic structure | `load_data` (+ tests), CSV validation, missing/malformed-file error handling |
| TASK-3: KPI cards implementation | `compute_total_sales`, `compute_total_orders` (+ tests), KPI rendering |
| TASK-4: Sales trend chart | `sales_by_month` (+ tests), trend chart rendering |
| TASK-5: Category and region breakdowns | `sales_by_category`, `sales_by_region` (+ tests), bar chart rendering |
| TASK-6: Testing and refinement | Full local run against PRD acceptance criteria; any fixes |
| TASK-7: Deployment to Streamlit Community Cloud | Developer-executed, final plan step, not part of this build |

The implementation plan's own step numbers (its "how") will each be tagged with the TASK-N they belong to, so the two numbering schemes stay distinct.

## Out of scope (per PRD Phase 2)

Authentication, real-time database integration, export, email alerts, filtering/date-range selection, drill-down, mobile-responsive design. None of these are touched by this design.

## Deployment note

The implementation plan's final step is deployment to Streamlit Community Cloud, explicitly marked as **developer-executed**: the plan builds everything up to a merge-ready feature branch, then stops and hands off. Deployment itself happens after merge, from `main`, run by the developer.
