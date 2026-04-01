![Made with Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-red)

# corruption-data-visualization
Data Engineering, EDA, and Visualization of Corruption Cases from Nepal's Special Court Database

## Overview
This project performs end-to-end analysis of corruption case records from Nepal's Special Bench,
aligned with **SDG 16: Peace, Justice & Strong Institutions**. It covers data cleaning,
exploratory data analysis, and an interactive dashboard for judicial monitoring.

## Setup & Run

### 1. Install dependencies
pip install -r requirements.txt

### 2. Start dashboard
streamlit run nepal_justice_dashboard.py

## Dashboard Features
- Interactive filters (date range, case category, pending status, registration era)
- KPI cards for operational monitoring (resolution rate, avg duration, backlog count)
- Multi-layer trend visualization (monthly series + 3-month rolling mean)
- Faceted small-multiple trends by top case categories
- Scenario-based comparison (pending vs non-pending cases)
- Correlation and anomaly-oriented views
- Cohort survival analysis — resolution probability by registration year
- Ethics, bias, and limitations panel

## Project Structure
- `Task3_EDA.ipynb` — Exploratory Data Analysis (10 sections, 12+ chart types)
- `nepal_justice_dashboard.py` — Streamlit interactive dashboard
- `requirements.txt` — Python dependencies
- `cleaned_court_data.csv` — Cleaned dataset from Task 2

## Dataset
- **Source:** Nepal Supreme Court Special Bench — Case Records
- **Period:** 2007–2025
- **Size:** ~5,000+ judicial case records
- **SDG Alignment:** SDG 16.3, 16.6, 16.7, 16.10

## Key Findings
- 67% of Special Bench capacity is consumed by administrative petitions
- Judge rotation independently doubles average case duration
- Pre-2015 cases have <20% resolution probability ("zombie cases")
- COVID-19 selectively cleared simple cases while deferring complex ones
