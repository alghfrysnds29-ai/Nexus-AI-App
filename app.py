import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime

# --- 1. إعدادات الهوية البصرية والواجهة ---
st.set_page_config(page_title="Nexus AI | Enterprise BI", page_icon="📊", layout="wide")

# تصميم CSS احترافي يدعم التوجه RTL والجمالية العالية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border-top: 4px solid #10b981; }
    .notification-badge { background-color: #ef4444; color: white; padding: 4px 8px; border-radius: 50%; font-size: 12px; vertical-align: top; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f1f5f9; border-radius: 10px 10px 0px 0px; gap: 1px; }
    .stTabs [aria-selected="true"] { background-color: #10b981 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك توليد البيانات الافتراضية (للأغراض التجريبية) ---
@st.cache_data
def generate_generic_data(rows=1000):
    np.random.seed(42)
    categories = ['فئة أ', 'فئة ب', 'فئة ج', 'فئة د']
    suppliers = [f'المورد {i}' for i in range(1, 21)]
    
    # إضافة بُعد الزمن: توليد تواريخ عشوائية خلال آخر 12 شهر
    end_date = pd.to_datetime('today')
    start_date = end_date - pd.DateOffset(days=365)
    random_dates = pd.to_datetime(np.random.randint(start_date.value, end_date.value, rows))
    
    data = {
        "تاريخ الطلب": random_dates,
        "المنتج": [f"عنصر تجاري {i}" for i in range(1, rows + 1)],
        "التصنيف": np.random.choice(categories, rows),
        "المورد": np.random.choice(suppliers, rows),
        "المخزون الحالي": np.random.randint(5, 1000, rows),
        "المبيعات الشهرية": np.random.randint(20, 2000, rows),
        "تكلفة الوحدة": np.random.uniform(10, 2000, rows).round(2),
        "سعر البيع": np.random.uniform(15, 4000, rows).round(2),
        "زمن التوريد (أيام)": np.random.randint(1, 30, rows),
        "المرتجعات": np.random.randint(0, 15, rows) # تم تقليلها لتكون نسبة واقعية
    }
    df = pd.DataFrame(data)
    # التأكد من منطقية السعر مقارنة بالتكلفة بهامش ربح يضمن عدم وجود خسارة افتراضية
    df['سعر البيع'] = df[['تكلفة الوحدة', 'سعر البيع']].max(axis=1) * 1.3
    return df 
# --- 3. محرك التحليل الذكي (The Intelligence Engine) ---
def advanced_analytics_engine(df, ship_cost, tax_pct, op_cost_pct):
    d = df.copy()
    
    # [أ] تحليل التكاليف الإضافية
    d['ضرائب ورسوم'] = d['سعر البيع'] * (tax_pct / 100)
    d['التكلفة الإجمالية للوحدة'] = d['تكلفة الوحدة'] + ship_cost + d['ضرائب ورسوم']
    
    # [ب] الربحية
    d['إجمالي الربح التقديري'] = (d['سعر البيع'] - d['التكلفة الإجمالية للوحدة']) * d['المبيعات الشهرية']
    d['صافي الربح النهائي'] = d['إجمالي الربح التقديري'] * (1 - op_cost_pct / 100)
    
    # [ج] إدارة المخزون (نقطة إعادة الطلب)
    avg_daily_sales = d['المبيعات الشهرية'] / 30
    d['مخزون الأمان'] = (avg_daily_sales * 1.5 * d['زمن التوريد (أيام)'] * 1.2 - (avg_daily_sales * d['زمن التوريد (أيام)'])).astype(int)
    d['نقطة إعادة الطلب'] = (avg_daily_sales * d['زمن التوريد (أيام)']).astype(int) + d['مخزون الأمان']
    
    # [د] تصنيف ABC الاستراتيجي
    d = d.sort_values(by='صافي الربح النهائي', ascending=False)
    d['Cum_Profit'] = d['صافي الربح النهائي'].cumsum()
    total_net = d['صافي الربح النهائي'].sum() if d['صافي الربح النهائي'].sum() != 0 else 1
    d['Profit_Pct'] = (d['Cum_Profit'] / total_net) * 100
    d['أهمية المنتج'] = d['Profit_Pct'].apply(lambda x: 'A (عالي الربحية)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (منخفض)'))
    
    return d

# --- 4. الشريط الجانبي والتحكم ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1548/1548914.png", width=100)
st.sidebar.title("إعدادات النظام")
business_name = st.sidebar.text_input("اسم المنشأة/المشروع", "نظام ذكاء الأعمال العام")

with st.sidebar.expander("💳 معايير التكلفة والضرائب"):
    ship_cost = st.number_input("متوسط شحن الوحدة", 0.0, 1000.0, 5.0)
    tax_pct = st.slider("نسبة الضرائب/الرسوم (%)", 0, 100, 15)
    op_cost = st.slider("المصاريف التشغيلية (%)", 0, 100, 10)

st.sidebar.markdown("---")
data_source = st.sidebar.radio("مصدر البيانات:", ["بيانات افتراضية للنظام", "رفع ملف Excel/CSV"])

if data_source == "رفع ملف Excel/CSV":
    uploaded_file = st.sidebar.file_uploader("اختر ملف البيانات", type=['xlsx', 'csv'])
    if uploaded_file:
        raw_df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
    else:
        st.info("يرجى رفع ملف للاستمرار، تم استخدام بيانات افتراضية مؤقتاً.")
        raw_df = generate_generic_data(500)
else:
    rows_to_gen = st.sidebar.slider("عدد السجلات المراد تحليلها", 100, 10000, 1000)
    raw_df = generate_generic_data(rows_to_gen)

# تشغيل المحرك
df = advanced_analytics_engine(raw_df, ship_cost, tax_pct, op_cost)

# --- 5. التنبيهات الذكية ---
critical_stock = df[df['المخزون الحالي'] <= df['نقطة إعادة الطلب']]
if not critical_stock.empty:
    st.markdown(f"### 🔔 تنبيهات الإدارة <span class='notification-badge'>{len(critical_stock.head(10))}</span>", unsafe_allow_html=True)
    with st.expander("المنتجات التي تتطلب إعادة طلب فورية"):
        st.warning(f"هناك {len(critical_stock)} منتجاً تجاوزوا نقطة الأمان.")
        st.table(critical_stock[['المنتج', 'المخزون الحالي', 'نقطة إعادة الطلب']].head(5))

# --- 6. لوحة القيادة (Dashboard) ---
st.title(f"📊 {business_name}")
st.subheader("تحليل الأداء الاستراتيجي والمالي")

# مقاييس الأداء الرئيسية (KPIs)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_profit = df['صافي الربح النهائي'].sum()
inventory_value = (df['المخزون الحالي'] * df['تكلفة الوحدة']).sum()
roi = (total_profit / (df['تكلفة الوحدة'] * df['المبيعات الشهرية']).sum()) * 100

kpi1.metric("إجمالي صافي الربح", f"{total_profit:,.0f}")
kpi2.metric("قيمة المخزون الراكد", f"{inventory_value:,.0f}")
kpi3.metric("معدل العائد ROI", f"{roi:.1f}%")
kpi4.metric("عدد المنتجات النشطة", f"{len(df):,}")

st.markdown("---")

# التبويبات الرئيسية
tab_finance, tab_inventory, tab_suppliers = st.tabs(["💰 التحليل المالي", "📦 إدارة المخزون", "🚛 تحليل الموردين"])

with tab_finance:
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(df, names='أهمية المنتج', values='صافي الربح النهائي', 
                         title="توزيع الأرباح حسب تصنيف ABC", hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        fig_bar = px.bar(df.groupby('التصنيف')['صافي الربح النهائي'].sum().reset_index(), 
                         x='التصنيف', y='صافي الربح النهائي', color='التصنيف',
                         title="أرباح القطاعات الرئيسية")
        st.plotly_chart(fig_bar, use_container_width=True)

with tab_inventory:
    st.subheader("المخزون الاحتياطي ونقاط الطلب")
    st.dataframe(df[['المنتج', 'التصنيف', 'المخزون الحالي', 'نقطة إعادة الطلب', 'أهمية المنتج']].head(100), use_container_width=True)
    
    fig_scatter = px.scatter(df.head(200), x="المخزون الحالي", y="نقطة إعادة الطلب", 
                             size="المبيعات الشهرية", color="أهمية المنتج", 
                             hover_name="المنتج", title="علاقة المخزون الحالي بحجم المبيعات")
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab_suppliers:
    st.subheader("تقييم كفاءة الموردين")
    sup_analysis = df.groupby('المورد').agg({
        'زمن التوريد (أيام)': 'mean',
        'صافي الربح النهائي': 'sum',
        'المنتج': 'count'
    }).reset_index().rename(columns={'المنتج': 'عدد الأصناف'})
    
    fig_sup = px.scatter(sup_analysis, x="زمن التوريد (أيام)", y="صافي الربح النهائي", 
                         size="عدد الأصناف", color="المورد", title="الموردون: السرعة مقابل الربحية")
    st.plotly_chart(fig_sup, use_container_width=True)

# --- 7. تصدير البيانات ---
st.markdown("---")
st.subheader("📥 تصدير التقارير الذكية")
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    st.download_button(
        label="تحميل التقرير كاملاً (Excel)",
        data=buffer.getvalue(),
        file_name=f"Report_{business_name}.xlsx",
        mime="application/vnd.ms-excel"
    )

with col_exp2:
    st.info("نظام التقارير التلقائية مفعل. يتم تحديث البيانات بناءً على المدخلات الحالية.")

st.markdown("---")
st.caption(f"تم التطوير بواسطة Nexus AI | إصدار الأعمال العام 2026 - الإصدار 3.0")

