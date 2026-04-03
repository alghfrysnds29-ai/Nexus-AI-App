import streamlit as st
import pandas as pd
import numpy as np

# إعدادات الصفحة الأساسية (تظهر في كل الصفحات)
st.set_page_config(page_title="Nexus AI | Enterprise", page_icon="🚀", layout="wide")

# CSS موحد لكل الصفحات لجعل التصميم متناسق
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    [data-testid="stMetricValue"] { font-size: 28px; color: #10b981; }
    .stDataFrame { border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 لوحة التحكم الرئيسية")
st.subheader("مرحباً بك في منصة Nexus للتحليل الذكي")

# --- محرك رفع البيانات وحفظها في الـ Session State ---
st.sidebar.header("📁 مركز البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف مبيعاتك (Excel/CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    # قراءة البيانات
    if uploaded_file.name.endswith('xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    
    # حفظ البيانات في "ذاكرة الجلسة" لتراها الصفحات الأخرى
    st.session_state['main_df'] = df
    st.success("✅ تم تحميل البيانات بنجاح! انتقل للصفحات الجانبية للتحليل.")
else:
    st.info("💡 يرجى رفع ملف من القائمة الجانبية للبدء، أو سيتم استخدام بيانات تجريبية.")
    # بيانات افتراضية إذا لم يرفع المستخدم ملفاً
    df_demo = pd.DataFrame({
        "المنتج": ["منتج A", "منتج B"],
        "المبيعات": [100, 200],
        "التكلفة": [50, 80]
    })
    st.session_state['main_df'] = df_demo

# عرض ملخص سريع في الصفحة الرئيسية
if 'main_df' in st.session_state:
    df = st.session_state['main_df']
    col1, col2, col3 = st.columns(3)
    col1.metric("عدد المنتجات", len(df))
    col2.metric("إجمالي السجلات", df.shape[0])
    col3.metric("حالة النظام", "متصل ✅")
    
    st.markdown("---")
    st.write("### معاينة سريعة للبيانات:")
    st.dataframe(df.head(10), use_container_width=True)
