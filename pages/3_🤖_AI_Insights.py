import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. التنسيق الجمالي (ثيم فخم متوافق مع باقي الصفحات)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background-color: #0e1117; }
    h1, h2, h3, p, span, label { color: #D4AF37 !important; font-family: 'Cairo', sans-serif; text-align: right; }
    div[data-testid="stMetric"] { background-color: #1c1f26; border: 1px solid #D4AF37; border-radius: 15px; padding: 15px; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 تحليلات Nexus AI والتنبؤ المستقبلي")
st.markdown("---")

# 2. التحقق من البيانات
if 'main_df' in st.session_state:
    df = st.session_state['main_df']
    
    # محاولة العثور على عمود رقمي (مبيعات أو أرباح)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numeric_cols) > 0:
        # اختيار العمود المراد التنبؤ به (يفضل المبيعات)
        target_col = next((c for c in numeric_cols if "مبيعات" in c or "ربح" in c or "Sales" in c), numeric_cols[0])
        
        st.subheader(f"تحليل اتجاه: {target_col}")
        
        # تجهيز البيانات للرياضيات
        y = df[target_col].values
        x = np.arange(len(y))
        
        # حساب خط الاتجاه (Linear Regression Trend)
        z = np.polyfit(x, y, 1) # معادلة الخط المستقيم
        p = np.poly1d(z)
        
        # التنبؤ بالنقطة القادمة (المستقبل)
        next_step = len(y) + 5 # توقع الخطوة القادمة
        predicted_val = p(next_step)
        current_avg = np.mean(y[-5:]) if len(y) > 5 else np.mean(y)
        
        # عرض النتائج في بطاقات فخمة
        c1, c2 = st.columns(2)
        with c1:
            diff = predicted_val - current_avg
            delta_color = "normal" if diff > 0 else "inverse"
            st.metric("التوقع للفترة القادمة", f"{predicted_val:,.0f}", f"{diff:,.1f}", delta_color=delta_color)
            
        with c2:
            trend_text = "📈 نمو مستمر" if z[0] > 0 else "📉 هبوط محتمل"
            st.markdown(f"### حالة السوق الحالية: \n ## {trend_text}")

        # الرسم البياني للتنبؤ (Plotly)
        fig = go.Figure()
        # البيانات الحقيقية
        fig.add_trace(go.Scatter(x=x, y=y, name='الأداء الفعلي', line=dict(color='#D4AF37', width=3)))
        # خط التنبؤ
        fig.add_trace(go.Scatter(x=x, y=p(x), name='مسار التنبؤ الذكي', line=dict(color='white', dash='dash')))
        
        fig.update_layout(
            title="رسم بياني لخط الاتجاه الزمني",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#D4AF37"),
            xaxis=dict(showgrid=False, title="الزمن/العمليات"),
            yaxis=dict(showgrid=False, title="القيمة"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # قسم النصيحة الذكية
        st.markdown("---")
        st.subheader("💡 توصية Nexus AI:")
        if z[0] > 0:
            st.success("البيانات تظهر اتجاهاً تصاعدياً. ننصح بزيادة الاستثمار وتوسيع المخزون لتلبية الطلب المتزايد.")
        else:
            st.warning("نلاحظ تباطؤاً في النمو. ننصح بمراجعة استراتيجية التسعار أو عمل حملات ترويجية لتنشيط المبيعات.")
            
    else:
        st.error("الملف المرفوع لا يحتوي على أعمدة رقمية كافية لإجراء التنبؤ.")
else:
    st.info("🚨 يرجى العودة للصفحة الرئيسية ورفع الملف أولاً لتفعيل محرك الذكاء الاصطناعي.")

st.markdown("---")
st.caption("Powered by Nexus AI Predictive Engine 2026")
