import streamlit as st
import pandas as pd
import plotly.express as px

# 1. التنسيق الجمالي (ثيم فخم)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #D4AF37 !important; font-family: 'Cairo', sans-serif; text-align: right; }
    div[data-testid="stMetric"] { background-color: #1c1f26; border: 1px solid #D4AF37; border-radius: 15px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💰 التحليل المالي الاستراتيجي")
st.markdown("---")

# 2. التحقق من البيانات
if 'main_df' in st.session_state:
    df = st.session_state['main_df']
    
    # محاولة العثور على أعمدة مالية (مبيعات، أرباح، تكلفة)
    cols = df.columns.tolist()
    sales_col = next((c for c in cols if "مبيعات" in c or "Sales" in c or "Revenue" in c), None)
    profit_col = next((c for c in cols if "ربح" in c or "Profit" in c), None)

    if sales_col:
        # حساب المؤشرات المالية
        total_sales = df[sales_col].sum()
        avg_deal = df[sales_col].mean()
        
        c1, c2 = st.columns(2)
        c1.metric("إجمالي الإيرادات", f"{total_sales:,.2f} $")
        c2.metric("متوسط قيمة العمليات", f"{avg_deal:,.2f} $")

        # رسم بياني مالي (توزيع المبيعات)
        st.subheader("📈 توزيع المبيعات العام")
        fig_sales = px.area(df, y=sales_col, title="مخطط تدفق السيولة",
                            line_shape="spline", color_discrete_sequence=['#D4AF37'])
        fig_sales.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#D4AF37"))
        st.plotly_chart(fig_sales, use_container_width=True)

        if profit_col:
            st.subheader("💹 تحليل الأرباح الصافية")
            fig_profit = px.line(df, y=profit_col, title="منحنى الربحية",
                                 color_discrete_sequence=['#FFFFFF']) # لون أبيض للتباين مع الذهبي
            fig_profit.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#D4AF37"))
            st.plotly_chart(fig_profit, use_container_width=True)
    else:
        st.warning("⚠️ لم يتم العثور على أعمدة مالية واضحة (مبيعات أو أرباح).")
else:
    st.error("🚨 الرجاء رفع ملف البيانات من الصفحة الرئيسية أولاً.")

st.markdown("---")
st.caption("Nexus AI Financial Module v3.0")
