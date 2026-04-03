import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title("🤖 التنبؤ الذكي بالطلب")

if 'main_df' in st.session_state:
    df = st.session_state['main_df']
    
    # محاولة إيجاد عمود أرقام للتحليل
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        target = numeric_cols[0]
        y = df[target].values
        x = np.arange(len(y))
        
        # خط الاتجاه
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, name='البيانات الفعلية', line=dict(color='#D4AF37')))
        fig.add_trace(go.Scatter(x=x, y=p(x), name='التوجه (Trend)', line=dict(color='white', dash='dash')))
        
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="#D4AF37"))
        st.plotly_chart(fig, use_container_width=True)
        
        status = "📈 صعود متوقع" if z[0] > 0 else "📉 هبوط محتمل"
        st.subheader(f"النتيجة: {status}")
    else:
        st.warning("الملف لا يحتوي على أعمدة رقمية للتحليل.")
else:
    st.error("الرجاء رفع ملف البيانات من الصفحة الرئيسية أولاً.")
