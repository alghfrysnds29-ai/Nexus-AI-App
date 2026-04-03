import streamlit as st
import plotly.express as px

st.set_page_config(page_title="إدارة المخزون", layout="wide")

st.title("📦 مراقبة المخزون والأمان")

if 'main_df' in st.session_state:
    df = st.session_state['main_df']
    
    st.write("### تحليل مستويات المخزون")
    # يمكنك إضافة كود حساب نقطة إعادة الطلب هنا
    st.dataframe(df, use_container_width=True)
else:
    st.error("رجاءً ارفع ملف البيانات من الصفحة الرئيسية أولاً.")
