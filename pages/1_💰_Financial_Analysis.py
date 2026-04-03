import streamlit as st
import plotly.express as px

st.set_page_config(page_title="التحليل المالي", layout="wide")

if 'main_df' in st.session_state:
    df = st.session_state['main_df']
    st.title("💰 تحليلات الأداء المالي")

    col_charts, col_table = st.columns([2, 1])

    with col_charts:
        # رسم بياني: مبيعات كل فئة أو منتج
        target_col = 'المنتج' if 'المنتج' in df.columns else df.columns[0]
        val_col = 'المبيعات' if 'المبيعات' in df.columns else df.columns[1]
        
        fig = px.bar(df.head(10), x=target_col, y=val_col, 
                     color=val_col, title="أعلى 10 عناصر مبيعاً",
                     color_continuous_scale='Viridis', template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        fig_pie = px.sunburst(df.head(20), path=[target_col], values=val_col, 
                              title="توزيع الحصص السوقية للمنتجات")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_table:
        st.write("### ملخص سريع")
        st.dataframe(df[[target_col, val_col]].sort_values(by=val_col, ascending=False), height=500)
else:
    st.error("❌ لا توجد بيانات! يرجى رفع الملف من الصفحة الرئيسية.")
