import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime, timedelta

# --- 1. إعدادات الهوية البصرية (Light Mode Professional) ---
st.set_page_config(page_title="Nexus AI | Enterprise BI", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border-top: 4px solid #10b981; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: #f1f5f9; border-radius: 10px 10px 0px 0px; }
    .stTabs [aria-selected="true"] { background-color: #10b981 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات الافتراضية (مع بُعد الزمن) ---
@st.cache_data
def generate_generic_data(rows=1000):
    np.random.seed(42)
    categories = ['إلكترونيات', 'مستحضرات تجميل', 'أدوات منزلية', 'أزياء']
    suppliers = [f'المورد {i}' for i in range(1, 11)]
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    random_dates = [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(rows)]
    
    data = {
        "تاريخ الطلب": random_dates,
        "المنتج": [f"منتج ذكي {i}" for i in range(1, rows + 1)],
        "التصنيف": np.random.choice(categories, rows),
        "المورد": np.random.choice(suppliers, rows),
        "المخزون الحالي": np.random.randint(0, 500, rows),
        "كمية المبيعات": np.random.randint(1, 100, rows),
        "تكلفة الوحدة": np.random.uniform(50, 1000, rows).round(2),
        "سعر البيع": np.random.uniform(70, 2000, rows).round(2),
        "زمن التوريد (أيام)": np.random.randint(3, 15, rows),
        "المرتجعات": np.random.randint(0, 5, rows)
    }
    df = pd.DataFrame(data)
    df['سعر البيع'] = df[['تكلفة الوحدة', 'سعر البيع']].max(axis=1) * 1.3
    return df

# --- 3. محرك التحليل الذكي المطور (E-commerce KPIs) ---
def advanced_analytics_engine(df, ship_cost, tax_pct, op_cost_pct):
    d = df.copy()
    d['إجمالي التكلفة'] = d['تكلفة الوحدة'] + ship_cost
    d['الضريبة'] = d['سعر البيع'] * (tax_pct / 100)
    d['GMV'] = d['سعر البيع'] * d['كمية المبيعات']
    d['صافي الربح'] = (d['سعر البيع'] - d['إجمالي التكلفة'] - d['الضريبة']) * d['كمية المبيعات']
    d['صافي الربح'] = d['صافي الربح'] * (1 - op_cost_pct / 100)
    d['نسبة المرتجعات'] = (d['المرتجعات'] / (d['كمية المبيعات'] + 1)) * 100
    
    # تصنيف ABC
    d = d.sort_values(by='صافي الربح', ascending=False)
    d['Cum_Profit_Pct'] = d['صافي الربح'].cumsum() / (d['صافي الربح'].sum() + 1) * 100
    d['أهمية المنتج'] = d['Cum_Profit_Pct'].apply(lambda x: 'A (نجم)' if x <= 70 else ('B (مستقر)' if x <= 90 else 'C (ضعيف)'))
    return d

# --- 4. الشريط الجانبي: التحكم، الربط (Mapping)، والفلاتر ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1548/1548914.png", width=80)
st.sidebar.title("إعدادات النظام")

data_source = st.sidebar.radio("مصدر البيانات:", ["بيانات النظام الافتراضية", "رفع ملف Excel/CSV"])

if data_source == "رفع ملف Excel/CSV":
    uploaded_file = st.sidebar.file_uploader("ارفع ملفك هنا", type=['xlsx', 'csv'])
    if uploaded_file:
        raw_df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
        # ميزة 5: نظام التوافق (Data Mapping)
        with st.sidebar.expander("🔗 ربط أعمدة ملفك بالنظام"):
            cols = raw_df.columns.tolist()
            map_date = st.selectbox("عمود التاريخ", cols)
            map_prod = st.selectbox("عمود المنتج", cols)
            map_sales = st.selectbox("عمود الكمية المباعة", cols)
            map_price = st.selectbox("عمود سعر البيع", cols)
            if st.button("تأكيد الربط"):
                raw_df = raw_df.rename(columns={map_date: 'تاريخ الطلب', map_prod: 'المنتج', map_sales: 'كمية المبيعات', map_price: 'سعر البيع'})
                raw_df['تاريخ الطلب'] = pd.to_datetime(raw_df['تاريخ الطلب'])
    else:
        raw_df = generate_generic_data(500)
else:
    raw_df = generate_generic_data(1000)

# ميزة 2: الفلاتر الديناميكية
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 فلاتر العرض")
selected_cats = st.sidebar.multiselect("الفئات", raw_df['التصنيف'].unique().tolist(), default=raw_df['التصنيف'].unique().tolist())
date_range = st.sidebar.date_input("الفترة الزمنية", [raw_df['تاريخ الطلب'].min(), raw_df['تاريخ الطلب'].max()])

# تطبيق الفلترة
mask = (raw_df['التصنيف'].isin(selected_cats)) & (raw_df['تاريخ الطلب'].dt.date >= date_range[0]) & (raw_df['تاريخ الطلب'].dt.date <= date_range[1])
filtered_df = raw_df.loc[mask]

# إعدادات التكاليف
with st.sidebar.expander("💰 معايير التكلفة"):
    ship = st.number_input("شحن الوحدة", 0, 100, 10)
    tax = st.slider("الضريبة %", 0, 25, 15)
    op = st.slider("مصاريف تشغيل %", 0, 50, 10)

final_df = advanced_analytics_engine(filtered_df, ship, tax, op)

# --- 5. لوحة القيادة و الـ KPIs المتقدمة ---
st.title(f"📊 لوحة ذكاء الأعمال | {datetime.now().year}")

# ميزة 6: KPIs احترافية
k1, k2, k3, k4 = st.columns(4)
gmv = final_df['GMV'].sum()
aov = gmv / (len(final_df) + 1)
inventory_turnover = (final_df['تكلفة الوحدة'] * final_df['كمية المبيعات']).sum() / ((final_df['المخزون الحالي'] * final_df['تكلفة الوحدة']).mean() + 1)
profit = final_df['صافي الربح'].sum()

k1.metric("إجمالي GMV", f"${gmv:,.0f}")
k2.metric("متوسط الطلب AOV", f"${aov:,.1f}")
k3.metric("دوران المخزون", f"{inventory_turnover:.2f}x")
k4.metric("صافي الربح", f"${profit:,.0f}", delta=f"{(profit/gmv*100):.1f}%")

# --- 6. التبويبات (Tabs) ---
t1, t2, t3 = st.tabs(["📈 تحليل النمو والمرتجعات", "🔮 تنبؤات AI", "📦 المخزون والتصنيع"])

with t1:
    col_a, col_b = st.columns(2)
    with col_a:
        # ميزة 1: تحليل السلاسل الزمنية
        daily = final_df.groupby('تاريخ الطلب')['GMV'].sum().reset_index()
        st.plotly_chart(px.line(daily, x='تاريخ الطلب', y='GMV', title="اتجاه المبيعات اليومي"), use_container_width=True)
    with col_b:
        # ميزة 3: تحليل المرتجعات
        bad_prods = final_df.nlargest(10, 'نسبة المرتجعات')
        st.plotly_chart(px.bar(bad_prods, x='المنتج', y='نسبة المرتجعات', title="المنتجات الأعلى مرتجعات ⚠️", color_discrete_sequence=['#ef4444']), use_container_width=True)

with t2:
    # ميزة 4: التنبؤ (AI Forecasting)
    st.subheader("🔮 تنبؤات نفاد المخزون")
    final_df['أيام النفاذ'] = (final_df['المخزون الحالي'] / (final_df['كمية المبيعات']/30 + 0.1)).astype(int)
    risk = final_df[final_df['أيام النفاذ'] < 10].sort_values('أيام النفاذ')
    if not risk.empty:
        st.error(f"تحذير: {len(risk)} منتجاً ستنفد خلال أقل من 10 أيام!")
        st.table(risk[['المنتج', 'المخزون الحالي', 'أيام النفاذ', 'المورد']].head(10))
    else:
        st.success("حالة المخزون ممتازة لجميع المنتجات.")

with t3:
    st.dataframe(final_df[['المنتج', 'التصنيف', 'أهمية المنتج', 'صافي الربح', 'نسبة المرتجعات']], use_container_width=True)

st.markdown("---")
st.caption("Nexus AI Enterprise v4.0 | تم التطوير بواسطة Mona Mohamed Ahmed 2026")
