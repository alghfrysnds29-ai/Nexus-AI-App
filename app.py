import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import google.generativeai as genai

# --- 1. إعداد الاتصال بـ Google AI Studio ---
# تم وضع مفتاحك الخاص هنا كما طلبتِ
API_KEY = "AIzaSyB_N6EddEKaftVX2DgrA_5_5jSK2T2DCvA"
genai.configure(api_key=API_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. إعدادات الهوية البصرية (Nexus AI) ---
st.set_page_config(page_title="Nexus AI - Supply Chain Command Center", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main { background-color: #0f172a; color: #f8fafc; }
    .stMetric { background: #1e293b; padding: 20px; border-radius: 15px; border: 1px solid #334155; }
    .report-card { background: #1e293b; padding: 25px; border-radius: 15px; border-right: 8px solid #3b82f6; box-shadow: 0 10px 15px rgba(0,0,0,0.2); direction: rtl; margin-top: 15px; }
    .stButton>button { width: 100%; border-radius: 12px; background: linear-gradient(90deg, #3b82f6, #1d4ed8); color: white; font-weight: bold; border: none; height: 3.5em; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. محرك البيانات (بيانات حقيقية لشركة تجارة إلكترونية) ---
@st.cache_data
def get_massive_demo_data():
    data = {
        "المنتج": ["عباية فاخرة", "عطر دهن العود", "ساعة ذكية Pro", "طقم بخور ملكي", "قفطان مغربي", "قهوة مختصة 1كجم", "مبخرة كهربائية"],
        "المخزون الحالي": [15, 80, 5, 120, 8, 200, 45],
        "المبيعات الشهرية": [150, 45, 95, 20, 40, 310, 15],
        "التكلفة (ر.س)": [250, 120, 450, 80, 300, 65, 110],
        "سعر البيع (ر.س)": [550, 350, 999, 220, 750, 145, 280],
        "المرتجعات (%)": [2.5, 1.2, 5.0, 0.5, 12.0, 1.0, 18.5]
    }
    df = pd.DataFrame(data)
    df['صافي الربح للمنتج'] = (df['سعر البيع (ر.س)'] - df['التكلفة (ر.س)']) * df['المبيعات الشهرية']
    return df

# --- 4. واجهة المستخدم الرئيسية ---
st.title("🦅 Nexus AI: Global Supply Chain Control")
st.markdown("### نظام منى محمد لإدارة العمليات والذكاء الاصطناعي")

# مركز الرفع في القائمة الجانبية
st.sidebar.header("📥 مركز البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف إكسل أو CSV لمتجرك", type=['csv', 'xlsx'])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
    st.sidebar.success("تم تحليل ملفك بنجاح!")
else:
    df = get_massive_demo_data()
    st.sidebar.info("يتم الآن عرض 'بيانات تجريبية'. ارفعي ملفك للتحليل الخاص.")

# --- 5. لوحة المؤشرات (Dashboard) ---
c1, c2, c3, c4 = st.columns(4)
total_revenue = (df['المبيعات الشهرية'] * df['سعر البيع (ر.س)']).sum()
total_profit = df['صافي الربح للمنتج'].sum()
avg_returns = df['المرتجعات (%)'].mean()

c1.metric("إجمالي المبيعات", f"{total_revenue:,} ر.س")
c2.metric("صافي الربح المتوقع", f"{total_profit:,} ر.س")
c3.metric("معدل المرتجعات", f"{avg_returns:.1f}%")
c4.metric("حالة الإمداد", "مستقر" if avg_returns < 10 else "خطر")

st.markdown("---")

# --- 6. التحليل البصري ---
col_charts_1, col_charts_2 = st.columns(2)

with col_charts_1:
    st.subheader("📊 أداء المنتجات (الربحية مقابل المخزون)")
    fig = px.scatter(df, x="المخزون الحالي", y="صافي الربح للمنتج", size="المبيعات الشهرية", color="المنتج", text="المنتج")
    st.plotly_chart(fig, use_container_width=True)

with col_charts_2:
    st.subheader("🤖 تحليل الاستدامة (Gemini AI)")
    st.write("اضغطي على الزر ليقوم الذكاء الاصطناعي بفحص أرقامك وتقديم توصيات استراتيجية.")
    
    if st.button("🌟 استشارة المستشار الذكي"):
        with st.spinner('جاري الاتصال بـ Google AI Studio...'):
            # تحضير البيانات لـ Gemini
            data_summary = df.to_string()
            prompt = f"""
            أنت خبير استراتيجي في سلاسل الإمداد والتسويق الرقمي للسوق السعودي.
            بناءً على هذه البيانات الحقيقية لمتجري:
            {data_summary}
            
            المطلوب:
            1. حدد أخطر منتج من حيث المرتجعات واقترح حلاً.
            2. أي منتج يجب أن أزيد ميزانية إعلاناته فوراً؟
            3. نصيحة لوجستية لتقليل تكلفة المخزون.
            أجب بلهجة احترافية وقوية.
            """
            
            response = ai_model.generate_content(prompt)
            st.markdown(f"<div class='report-card'>{response.text}</div>", unsafe_allow_html=True)
            st.balloons()

# --- 7. تفاصيل إضافية ---
st.markdown("---")
with st.expander("📂 معاينة البيانات الخام"):
    st.dataframe(df, use_container_width=True)

st.caption("تم التطوير بواسطة Nexus AI - جميع الحقوق محفوظة لمنى محمد")
