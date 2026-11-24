
import html
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Customer Churn Risk Dashboard",
    layout="wide"
)

# ---------- Palette ----------
NAVY = "#003299"
YELLOW = "#FFB400"
ORANGE = "#FF4B00"
GREEN = "#65B800"
SKY = "#00B1EA"
GREY = "#5C5C5C"

RISK_COLORS = {"Low": GREEN, "Moderate": SKY, "High": YELLOW, "Critical": ORANGE}
risk_options = list(RISK_COLORS.keys())

# ---------- Styling ----------
st.markdown("""
<style>
html, body, .stApp, [class*="css"] { font-family: Arial, Helvetica, sans-serif; }
.stApp { background: #FFFFFF; color: #333333; }
.block-container { padding-top: 0.5rem; max-width: 1280px; }
header[data-testid="stHeader"] { background: transparent; }
h1, h2, h3 { color: #003299; font-family: Arial, Helvetica, sans-serif; }

/* Top bar + navigation */
.top-bar { display:flex; justify-content:space-between; align-items:flex-end;
           padding:18px 0 12px; border-bottom:1px solid #D9DEE8; }
.brand-title { font-size:1.35rem; font-weight:700; color:#003299; line-height:1.2; }
.brand-sub { font-size:.75rem; color:#5C5C5C; letter-spacing:.06em; text-transform:uppercase; }
.top-meta { font-size:.8rem; color:#5C5C5C; }
.nav-bar { display:flex; flex-wrap:wrap; gap:28px; padding:12px 0;
           border-bottom:3px solid #003299; margin-bottom:28px; }
.nav-bar a { color:#003299 !important; text-decoration:none !important;
             font-weight:700; font-size:.92rem; }
.nav-bar a:hover { color:#FFB400 !important; }

/* Feature banner */
.hero { background:#003299; padding:36px 40px; margin-bottom:32px; }
.hero .label { color:#FFB400; }
.hero h1 { color:#FFFFFF !important; font-size:2.1rem; margin:6px 0 10px; padding:0; }
.hero p { max-width:780px; color:#E6EAF5; font-size:1rem; line-height:1.55; margin:0; }

/* Labels + section titles */
.label { font-size:.72rem; font-weight:700; letter-spacing:.08em;
         text-transform:uppercase; color:#5C5C5C; }
.section-title { font-size:1.45rem; font-weight:700; color:#003299;
                 margin:36px 0 14px; padding-bottom:8px; border-bottom:1px solid #D9DEE8; }

/* KPI cards */
.kpi { border-top:4px solid #003299; background:#F4F6FB; padding:18px 20px; }
.kpi.high { border-top-color:#FFB400; }
.kpi.critical { border-top-color:#FF4B00; }
.kpi .value { font-size:2rem; font-weight:700; color:#003299; margin-top:6px; }
.kpi .note { font-size:.8rem; color:#5C5C5C; }

/* News-feed style list */
.feed-item { padding:14px 0; border-bottom:1px solid #D9DEE8; }
.feed-item .meta { font-size:.72rem; color:#5C5C5C; text-transform:uppercase; letter-spacing:.06em; }
.feed-item .title { color:#003299; font-weight:700; font-size:1rem; margin-top:4px; }
.pill { display:inline-block; padding:1px 8px; font-size:.68rem; font-weight:700;
        color:#FFFFFF; margin-right:8px; }

/* Sidebar */
section[data-testid="stSidebar"] { background:#F4F6FB; border-right:1px solid #D9DEE8; }
section[data-testid="stSidebar"] h2 { color:#003299; font-size:1rem;
        text-transform:uppercase; letter-spacing:.08em; }

/* Download button */
.stDownloadButton button { background:#003299; color:#FFFFFF; border:none; border-radius:0;
        font-weight:700; padding:.65rem 1.4rem; text-transform:uppercase;
        letter-spacing:.06em; font-size:.8rem; }
.stDownloadButton button:hover { background:#FFB400; color:#003299; border:none; }

/* Footer */
.footer { background:#003299; color:#C9D3EE; padding:28px 40px; margin-top:48px; font-size:.8rem; }
.footer strong { color:#FFFFFF; }
</style>
""", unsafe_allow_html=True)

# ---------- Data ----------
@st.cache_data
def load_data():
    return pd.read_csv("operational_customer_churn_risk.csv")

df = load_data()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

selected_risks = st.sidebar.multiselect(
    "Risk categories", risk_options, default=risk_options
)

if "Geography" in df.columns:
    geography_options = sorted(df["Geography"].dropna().unique())
    selected_geographies = st.sidebar.multiselect(
        "Geography", geography_options, default=geography_options
    )
else:
    selected_geographies = []

filtered_df = df[df["Risk_Category"].isin(selected_risks)]
if "Geography" in df.columns:
    filtered_df = filtered_df[filtered_df["Geography"].isin(selected_geographies)]

sort_col = "Churn_Probability" if "Churn_Probability" in df.columns else "Churn_Probability_Percent"
pct_col = "Churn_Probability_Percent"

# ---------- Header ----------
today = pd.Timestamp.today().strftime("%d %B %Y")

