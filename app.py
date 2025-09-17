# app.py — HCD Interactive App (Schema‑Aware v3 for insurance.csv)
# Locked defaults + Insight Cards tailored to the classic insurance dataset
# Columns expected (if present): age, sex, bmi, children, smoker, region, charges

import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="HCD Interactive App", page_icon="✨", layout="wide")
st.title("✨ Exploring Human-Centered Design Through Interactive Apps")
st.write(
    "Upload a CSV and explore it with simple, opinionated controls. This build is tuned for "
    "the **insurance.csv** schema (bmi/charges/smoker/region), but still adapts to others."
)

# -------------------------
# Data loading
# -------------------------

st.header("1) Load your dataset")
st.caption("Upload any CSV. Categorical columns become filters; numeric columns power charts.")

uploaded = st.file_uploader("Upload a CSV file", type=["csv"], help="Headers required on the first row.")

@st.cache_data(show_spinner=False)
def load_csv(file_bytes: bytes | None) -> pd.DataFrame:
    if file_bytes:
        df = pd.read_csv(io.BytesIO(file_bytes))
    else:
        # Tiny fallback demo
        rng = np.random.default_rng(7)
        df = pd.DataFrame({
            "category": rng.choice(list("ABCDE"), 400),
            "city": rng.choice(["North","South","East","West"], 400),
            "value": rng.normal(100, 25, 400).round(1),
            "cost": rng.gamma(3, 50, 400).round(1)
        })
    # Gentle date parsing for any 'date' columns
    for c in df.columns:
        if "date" in c.lower():
            try:
                df[c] = pd.to_datetime(df[c])
            except Exception:
                pass
    return df

df = load_csv(uploaded.getvalue() if uploaded else None)

# Preview & schema
left, right = st.columns([2, 1])
with left:
    st.subheader("Preview")
    st.dataframe(df.head(50), use_container_width=True)
with right:
    st.subheader("Schema")
    st.write({"rows": int(len(df)), "columns": list(df.columns)})

# Identify types
num_cols = df.select_dtypes(include=["number"]).columns.tolist()
cat_cols = df.select_dtypes(include=["object","category","bool"]).columns.tolist()
maybe_date_cols = [c for c in df.columns if ("date" in c.lower()) or (np.issubdtype(df[c].dtype, np.datetime64))]

# -------------------------
# Interactive filters (locked sensible defaults for insurance.csv)
# -------------------------

st.header("2) Explore (filters)")
with st.container():
    st.markdown("Pick **one** category to filter and a **numeric** range to focus the view.")

    # Category column (default -> smoker, else region, else sex, else first categorical)
    cat_col_default_candidates = ["smoker", "region", "sex", "category", "city"]
    default_cat = next((c for c in cat_col_default_candidates if c in df.columns), None)

    if len(cat_cols) > 0:
        cat_choices = ["(none)"] + cat_cols
        cat_index = cat_choices.index(default_cat) if (default_cat in cat_cols) else 0
        cat_col = st.selectbox("Categorical column (optional)", cat_choices, index=cat_index)
        if cat_col == "(none)":
            cat_col = None
    else:
        cat_col = None

    # Category values default to ALL (clear mental model, no hidden filter)
    sel_categories = None
    if cat_col is not None:
        cat_values = sorted(pd.Series(df[cat_col].astype(str)).dropna().unique().tolist())
        sel_categories = st.multiselect("Values", cat_values, default=cat_values)

    # Numeric column (default -> charges, else bmi, else first numeric)
    num_default_candidates = ["charges", "bmi", "value", "cost"]
    default_num = next((c for c in num_default_candidates if c in df.columns and df[c].dtype.kind in "if"), None)

    if len(num_cols) > 0:
        num_choices = ["(none)"] + num_cols
        num_index = num_choices.index(default_num) if (default_num in num_cols) else 0
        chosen_num = st.selectbox("Numeric column (for range filter, optional)", num_choices, index=num_index)
        if chosen_num != "(none)":
            lo, hi = float(np.nanmin(df[chosen_num])), float(np.nanmax(df[chosen_num]))
            # Slightly trimmed range for nicer defaults if charges has big outliers
            if chosen_num == "charges":
                q5, q95 = np.nanpercentile(df[chosen_num], [5, 95])
                default_range = (float(q5), float(q95))
            else:
                default_range = (lo, hi)
            num_range = st.slider("Range", min_value=lo, max_value=hi, value=default_range)
        else:
            chosen_num, num_range = None, None
    else:
        chosen_num, num_range = None, None

