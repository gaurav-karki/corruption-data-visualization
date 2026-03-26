from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Corruption Case Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    base = Path(__file__).resolve().parent
    candidates = [
        base / "data" / "task2_feature_engineered_dataset.csv",
        base / "data" / "task2_cleaned_dataset.csv",
        base / "data" / "final_dataset_for_visualization_enhanced.csv",
        base / "data" / "data-1774253631395.csv",
    ]

    for path in candidates:
        if path.exists():
            df = pd.read_csv(path)
            df.attrs["source_path"] = str(path)
            return df

    raise FileNotFoundError("No supported dataset found in ./data")


def pick_col(df: pd.DataFrame, options: list[str]) -> str | None:
    for name in options:
        if name in df.columns:
            return name
    return None


def prep_data(df: pd.DataFrame) -> dict[str, str | None]:
    date_col = pick_col(df, ["registration_date_ad", "first_hearing_date", "last_hearing_date"])
    cat_col = pick_col(df, ["category", "case_type", "common_decision_type"])
    duration_col = pick_col(df, ["duration_days", "case_duration_days", "hearing_span_days"])
    hearings_col = pick_col(df, ["total_hearings", "distinct_judges", "distinct_lawyers"])
    status_col = pick_col(df, ["verdict_status", "case_status", "hearing_case_status"])

    if date_col is not None:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    for col in [duration_col, hearings_col]:
        if col is not None:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if status_col is not None:
        df[status_col] = df[status_col].astype(str).str.strip().str.lower()

    return {
        "date_col": date_col,
        "cat_col": cat_col,
        "duration_col": duration_col,
        "hearings_col": hearings_col,
        "status_col": status_col,
    }


def draw_header(source: str) -> None:
    st.title("Corruption Case Intelligence Dashboard")
    st.caption(
        "Task 4: Advanced Visualization and Insight. "
        f"Data source: {source}"
    )


# Multi-layer visualization: observed trend + rolling baseline.
def render_trend(df: pd.DataFrame, date_col: str) -> None:
    trend = (
        df.dropna(subset=[date_col])
        .set_index(date_col)
        .resample("M")
        .size()
        .rename("case_count")
        .reset_index()
    )
    trend["rolling_3m"] = trend["case_count"].rolling(3, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=trend[date_col],
            y=trend["case_count"],
            mode="lines+markers",
            name="Monthly Cases",
            line=dict(color="#0077B6", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=trend[date_col],
            y=trend["rolling_3m"],
            mode="lines",
            name="3-Month Rolling Mean",
            line=dict(color="#F4A261", width=3, dash="dot"),
        )
    )
    fig.update_layout(
        title="Monthly Case Inflow with Rolling Baseline",
        xaxis_title="Month",
        yaxis_title="Case Count",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_facets(df: pd.DataFrame, date_col: str, cat_col: str) -> None:
    top_categories = (
        df[cat_col].astype(str).value_counts().head(4).index
        if cat_col in df.columns
        else []
    )
    facet_df = df[df[cat_col].astype(str).isin(top_categories)].copy()
    facet_df["month"] = pd.to_datetime(facet_df[date_col], errors="coerce").dt.to_period("M").dt.to_timestamp()

    grouped = (
        facet_df.dropna(subset=["month"])
        .groupby(["month", cat_col], as_index=False)
        .size()
        .rename(columns={"size": "case_count"})
    )

    fig = px.line(
        grouped,
        x="month",
        y="case_count",
        color=cat_col,
        facet_col=cat_col,
        facet_col_wrap=2,
        markers=True,
        title="Faceted Monthly Trends by Top Categories",
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=60, b=20))
    st.plotly_chart(fig, use_container_width=True)