st.markdown(f"""
<div class="top-bar">
  <div>
    <div class="brand-sub">Risk Analytics</div>
    <div class="brand-title">Customer Churn Risk Dashboard</div>
  </div>
  <div class="top-meta">Updated {today}</div>
</div>
<div class="nav-bar">
  <a href="#overview">Overview</a>
  <a href="#distribution">Risk distribution</a>
  <a href="#records">Customer records</a>
  <a href="#report">Report</a>
</div>
<div class="hero" id="overview">
  <div class="label">Model output</div>
  <h1>Predictive modelling and risk scoring for customer churn</h1>
  <p>Churn-risk predictions generated by a Random Forest classification model.
     Use the filters to focus on specific risk categories or geographies.</p>
</div>
""", unsafe_allow_html=True)

# ---------- KPIs ----------
total = len(filtered_df)
high = int((filtered_df["Risk_Category"] == "High").sum())
critical = int((filtered_df["Risk_Category"] == "Critical").sum())
avg_score = f"{filtered_df[pct_col].mean():.2f}%" if not filtered_df.empty else "N/A"

def kpi(label, value, note, cls=""):
    return f"""<div class="kpi {cls}">
      <div class="label">{label}</div>
      <div class="value">{value}</div>
      <div class="note">{note}</div></div>"""

c1, c2, c3, c4 = st.columns(4)
c1.markdown(kpi("Total customers", f"{total:,}", "In current selection"), unsafe_allow_html=True)
c2.markdown(kpi("High risk", f"{high:,}", "Customers flagged High", "high"), unsafe_allow_html=True)
c3.markdown(kpi("Critical risk", f"{critical:,}", "Customers flagged Critical", "critical"), unsafe_allow_html=True)
c4.markdown(kpi("Average churn score", avg_score, "Mean predicted probability"), unsafe_allow_html=True)

# ---------- Distribution + top-risk feed ----------
left, right = st.columns([2, 1], gap="large")

with left:
    st.markdown('<div class="section-title" id="distribution">Customer risk distribution</div>',
                unsafe_allow_html=True)
    if not filtered_df.empty:
        risk_counts = (
            filtered_df["Risk_Category"].value_counts()
            .reindex(risk_options, fill_value=0)
            .rename_axis("Risk_Category")
            .reset_index(name="Customers")
        )
        chart = (
            alt.Chart(risk_counts)
            .mark_bar(size=56)
            .encode(
                x=alt.X("Risk_Category:N", sort=risk_options, title=None,
                        axis=alt.Axis(labelAngle=0)),
                y=alt.Y("Customers:Q", title="Customers"),
                color=alt.Color("Risk_Category:N",
                                scale=alt.Scale(domain=risk_options,
                                                range=list(RISK_COLORS.values())),
                                legend=None),
                tooltip=["Risk_Category", "Customers"],
            )
            .properties(height=330)
            .configure_axis(labelFont="Arial", titleFont="Arial",
                            labelColor=GREY, titleColor=GREY,
                            gridColor="#E6EAF2", domainColor="#D9DEE8")
            .configure_view(strokeWidth=0)
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No customers match the current filters.")

with right:
    st.markdown('<div class="section-title">Highest-risk customers</div>',
                unsafe_allow_html=True)
    id_col = next((c for c in ["CustomerId", "Customer_ID", "CustomerID", "Surname"]
                   if c in filtered_df.columns), None)
    top = filtered_df.sort_values(sort_col, ascending=False).head(5)
    items = ""
    for idx, row in top.iterrows():
        cat = row["Risk_Category"]
        name = html.escape(str(row[id_col])) if id_col else f"Record {idx}"
        geo = f" · {html.escape(str(row['Geography']))}" if "Geography" in row else ""
        items += f"""<div class="feed-item">
          <div class="meta"><span class="pill" style="background:{RISK_COLORS.get(cat, NAVY)}">{cat}</span>
          {row[pct_col]:.1f}% churn probability{geo}</div>
          <div class="title">Customer {name}</div></div>"""
    st.markdown(items or "<p>No records.</p>", unsafe_allow_html=True)

# ---------- Records table ----------
st.markdown('<div class="section-title" id="records">Customer risk records</div>',
            unsafe_allow_html=True)

col_cfg = {}
if pct_col in filtered_df.columns:
    col_cfg[pct_col] = st.column_config.ProgressColumn(
        "Churn probability", min_value=0, max_value=100, format="%.1f%%"
    )

st.dataframe(
    filtered_df.sort_values(sort_col, ascending=False),
    use_container_width=True,
    hide_index=True,
    column_config=col_cfg,
)

# ---------- Download ----------
st.markdown('<div class="section-title" id="report">Report</div>', unsafe_allow_html=True)
st.download_button(
    label="Download filtered risk report",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_customer_churn_risk.csv",
    mime="text/csv",
)

# ---------- Footer ----------
st.markdown(f"""
<div class="footer">
  <strong>Customer Churn Risk Dashboard</strong><br>
  Predictions from a Random Forest classification model · Generated {today}<br>
  For internal analytical use.
</div>
""", unsafe_allow_html=True)
