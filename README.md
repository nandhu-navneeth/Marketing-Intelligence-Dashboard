# Marketing Intelligence Dashboard

Production-ready Streamlit BI dashboard to connect daily marketing activity (Facebook/Google/TikTok) to business outcomes (orders, revenue, profit) over time. Includes ingestion, validation, transformation, metrics, auto-insights, and a multi-page interactive UI with filters and drilldowns.

- Tech: Python 3.11, pandas, numpy, pydantic, plotly.express, streamlit, pytest, statsmodels (optional)
- Hosting: Streamlit Community Cloud (preferred) or Render
- Data: Expect CSVs in `data/` or upload a `.zip` in the app

## Repo Structure
```
marketing-intel-dashboard/
├─ app/
│  ├─ Home.py
│  ├─ 01_Overview.py
│  ├─ 02_Channel_Drilldown.py
│  ├─ 03_Campaigns.py
│  ├─ 04_Cohorts_and_Customers.py
│  ├─ 05_Profitability_and_COGS.py
│  ├─ 06_Notes_and_Assumptions.py
│  └─ components/
├─ src/
│  ├─ io_load.py
│  ├─ validate.py
│  ├─ transform.py
│  ├─ metrics.py
│  ├─ insights.py
│  ├─ viz.py
│  └─ config.py
├─ tests/
├─ data/
├─ .streamlit/config.toml
├─ requirements.txt
├─ README.md
├─ LICENSE
└─ .gitignore
```

## Data Contracts & Normalization
- Ad platform files: `date`, `tactic`, `state`, `campaign`, `impressions`, `clicks`, `spend`, `attributed_revenue`
- Business file: `date`, `orders`, `new_orders`, `new_customers`, `total_revenue`, `gross_profit`, `cogs`
- Column names are standardized to lowercase snake_case
- Per-platform tables gain a `channel` column in transforms

## Local Setup
1. Python 3.11
2. Install deps: `pip install -r requirements.txt`
3. Run tests: `pytest -q` (optional)
4. Launch app: `streamlit run app/Home.py`
5. Use provided sample CSVs in `data/` or upload a `.zip` containing the four CSVs.

## Streamlit Cloud Deployment
1. Push this repo to GitHub (public). License is MIT.
2. Go to https://streamlit.io → Deploy app → connect the repo → set entry point to `app/Home.py`.
3. Ensure `requirements.txt` is detected. Optional: include `data/` for demo, or rely on file upload.
4. Copy the URL and share.

Hosted link (to be added after deploy):
- https://streamlit.app/your-org/marketing-intel-dashboard (placeholder)

## Render (Alternative)
Provide a simple `render.yaml` service pointing to `streamlit run app/Home.py`. Make sure to set a persistent disk if you want to keep uploaded files (optional).

## Pages Overview
- Home: KPIs, core time series, channel mix, insights, validation warnings
- Overview: KPI cards, blended vs business outcomes
- Channel Drilldown: tactic treemap, campaign league table, spend vs ROAS scatter
- Campaigns: Pareto chart + exportable detail table
- Cohorts & Customers: new customers, new customer rate, AOV trend (proxy)
- Profitability & COGS: GM% vs COGS%, revenue vs gross profit
- Notes & Assumptions: data dictionary, metrics, quality flags, caveats

## Assumptions & Caveats
- `attributed_revenue` is platform-attributed and differs from `total_revenue` (GAAP). Use for ROAS and directional analysis.
- Date continuity checks report gaps but do not fail.
- Negative spend/impressions dropped. Rows with clicks>0 & impressions==0 are flagged.
- Cohort/retention views are proxies due to limited customer-level inputs.

## Tests
- Metrics functions: zero-division guards, expected outputs
- Transform: join integrity and column presence

## Screenshots
- Add screenshots after deployment if desired.

## License
MIT. See `LICENSE`.
