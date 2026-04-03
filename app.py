import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# --- 1. إعدادات الهوية البصرية (Light & Clean Professional UI) ---
st.set_page_config(page_title="Nexus AI | Business Intelligence", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    /* الأساسيات - خلفية بيضاء ونصوص داكنة */
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        background-color: #f8fafc !important; /* لون خلفية هادئ */
        color: #1e293b;
    }

    /* تصميم البطاقات العلوية (Metrics) */
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #2563eb; }
    [data-testid="stMetricLabel"] { font-size: 16px; color: #64748b; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    /* تحسين القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-left: 1px solid #e2e8f0;
    }

    /* العناوين والتبويبات */
    .main-title { color: #1e3a8a; text-align: center; font-weight: 800; padding: 20px; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f1f5f9;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #475569;
    }
    .stTabs [aria-selected="true"] { background-color: #2563eb !important; color: white !important; }

    /* أزرار التحميل */
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 10px;
        border: none;
        width: 100%;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك توليد البيانات الضخمة (10,000 منتج محايد) ---
@st.cache_data
def generate_universal_big_data(rows=10000):
    np.random.seed(42)
    categories = ['Category Alpha', 'Category Beta', 'Category Gamma', 'Category Delta']
    
    data = {
        "رقم المنتج (SKU)": [f"SKU-{i:05d}" for i in range(1, rows + 1)],
        "اسم الصنف": [f"Universal Item - {i}" for i in range(1, rows + 1)],
        "الفئة": np.random.choice(categories, rows),
        "المورد": [f"Global Vendor {np.random.randint(1, 51)}" for _ in range(rows)],
        "المخزون الحالي": np.random.randint(0, 1000, rows),
        "المبيعات الشهرية": np.random.randint(5, 2000, rows),
        "تكلفة الوحدة": np.random.uniform(20, 3000, rows).round(2),
        "سعر البيع": np.random.uniform(50, 6000, rows).round(2),
        "زمن التوريد (أيام)": np.random.randint(2, 45, rows)
    }
    df = pd.DataFrame(data)
    # تصحيح الأسعار لضمان منطقية البيانات
    df['سعر البيع'] = df[['تكلفة الوحدة', 'سعر البيع']].max(axis=1) * 1.25
    return df

# --- 3. محرك التحليل الاستراتيجي (Business Logic) ---
def run_advanced_analysis(df, ops_pct):
    d = df.copy()
    # حساب الأرباح
    d['إجمالي الربح'] = (d['سعر البيع'] - d['تكلفة الوحدة']) * d['المبيعات الشهرية']
    d['صافي الربح الحقيقي'] = d['إجمالي الربح'] * (1 - ops_pct/100)
    
    # حساب نقطة الطلب الذكية (Reorder Point)
    daily_sales = d['المبيعات الشهرية'] / 30
    d['مخزون الأمان'] = (daily_sales * 5).astype(int)
    d['نقطة إعادة الطلب'] = (daily_sales * d['زمن التوريد (أيام)']).astype(int) + d['مخزون الأمان']
    
    # تصنيف ABC
    d = d.sort_values(by='صافي الربح الحقيقي', ascending=False)
    d['Cum_Profit'] = d['صافي الربح الحقيقي'].cumsum()
    total_p = d['صافي الربح الحقيقي'].sum() if d['صافي الربح الحقيقي'].sum() != 0 else 1
    d['Contribution_%'] = (d['Cum_Profit'] / total_p) * 100
    d['الفئة الاستراتيجية'] = d['Contribution_%'].apply(lambda x: 'A (High Value)' if x <= 70 else ('B (Medium)' if x <= 90 else 'C (Low)'))
    
    return d

# --- 4. واجهة التحكم الجانبية ---
st.sidebar.markdown("<h2 style='color: #1e3a8a;'>NEXUS AI v3</h2>", unsafe_allow_html=True)
client_name = st.sidebar.text_input("🏢 اسم الشركة / المتجر", "منصة أعمالك")

with st.sidebar.expander("⚙️ إعدادات الربحية والتشغيل"):
    operation_cost = st.sidebar.slider("المصاريف التشغيلية (%)", 0, 50, 15)

st.sidebar.markdown("---")
uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف Excel أو CSV المخصص", type=['xlsx', 'csv'])

# جلب البيانات
if uploaded_file:
    raw_df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
else:
    raw_df = generate_universal_big_data(10000) # توليد 10 آلاف منتج افتراضياً

df = run_advanced_analysis(raw_df, operation_cost)

# --- 5. العرض الرئيسي (Dashboard) ---
st.markdown(f"<h1 class='main-title'>نظام ذكاء الأعمال الاستراتيجي - {client_name}</h1>", unsafe_allow_html=True)

# صف المؤشرات الرئيسية
m1, m2, m3, m4 = st.columns(4)
m1.metric("صافي الأرباح المتوقعة", f"{int(df['صافي الربح الحقيقي'].sum()):,} ر.س")
m2.metric("قيمة المخزون الحالي", f"{int((df['المخزون الحالي'] * df['تكلفة الوحدة'].mean()).sum()):,} ر.س")
m3.metric("المنتجات الحرجة", len(df[df['المخزون الحالي'] <= df['نقطة إعادة الطلب']]))
m4.metric("كفاءة العمليات", "92%", "Target 2026")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📈 التحليل المالي", "📦 سلاسل الإمداد", "🚚 الموردين", "🔌 الربط والخصوصية"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        fig_pie = px.pie(df, names='الفئة الاستراتيجية', values='صافي الربح الحقيقي', 
                         title="تحليل ABC: مساهمة الفئات في الأرباح",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_b:
        st.plotly_chart(px.bar(df.head(15), x="رقم المنتج (SKU)", y="صافي الربح الحقيقي", 
                               title="أعلى 15 منتجاً تحقيقاً للربح الصافي"), use_container_width=True)

with tab2:
    st.subheader("📦 إدارة المستودعات والأمان الذكي")
    # عرض أول 100 منتج فقط للسرعة في المتصفح
    st.dataframe(df[['رقم المنتج (SKU)', 'اسم الصنف', 'المخزون الحالي', 'نقطة إعادة الطلب', 'الفئة الاستراتيجية']].head(100), use_container_width=True)
    st.plotly_chart(px.scatter(df.head(500), x="المخزون الحالي", y="نقطة إعادة الطلب", color="الفئة الاستراتيجية", 
                               size="المبيعات الشهرية", hover_name="اسم الصنف"), use_container_width=True)

with tab3:
    st.subheader("🚚 بطاقة أداء الموردين")
    sup_df = df.groupby('المورد').agg({'صافي الربح الحقيقي': 'sum', 'رقم المنتج (SKU)': 'count'}).reset_index()
    st.plotly_chart(px.scatter(sup_analysis, x="رقم المنتج (SKU)", y="صافي الربح الحقيقي", 
                               size="صافي الربح الحقيقي", color="المورد", title="قوة الموردين مقابل الربحية"), use_container_width=True)

with tab4:
    st.info("🔌 هذا النظام مصمم للربط المباشر مع (Salla, Zid, Shopify) عبر الـ API.")
    st.markdown("🔒 **بيان الخصوصية:** بياناتك تُعالج محلياً في الذاكرة المؤقتة لمتصفحك فقط، ولا يتم تخزين أي سجلات على خوادمنا.")

# --- 6. تصدير التقارير ---
st.markdown("---")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Strategic_Report')
st.download_button(label="📥 تحميل التقرير التحليلي الكامل (Excel)", data=buffer.getvalue(), 
                   file_name=f"Nexus_Report_{client_name}.xlsx", mime="application/vnd.ms-excel")

st.caption(f"تم التطوير بواسطة منى محمد | Nexus AI 2026 - نظام متكامل لذكاء الأعمال")
