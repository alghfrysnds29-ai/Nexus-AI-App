import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
import os
from datetime import datetime, timedelta

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="Nexus AI | Enterprise BI", page_icon="📊", layout="wide")

# تصميم CSS مخصص للواجهة الاحترافية (Light Mode) ودعم اللغة العربية RTL
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

# --- 2. محركات البيانات والتحليل ---

@st.cache_data
def generate_generic_data(rows=1000):
    """دالة احتياطية لتوليد بيانات بسيطة في حال فشل النظام الضخم"""
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

@st.cache_data
def load_huge_data():
    """دالة جلب 50 ألف سطر من ملف خارجي"""
    file_path = "huge_nexus_data.csv"
    if not os.path.exists(file_path):
        try:
            import data_manager 
            df = data_manager.create_huge_database(file_path, rows=50000)
        except:
            return generate_generic_data(1000)
    else:
        df = pd.read_csv(file_path)
        df['تاريخ الطلب'] = pd.to_datetime(df['تاريخ الطلب'])
    return df

def advanced_analytics_engine(df, ship_cost, tax_pct, op_cost_pct):
    """المحرك الحسابي للـ KPIs والربحية"""
    d = df.copy()
    d['إجمالي التكلفة'] = d['تكلفة الوحدة'] + ship_cost
    d['الضريبة'] = d['سعر البيع'] * (tax_pct / 100)
    d['GMV'] = d['سعر البيع'] * d['كمية المبيعات']
    d['صافي الربح'] = (d['سعر البيع'] - d['إجمالي التكلفة'] - d['الضريبة']) * d['كمية المبيعات']
    d['صافي الربح'] = d['صافي الربح'] * (1 - op_cost_pct / 100)
    d['نسبة المرتجعات'] = (d['المرتجعات'] / (d['كمية المبيعات'] + 1)) * 100
    
    d = d.sort_values(by='صافي الربح', ascending=False)
    total_profit = d['صافي الربح'].sum() if d['صافي الربح'].sum() != 0 else 1
    d['Cum_Profit_Pct'] = d['صافي الربح'].cumsum() / total_profit * 100
    d['أهمية المنتج'] = d['Cum_Profit_Pct'].apply(lambda x: 'A (نجم)' if x <= 70 else ('B (مستقر)' if x <= 90 else 'C (ضعيف)'))
    return d

# --- 3. بناء الواجهة والشريط الجانبي ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1548/1548914.png", width=80)
st.sidebar.title("إعدادات Nexus AI")

data_source = st.sidebar.radio("مصدر البيانات:", ["قاعدة بيانات النظام (50k)", "رفع ملف Excel/CSV"])

# منطق جلب البيانات بناءً على المصدر
if data_source == "رفع ملف Excel/CSV":
    uploaded_file = st.sidebar.file_uploader("ارفع ملفك هنا", type=['xlsx', 'csv'])
    if uploaded_file:
        raw_df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
        with st.sidebar.expander("🔗 ربط الأعمدة"):
            cols = raw_df.columns.tolist()
            map_date = st.selectbox("التاريخ", cols)
            map_prod = st.selectbox("المنتج", cols)
            map_sales = st.selectbox("الكمية", cols)
            map_price = st.selectbox("السعر", cols)
            if st.button("تأكيد الربط"):
                raw_df = raw_df.rename(columns={map_date: 'تاريخ الطلب', map_prod: 'المنتج', map_sales: 'كمية المبيعات', map_price: 'سعر البيع'})
                raw_df['تاريخ الطلب'] = pd.to_datetime(raw_df['تاريخ الطلب'])
    else:
        st.warning("يرجى رفع ملف. تم استخدام بيانات افتراضية مؤقتاً.")
        raw_df = generate_generic_data(1000)
else:
    raw_df = load_huge_data()

# --- 4. الفلاتر والتحليل الذكي ---
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 فلاتر البحث")