def render_scatter(df: pd.DataFrame, x_col: str, y_col: str, cat_col: str | None) -> None:
    cols = [x_col, y_col] + ([cat_col] if cat_col else [])
    plot_df = df[cols].dropna().copy()

    if len(plot_df) == 0:
        st.info("Not enough data for scatter plot.")
        return

    fig = px.scatter(
        plot_df,
        x=x_col,
        y=y_col,
        color=cat_col if cat_col else None,
        opacity=0.7,
        title="Process Load vs Duration",
        labels={x_col: "Hearing/Load Proxy", y_col: "Duration (days)"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_box(df: pd.DataFrame, y_col: str, cat_col: str | None) -> None:
    if cat_col is None:
        st.info("No category column available for boxplot.")
        return

    top_cats = df[cat_col].astype(str).value_counts().head(10).index
    plot_df = df[df[cat_col].astype(str).isin(top_cats)].copy()

    fig = px.box(
        plot_df,
        x=cat_col,
        y=y_col,
        color=cat_col,
        title="Duration Distribution Across Top Categories",
        points="outliers",
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def render_heatmap(df: pd.DataFrame) -> None:
    num_df = df.select_dtypes(include=[np.number])
    if num_df.shape[1] < 2:
        st.info("Not enough numeric features for correlation heatmap.")
        return

    corr = num_df.corr(numeric_only=True).round(2)
    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Numeric Correlation Heatmap",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_scenario(df: pd.DataFrame, status_col: str | None, duration_col: str, hearings_col: str | None) -> None:
    if status_col is None:
        st.info("No status column available for scenario comparison.")
        return

    work = df.copy()
    work["scenario"] = np.where(work[status_col].str.contains("pending|चलिरहेको", na=False), "Pending", "Non-Pending")

    agg = {
        duration_col: "median",
    }
    if hearings_col:
        agg[hearings_col] = "mean"

    summary = work.groupby("scenario", as_index=False).agg(agg)

    left, right = st.columns(2)
    with left:
        fig_d = px.bar(
            summary,
            x="scenario",
            y=duration_col,
            color="scenario",
            title="Scenario Comparison: Median Duration",
        )
        fig_d.update_layout(showlegend=False)
        st.plotly_chart(fig_d, use_container_width=True)

    if hearings_col:
        with right:
            fig_h = px.bar(
                summary,
                x="scenario",
                y=hearings_col,
                color="scenario",
                title="Scenario Comparison: Average Hearings",
            )
            fig_h.update_layout(showlegend=False)
            st.plotly_chart(fig_h, use_container_width=True)


def render_kpis(df: pd.DataFrame, duration_col: str | None, hearings_col: str | None) -> None:
    total_cases = int(len(df))

    duration_median = float(df[duration_col].median()) if duration_col else float("nan")
    hearings_mean = float(df[hearings_col].mean()) if hearings_col else float("nan")

    outlier_share = np.nan
    if duration_col:
        q1 = df[duration_col].quantile(0.25)
        q3 = df[duration_col].quantile(0.75)
        iqr = q3 - q1
        upper = q3 + 1.5 * iqr
        outlier_share = (df[duration_col] > upper).mean() * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cases", f"{total_cases:,}")
    c2.metric("Median Duration (days)", "N/A" if np.isnan(duration_median) else f"{duration_median:.1f}")
    c3.metric("Avg Hearings", "N/A" if np.isnan(hearings_mean) else f"{hearings_mean:.2f}")
    c4.metric("Long-Tail Outliers", "N/A" if np.isnan(outlier_share) else f"{outlier_share:.2f}%")


def main() -> None:
    df = load_data()
    source = df.attrs.get("source_path", "unknown")
    cols = prep_data(df)

    draw_header(source)

    if cols["date_col"] is None or cols["duration_col"] is None:
        st.error("Missing required columns for dashboard. Need date + duration columns.")
        st.dataframe(df.head())
        st.stop()

    with st.sidebar:
        st.header("Filters")
        date_col = cols["date_col"]
        cat_col = cols["cat_col"]
        status_col = cols["status_col"]

        min_date = pd.to_datetime(df[date_col], errors="coerce").min()
        max_date = pd.to_datetime(df[date_col], errors="coerce").max()
        if pd.notna(min_date) and pd.notna(max_date):
            start_date, end_date = st.date_input(
                "Date Range",
                value=(min_date.date(), max_date.date()),
            )
            df = df[(df[date_col] >= pd.to_datetime(start_date)) & (df[date_col] <= pd.to_datetime(end_date))]

        if cat_col is not None:
            categories = sorted(df[cat_col].astype(str).dropna().unique().tolist())
            selected = st.multiselect("Categories", options=categories, default=categories[: min(8, len(categories))])
            if selected:
                df = df[df[cat_col].astype(str).isin(selected)]

        if status_col is not None:
            pending_only = st.checkbox("Pending cases only", value=False)
            if pending_only:
                df = df[df[status_col].str.contains("pending|चलिरहेको", na=False)]

    st.subheader("Executive KPIs")
    render_kpis(df, cols["duration_col"], cols["hearings_col"])

    st.subheader("Advanced Visual Analysis")
    render_trend(df, cols["date_col"])

    if cols["cat_col"]:
        render_facets(df, cols["date_col"], cols["cat_col"])

    left, right = st.columns(2)
    with left:
        render_scatter(df, cols["hearings_col"] or cols["duration_col"], cols["duration_col"], cols["cat_col"])
    with right:
        render_box(df, cols["duration_col"], cols["cat_col"])

    render_heatmap(df)
    render_scenario(df, cols["status_col"], cols["duration_col"], cols["hearings_col"])

    with st.expander("Ethics, Bias, and Limitations"):
        st.markdown(
            "- This dashboard reflects recorded judicial/administrative events and may under-represent unreported corruption contexts.\n"
            "- Category and status coding can introduce institutional bias when comparing groups.\n"
            "- Visual relationships are associative, not causal; policy decisions should combine this evidence with domain validation."
        )


if __name__ == "__main__":
    main()
