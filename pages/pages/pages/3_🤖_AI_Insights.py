import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="التنبؤ الذكي", layout="wide")

# CSS الثيم الذهبي والأسود
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"], .main { background-color: #121212; color: #D4AF37; font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .stMetric { background-color: #1e1e1e; border: 1px solid #D4AF37; border-radius: 10px; }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; }
    h1, h2, h3 { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 مساعد Nexus للتنبؤ الذكي")

if 'main_df' in st.session_state:
    df = st.session_state['main_df']
    
    # محاكاة بيانات زمنية إذا لم تتوفر تواريخ (لتفعيل خط الاتجاه)
    # سنفترض أن الصفوف تمثل مبيعات أيام متتالية
    y = df['المبيعات'].values if 'المبيعات' in df.columns else np.random.randint(100, 500, len(df))
    x = np.arange(len(y))
    
    # حساب خط الاتجاه الرياضي (Linear Regression)
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    
    # التنبؤ بالشهر القادم (30 نقطة إضافية)
    next_val = p(len(y) + 30)
    current_avg = np.mean(y[-7:]) # متوسط آخر 7 أيام
    
    # عرض النتيجة
    c1, c2 = st.columns(2)
    with c1:
        diff = next_val - current_avg
        st.metric("توقع مبيعات الشهر القادم", f"{next_val:,.0f}", f"{diff:,.0f} عن الحالي")
        
    with c2:
        status = "📈 نمو متوقع" if diff > 0 else "📉 انخفاض محتمل"
        st.subheader(f"حالة السوق: {status}")
        st.write("بناءً على تحليل الاتجاه الحالي، ننصح بضبط مستويات المخزون.")

    # الرسم البياني لخط الاتجاه
    fig = go.Figure()
    # البيانات الحقيقية
    fig.add_trace(go.Scatter(x=x, y=y, name='المبيعات الفعلية', line=dict(color='#D4AF37')))
    # خط الاتجاه
    fig.add_trace(go.Scatter(x=x, y=p(x), name='خط الاتجاه (Trend)', line=dict(color='white', dash='dash')))
    
    fig.update_layout(title="تحليل الاتجاه العام للمبيعات",
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(color="#D4AF37"),
                      xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False))
    
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("يرجى رفع البيانات من الصفحة الرئيسية.")
