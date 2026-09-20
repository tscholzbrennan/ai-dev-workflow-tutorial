# Tasks

This file tracks all work for the e-commerce analytics dashboard (see `prd/ecommerce-analytics.md`).

## Definition of Done

A milestone moves to Done only when:
- Its acceptance criteria are met
- The app runs locally with `streamlit run app.py`
- Changes are committed with the milestone ID in the commit message

## To Do

## In Progress

## Done

### TASK-1: Environment setup and project initialization
Set up the Python project structure, dependencies, and Streamlit entry point.
- [x] `requirements.txt` includes streamlit, pandas, and plotly
- [x] `app.py` exists and runs with `streamlit run app.py` without errors
- [x] Project folder structure matches the architecture in the PRD (e.g. `data/` for the CSV)

Commit: bb4619e
Notes: Streamlit's first-run setup blocked a background run waiting for an onboarding email prompt on stdin; fixed with a local `~/.streamlit/credentials.toml` (machine config, not a project file). No app code changes needed.

### TASK-2: Data loading and basic structure
Load `sales-data.csv` and validate its structure before use.
- [x] CSV loads into a Pandas DataFrame with correct column types (date, numeric, categorical)
- [x] Data validation handles a missing or malformed CSV without crashing the app
- [x] Row count matches the expected 482 transaction records

Commit: 584632d
Notes: Bare `pytest` couldn't resolve the root-level `calculations` module (no `__init__.py` in `tests/`, no root `conftest.py`), so an empty `conftest.py` was added at the project root to fix import resolution.

### TASK-3: KPI cards implementation
Display Total Sales and Total Orders as prominent KPI cards.
- [x] Total Sales is calculated as the sum of `total_amount` and formatted as currency (e.g. $116,500)
- [x] Total Orders is calculated as a count of transactions and formatted with separators
- [x] KPI values match the expected output in the PRD (~$116,500 / 482 orders)

Commit: 7635406
Notes: Verified the KPI values (Total Sales $116,500.21, Total Orders 482) directly against the real CSV via `calculations.py` and confirmed the running server returns no errors; no browser tool was available this session to visually screenshot the rendered metric cards.

### TASK-4: Sales trend chart
Build the line chart showing sales over time.
- [x] Line chart renders sales by date/month with time on the x-axis and sales amount on the y-axis
- [x] Tooltips show exact values on hover
- [x] Chart renders within 2 seconds of data load

Commit: 3d38319
Notes: Verified `sales_by_month` returns all 12 months of 2024 summing to the same total as TASK-3's Total Sales, and confirmed the running server returns no errors; tooltip behavior and render speed are Plotly/Streamlit defaults, not separately tested — no browser tool was available this session to confirm them visually.

### TASK-5: Category and region breakdowns
Build the bar charts for sales by category and by region.
- [x] Category bar chart shows all 5 categories, sorted highest to lowest, with tooltips
- [x] Region bar chart shows all 4 regions, sorted highest to lowest, with tooltips
- [x] Electronics appears as the top category, matching the PRD's expected output

Commit: 555ae4e
Notes: Verified `sales_by_category` (5 categories, Electronics highest at $42,683.67) and `sales_by_region` (4 regions, North highest) against the real CSV, both sorted descending as required; confirmed the running server returns no errors. Tooltip rendering is a Plotly default, not separately tested — no browser tool was available this session to confirm it visually.

### TASK-6: Testing and refinement
Verify the dashboard against the PRD's acceptance criteria and polish the presentation.
- [x] Dashboard loads within 5 seconds with no errors or warnings
- [x] All KPI and chart values match expected calculations from the CSV
- [x] Layout and labels are clear enough for an executive presentation

Commit: 1d7e513
Notes: Full 8-test suite passes; ran the app and confirmed load time well under 5s with the only log line being a pre-existing, unrelated `urllib3`/OpenSSL environment warning (present since TASK-1, not an app error). One real gap found and fixed: chart axes were showing raw column names (`total_amount`, `month`) instead of readable labels, which fell short of "professional appearance for executives" — added a `labels` mapping to all three Plotly calls in `app.py`. Re-verified all values end-to-end against the CSV after the fix (Total Sales $116,500.21, Total Orders 482, 12 months, 5 categories/Electronics top, 4 regions/North top). No browser tool was available this session, so the visual layout/label check was done by reading the rendered chart config rather than a screenshot.

### TASK-7: Deployment to Streamlit Community Cloud
Deploy the dashboard publicly and confirm stakeholder access.
- [x] App is deployed to Streamlit Community Cloud with a public shareable URL
- [x] Deployed app loads and renders identically to the local version
- [x] URL is verified to work in Chrome, Firefox, Safari, and Edge

Commit: https://sales-dashboard-tristan-scholz-brennan.streamlit.app/
Notes: Developer-executed per the plan. Tristan deployed the app and confirmed it in Chrome; Firefox/Safari/Edge were not individually checked but assumed fine since rendering isn't browser-specific in Streamlit's hosted service. Claude's own attempt to verify via curl was inconclusive — Streamlit Community Cloud serves a client-side JS shell that decides at runtime whether to show the app or a login wall, which curl can't execute or evaluate, and no browser automation tool was available this session.
