import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(
    page_title="Nexus AI | نظام إدارة البيانات", 
    page_icon="💎", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. تنسيق الواجهة (CSS) لتصحيح RTL ودعم الخطوط ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    
    .stMetric {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-right: 5px solid #007bff;
    }
    
    /* محاذاة العناصر في الشريط الجانبي */
    [data-testid="stSidebar"] {
        direction: rtl;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. محرك توليد البيانات التجريبية ---
@st.cache_data
def load_data(rows=1000):
    np.random.seed(42)
    categories = ['إلكترونيات', 'مستلزمات منزلية', 'أزياء', 'أدوات تجميل', 'ألعاب أطفال']
    suppliers = [f'المورد العالمي {i}' for i in range(1, 11)]
    
    data = {
        "المنتج": [f"منتج نمطي {i}" for i in range(1, rows + 1)],
        "الفئة": np.random.choice(categories, rows),
        "المورد": np.random.choice(suppliers, rows),
        "المخزون": np.random.randint(10, 500, rows),
        "المبيعات": np.random.randint(5, 1000, rows),
        "التكلفة": np.random.uniform(20, 1500, rows).round(2),
        "سعر_البيع": np.random.uniform(50, 3000, rows).round(2),
        "زمن_التوريد": np.random.randint(3, 30, rows)
    }
    
    df = pd.DataFrame(data)
    # تصحيح الأسعار لضمان وجود ربح
    df['سعر_البيع'] = df[['التكلفة', 'سعر_البيع']].max(axis=1) + 20
    return df

# --- 4. محرك التحليل والعمليات الحسابية ---
def perform_analysis(df, ship_cost, tax_rate, op_rate):
    d = df.copy()
    
    # حساب التكاليف
    d['تكلفة_الهبوط'] = d['التكلفة'] + ship_cost
    d['ضريبة_القيمة'] = d['سعر_البيع'] * (tax_rate / 100)
    
    # حساب الأرباح
    d['إجمالي_الربح'] = (d['سعر_البيع'] - (d['تكلفة_الهبوط'] + d['ضريبة_القيمة'])) * d['المبيعات']
    d['صافي_الربح'] = d['إجمالي_الربح'] * (1 - (op_rate / 100))
    
    # لوجستيات المخزون
    d['نقطة_إعادة_الطلب'] = ((d['المبيعات'] / 30) * d['زمن_التوريد'] * 1.2).astype(int)
    
    # تصنيف ABC
    d = d.sort_values(by='صافي_الربح', ascending=False)
    d['الربح_التراكمي'] = d['صافي_الربح'].cumsum()
    total_profit = d['صافي_الربح'].sum() if d['صافي_الربح'].sum() != 0 else 1
    d['نسبة_الربح'] = (d['الربح_التراكمي'] / total_profit) * 100
    
    d['التصنيف'] = d['نسبة_الربح'].apply(
        lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)')
    )
    
    return d

# --- 5. الشريط الجانبي والمدخلات ---
st.sidebar.header("⚙️ إعدادات النظام")
store_name = st.sidebar.text_input("اسم المشروع/المتجر", "مؤسسة الأعمال الذكية")

with st.sidebar.expander("📊 معايير الحساب المالية"):
    shipping = st.number_input("تكلفة الشحن للقطعة", 0.0, 500.0, 15.0)
    tax = st.slider("نسبة الضريبة (%)", 0, 25, 15)
    ops = st.slider("المصاريف التشغيلية (%)", 0, 50, 10)

# خيار رفع الملفات أو استخدام البيانات التجريبية
uploaded_file = st.sidebar.file_uploader("ارفع ملف مبيعاتك (اختياري)", type=['csv', 'xlsx'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('csv'):
            raw_data = pd.read_csv(uploaded_file)
        else:
            raw_data = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"حدث خطأ في قراءة الملف: {e}")
        raw_data = load_data()
else:
    raw_data = load_data()

# تنفيذ التحليل
df = perform_analysis(raw_data, shipping, tax, ops)

# --- 6. الواجهة الرئيسية والعرض ---
st.title(f"🚀 لوحة تحكم: {store_name}")

# صف المؤشرات الرئيسية
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("صافي الأرباح الكلية", f"{df['صافي_الربح'].sum():,.0f} ر.س")
with kpi2:
    stock_value = (df['المخزون'] * df['التكلفة']).sum()
    st.metric("قيمة المخزون الحالية", f"{stock_value:,.0f} ر.س")
with kpi3:
    critical_count = len(df[df['المخزون'] <= df['نقطة_إعادة_الطلب']])
    st.metric("منتجات تحتاج طلب", critical_count, delta_color="inverse")
with kpi4:
    roi = (df['صافي_الربح'].sum() / stock_value * 100) if stock_value > 0 else 0
    st.metric("العائد المتوقع (ROI)", f"{roi:.1f}%")

st.markdown("---")

# تبويبات العرض
tab1, tab2, tab3 = st.tabs(["📈 التحليل المالي", "📦 إدارة المخزون", "📋 تفاصيل البيانات"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        fig1 = px.pie(df, names='التصنيف', values='صافي_الربح', title="توزيع الربح حسب أهمية المنتجات (ABC)")
        st.plotly_chart(fig1, use_container_width=True)
    with col_b:
        fig2 = px.bar(df.groupby('الفئة')['صافي_الربح'].sum().reset_index(), 
                      x='الفئة', y='صافي_الربح', color='الفئة', title="صافي الربح حسب فئة المنتج")
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("⚠️ تنبيهات المخزون الحرجة")
    critical_df = df[df['المخزون'] <= df['نقطة_إعادة_الطلب']].head(20)
    if not critical_df.empty:
        st.dataframe(critical_df[['المنتج', 'المخزون', 'نقطة_إعادة_الطلب', 'المورد']], use_container_width=True)
    else:
        st.success("جميع مستويات المخزون ضمن النطاق الآمن.")

with tab3:
    st.subheader("قاعدة البيانات الكاملة المعالجة")
    st.dataframe(df, use_container_width=True)

# --- 7. تصدير التقارير ---
st.markdown("---")
st.subheader("📑 تصدير التقارير")

# دالة تحويل البيانات إلى Excel بصيغة Bytes
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Report')
        # تنسيق بسيط للأعمدة
        writer.close()
    return output.getvalue()

excel_data = to_excel(df)

st.download_button(
    label="📥 تحميل التقرير التحليلي الكامل (Excel)",
    data=excel_data,
    file_name=f"Report_{store_name}_{datetime.now().strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption("تم تطوير النظام بواسطة Nexus AI Enterprise 2026")
