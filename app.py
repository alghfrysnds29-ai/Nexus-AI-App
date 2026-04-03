import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. إعدادات الهوية البصرية ---
st.set_page_config(page_title="Nexus AI - Enterprise Analytics", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    .report-card { background: white; padding: 20px; border-radius: 15px; border-right: 8px solid #3b82f6; box-shadow: 0 4px 12px rgba(0,0,0,0.1); direction: rtl; margin-bottom: 15px; }
    .stMetric { background: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة توليد بيانات حقيقية (Demo Data) ---
def get_demo_data():
    return pd.DataFrame([
        {"المنتج": "عباية كلاسيك سوداء", "المخزون": 45, "المبيعات": 120, "التكلفة": 150, "سعر البيع": 350, "المرتجعات": 5},
        {"المنتج": "عطر لافندر 100مل", "المخزون": 12, "المبيعات": 340, "التكلفة": 80, "سعر البيع": 199, "المرتجعات": 12},
        {"المنتج": "ساعة ذكية Pro", "المخزون": 5, "المبيعات": 85, "التكلفة": 400, "سعر البيع": 850, "المرتجعات": 2},
        {"المنتج": "طقم بخور ملكي", "المخزون": 80, "المبيعات": 20, "التكلفة": 120, "سعر البيع": 280, "المرتجعات": 0}
    ])

# --- 3. واجهة المستخدم ---
st.title("🦅 Nexus AI Enterprise")
st.markdown("### حلول تحليل البيانات المتقدمة للمتاجر الإلكترونية")

# سحب الملف من المستخدم
st.sidebar.header("📥 مركز رفع البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف إكسل أو CSV لمتجرك", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("تم رفع الملف بنجاح!")
    except Exception as e:
        st.sidebar.error("خطأ في قراءة الملف. تأكد من الصيغة.")
        df = get_demo_data()
else:
    st.sidebar.info("يتم عرض 'بيانات تجريبية' لشركة افتراضية حالياً. ارفع ملفك للتحليل الخاص.")
    df = get_demo_data()

# --- 4. لوحة المؤشرات الذكية ---
total_revenue = (df['المبيعات'] * df['سعر البيع']).sum()
total_profit = ((df['سعر البيع'] - df['التكلفة']) * df['المبيعات']).sum()
avg_return_rate = (df['المرتجعات'].sum() / df['المبيعات'].sum()) * 100

c1, c2, c3 = st.columns(3)
c1.metric("إجمالي المبيعات", f"{total_revenue:,} ريال")
c2.metric("صافي الأرباح المتوقعة", f"{total_profit:,} ريال")
c3.metric("معدل المرتجعات العام", f"{avg_return_rate:.1f}%")

st.markdown("---")

# --- 5. التحليل البصري ---
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📊 أداء المنتجات (الربح مقابل المخزون)")
    df['الربح'] = (df['سعر البيع'] - df['التكلفة']) * df['المبيعات']
    fig = px.scatter(df, x="المخزون", y="الربح", size="المبيعات", color="المنتج", text="المنتج")
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("💡 توصيات الذكاء الاصطناعي")
    
    # منطق التحليل التلقائي
    for index, row in df.iterrows():
        if row['المخزون'] < 10:
            st.markdown(f"<div class='report-card'>⚠️ <b>خطر نفاذ:</b> المنتج '{row['المنتج']}' شارف على الانتهاء. أوقف الإعلانات فوراً أو اطلب كمية جديدة.</div>", unsafe_allow_html=True)
        if row['المرتجعات'] > (row['المبيعات'] * 0.1):
            st.markdown(f"<div class='report-card' style='border-right-color: #ef4444;'>🚨 <b>خسارة مرتجعات:</b> المنتج '{row['المنتج']}' لديه نسبة استرجاع عالية. راجع الجودة أو الوصف.</div>", unsafe_allow_html=True)
        if row['المخزون'] > 50 and row['المبيعات'] < 30:
            st.markdown(f"<div class='report-card' style='border-right-color: #f59e0b;'>📦 <b>مخزون راكد:</b> المنتج '{row['المنتج']}' لا يباع جيداً. اقترح عمل عرض 'اشتر واحد واحصل على الثاني مجاناً'.</div>", unsafe_allow_html=True)

# عرض الجدول الكامل
with st.expander("👁️ عرض جدول البيانات الكامل"):
    st.write(df)
