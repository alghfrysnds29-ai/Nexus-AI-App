import streamlit as st
import pandas as pd

# إعداد الصفحة - يجب أن يكون أول سطر برمي
st.set_page_config(page_title="Nexus AI Luxury", page_icon="💎", layout="wide")

# تصميم CSS فخم (ذهبي وأسود)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #D4AF37 !important; font-family: 'Cairo', sans-serif; text-align: right; }
    div[data-testid="stMetric"] { background-color: #1c1f26; border: 1px solid #D4AF37; border-radius: 15px; padding: 20px; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; }
    .stDataFrame { border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

st.title("💎 منصة Nexus AI للتحليل الاستراتيجي")
st.markdown("---")

# رفع الملف وحفظه في ذاكرة الجلسة
with st.sidebar:
    st.header("📥 مركز البيانات")
    uploaded_file = st.file_uploader("ارفع ملف Excel أو CSV", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
        st.session_state['main_df'] = df
        st.success("✅ تم تفعيل البيانات بنجاح! انتقل للصفحات الجانبية.")
        
        c1, c2 = st.columns(2)
        c1.metric("إجمالي السجلات", len(df))
        c2.metric("حالة النظام", "متصل بالذكاء الاصطناعي")
        
        st.subheader("🔍 معاينة البيانات")
        st.dataframe(df.head(10), use_container_width=True)
    except Exception as e:
        st.error(f"حدث خطأ: {e}")
else:
    st.info("💡 يرجى رفع ملف البيانات من القائمة الجانبية للبدء.")
