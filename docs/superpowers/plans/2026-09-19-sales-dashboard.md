# Sales Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Phase 1 Streamlit sales dashboard from `prd/ecommerce-analytics.md` — KPI cards, a monthly sales trend chart, and category/region breakdowns — reading from `data/sales-data.csv`.

**Architecture:** A pure-pandas `calculations.py` module (no Streamlit dependency, fully covered by pytest) supplies data loading and aggregation functions; `app.py` imports from it and only handles Streamlit rendering (layout, formatting, Plotly charts). Each milestone in `TASKS.md` maps to one plan task below (tagged `[TASK-N]`); the plan's own "Task 1, Task 2, ..." numbering is separate from those milestone IDs.

**Tech Stack:** Python 3.11+, Streamlit, Pandas, Plotly (`plotly.express`), pytest.

**Spec:** `docs/superpowers/specs/2026-09-19-sales-dashboard-design.md`

## Global Constraints

- Work on the existing `feature/sales-dashboard` branch. Do not create a git worktree.
- Dependencies live in a plain `venv/` virtual environment with `requirements.txt` (no uv/conda). `venv/` is already covered by `.gitignore`.
- Activate the virtual environment before running any `pytest` or `streamlit` command: `source venv/bin/activate` (macOS/Linux) or `venv\Scripts\activate` (Windows).
- `calculations.py` must never import `streamlit` — it is tested with plain pytest, independent of the UI.
- Every commit message includes the milestone ID (`TASK-N`) it belongs to, per `TASKS.md`'s Definition of Done.
- Task 7 (deployment) is **developer-executed**. Do not run its steps automatically — stop after Task 6 and hand off.

---

### Task 1: Project scaffold [TASK-1: Environment setup and project initialization]

**Files:**
- Create: `requirements.txt`
- Create: `app.py`
- Create: `venv/` (via `python3 -m venv venv`; gitignored, not committed)

**Interfaces:**
- Consumes: nothing (first task)
- Produces: a running (empty) Streamlit page at `app.py`; an activated virtual environment with `streamlit`, `pandas`, `plotly`, and `pytest` installed, matching what every later task assumes is available

- [ ] **Step 1: Create `requirements.txt`**

```
streamlit
pandas
plotly
pytest
```

- [ ] **Step 2: Create the virtual environment and install dependencies**

Run:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Expected: install completes with no errors; `pip list` shows streamlit, pandas, plotly, pytest.

- [ ] **Step 3: Create the `app.py` skeleton**

```python
import streamlit as st

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")
```

- [ ] **Step 4: Run the app and confirm it starts without errors**

Run: `streamlit run app.py`
Expected: terminal prints a Local URL (e.g. `http://localhost:8501`); opening it shows a page titled "ShopSmart Sales Dashboard" with no error text. Stop the server (Ctrl+C) when confirmed.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt app.py
git commit -m "$(cat <<'EOF'
TASK-1: scaffold project, venv, and Streamlit entry point

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Data loading and validation [TASK-2: Data loading and basic structure]

**Files:**
- Create: `calculations.py`
- Create: `tests/test_calculations.py`
- Modify: `app.py`

