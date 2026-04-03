import streamlit as st
import pandas as pd

# 1. الإعدادات (يجب أن يكون أول أمر)
st.set_page_config(page_title="Nexus AI Luxury", page_icon="💎", layout="wide")

# 2. التنسيق (CSS) لثيم فخم
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #D4AF37 !important; font-family: 'Cairo', sans-serif; text-align: right; }
    div[data-testid="stMetric"] { background-color: #1c1f26; border: 1px solid #D4AF37; border-radius: 15px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 لوحة تحكم Nexus AI")

# رفع البيانات وحفظها في الذاكرة
uploaded_file = st.sidebar.file_uploader("ارفع بياناتك (Excel/CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        st.session_state['main_df'] = df
        st.success("✅ تم تحميل البيانات. انتقل للصفحات الجانبية للتحليل.")
        
        m1, m2 = st.columns(2)
        m1.metric("إجمالي السجلات", len(df))
        m2.metric("حالة النظام", "نشط")
        st.dataframe(df.head(10))
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
else:
    st.info("💡 يرجى رفع ملف من القائمة الجانبية للبدء.")