# Apply filters
filt_df = df.copy()
if cat_col is not None and sel_categories is not None and len(sel_categories) > 0:
    filt_df = filt_df[filt_df[cat_col].astype(str).isin(sel_categories)]
if chosen_num is not None and num_range is not None:
    lo, hi = num_range
    filt_df = filt_df[(filt_df[chosen_num] >= lo) & (filt_df[chosen_num] <= hi)]

st.success(f"Filtered rows: {len(filt_df):,} (of {len(df):,})")

# -------------------------
# Visualizations (defaults tuned for insurance.csv)
# -------------------------

st.header("3) Visualize")
chart_type = st.radio(
    "Chart type",
    [
        "Scatter: X vs Y (default BMI vs Charges)",
        "Bar: aggregate by category",
        "Histogram: numeric distribution",
        "Box: numeric by category",
        "Line: time series (if date column)",
    ],
)

# Helper for aggregator
AGGS = {"sum": np.nansum, "mean": np.nanmean, "median": np.nanmedian, "count": lambda x: np.sum(pd.notna(x))}
has_date = len(maybe_date_cols) > 0

if chart_type.startswith("Scatter"):
    if len(num_cols) < 2:
        st.info("Need at least two numeric columns.")
    else:
        default_x = "bmi" if "bmi" in num_cols else num_cols[0]
        default_y = "charges" if "charges" in num_cols else (num_cols[1] if len(num_cols) > 1 else num_cols[0])
        xcol = st.selectbox("X (numeric)", num_cols, index=num_cols.index(default_x) if default_x in num_cols else 0)
        ycol = st.selectbox("Y (numeric)", num_cols, index=num_cols.index(default_y) if default_y in num_cols else (1 if len(num_cols)>1 else 0))
        color_by = st.selectbox("Color by (optional)", ["(none)"] + cat_cols, index=(cat_cols.index("smoker")+1) if "smoker" in cat_cols else 0)
        color_arg = None if color_by == "(none)" else color_by
        fig = px.scatter(
            filt_df, x=xcol, y=ycol, color=color_arg,
            hover_data=[c for c in df.columns if c not in [xcol, ycol]],
            title=f"{ycol} vs {xcol}"
        )
        st.plotly_chart(fig, use_container_width=True)

elif chart_type.startswith("Bar"):
    if len(cat_cols) == 0 or len(num_cols) == 0:
        st.info("Need at least one categorical and one numeric column.")
    else:
        bar_cat_default = "region" if "region" in cat_cols else (cat_cols[0])
        bar_val_default = "charges" if "charges" in num_cols else num_cols[0]
        bar_cat = st.selectbox("Group by (category)", cat_cols, index=cat_cols.index(bar_cat_default))
        bar_val = st.selectbox("Measure (numeric)", num_cols, index=num_cols.index(bar_val_default))
        agg_fn_name = st.selectbox("Aggregation", list(AGGS.keys()), index=1)  # mean
        g = filt_df.groupby(bar_cat, as_index=False)[bar_val].agg(AGGS[agg_fn_name])
        g = g.sort_values(bar_val, ascending=False)
        fig = px.bar(g, x=bar_cat, y=bar_val, title=f"{agg_fn_name.title()} of {bar_val} by {bar_cat}")
        st.plotly_chart(fig, use_container_width=True)

elif chart_type.startswith("Histogram"):
    if len(num_cols) == 0:
        st.info("Need at least one numeric column.")
    else:
        hist_default = "bmi" if "bmi" in num_cols else num_cols[0]
        hist_val = st.selectbox("Numeric column", num_cols, index=num_cols.index(hist_default))
        bins = st.slider("Bins", 5, 100, 30)
        fig = px.histogram(filt_df, x=hist_val, nbins=bins, title=f"Distribution of {hist_val}")
        st.plotly_chart(fig, use_container_width=True)

elif chart_type.startswith("Box"):
    if len(cat_cols) == 0 or len(num_cols) == 0:
        st.info("Need at least one categorical and one numeric column.")
    else:
        box_cat_default = "smoker" if "smoker" in cat_cols else cat_cols[0]
        box_val_default = "charges" if "charges" in num_cols else num_cols[0]
        box_cat = st.selectbox("Category", cat_cols, index=cat_cols.index(box_cat_default))
        box_val = st.selectbox("Numeric", num_cols, index=num_cols.index(box_val_default))
        fig = px.box(filt_df, x=box_cat, y=box_val, points="outliers", title=f"{box_val} by {box_cat}")
        st.plotly_chart(fig, use_container_width=True)