# التأكد من صحة التواريخ للفلاتر
raw_df['تاريخ الطلب'] = pd.to_datetime(raw_df['تاريخ الطلب'])
all_cats = raw_df['التصنيف'].unique().tolist()
selected_cats = st.sidebar.multiselect("الفئات", all_cats, default=all_cats)
date_range = st.sidebar.date_input("الفترة", [raw_df['تاريخ الطلب'].min().date(), raw_df['تاريخ الطلب'].max().date()])

# تطبيق الفلترة الفعلية
mask = (raw_df['التصنيف'].isin(selected_cats)) & \
       (raw_df['تاريخ الطلب'].dt.date >= date_range[0]) & \
       (raw_df['تاريخ الطلب'].dt.date <= date_range[1])
filtered_df = raw_df.loc[mask]

# إعدادات التكاليف
with st.sidebar.expander("💰 معايير التكلفة"):
    ship = st.number_input("شحن الوحدة", 0, 100, 10)
    tax = st.slider("الضريبة %", 0, 25, 15)
    op = st.slider("مصاريف تشغيل %", 0, 50, 10)

# تشغيل المحرك على البيانات المفلترة
final_df = advanced_analytics_engine(filtered_df, ship, tax, op)

# --- 5. عرض لوحة القيادة (Dashboard) ---
st.title(f"📊 لوحة ذكاء الأعمال | {datetime.now().year}")

# صف الـ KPIs الأساسية
k1, k2, k3, k4 = st.columns(4)
gmv = final_df['GMV'].sum()
aov = gmv / (len(final_df) + 1)
turnover = (final_df['تكلفة الوحدة'] * final_df['كمية المبيعات']).sum() / ((final_df['المخزون الحالي'] * final_df['تكلفة الوحدة']).mean() + 1)
profit = final_df['صافي الربح'].sum()

k1.metric("إجمالي GMV", f"${gmv:,.0f}")
k2.metric("متوسط الطلب AOV", f"${aov:,.1f}")
k3.metric("دوران المخزون", f"{turnover:.2f}x")
k4.metric("صافي الربح", f"${profit:,.0f}", delta=f"{(profit/gmv*100 if gmv !=0 else 0):.1f}%")

# التبويبات
tab1, tab2, tab3 = st.tabs(["📈 تحليل النمو", "🔮 تنبؤات AI", "📦 المخزون"])

with tab1:
    c_a, c_b = st.columns(2)
    with c_a:
        daily = final_df.groupby('تاريخ الطلب')['GMV'].sum().reset_index()
        st.plotly_chart(px.line(daily, x='تاريخ الطلب', y='GMV', title="اتجاه المبيعات"), use_container_width=True)
    with c_b:
        bad = final_df.nlargest(10, 'نسبة المرتجعات')
        st.plotly_chart(px.bar(bad, x='المنتج', y='نسبة المرتجعات', title="المرتجعات الحرجة ⚠️", color_discrete_sequence=['#ef4444']), use_container_width=True)

with tab2:
    st.subheader("🔮 تنبؤات نفاد المخزون المتوقعة")
    final_df['أيام النفاذ'] = (final_df['المخزون الحالي'] / (final_df['كمية المبيعات']/30 + 0.1)).astype(int)
    risk = final_df[final_df['أيام النفاذ'] < 10].sort_values('أيام النفاذ')
    if not risk.empty:
        st.error(f"تحذير: {len(risk)} منتجاً ستنفد خلال أقل من 10 أيام!")
        st.dataframe(risk[['المنتج', 'المخزون الحالي', 'أيام النفاذ', 'المورد']].head(20), use_container_width=True)
    else:
        st.success("حالة المخزون مستقرة للفترة القادمة.")

with tab3:
    st.dataframe(final_df[['المنتج', 'التصنيف', 'أهمية المنتج', 'صافي الربح', 'المخزون الحالي']], use_container_width=True)

st.markdown("---")
st.caption("Nexus AI Enterprise v4.0 | تم التطوير بواسطة Mona Mohamed Ahmed 2026")
