"""
app.py
------
Streamlit frontend for Online Food Delivery Dataset Analysis.
Run with:  streamlit run food_delivery_analysis/app.py
"""

import os
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# ── Path resolution so the module can be run from any CWD ────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data_loader import (
    INCOME_ORDER,
    EDU_ORDER,
    load_data,
    pct_series,
    crosstab_pct,
    summary_stats,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🍔 Food Delivery Analytics",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Colour palette ────────────────────────────────────────────────────────────
PALETTE = px.colors.qualitative.Set2
PALETTE_CONT = px.colors.sequential.Teal
ACCENT = "#2563EB"

# ══════════════════════════════════════════════════════════════════════════════
# Helper utilities
# ══════════════════════════════════════════════════════════════════════════════

def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"


def kpi_card(col, label: str, value, sub: str = "", delta: str = ""):
    with col:
        st.metric(label=label, value=value, delta=delta if delta else None)
        if sub:
            st.caption(sub)


def section_header(title: str, icon: str = ""):
    st.markdown(f"### {icon} {title}" if icon else f"### {title}")
    st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# Data loading (cached)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="Loading & cleaning dataset …")
def get_data(filepath: str) -> pd.DataFrame:
    return load_data(filepath)


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar(df: pd.DataFrame):
    st.sidebar.image(
        "https://img.icons8.com/color/96/food-delivery.png", width=64
    )
    st.sidebar.title("Food Delivery Analytics")
    st.sidebar.markdown("**Dataset:** Online Food Delivery Survey")
    st.sidebar.divider()

    st.sidebar.subheader("🔍 Filters")

    genders = ["All"] + sorted(df["Gender"].dropna().unique().tolist())
    sel_gender = st.sidebar.selectbox("Gender", genders)

    occupations = ["All"] + sorted(df["Occupation"].dropna().unique().tolist())
    sel_occ = st.sidebar.selectbox("Occupation", occupations)

    incomes = ["All"] + [i for i in INCOME_ORDER if i in df["Monthly Income"].cat.categories]
    sel_income = st.sidebar.selectbox("Monthly Income", incomes)

    marital = ["All"] + sorted(df["Marital Status"].dropna().unique().tolist())
    sel_marital = st.sidebar.selectbox("Marital Status", marital)

    age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
    sel_age = st.sidebar.slider("Age Range", age_min, age_max, (age_min, age_max))

    st.sidebar.divider()
    st.sidebar.caption("IBM Bob Internship Project · Data Analytics")

    # Apply filters
    fdf = df.copy()
    if sel_gender != "All":
        fdf = fdf[fdf["Gender"] == sel_gender]
    if sel_occ != "All":
        fdf = fdf[fdf["Occupation"] == sel_occ]
    if sel_income != "All":
        fdf = fdf[fdf["Monthly Income"] == sel_income]
    if sel_marital != "All":
        fdf = fdf[fdf["Marital Status"] == sel_marital]
    fdf = fdf[(fdf["Age"] >= sel_age[0]) & (fdf["Age"] <= sel_age[1])]

    return fdf


# ══════════════════════════════════════════════════════════════════════════════
# Tab 1 – Overview / KPIs
# ══════════════════════════════════════════════════════════════════════════════

def tab_overview(df: pd.DataFrame, raw_df: pd.DataFrame):
    section_header("Dashboard Overview", "📊")

    stats = summary_stats(df)

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card(c1, "Total Customers", stats["total_customers"])
    kpi_card(c2, "Order Online", f"{stats['order_online_pct']}%",
             sub=f"{stats['order_online_count']} customers")
    kpi_card(c3, "Positive Feedback", f"{stats['positive_feedback_pct']}%",
             sub=f"{stats['positive_feedback_count']} customers")
    kpi_card(c4, "Average Age", stats["avg_age"])
    kpi_card(c5, "Avg Family Size", stats["avg_family_size"])

    st.divider()

    col_left, col_right = st.columns(2)

    # ── Online ordering donut ──────────────────────────────────────────────
    with col_left:
        st.subheader("Online Ordering Rate")
        order_counts = df["Output"].value_counts().reset_index()
        order_counts.columns = ["Orders Online", "Count"]
        fig = px.pie(
            order_counts, names="Orders Online", values="Count",
            hole=0.55, color_discrete_sequence=[PALETTE[0], PALETTE[1]],
        )
        fig.update_traces(textinfo="percent+label", pull=[0.04, 0])
        fig.update_layout(margin=dict(t=10, b=10), legend=dict(orientation="h"))
        st.plotly_chart(fig, use_container_width=True)

    # ── Feedback donut ──────────────────────────────────────────────────────
    with col_right:
        st.subheader("Customer Feedback Distribution")
        fb_counts = df["Feedback"].value_counts().reset_index()
        fb_counts.columns = ["Feedback", "Count"]
        fig2 = px.pie(
            fb_counts, names="Feedback", values="Count",
            hole=0.55, color_discrete_sequence=[PALETTE[2], PALETTE[3]],
        )
        fig2.update_traces(textinfo="percent+label", pull=[0.04, 0])
        fig2.update_layout(margin=dict(t=10, b=10), legend=dict(orientation="h"))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Data quality report ────────────────────────────────────────────────
    with st.expander("🔧 Data Quality Report", expanded=False):
        q1, q2, q3, q4 = st.columns(4)
        q1.metric("Raw Rows", len(raw_df))
        q2.metric("Duplicates Removed", raw_df.attrs.get("duplicates_removed", 0))
        q3.metric("Clean Rows", len(df))
        q4.metric("Columns", len(df.columns))

        st.markdown("**Missing values after cleaning:**")
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if missing.empty:
            st.success("✅ No missing values in any column.")
        else:
            st.dataframe(missing.rename("Missing Count"), use_container_width=True)

    # ── Raw data preview ────────────────────────────────────────────────────
    with st.expander("📋 Preview Clean Dataset", expanded=False):
        st.dataframe(df.head(50), use_container_width=True, height=350)


