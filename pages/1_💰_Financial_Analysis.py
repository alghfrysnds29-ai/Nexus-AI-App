import streamlit as st
import plotly.express as px

st.set_page_config(page_title="التحليل المالي", layout="wide")

st.title("💰 التحليل المالي والربحية")

if 'main_df' in st.session_state:
    df = st.session_state['main_df']
    
    # هنا نضع كود الرسم البياني المالي
    if 'المبيعات' in df.columns:
        fig = px.pie(df, names='المنتج', values='المبيعات', title="توزيع المبيعات حسب المنتج", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("البيانات المرفوعة لا تحتوي على عمود 'المبيعات'.")
else:
    st.error("رجاءً ارفع ملف البيانات من الصفحة الرئيسية أولاً.")