elif chart_type.startswith("Line"):
    if not len(maybe_date_cols) > 0:
        st.info("No date-like column detected. Add/rename a date column to use a time series chart.")
    else:
        dcol = st.selectbox("Date column", maybe_date_cols)
        ts_val = st.selectbox("Measure (numeric)", num_cols)
        fig = px.line(filt_df.sort_values(dcol), x=dcol, y=ts_val, title=f"{ts_val} over time")
        st.plotly_chart(fig, use_container_width=True)

# -------------------------
# Insight Cards (tailored to insurance.csv)
# -------------------------

st.header("4) Insight Cards")
colA, colB, colC = st.columns(3)

# Overall vs smoker segments (if available)
if "charges" in filt_df.columns and "smoker" in filt_df.columns:
    overall = float(np.nanmean(filt_df["charges"])) if len(filt_df) else np.nan
    smokers_mask = filt_df["smoker"].astype(str).str.lower() == "yes"
    nonsmokers_mask = filt_df["smoker"].astype(str).str.lower() == "no"
    smokers = float(np.nanmean(filt_df.loc[smokers_mask, "charges"])) if smokers_mask.any() else np.nan
    nonsmokers = float(np.nanmean(filt_df.loc[nonsmokers_mask, "charges"])) if nonsmokers_mask.any() else np.nan
    with colA:
        st.metric("Avg charges (all)", f"${overall:,.0f}")
    with colB:
        delta = (smokers - overall) if np.isfinite(smokers) and np.isfinite(overall) else 0
        st.metric("Avg charges (smokers)", f"${smokers:,.0f}", delta=f"{delta:,.0f} vs all")
    with colC:
        delta = (nonsmokers - overall) if np.isfinite(nonsmokers) and np.isfinite(overall) else 0
        st.metric("Avg charges (non-smokers)", f"${nonsmokers:,.0f}", delta=f"{delta:,.0f} vs all")
else:
    with colA:
        st.metric("Rows (filtered)", f"{len(filt_df):,}")
    with colB:
        st.metric("Numeric cols", str(len(num_cols)))
    with colC:
        st.metric("Categorical cols", str(len(cat_cols)))

# Secondary insights (BMI, region breakdown)
colD, colE = st.columns(2)
if "bmi" in filt_df.columns:
    bmi_median = float(np.nanmedian(filt_df["bmi"]))
    obese_rate = float(np.mean(filt_df["bmi"] >= 30) * 100)
    with colD:
        st.metric("Median BMI", f"{bmi_median:.1f}")
    with colE:
        st.metric("Obesity rate (BMI≥30)", f"{obese_rate:.1f}%")

if "region" in filt_df.columns and "charges" in filt_df.columns:
    g = filt_df.groupby("region", as_index=False)["charges"].mean().sort_values("charges", ascending=False)
    fig = px.bar(g, x="region", y="charges", title="Mean charges by region")
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Show descriptive statistics"):
    st.dataframe(filt_df.describe(include="all"), use_container_width=True)

# -------------------------
# Reflection template
# -------------------------

st.header("5) Reflection template (copy/paste)")
st.markdown(
    """
**How I used ChatGPT:**  
ChatGPT helped me with fine-tuning the schema‑aware Streamlit app, offering suggestions to help reduce unnecessary features, change the columns and visualizations, set sensible defaults for insurance.csv (BMI vs Charges, color by smoker), and suggested Insight Cards to surface key comparisons immediately. GPT also helped me generate this README.md

**Why these interactions are HCD‑friendly:**  
Fewer, clearer choices (one category + one numeric range) with meaningful defaults reduce cognitive load. Immediate feedback via metrics and charts supports quick iteration and exploration.
    """
)

st.divider()
with st.sidebar:
    st.header("Quick actions")
    if st.button("Reset app"):
        st.experimental_rerun()
    st.markdown(
        "**Run locally:**\n"
        "1) `pip install streamlit pandas plotly numpy`\n"
        "2) Save as `app.py`\n"
        "3) `streamlit run app.py`\n"
        "Then upload your CSV (e.g., insurance.csv) and explore."
    )
