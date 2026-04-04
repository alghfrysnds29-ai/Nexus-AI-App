import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt

# =========================
# إعدادات عامة
# =========================
st.set_page_config(
    page_title="Store Analytics Dashboard",
    layout="wide"
)

# =========================
# CSS: Animations + Design System + Branding
# =========================
st.markdown("""
<style>
* {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif;
}

/* Fade-in للصفحة */
.stApp { animation: fadeIn 0.8s ease-in; }
@keyframes fadeIn { from {opacity:0;} to {opacity:1;} }

/* Slide-in للبطاقات */
.stMetric, .stDataFrame, .stTable {
  animation: slideIn 0.6s ease-out;
}
@keyframes slideIn { from {transform:translateY(20px);opacity:0;} to {transform:translateY(0);opacity:1;} }

/* Hover effect */
.stMetric:hover {
  transform: scale(1.02);
  box-shadow: 0 6px 14px rgba(0,0,0,0.1);
}

/* Buttons */
button, .stButton>button {
  background-color: #111827;
  color: #fff;
  border-radius: 8px;
  padding: 8px 16px;
}
button:hover { background-color: #374151; }

/* Sticky Header */
header, .block-container h2 {
  position: sticky;
  top: 0;
  background: inherit;
  z-index: 999;
}

/* Bottom Navigation */
.bottom-nav {
  position: fixed;
  bottom: 0;
  width: 100%;
  background: #fff;
  display: flex;
  justify-content: space-around;
  padding: 10px;
  border-top: 1px solid #e5e7eb;
}
.bottom-nav a { text-decoration:none; color:#111827; font-weight:500; }
</style>
""", unsafe_allow_html=True)

# =========================
# Hero Section
# =========================
st.markdown("""
<div style="text-align:center; padding:20px;">
  <h1 style="font-weight:700;">Store Analytics Dashboard</h1>
  <p>Transform your data into actionable insights</p>
</div>
""", unsafe_allow_html=True)

# =========================
# Dark/Light Mode Toggle
# =========================
mode = st.sidebar.radio("Theme Mode", ["Light", "Dark"])
if mode == "Dark":
    st.markdown("<style>.stApp{background:#111827;color:#f9fafb}</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp{background:#f5f5f7;color:#111827}</style>", unsafe_allow_html=True)

# =========================
# Language Toggle (English default)
# =========================
lang = st.sidebar.radio("Language", ["English", "Arabic"], index=0)

translations = {
    "English": {
        "Dashboard": "Dashboard",
        "Revenue": "Revenue",
        "Orders": "Orders",
        "Customers": "Customers",
    },
    "Arabic": {
        "Dashboard": "لوحة التحكم",
        "Revenue": "الإيرادات",
        "Orders": "الطلبات",
        "Customers": "العملاء",
    }
}
def t(key): return translations[lang].get(key, key)

# =========================
# بيانات وهمية
# =========================
@st.cache_data
def generate_data():
    dates = pd.date_range(end=dt.date.today(), periods=30)
    df = pd.DataFrame({
        "date": dates,
        "revenue": np.random.randint(1000,5000,len(dates)),
        "orders": np.random.randint(50,200,len(dates)),
        "customers": np.random.randint(30,100,len(dates))
    })
    return df
df = generate_data()

# =========================
# Search Bar ذكي
# =========================
search_query = st.sidebar.text_input("Search")
if search_query:
    results = df[df.apply(lambda row: search_query.lower() in str(row.values).lower(), axis=1)]
    st.write("Search Results:")
    st.dataframe(results)

# =========================
# عرض KPIs
# =========================
st.header(t("Dashboard"))
col1, col2, col3 = st.columns(3)
col1.metric(t("Revenue"), f"{df['revenue'].sum():,.0f}")
col2.metric(t("Orders"), f"{df['orders'].sum():,}")
col3.metric(t("Customers"), f"{df['customers'].sum():,}")

# =========================
# Bottom Navigation
# =========================
st.markdown("""
<div class="bottom-nav">
  <a href="#">Home</a>
  <a href="#">Analytics</a>
  <a href="#">Settings</a>
</div>
""", unsafe_allow_html=True)