**Interfaces:**
- Consumes: `data/sales-data.csv` (existing sample file, 482 rows, columns `date, order_id, product, category, region, quantity, unit_price, total_amount`)
- Produces: `load_data(path: str) -> pd.DataFrame` — raises `ValueError` on a missing file or a missing/unparseable required column. `app.py` holds a module-level `sales_df` loaded through it, with `st.stop()` called on failure. Later tasks' calculation functions take this `sales_df` as their input.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_calculations.py`:
```python
import pandas as pd
import pytest

from calculations import load_data


def test_load_data_raises_on_missing_file(tmp_path):
    missing_path = tmp_path / "does_not_exist.csv"
    with pytest.raises(ValueError, match="Could not find data file"):
        load_data(str(missing_path))


def test_load_data_raises_on_missing_column(tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text(
        "date,order_id,product,region,quantity,unit_price,total_amount\n"
        "2024-01-15,ORD-1,Widget,North,1,10.0,10.0\n"
    )
    with pytest.raises(ValueError, match="Missing required column"):
        load_data(str(csv_path))


def test_load_data_returns_dataframe_with_parsed_types(tmp_path):
    csv_path = tmp_path / "good.csv"
    csv_path.write_text(
        "date,order_id,product,category,region,quantity,unit_price,total_amount\n"
        "2024-01-15,ORD-1,Widget,Electronics,North,2,5.0,10.0\n"
    )
    df = load_data(str(csv_path))
    assert len(df) == 1
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert df.loc[0, "total_amount"] == 10.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_calculations.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'calculations'` (the module doesn't exist yet).

- [ ] **Step 3: Implement `calculations.py`**

```python
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = [
    "date", "order_id", "product", "category",
    "region", "quantity", "unit_price", "total_amount",
]

NUMERIC_COLUMNS = ["quantity", "unit_price", "total_amount"]


def load_data(path: str) -> pd.DataFrame:
    if not Path(path).exists():
        raise ValueError(f"Could not find data file: {path}")

    df = pd.read_csv(path)

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(missing)}")

    try:
        df["date"] = pd.to_datetime(df["date"])
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Could not parse 'date' column: {exc}") from exc

    for col in NUMERIC_COLUMNS:
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Could not parse '{col}' column as numeric: {exc}") from exc

    return df
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_calculations.py -v`
Expected: 3 passed.

- [ ] **Step 5: Wire `load_data` into `app.py` with error handling**

Update `app.py`:
```python
import streamlit as st

from calculations import load_data

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")

DATA_PATH = "data/sales-data.csv"

try:
    sales_df = load_data(DATA_PATH)
except ValueError as e:
    st.error(f"Could not load sales data: {e}")
    st.stop()
```

- [ ] **Step 6: Run the app to confirm it still loads cleanly**

Run: `streamlit run app.py`
Expected: page loads with no error banner (the real CSV is valid). Stop the server when confirmed.

- [ ] **Step 7: Commit**

```bash
git add calculations.py tests/test_calculations.py app.py
git commit -m "$(cat <<'EOF'
TASK-2: add load_data with validation and tests

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: KPI cards [TASK-3: KPI cards implementation]

**Files:**
- Modify: `calculations.py`
- Modify: `tests/test_calculations.py`
- Modify: `app.py`

**Interfaces:**
- Consumes: `sales_df` (from Task 2's `load_data`)
- Produces: `compute_total_sales(df: pd.DataFrame) -> float`, `compute_total_orders(df: pd.DataFrame) -> int`, rendered as two `st.metric` cards in `app.py`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_calculations.py` (this helper is reused by Tasks 4 and 5's tests too):
```python
from calculations import compute_total_orders, compute_total_sales


def _sample_df():
    return pd.DataFrame({
        "date": pd.to_datetime(["2024-01-15", "2024-01-20", "2024-02-05", "2024-02-10"]),
        "category": ["Electronics", "Audio", "Electronics", "Accessories"],
        "region": ["North", "South", "North", "West"],
        "total_amount": [100.0, 50.0, 200.0, 25.0],
    })


def test_compute_total_sales():
    df = _sample_df()
    assert compute_total_sales(df) == 375.0


def test_compute_total_orders():
    df = _sample_df()
    assert compute_total_orders(df) == 4
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_calculations.py -v`
Expected: FAIL with `ImportError: cannot import name 'compute_total_orders'` (functions don't exist yet).

- [ ] **Step 3: Implement the functions**

Add to `calculations.py`:
```python
def compute_total_sales(df: pd.DataFrame) -> float:
    return float(df["total_amount"].sum())


def compute_total_orders(df: pd.DataFrame) -> int:
    return len(df)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_calculations.py -v`
Expected: 5 passed.

- [ ] **Step 5: Render the KPI cards**

Update `app.py` (add after the `try/except` block):
```python
from calculations import compute_total_orders, compute_total_sales, load_data

# ... (existing load_data try/except block stays as-is)

total_sales = compute_total_sales(sales_df)
total_orders = compute_total_orders(sales_df)

col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${total_sales:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
```

- [ ] **Step 6: Run the app and confirm the KPI values**

Run: `streamlit run app.py`
Expected: two metric cards appear showing Total Sales near `$116,500` and Total Orders `482`, matching the PRD's Expected Output table. Stop the server when confirmed.

- [ ] **Step 7: Commit**

```bash
git add calculations.py tests/test_calculations.py app.py
git commit -m "$(cat <<'EOF'
TASK-3: add KPI calculations and render KPI cards

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Sales trend chart [TASK-4: Sales trend chart]

**Files:**
- Modify: `calculations.py`
- Modify: `tests/test_calculations.py`
- Modify: `app.py`

**Interfaces:**
- Consumes: `sales_df`, the `_sample_df()` test helper (from Task 3)
- Produces: `sales_by_month(df: pd.DataFrame) -> pd.DataFrame` with columns `["month", "total_amount"]`, sorted chronologically; rendered as a Plotly line chart in `app.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_calculations.py`:
```python
from calculations import sales_by_month


def test_sales_by_month():
    df = _sample_df()
    result = sales_by_month(df)
    assert list(result["month"]) == ["2024-01", "2024-02"]
    assert list(result["total_amount"]) == [150.0, 225.0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_calculations.py -v`
Expected: FAIL with `ImportError: cannot import name 'sales_by_month'`.

- [ ] **Step 3: Implement `sales_by_month`**

Add to `calculations.py`:
```python
def sales_by_month(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.assign(month=df["date"].dt.strftime("%Y-%m"))
        .groupby("month", as_index=False)["total_amount"]
        .sum()
        .sort_values("month")
        .reset_index(drop=True)
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_calculations.py -v`
Expected: 6 passed.

- [ ] **Step 5: Render the trend chart**

Update `app.py`:
```python
import plotly.express as px

from calculations import compute_total_orders, compute_total_sales, load_data, sales_by_month

# ... (existing KPI code stays as-is)

monthly_df = sales_by_month(sales_df)
fig_trend = px.line(
    monthly_df, x="month", y="total_amount",
    title="Sales Trend by Month", markers=True,
)
st.plotly_chart(fig_trend, use_container_width=True)
```

- [ ] **Step 6: Run the app and confirm the chart**

Run: `streamlit run app.py`
Expected: a line chart appears below the KPI cards with 12 monthly points; hovering a point shows its exact value. Stop the server when confirmed.

- [ ] **Step 7: Commit**

```bash
git add calculations.py tests/test_calculations.py app.py
git commit -m "$(cat <<'EOF'
TASK-4: add sales_by_month and render trend chart

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Category and region breakdowns [TASK-5: Category and region breakdowns]

**Files:**
- Modify: `calculations.py`
- Modify: `tests/test_calculations.py`
- Modify: `app.py`

**Interfaces:**
- Consumes: `sales_df`, the `_sample_df()` test helper (from Task 3)
- Produces: `sales_by_category(df: pd.DataFrame) -> pd.DataFrame` and `sales_by_region(df: pd.DataFrame) -> pd.DataFrame`, each with columns `["category"|"region", "total_amount"]` sorted descending by `total_amount`; rendered as two side-by-side Plotly bar charts in `app.py`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_calculations.py`:
```python
from calculations import sales_by_category, sales_by_region


def test_sales_by_category():
    df = _sample_df()
    result = sales_by_category(df)
    assert list(result["category"]) == ["Electronics", "Audio", "Accessories"]
    assert list(result["total_amount"]) == [300.0, 50.0, 25.0]


def test_sales_by_region():
    df = _sample_df()
    result = sales_by_region(df)
    assert list(result["region"]) == ["North", "South", "West"]
    assert list(result["total_amount"]) == [300.0, 50.0, 25.0]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_calculations.py -v`
Expected: FAIL with `ImportError: cannot import name 'sales_by_category'`.

- [ ] **Step 3: Implement the functions**

Add to `calculations.py`:
```python
def sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("category", as_index=False)["total_amount"]
        .sum()
        .sort_values("total_amount", ascending=False)
        .reset_index(drop=True)
    )


def sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("region", as_index=False)["total_amount"]
        .sum()
        .sort_values("total_amount", ascending=False)
        .reset_index(drop=True)
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_calculations.py -v`
Expected: 8 passed.

- [ ] **Step 5: Render the bar charts**

Update `app.py`:
```python
from calculations import (
    compute_total_orders,
    compute_total_sales,
    load_data,
    sales_by_category,
    sales_by_month,
    sales_by_region,
)

# ... (existing trend chart code stays as-is)

category_df = sales_by_category(sales_df)
region_df = sales_by_region(sales_df)

col3, col4 = st.columns(2)
fig_category = px.bar(category_df, x="category", y="total_amount", title="Sales by Category")
col3.plotly_chart(fig_category, use_container_width=True)

fig_region = px.bar(region_df, x="region", y="total_amount", title="Sales by Region")
col4.plotly_chart(fig_region, use_container_width=True)
```

- [ ] **Step 6: Run the app and confirm both charts**

Run: `streamlit run app.py`
Expected: two bar charts appear side by side below the trend chart. Category chart's tallest bar is Electronics; both charts are sorted highest to lowest with hover tooltips. Stop the server when confirmed.

- [ ] **Step 7: Commit**

```bash
git add calculations.py tests/test_calculations.py app.py
git commit -m "$(cat <<'EOF'
TASK-5: add category/region breakdowns and render bar charts

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Testing and refinement [TASK-6: Testing and refinement]

**Files:**
- Modify: any of `app.py` / `calculations.py` (only if a check below fails)

**Interfaces:**
- Consumes: the complete dashboard from Tasks 1–5
- Produces: a dashboard verified against every PRD acceptance criterion, with the full test suite passing

- [ ] **Step 1: Run the full test suite**

Run: `pytest -v`
Expected: all 8 tests pass (3 from Task 2, 2 from Task 3, 1 from Task 4, 2 from Task 5).

- [ ] **Step 2: Run the app and check it against the PRD's Acceptance Criteria section**

Run: `streamlit run app.py`, then open the Local URL and check each item from `prd/ecommerce-analytics.md`'s Acceptance Criteria section by eye:
- KPIs visible: Total Sales (~$116,500) and Total Orders (482) displayed prominently
- Trend chart works: line chart shows sales over time, values match the data
- Category chart works: bars sorted highest to lowest, all 5 categories present, Electronics on top
- Region chart works: bars sorted highest to lowest, all 4 regions present
- Data loads correctly: no mismatched or missing values
- No errors: no error banners or console warnings on load
- Professional appearance: readable labels, no layout overlap, suitable for an executive audience

- [ ] **Step 3: Fix anything that fails the checklist**

If a check in Step 2 fails, make the minimal fix in `app.py` or `calculations.py`, re-run `pytest -v` to confirm nothing broke, and re-check the specific failed item in the browser. Repeat until every item passes. (No code is prescribed here since the fix depends on what, if anything, fails.)

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "$(cat <<'EOF'
TASK-6: verify dashboard against PRD acceptance criteria

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```
(If Step 3 required no changes, skip this commit — there's nothing to save.)

---

### Task 7: Deploy to Streamlit Community Cloud [TASK-7: Deployment to Streamlit Community Cloud] — DEVELOPER-EXECUTED

**This task is not run by the agent.** Stop here after Task 6 and hand off. The developer runs this task themselves, from `main`, after reviewing and merging `feature/sales-dashboard`.

**Files:** none touched by an agent in this task.

- [ ] **Step 1 (developer):** Merge `feature/sales-dashboard` into `main` and push `main` to GitHub.
- [ ] **Step 2 (developer):** Sign in to Streamlit Community Cloud, create a new app pointing at the GitHub repo, `main` branch, `app.py` as the entry point.
- [ ] **Step 3 (developer):** Deploy and wait for the build to finish.
- [ ] **Step 4 (developer):** Open the public URL and confirm the dashboard renders identically to the local version.
- [ ] **Step 5 (developer):** Verify the URL in Chrome, Firefox, Safari, and Edge.
- [ ] **Step 6 (developer):** Check TASK-7's acceptance criteria in `TASKS.md`, record the deployment on its Commit line (or a Notes line with the public URL), and move it to Done.
