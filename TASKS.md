# Tasks

This file tracks all work for the e-commerce analytics dashboard (see `prd/ecommerce-analytics.md`).

## Definition of Done

A milestone moves to Done only when:
- Its acceptance criteria are met
- The app runs locally with `streamlit run app.py`
- Changes are committed with the milestone ID in the commit message

## To Do

### TASK-5: Category and region breakdowns
Build the bar charts for sales by category and by region.
- [ ] Category bar chart shows all 5 categories, sorted highest to lowest, with tooltips
- [ ] Region bar chart shows all 4 regions, sorted highest to lowest, with tooltips
- [ ] Electronics appears as the top category, matching the PRD's expected output

Commit:

### TASK-6: Testing and refinement
Verify the dashboard against the PRD's acceptance criteria and polish the presentation.
- [ ] Dashboard loads within 5 seconds with no errors or warnings
- [ ] All KPI and chart values match expected calculations from the CSV
- [ ] Layout and labels are clear enough for an executive presentation

Commit:

### TASK-7: Deployment to Streamlit Community Cloud
Deploy the dashboard publicly and confirm stakeholder access.
- [ ] App is deployed to Streamlit Community Cloud with a public shareable URL
- [ ] Deployed app loads and renders identically to the local version
- [ ] URL is verified to work in Chrome, Firefox, Safari, and Edge

Commit:

## In Progress

### TASK-4: Sales trend chart
Build the line chart showing sales over time.
- [ ] Line chart renders sales by date/month with time on the x-axis and sales amount on the y-axis
- [ ] Tooltips show exact values on hover
- [ ] Chart renders within 2 seconds of data load

Commit:

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
