import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. إعدادات الهوية البصرية (اللون الفاتح الملكي) ---
st.set_page_config(page_title="Nexus SCM Pro", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap');
    :root { --primary: #2563eb; --bg: #f8fafc; --text: #1e293b; }
    html, body, [class*="css"] { font-family: 'IBM Plex Sans Arabic', sans-serif; direction: rtl; text-align: right; background-color: var(--bg); color: var(--text); }
    .exec-card { background: white; border: 1px solid #e2e8f0; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); transition: 0.3s; }
    .exec-card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: var(--primary); }
    .ai-box { background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); border-right: 5px solid var(--primary); padding: 20px; border-radius: 12px; margin-bottom: 25px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background: white; border-radius: 10px 10px 0 0; border: 1px solid #e2e8f0; padding: 10px 30px; }
    .stTabs [aria-selected="true"] { background: var(--primary) !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محركات البيانات (Data Engines) ---
@st.cache_data
def load_all_data():
    # بيانات التنفيذي
    df_exec = pd.DataFrame({'الشهر': ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"],
                           'الإيرادات': [250000, 280000, 240000, 310000, 295000, 340000],
                           'المصاريف': [180000, 190000, 175000, 210000, 205000, 220000]})
    # بيانات التنبؤ
    dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    df_fore = pd.DataFrame({'التاريخ': dates, 'الطلب': [100 + (i*1.2) + np.random.randint(-10,10) for i in range(30)]})
    # بيانات الموردين
    df_sup = pd.DataFrame({'المورد': ['مورد أ', 'مورد ب', 'مورد ج'], 'الجودة': [95, 80, 88], 'الوقت': [5, 12, 7]})
    return df_exec, df_fore, df_sup

df_exec, df_fore, df_sup = load_all_data()

# --- 3. الهيكل الرئيسي (Main UI) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/5968/5968204.png", width=50) # شعار افتراضي
    st.title("Nexus Pro")
    st.markdown("---")
    st.write("👤 **المدير:** منى محمد")
    st.info("💡 **تنبيه:** 3 شحنات قادمة اليوم")
    st.markdown("---")
    st.button("⚙️ الإعدادات")
    st.button("🔴 تسجيل الخروج")

st.markdown("<h1 style='font-weight:800;'>🚀 منصة Nexus لذكاء سلاسل الإمداد</h1>", unsafe_allow_html=True)

# بنر الذكاء الاصطناعي
st.markdown("""<div class="ai-box"><h4>✨ توصيات Nexus AI اليوم:</h4>
<p>تحليل البيانات يشير لارتفاع الطلب بنسبة 15% الأسبوع القادم. تأكد من تفعيل شحن "مورد أ" لتغطية العجز.</p></div>""", unsafe_allow_html=True)

# التبويبات
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏢 برج المراقبة", "🔮 التنبؤ الذكي", "📦 المخزون العالي", "🚚 الموردين", "🔄 المرتجعات"])

with tab1:
    k1, k2, k3 = st.columns(3)
    k1.metric("إجمالي السيولة", "340,000 ر.س", "12%")
    k2.metric("المخزون الميت", "145 قطعة", "-4%")
    k3.metric("دقة التوصيل", "96.5%", "1.2%")
    
    fig = px.area(df_exec, x='الشهر', y='الإيرادات', title="نمو التدفق النقدي", color_discrete_sequence=['#2563eb'])
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("توقعات الطلب لـ 30 يوماً القادمة")
    fig_f = px.line(df_fore, x='التاريخ', y='الطلب', markers=True)
    st.plotly_chart(fig_f, use_container_width=True)
    st.warning("⚠️ خطر نفاذ مخزون منتج 'SKU-55' في تاريخ 12 إبريل")

with tab3:
    st.subheader("تحليل ABC للمخزون")
    # مصفوفة وهمية سريعة
    df_abc = pd.DataFrame({'الفئة': ['A (حيوي)', 'B (متوسط)', 'C (ثانوي)'], 'القيمة': [70, 20, 10]})
    st.plotly_chart(px.pie(df_abc, names='الفئة', values='القيمة', hole=.4), use_container_width=True)

with tab4:
    st.subheader("تقييم أداء الموردين")
    st.table(df_sup)
    st.plotly_chart(px.scatter(df_sup, x='الوقت', y='الجودة', text='المورد', size='الجودة'), use_container_width=True)

with tab5:
    st.subheader("تحليل المرتجعات")
    st.bar_chart({'عيب مصنعي': 20, 'مقاس خاطئ': 50, 'تأخر شحن': 15})
    st.markdown("---")
    st.button("📥 تحميل التقرير النهائي (PDF)")

st.caption("Nexus BI Solution - الإصدار 2026")