# ══════════════════════════════════════════════════════════════════════════════
# Tab 2 – Customer Demographics
# ══════════════════════════════════════════════════════════════════════════════

def tab_demographics(df: pd.DataFrame):
    section_header("Customer Demographics", "👥")

    col1, col2 = st.columns(2)

    # ── Gender distribution ────────────────────────────────────────────────
    with col1:
        st.subheader("Gender Distribution")
        gen_df = pct_series(df["Gender"])
        fig = px.bar(
            gen_df, x="Gender", y="Count",
            text="Percentage (%)",
            color="Gender", color_discrete_sequence=PALETTE,
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(showlegend=False, yaxis_title="Count",
                          margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # ── Marital status ─────────────────────────────────────────────────────
    with col2:
        st.subheader("Marital Status")
        ms_df = pct_series(df["Marital Status"])
        fig2 = px.pie(
            ms_df, names="Marital Status", values="Count",
            color_discrete_sequence=PALETTE,
        )
        fig2.update_traces(textinfo="percent+label")
        fig2.update_layout(margin=dict(t=20, b=10))
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    col3, col4 = st.columns(2)

    # ── Age distribution ───────────────────────────────────────────────────
    with col3:
        st.subheader("Age Distribution")
        fig3 = px.histogram(
            df, x="Age", nbins=20,
            color_discrete_sequence=[ACCENT],
            opacity=0.85,
        )
        fig3.update_layout(bargap=0.05, yaxis_title="Count",
                           xaxis_title="Age", margin=dict(t=20))
        st.plotly_chart(fig3, use_container_width=True)

    # ── Age group bar ──────────────────────────────────────────────────────
    with col4:
        st.subheader("Customers by Age Group")
        ag_df = df["Age Group"].value_counts().sort_index().reset_index()
        ag_df.columns = ["Age Group", "Count"]
        ag_df["Pct"] = (ag_df["Count"] / ag_df["Count"].sum() * 100).round(1)
        fig4 = px.bar(
            ag_df, x="Age Group", y="Count",
            text="Pct",
            color="Age Group", color_discrete_sequence=PALETTE,
        )
        fig4.update_traces(texttemplate="%{text}%", textposition="outside")
        fig4.update_layout(showlegend=False, margin=dict(t=20))
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    col5, col6 = st.columns(2)

    # ── Occupation ─────────────────────────────────────────────────────────
    with col5:
        st.subheader("Occupation Breakdown")
        occ_df = df["Occupation"].value_counts().reset_index()
        occ_df.columns = ["Occupation", "Count"]
        occ_df["Pct"] = (occ_df["Count"] / occ_df["Count"].sum() * 100).round(1)
        fig5 = px.bar(
            occ_df.sort_values("Count"), x="Count", y="Occupation",
            orientation="h", text="Pct",
            color="Count", color_continuous_scale=PALETTE_CONT,
        )
        fig5.update_traces(texttemplate="%{text}%", textposition="outside")
        fig5.update_layout(coloraxis_showscale=False, margin=dict(t=20),
                           yaxis_title="", xaxis_title="Count")
        st.plotly_chart(fig5, use_container_width=True)

    # ── Education ──────────────────────────────────────────────────────────
    with col6:
        st.subheader("Educational Qualifications")
        edu_order = [e for e in EDU_ORDER if e in df["Educational Qualifications"].cat.categories]
        edu_df = (
            df["Educational Qualifications"]
            .value_counts()
            .reindex(edu_order)
            .reset_index()
        )
        edu_df.columns = ["Education", "Count"]
        edu_df["Pct"] = (edu_df["Count"] / edu_df["Count"].sum() * 100).round(1)
        fig6 = px.bar(
            edu_df, x="Education", y="Count",
            text="Pct",
            color="Education", color_discrete_sequence=PALETTE,
        )
        fig6.update_traces(texttemplate="%{text}%", textposition="outside")
        fig6.update_layout(showlegend=False, margin=dict(t=20),
                           xaxis_title="Education Level")
        st.plotly_chart(fig6, use_container_width=True)

    st.divider()
    col7, col8 = st.columns(2)

    # ── Income distribution ────────────────────────────────────────────────
    with col7:
        st.subheader("Monthly Income Distribution")
        inc_order = [i for i in INCOME_ORDER if i in df["Monthly Income"].cat.categories]
        inc_df = (
            df["Monthly Income"]
            .value_counts()
            .reindex(inc_order)
            .reset_index()
        )
        inc_df.columns = ["Income Bracket", "Count"]
        inc_df["Pct"] = (inc_df["Count"] / inc_df["Count"].sum() * 100).round(1)
        fig7 = px.funnel(
            inc_df, x="Count", y="Income Bracket",
            color_discrete_sequence=[ACCENT],
        )
        fig7.update_layout(margin=dict(t=20), yaxis_title="")
        st.plotly_chart(fig7, use_container_width=True)

    # ── Family size ────────────────────────────────────────────────────────
    with col8:
        st.subheader("Family Size Distribution")
        fs_df = df["Family size"].value_counts().sort_index().reset_index()
        fs_df.columns = ["Family Size", "Count"]
        fs_df["Pct"] = (fs_df["Count"] / fs_df["Count"].sum() * 100).round(1)
        fig8 = px.bar(
            fs_df, x="Family Size", y="Count",
            text="Pct",
            color="Family Size", color_continuous_scale=PALETTE_CONT,
        )
        fig8.update_traces(texttemplate="%{text}%", textposition="outside")
        fig8.update_layout(coloraxis_showscale=False, margin=dict(t=20),
                           xaxis_title="Family Size (members)")
        st.plotly_chart(fig8, use_container_width=True)

    # ── Summary table ──────────────────────────────────────────────────────
    with st.expander("📊 Full Demographic Summary Table"):
        demo_summary = pd.DataFrame({
            "Metric": ["Average Age", "Most Common Age Group", "Most Common Gender",
                       "Most Common Marital Status", "Most Common Occupation",
                       "Most Common Income", "Most Common Education",
                       "Average Family Size"],
            "Value": [
                f"{df['Age'].mean():.1f} yrs",
                str(df["Age Group"].mode()[0]),
                str(df["Gender"].mode()[0]),
                str(df["Marital Status"].mode()[0]),
                str(df["Occupation"].mode()[0]),
                str(df["Monthly Income"].mode()[0]),
                str(df["Educational Qualifications"].mode()[0]),
                f"{df['Family size'].mean():.1f}",
            ],
        })
        st.dataframe(demo_summary, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# Tab 3 – Ordering Behaviour
# ══════════════════════════════════════════════════════════════════════════════

def tab_ordering(df: pd.DataFrame):
    section_header("Online Ordering Behaviour", "🛒")

    col1, col2 = st.columns(2)

    # ── Customer type ──────────────────────────────────────────────────────
    with col1:
        st.subheader("Customer Type")
        ct_df = pct_series(df["Customer Type"])
        fig = px.pie(
            ct_df, names="Customer Type", values="Count",
            color_discrete_sequence=PALETTE,
        )
        fig.update_traces(textinfo="percent+label", pull=[0.04] + [0] * 10)
        fig.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # ── Ordering rate by gender ────────────────────────────────────────────
    with col2:
        st.subheader("Ordering Rate by Gender")
        ct_gender = pd.crosstab(df["Gender"], df["Output"], normalize="index").mul(100).round(1)
        ct_gender = ct_gender.reset_index()
        fig2 = px.bar(
            ct_gender, x="Gender", y=["Yes", "No"] if "No" in ct_gender.columns else ["Yes"],
            barmode="stack",
            color_discrete_map={"Yes": PALETTE[0], "No": PALETTE[3]},
            labels={"value": "Percentage (%)", "variable": "Orders Online"},
        )
        fig2.update_layout(legend_title="Orders Online", margin=dict(t=20))
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    col3, col4 = st.columns(2)

    # ── Ordering rate by occupation ────────────────────────────────────────
    with col3:
        st.subheader("Ordering Rate by Occupation")
        occ_order = (
            df.groupby("Occupation")["Orders Online"]
            .mean()
            .mul(100)
            .round(1)
            .sort_values(ascending=True)
            .reset_index()
        )
        occ_order.columns = ["Occupation", "% Order Online"]
        fig3 = px.bar(
            occ_order, x="% Order Online", y="Occupation",
            orientation="h", text="% Order Online",
            color="% Order Online", color_continuous_scale=PALETTE_CONT,
        )
        fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig3.update_layout(coloraxis_showscale=False, xaxis_range=[0, 110],
                           margin=dict(t=20), yaxis_title="")
        st.plotly_chart(fig3, use_container_width=True)

    # ── Ordering rate by income ────────────────────────────────────────────
    with col4:
        st.subheader("Ordering Rate by Income Bracket")
        inc_order = [i for i in INCOME_ORDER if i in df["Monthly Income"].cat.categories]
        inc_rate = (
            df.groupby("Monthly Income", observed=True)["Orders Online"]
            .mean()
            .mul(100)
            .round(1)
            .reindex(inc_order)
            .reset_index()
        )
        inc_rate.columns = ["Monthly Income", "% Order Online"]
        fig4 = px.line(
            inc_rate, x="Monthly Income", y="% Order Online",
            markers=True, text="% Order Online",
            color_discrete_sequence=[ACCENT],
        )
        fig4.update_traces(texttemplate="%{text:.1f}%", textposition="top center",
                           line_width=3, marker_size=10)
        fig4.update_layout(yaxis_range=[0, 110], margin=dict(t=20))
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    col5, col6 = st.columns(2)

    # ── Customer type by age group ─────────────────────────────────────────
    with col5:
        st.subheader("Customer Type by Age Group")
        ct_age = pd.crosstab(df["Age Group"], df["Customer Type"])
        ct_age_pct = ct_age.div(ct_age.sum(axis=1), axis=0).mul(100).round(1)
        fig5 = px.bar(
            ct_age_pct.reset_index(), x="Age Group",
            y=ct_age_pct.columns.tolist(),
            barmode="stack",
            color_discrete_sequence=PALETTE,
            labels={"value": "Percentage (%)", "variable": "Customer Type"},
        )
        fig5.update_layout(legend_title="Customer Type", margin=dict(t=20))
        st.plotly_chart(fig5, use_container_width=True)

    # ── Ordering by education ──────────────────────────────────────────────
    with col6:
        st.subheader("Online Ordering Rate by Education")
        edu_order = [e for e in EDU_ORDER if e in df["Educational Qualifications"].cat.categories]
        edu_rate = (
            df.groupby("Educational Qualifications", observed=True)["Orders Online"]
            .mean()
            .mul(100)
            .round(1)
            .reindex(edu_order)
            .reset_index()
        )
        edu_rate.columns = ["Education", "% Order Online"]
        fig6 = px.bar(
            edu_rate, x="Education", y="% Order Online",
            text="% Order Online",
            color="% Order Online", color_continuous_scale=PALETTE_CONT,
        )
        fig6.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig6.update_layout(coloraxis_showscale=False, yaxis_range=[0, 110],
                           margin=dict(t=20), xaxis_title="Education Level")
        st.plotly_chart(fig6, use_container_width=True)

    st.divider()

    # ── Heatmap: Income vs Marital Status ordering rate ───────────────────
    st.subheader("Ordering Rate Heatmap: Income vs Marital Status")
    pivot = (
        df.groupby(["Monthly Income", "Marital Status"], observed=True)["Orders Online"]
        .mean()
        .mul(100)
        .round(1)
        .reset_index()
        .pivot(index="Monthly Income", columns="Marital Status", values="Orders Online")
        .reindex(INCOME_ORDER)
    )
    fig_hm = px.imshow(
        pivot, text_auto=True, aspect="auto",
        color_continuous_scale="Blues",
        labels=dict(color="% Order Online"),
    )
    fig_hm.update_layout(margin=dict(t=20))
    st.plotly_chart(fig_hm, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# Tab 4 – Feedback Analysis
# ══════════════════════════════════════════════════════════════════════════════

def tab_feedback(df: pd.DataFrame):
    section_header("Customer Feedback Analysis", "💬")

    col1, col2 = st.columns(2)

    # ── Feedback by gender ─────────────────────────────────────────────────
    with col1:
        st.subheader("Feedback by Gender")
        fb_gen = pd.crosstab(df["Gender"], df["Feedback"], normalize="index").mul(100).round(1)
        fig = px.bar(
            fb_gen.reset_index(), x="Gender",
            y=fb_gen.columns.tolist(),
            barmode="group",
            color_discrete_map={"Positive": PALETTE[2], "Negative": PALETTE[3]},
            labels={"value": "Percentage (%)", "variable": "Feedback"},
        )
        fig.update_layout(legend_title="Feedback", margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

    # ── Feedback by occupation ─────────────────────────────────────────────
    with col2:
        st.subheader("Positive Feedback Rate by Occupation")
        occ_fb = (
            df.groupby("Occupation")["Positive Feedback"]
            .mean()
            .mul(100)
            .round(1)
            .sort_values(ascending=True)
            .reset_index()
        )
        occ_fb.columns = ["Occupation", "% Positive Feedback"]
        fig2 = px.bar(
            occ_fb, x="% Positive Feedback", y="Occupation",
            orientation="h", text="% Positive Feedback",
            color="% Positive Feedback", color_continuous_scale="Greens",
        )
        fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig2.update_layout(coloraxis_showscale=False, xaxis_range=[0, 115],
                           margin=dict(t=20), yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    col3, col4 = st.columns(2)

    # ── Feedback vs ordering ───────────────────────────────────────────────
    with col3:
        st.subheader("Feedback vs Online Ordering Decision")
        fb_out = pd.crosstab(df["Feedback"], df["Output"])
        fb_out_pct = fb_out.div(fb_out.sum(axis=1), axis=0).mul(100).round(1)
        fig3 = px.bar(
            fb_out_pct.reset_index(), x="Feedback",
            y=fb_out_pct.columns.tolist(),
            barmode="stack",
            color_discrete_map={"Yes": PALETTE[0], "No": PALETTE[3]},
            labels={"value": "Percentage (%)", "variable": "Orders Online"},
        )
        fig3.update_layout(legend_title="Orders Online", margin=dict(t=20))
        st.plotly_chart(fig3, use_container_width=True)

    # ── Feedback by income ─────────────────────────────────────────────────
    with col4:
        st.subheader("Positive Feedback Rate by Income")
        inc_order = [i for i in INCOME_ORDER if i in df["Monthly Income"].cat.categories]
        inc_fb = (
            df.groupby("Monthly Income", observed=True)["Positive Feedback"]
            .mean()
            .mul(100)
            .round(1)
            .reindex(inc_order)
            .reset_index()
        )
        inc_fb.columns = ["Monthly Income", "% Positive Feedback"]
        fig4 = px.line(
            inc_fb, x="Monthly Income", y="% Positive Feedback",
            markers=True, text="% Positive Feedback",
            color_discrete_sequence=["green"],
        )
        fig4.update_traces(texttemplate="%{text:.1f}%", textposition="top center",
                           line_width=3, marker_size=10)
        fig4.update_layout(yaxis_range=[0, 115], margin=dict(t=20))
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()
    col5, col6 = st.columns(2)

    # ── Feedback by age group ──────────────────────────────────────────────
    with col5:
        st.subheader("Feedback by Age Group")
        fb_age = pd.crosstab(df["Age Group"], df["Feedback"], normalize="index").mul(100).round(1)
        fig5 = px.bar(
            fb_age.reset_index(), x="Age Group",
            y=fb_age.columns.tolist(),
            barmode="group",
            color_discrete_map={"Positive": PALETTE[2], "Negative": PALETTE[3]},
            labels={"value": "Percentage (%)", "variable": "Feedback"},
        )
        fig5.update_layout(legend_title="Feedback", margin=dict(t=20))
        st.plotly_chart(fig5, use_container_width=True)

    # ── Feedback by marital status ─────────────────────────────────────────
    with col6:
        st.subheader("Feedback by Marital Status")
        fb_ms = pd.crosstab(df["Marital Status"], df["Feedback"], normalize="index").mul(100).round(1)
        fig6 = px.bar(
            fb_ms.reset_index(), x="Marital Status",
            y=fb_ms.columns.tolist(),
            barmode="group",
            color_discrete_map={"Positive": PALETTE[2], "Negative": PALETTE[3]},
            labels={"value": "Percentage (%)", "variable": "Feedback"},
        )
        fig6.update_layout(legend_title="Feedback", margin=dict(t=20))
        st.plotly_chart(fig6, use_container_width=True)

    # ── Feedback heatmap by education ──────────────────────────────────────
    st.divider()
    st.subheader("Feedback Distribution by Education Level")
    edu_order = [e for e in EDU_ORDER if e in df["Educational Qualifications"].cat.categories]
    fb_edu = (
        pd.crosstab(df["Educational Qualifications"], df["Feedback"], normalize="index")
        .mul(100)
        .round(1)
        .reindex(edu_order)
    )
    fig_hm = px.imshow(
        fb_edu, text_auto=True, aspect="auto",
        color_continuous_scale="RdYlGn",
        labels=dict(color="% of Segment"),
    )
    fig_hm.update_layout(margin=dict(t=20))
    st.plotly_chart(fig_hm, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# Tab 5 – Income & Family Insights
# ══════════════════════════════════════════════════════════════════════════════

def tab_income_family(df: pd.DataFrame):
    section_header("Income & Family Size Insights", "💰")

    col1, col2 = st.columns(2)

    # ── Income by gender ────────────────────────────────────────────────────
    with col1:
        st.subheader("Income Brackets by Gender")
        inc_order = [i for i in INCOME_ORDER if i in df["Monthly Income"].cat.categories]
        ig = pd.crosstab(df["Monthly Income"], df["Gender"], normalize="index").mul(100).round(1)
        ig = ig.reindex(inc_order)
        fig = px.bar(
            ig.reset_index(), x="Monthly Income",
            y=ig.columns.tolist(),
            barmode="stack",
            color_discrete_sequence=PALETTE,
            labels={"value": "% within Income Bracket", "variable": "Gender"},
        )
        fig.update_layout(legend_title="Gender", margin=dict(t=20),
                          xaxis_title="Income Bracket")
        st.plotly_chart(fig, use_container_width=True)

    # ── Income by occupation ────────────────────────────────────────────────
    with col2:
        st.subheader("Occupation vs Income (Count Heatmap)")
        occ_inc = pd.crosstab(df["Occupation"], df["Monthly Income"])
        occ_inc = occ_inc.reindex(columns=INCOME_ORDER, fill_value=0)
        fig2 = px.imshow(
            occ_inc, text_auto=True, aspect="auto",
            color_continuous_scale="Blues",
            labels=dict(color="Count"),
        )
        fig2.update_layout(margin=dict(t=20),
                           xaxis_title="Income Bracket",
                           yaxis_title="Occupation")
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()
    col3, col4 = st.columns(2)

    # ── Family size vs ordering ────────────────────────────────────────────
    with col3:
        st.subheader("Family Size vs Online Ordering Rate")
        fs_rate = (
            df.groupby("Family size")["Orders Online"]
            .agg(["mean", "count"])
            .reset_index()
        )
        fs_rate.columns = ["Family Size", "Order Rate", "Count"]
        fs_rate["Order Rate %"] = (fs_rate["Order Rate"] * 100).round(1)
        fig3 = px.scatter(
            fs_rate, x="Family Size", y="Order Rate %",
            size="Count", text="Order Rate %",
            color="Order Rate %", color_continuous_scale=PALETTE_CONT,
            size_max=50,
        )
        fig3.update_traces(texttemplate="%{text:.1f}%", textposition="top center")
        fig3.update_layout(coloraxis_showscale=False, yaxis_range=[0, 115],
                           margin=dict(t=20))
        st.plotly_chart(fig3, use_container_width=True)

    # ── Family size by marital status ──────────────────────────────────────
    with col4:
        st.subheader("Family Size Distribution by Marital Status")
        fig4 = px.box(
            df, x="Marital Status", y="Family size",
            color="Marital Status",
            color_discrete_sequence=PALETTE,
            points="all",
        )
        fig4.update_layout(showlegend=False, margin=dict(t=20),
                           yaxis_title="Family Size")
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    # ── Income vs education combined ───────────────────────────────────────
    st.subheader("Income Distribution across Education Levels")
    edu_inc = pd.crosstab(
        df["Educational Qualifications"], df["Monthly Income"]
    ).reindex(
        index=[e for e in EDU_ORDER if e in df["Educational Qualifications"].cat.categories],
        columns=INCOME_ORDER,
        fill_value=0,
    )
    edu_inc_pct = edu_inc.div(edu_inc.sum(axis=1), axis=0).mul(100).round(1)
    fig_stacked = px.bar(
        edu_inc_pct.reset_index(), x="Educational Qualifications",
        y=INCOME_ORDER,
        barmode="stack",
        color_discrete_sequence=PALETTE,
        labels={"value": "Percentage (%)", "variable": "Income Bracket"},
    )
    fig_stacked.update_layout(
        legend_title="Income Bracket", margin=dict(t=20),
        xaxis_title="Education Level",
    )
    st.plotly_chart(fig_stacked, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# Tab 6 – Comparative Analysis
# ══════════════════════════════════════════════════════════════════════════════

def tab_comparative(df: pd.DataFrame):
    section_header("Comparative & Cross-Segment Analysis", "🔀")

    # ── Radar: demographic profile of orderers vs non-orderers ─────────────
    st.subheader("Demographic Profile: Online Orderers vs Non-Orderers")
    dims = {
        "Avg Age (norm)": lambda g: g["Age"].mean() / df["Age"].max(),
        "Avg Family Size (norm)": lambda g: g["Family size"].mean() / df["Family size"].max(),
        "% Positive Feedback": lambda g: g["Positive Feedback"].mean(),
        "% Post Graduate": lambda g: (g["Educational Qualifications"] == "Post Graduate").mean(),
        "% Employee": lambda g: (g["Occupation"] == "Employee").mean(),
    }
    radar_data = {}
    for label, func in dims.items():
        for output_val in ["Yes", "No"]:
            grp = df[df["Output"] == output_val]
            radar_data.setdefault(output_val, {})[label] = round(func(grp), 3)

    categories = list(dims.keys())
    fig_radar = go.Figure()
    color_map = {"Yes": PALETTE[0], "No": PALETTE[3]}
    for grp_name, values in radar_data.items():
        r_vals = [values[c] for c in categories]
        r_vals.append(r_vals[0])
        theta = categories + [categories[0]]
        fig_radar.add_trace(go.Scatterpolar(
            r=r_vals, theta=theta,
            fill="toself", name=f"Orders Online: {grp_name}",
            line_color=color_map.get(grp_name, PALETTE[1]),
            opacity=0.75,
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True, margin=dict(t=30),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()
    col1, col2 = st.columns(2)

    # ── Age distribution by output ─────────────────────────────────────────
    with col1:
        st.subheader("Age Distribution: Orderers vs Non-Orderers")
        fig = px.histogram(
            df, x="Age", color="Output", barmode="overlay",
            nbins=20, opacity=0.75,
            color_discrete_map={"Yes": PALETTE[0], "No": PALETTE[3]},
            labels={"Output": "Orders Online"},
        )
        fig.update_layout(legend_title="Orders Online", margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

    # ── Customer type vs feedback ──────────────────────────────────────────
    with col2:
        st.subheader("Customer Type × Feedback")
        ct_fb = pd.crosstab(df["Customer Type"], df["Feedback"], normalize="index").mul(100).round(1)
        fig2 = px.bar(
            ct_fb.reset_index(), x="Customer Type",
            y=ct_fb.columns.tolist(),
            barmode="group",
            color_discrete_map={"Positive": PALETTE[2], "Negative": PALETTE[3]},
            labels={"value": "Percentage (%)", "variable": "Feedback"},
        )
        fig2.update_layout(legend_title="Feedback", margin=dict(t=20))
        st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Sunburst: occupation → income → output ─────────────────────────────
    st.subheader("Sunburst: Occupation → Income → Ordering Decision")
    sb_df = (
        df.groupby(["Occupation", "Monthly Income", "Output"], observed=True)
        .size()
        .reset_index(name="Count")
    )
    fig3 = px.sunburst(
        sb_df, path=["Occupation", "Monthly Income", "Output"],
        values="Count", color="Count",
        color_continuous_scale=PALETTE_CONT,
    )
    fig3.update_layout(margin=dict(t=20))
    st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# Tab 7 – Business Insights
# ══════════════════════════════════════════════════════════════════════════════

def tab_insights(df: pd.DataFrame):
    section_header("Business Insights & Recommendations", "💡")

    # ── Compute key metrics ────────────────────────────────────────────────
    stats = summary_stats(df)
    top_occ = df["Occupation"].value_counts().idxmax()
    top_inc = str(df["Monthly Income"].value_counts().idxmax())
    top_edu = str(df["Educational Qualifications"].value_counts().idxmax())

    best_occ_order = (
        df.groupby("Occupation")["Orders Online"].mean().idxmax()
    )
    best_edu_fb = (
        df.groupby("Educational Qualifications", observed=True)["Positive Feedback"]
        .mean()
        .idxmax()
    )

    # ── Insight cards ──────────────────────────────────────────────────────
    insights = [
        {
            "icon": "📱",
            "title": "High Digital Adoption",
            "body": (
                f"**{stats['order_online_pct']}%** of surveyed customers already order food online. "
                f"This signals a mature, receptive market for delivery platforms."
            ),
            "action": "Invest in retention and loyalty programs for existing online customers.",
            "color": "#EFF6FF",
        },
        {
            "icon": "🎓",
            "title": "Student Segment Dominates",
            "body": (
                f"**{top_occ}s** are the most represented occupational group, and "
                f"**{top_edu}** is the most common education level. "
                f"Young, educated users drive most of the volume."
            ),
            "action": "Launch student discount campaigns, combo meal deals, and referral programs targeting college areas.",
            "color": "#F0FDF4",
        },
        {
            "icon": "💬",
            "title": "Strong Positive Sentiment",
            "body": (
                f"**{stats['positive_feedback_pct']}%** of customers gave positive feedback. "
                f"The occupation with the best online ordering adoption is **{best_occ_order}**."
            ),
            "action": "Leverage positive reviews in marketing; investigate sources of negative feedback to reduce churn.",
            "color": "#F0FDF4",
        },
        {
            "icon": "💰",
            "title": "Low-Income Segments Order Too",
            "body": (
                f"Even the **No Income** bracket shows substantial online ordering. "
                f"The most common income group is **{top_inc}**. "
                f"Price sensitivity is a key factor."
            ),
            "action": "Introduce micro-bundles, free delivery thresholds, and wallet/UPI-friendly payment options.",
            "color": "#FFFBEB",
        },
        {
            "icon": "👨‍👩‍👧",
            "title": "Larger Families Order More",
            "body": (
                f"Family size positively correlates with online ordering frequency. "
                f"Average family size among frequent orderers is higher."
            ),
            "action": "Promote family meal plans, group discounts, and bundle offers for 4+ member households.",
            "color": "#FFF7ED",
        },
        {
            "icon": "📊",
            "title": "Frequent vs New Customers",
            "body": (
                "A significant share of customers are tagged 'Frequent' or 'Regular'. "
                "New customer acquisition still has room to grow."
            ),
            "action": "Create targeted 'first order free' campaigns for New customers; gamify loyalty for Frequent customers.",
            "color": "#F5F3FF",
        },
        {
            "icon": "🌍",
            "title": "Geographic Concentration",
            "body": (
                "Most orders are concentrated in Bangalore (560xxx pin codes). "
                "The data is geographically skewed towards a single metro."
            ),
            "action": "Expand partnerships into Tier-2 cities; conduct separate surveys for broader coverage.",
            "color": "#FFF1F2",
        },
        {
            "icon": "📐",
            "title": "Education Drives Satisfaction",
            "body": (
                f"Customers with **{best_edu_fb}** education give the highest rate of positive feedback. "
                f"Educational background shapes service expectations."
            ),
            "action": "Tailor the app UX and communication style to match the dominant Post Graduate / Graduate segment.",
            "color": "#ECFDF5",
        },
    ]

    for i in range(0, len(insights), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j < len(insights):
                ins = insights[i + j]
                with col:
                    st.markdown(
                        f"""
                        <div style="background:{ins['color']};border-radius:10px;
                                    padding:16px 20px;margin-bottom:16px;
                                    border-left:4px solid #3b82f6;">
                            <h4 style="margin:0 0 6px 0;">{ins['icon']} {ins['title']}</h4>
                            <p style="margin:0 0 8px 0;color:#374151;">{ins['body']}</p>
                            <p style="margin:0;color:#1e40af;font-size:0.88em;">
                                💼 <strong>Action:</strong> {ins['action']}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    st.divider()

    # ── Summary metrics table ──────────────────────────────────────────────
    st.subheader("📋 Summary Statistics by Segment")
    summary_rows = []
    for occ in df["Occupation"].unique():
        sub = df[df["Occupation"] == occ]
        summary_rows.append({
            "Occupation": occ,
            "Count": len(sub),
            "% of Total": f"{len(sub)/len(df)*100:.1f}%",
            "Avg Age": f"{sub['Age'].mean():.1f}",
            "% Order Online": f"{sub['Orders Online'].mean()*100:.1f}%",
            "% Positive Feedback": f"{sub['Positive Feedback'].mean()*100:.1f}%",
            "Avg Family Size": f"{sub['Family size'].mean():.1f}",
        })
    summary_df = pd.DataFrame(summary_rows).sort_values("Count", ascending=False)
    st.dataframe(summary_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # ── Locate the dataset ─────────────────────────────────────────────────
    script_dir = os.path.dirname(os.path.abspath(__file__))
    possible_paths = [
        os.path.join(script_dir, "online food delivery dataset.csv"),
        os.path.join(script_dir, "..", "online food delivery dataset.csv"),
        "online food delivery dataset.csv",
    ]
    dataset_path = None
    for p in possible_paths:
        if os.path.exists(p):
            dataset_path = p
            break

    # ── Header ─────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="background:linear-gradient(90deg,#1e3a5f,#2563EB);
                    color:white;padding:24px 32px;border-radius:12px;margin-bottom:8px;">
            <h1 style="margin:0;font-size:2rem;">🍔 Online Food Delivery Analytics</h1>
            <p style="margin:6px 0 0 0;opacity:0.85;font-size:1.05rem;">
                Data-driven insights into customer demographics, ordering behaviour, and satisfaction
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── File uploader fallback ─────────────────────────────────────────────
    if dataset_path is None:
        st.warning("⚠️ Dataset not found automatically. Please upload it below.")
        uploaded = st.file_uploader(
            "Upload 'online food delivery dataset.csv'", type="csv"
        )
        if uploaded is None:
            st.info("👆 Upload the dataset to begin analysis.")
            st.stop()
        import tempfile, shutil
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            shutil.copyfileobj(uploaded, tmp)
            dataset_path = tmp.name

    # ── Load data ──────────────────────────────────────────────────────────
    try:
        raw_df = get_data(dataset_path)
    except Exception as e:
        st.error(f"Failed to load dataset: {e}")
        st.stop()

    # ── Sidebar filters ────────────────────────────────────────────────────
    df = render_sidebar(raw_df)

    if df.empty:
        st.warning("⚠️ No data matches the selected filters. Please adjust the sidebar.")
        st.stop()

    filtered_note = (
        f"Showing **{len(df):,}** of **{len(raw_df):,}** records"
        if len(df) < len(raw_df)
        else f"Showing all **{len(df):,}** records"
    )
    st.caption(filtered_note)

    # ── Tab navigation ─────────────────────────────────────────────────────
    tabs = st.tabs([
        "📊 Overview",
        "👥 Demographics",
        "🛒 Ordering Behaviour",
        "💬 Feedback",
        "💰 Income & Family",
        "🔀 Comparative",
        "💡 Insights",
    ])

    with tabs[0]:
        tab_overview(df, raw_df)
    with tabs[1]:
        tab_demographics(df)
    with tabs[2]:
        tab_ordering(df)
    with tabs[3]:
        tab_feedback(df)
    with tabs[4]:
        tab_income_family(df)
    with tabs[5]:
        tab_comparative(df)
    with tabs[6]:
        tab_insights(df)


if __name__ == "__main__":
    main()
