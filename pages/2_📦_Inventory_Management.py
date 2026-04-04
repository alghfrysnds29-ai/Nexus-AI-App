import streamlit as st
import pandas as pd
import plotly.express as px

# 1. إعداد الصفحة (نلاحظ عدم تكرار set_page_config إذا كان يسبب مشاكل في بعض الإصدارات، لكن سنضعه هنا لضمان الثيم)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #D4AF37 !important; font-family: 'Cairo', sans-serif; text-align: right; }
    div[data-testid="stMetric"] { background-color: #1c1f26; border: 1px solid #D4AF37; border-radius: 15px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; }
    /* تحسين شكل الجدول */
    .stDataFrame { border: 1px solid #D4AF37; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📦 إدارة المخزون وسلاسل الإمداد")
st.markdown("---")

# 2. التحقق من وجود بيانات في ذاكرة الجلسة
if 'main_df' in st.session_state:
    df = st.session_state['main_df']

    # محاولة تحديد الأعمدة المناسبة (المخزون، المنتج)
    # سنبحث عن أعمدة تحتوي على كلمات "مخزون" أو "كمية" أو "المنتج"
    cols = df.columns.tolist()
    prod_col = next((c for c in cols if "منتج" in c or "الاسم" in c), cols[0])
    stock_col = next((c for c in cols if "مخزون" in c or "كمية" in c or "Stock" in c), None)

    if stock_col:
        # حساب إحصائيات المخزون
        total_stock = df[stock_col].sum()
        avg_stock = df[stock_col].mean()
        low_stock_count = len(df[df[stock_col] < 10]) # افترضنا أن أقل من 10 هو مخزون منخفض

        # عرض البطاقات الذهبية
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي القطع في المخزن", f"{total_stock:,.0f}")
        c2.metric("متوسط المخزون لكل منتج", f"{avg_stock:,.1f}")
        c3.metric("منتجات قاربت على النفاذ", low_stock_count)

        st.markdown("---")

        # رسم بياني للمخزون (أعلى 15 منتج)
        st.subheader("📊 تحليل مستويات المخزون الحالي")
        fig_stock = px.bar(
            df.sort_values(by=stock_col, ascending=False).head(15),
            x=prod_col,
            y=stock_col,
            title="أعلى 15 منتج من حيث كمية المخزون",
            color_continuous_scale='Sunset',
            color=stock_col,
            template="plotly_dark"
        )
        fig_stock.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#D4AF37"))
        st.plotly_chart(fig_stock, use_container_width=True)

        # جدول البيانات التفصيلي
        st.subheader("📋 تفاصيل المستودع")
        st.dataframe(df[[prod_col, stock_col]].sort_values(by=stock_col), use_container_width=True)
    
    else:
        st.warning("⚠️ لم يتم العثور على عمود باسم 'المخزون' أو 'الكمية' في ملفك. يرجى التأكد من تسمية الأعمدة بشكل صحيح.")
        st.write("الأعمدة المتاحة في ملفك هي:", cols)

else:
    st.error("🚨 لا توجد بيانات! يرجى العودة للصفحة الرئيسية ورفع ملف Excel/CSV أولاً.")
    if st.button("العودة للرئيسية"):
        st.switch_page("Main_Dashboard.py")

st.markdown("---")
st.caption("Nexus AI Inventory Module v3.0")
