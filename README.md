# corruption-data-visualization
Data Engineering, EDA, and Visualization of Corruption Cases from Special Court Database

## Task 4 Dashboard (Streamlit)

This repository includes a Streamlit app for Task 4 advanced visualization:

- Script: streamlit_app.py
- Primary input: data/task2_feature_engineered_dataset.csv
- Fallback inputs: other CSV files in data/

### Run

1. Install dependencies:
	pip install -r requirements.txt
2. Start dashboard:
	streamlit run streamlit_app.py

### Dashboard Features

- Interactive filters (date, category, pending status)
- KPI cards for operational monitoring
- Multi-layer trend visualization (monthly series + rolling mean)
- Faceted small-multiple trends by top categories
- Scenario-based comparison (pending vs non-pending)
- Correlation and anomaly-oriented views
- Ethics, bias, and limitations panel
