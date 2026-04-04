import streamlit as st
import pandas as pd
import numpy as np

# 1. إعداد الصفحة
st.set_page_config(page_title="Nexus AI Luxury", page_icon="💎", layout="wide")

# 2. التنسيق الجمالي (ذهبي وأسود)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #D4AF37 !important; font-family: 'Cairo', sans-serif; text-align: right; }
    div[data-testid="stMetric"] { background-color: #1c1f26; border: 1px solid #D4AF37; border-radius: 15px; padding: 20px; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; }
    .stButton>button { background-color: #D4AF37; color: black; border-radius: 10px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 منصة Nexus AI للتحليل الذكي")

# 3. دالة إنشاء بيانات تجريبية
def load_demo_data():
    data = {
        'المنتج': ['آيفون 15 برو', 'ماك بوك إير', 'سماعات سوني', 'ساعة أبل', 'شاشة سامسونج', 'لوحة مفاتيح', 'كاميرا كانون'],
        'المبيعات': [5000, 8500, 1200, 2300, 4100, 450, 6700],
        'المخزون': [25, 12, 45, 8, 18, 60, 5],
        'التكلفة': [4200, 7000, 900, 1800, 3200, 200, 5500]
    }
    return pd.DataFrame(data)

# 4. القائمة الجانبية
with st.sidebar:
    st.header("📥 مركز البيانات")
    
    # خيار رفع ملف
    uploaded_file = st.file_uploader("ارفع ملف Excel أو CSV", type=['xlsx', 'csv'])
    
    st.markdown("---")
    # خيار البيانات التجريبية
    if st.button("🚀 تشغيل البيانات التجريبية"):
        st.session_state['main_df'] = load_demo_data()
        st.success("تم تحميل بيانات Nexus التجريبية!")

# 5. عرض البيانات
if 'main_df' in st.session_state:
    df = st.session_state['main_df']
    
    st.success("✅ البيانات جاهزة للتحليل")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي المنتجات", len(df))
    c2.metric("إجمالي المبيعات", f"{df['المبيعات'].sum():,.0f} $")
    c3.metric("حالة النظام", "بيانات Nexus")
    
    st.subheader("🔍 معاينة الجدول الحالي")
    st.dataframe(df, use_container_width=True)
else:
    st.info("💡 يرجى رفع ملف أو الضغط على 'تشغيل البيانات التجريبية' من القائمة الجانبية.")

st.markdown("---")
st.caption("Nexus AI Enterprise 2026")
