import streamlit as st
import pandas as pd

# الإعدادات
st.set_page_config(page_title="Nexus AI | Enterprise", page_icon="📊", layout="wide")

# CSS متقدم للبطاقات والخطوط
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    /* الخلفية الكلية */
    .stApp {
        background-color: #0e1117;
    }
    /* بطاقات KPI فخمة */
    .kpi-card {
        background: linear-gradient(145deg, #1e1e1e, #121212);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 5px 5px 15px #050505, -5px -5px 15px #1f1f1f;
        text-align: center;
        border: 1px solid #D4AF37;
        color: #D4AF37;
    }
    /* العناوين ذهبية */
    h1, h2, h3, p {
        color: #D4AF37 !important;
        font-family: 'Cairo', sans-serif;
    }
    /* تعديل شكل الـ Sidebar */
    [data-testid="stSidebar"] {
        background-color: #121212;
        border-left: 1px solid #D4AF37;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 مرحباً بك في Nexus BI")
st.write("المنصة المتكاملة لتحليل بياناتك التجارية بذكاء.")

# رفع البيانات
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1548/1548914.png", width=80)
    st.header("إعدادات البيانات")
    uploaded_file = st.file_uploader("ارفع ملفك هنا", type=['xlsx', 'csv'])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
    st.session_state['main_df'] = df
    st.sidebar.success("✅ البيانات جاهزة")
    
    # عرض إحصائيات سريعة (KPIs) بشكل جمالي
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='kpi-card'><h3>📦 المنتجات</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2:
        # نفترض وجود عمود مبيعات، إذا لم يوجد نضع 0
        sales_val = df['المبيعات'].sum() if 'المبيعات' in df.columns else 0
        st.markdown(f"<div class='kpi-card' style='border-right-color:#3b82f6;'><h3>💰 إجمالي المبيعات</h3><h2>{sales_val:,.0f}</h2></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='kpi-card' style='border-right-color:#f59e0b;'><h3>🕒 حالة التحديث</h3><h2>لحظي</h2></div>", unsafe_allow_html=True)

    st.info("💡 نصيحة: انتقل إلى 'التحليل المالي' في القائمة الجانبية لرؤية الرسوم البيانية.")
else:
    st.warning("👈 يرجى رفع ملف من القائمة الجانبية للبدء.")
