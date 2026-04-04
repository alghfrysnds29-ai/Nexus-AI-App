import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime, timedelta

# --- 1. إعدادات الهوية البصرية والواجهة ---
st.set_page_config(page_title="Nexus AI | Enterprise BI", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border-top: 4px solid #10b981; }
    .notification-badge { background-color: #ef4444; color: white; padding: 4px 8px; border-radius: 50%; font-size: 12px; vertical-align: top; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f1f5f9; border-radius: 10px 10px 0px 0px; }
    .stTabs [aria-selected="true"] { background-color: #10b981 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك توليد البيانات الزمنية (Time-Series) ---
@st.cache_data
def generate_generic_data(rows=1000):
    np.random.seed(42)
    categories = ['إلكترونيات', 'مستحضرات تجميل', 'أدوات منزلية', 'أزياء']
    suppliers = [f'المورد {i}' for i in range(1, 11)]
    
    # توليد تواريخ عشوائية للسنة الماضية
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

# --- 3. محرك التحليل الذكي المطور (E-commerce Engine) ---
def advanced_analytics_engine(df, ship_cost, tax_pct, op_cost_pct):
    d = df.copy()
    # حساب المقاييس الأساسية
    d['إجمالي التكلفة'] = d['تكلفة الوحدة'] + ship_cost
    d['الضريبة'] = d['سعر البيع'] * (tax_pct / 100)
    d['GMV'] = d['سعر البيع'] * d['كمية المبيعات']
    d['صافي الربح'] = (d['سعر البيع'] - d['إجمالي التكلفة'] - d['الضريبة']) * d['كمية المبيعات']
    d['صافي الربح'] = d['صافي الربح'] * (1 - op_cost_pct / 100)
    
    # تحليل المرتجعات
    d['نسبة المرتجعات'] = (d['المرتجعات'] / d['كمية المبيعات']) * 100
    
    # إدارة المخزون ونقطة إعادة الطلب
    avg_daily_sales = d['كمية المبيعات'].mean() / 30
    d['مخزون الأمان'] = (avg_daily_sales * d['زمن التوريد (أيام)'] * 0.5).astype(int)
    d['نقطة إعادة الطلب'] = (avg_daily_sales * d['زمن التوريد (أيام)']).astype(int) + d['مخزون الأمان']
    
    # تصنيف ABC
    d = d.sort_values(by='صافي الربح', ascending=False)
    d['Cum_Profit_Pct'] = d['صافي الربح'].cumsum() / d['صافي الربح'].sum() * 100
    d['أهمية المنتج'] = d['Cum_Profit_Pct'].apply(lambda x: 'A (نجم)' if x <= 70 else ('B (مستقر)' if x <= 90 else 'C (ضعيف)'))
    
    return d# --- 4. الشريط الجانبي ونظام التوافق (Data Mapping) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1548/1548914.png", width=80)
st.sidebar.title("إعدادات Nexus AI")

data_source = st.sidebar.radio("مصدر البيانات:", ["بيانات النظام الافتراضية", "رفع ملف متجرك الخاص"])
raw_df = None

if data_source == "رفع ملف متجرك الخاص":
    uploaded_file = st.sidebar.file_uploader("ارفع ملف Excel أو CSV", type=['xlsx', 'csv'])
    if uploaded_file:
        raw_df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
        st.sidebar.success("تم رفع الملف بنجاح")
        
        # ميزة 5: نظام التوافق (Data Mapping)
        with st.sidebar.expander("🔗 ربط أعمدة ملفك بالنظام"):
            col_map = {}
            columns = raw_df.columns.tolist()
            col_map['تاريخ الطلب'] = st.selectbox("عمود التاريخ", columns)
            col_map['المنتج'] = st.selectbox("عمود اسم المنتج", columns)
            col_map['كمية المبيعات'] = st.selectbox("عمود الكمية المباعة", columns)
            col_map['سعر البيع'] = st.selectbox("عمود سعر البيع", columns)
            
            if st.button("تطبيق الربط"):
                raw_df = raw_df.rename(columns={v: k for k, v in col_map.items()})
                raw_df['تاريخ الطلب'] = pd.to_datetime(raw_df['تاريخ الطلب'])
    else:
        st.info("في انتظار الملف... تم استخدام بيانات تجريبية.")
        raw_df = generate_generic_data()
else:
    raw_df = generate_generic_data(2000)

# ميزة 2: الفلاتر الديناميكية
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 فلاتر البحث")
all_cats = raw_df['التصنيف'].unique().tolist()
selected_cats = st.sidebar.multiselect("الفئات", all_cats, default=all_cats)
date_range = st.sidebar.date_input("الفترة الزمنية", [raw_df['تاريخ الطلب'].min(), raw_df['تاريخ الطلب'].max()])

# تطبيق الفلاتر
mask = (raw_df['التصنيف'].isin(selected_cats)) & \
       (raw_df['تاريخ الطلب'].dt.date >= date_range[0]) & \
       (raw_df['تاريخ الطلب'].dt.date <= date_range[1])
filtered_df = raw_df.loc[mask]

# تشغيل المحرك
with st.sidebar.expander("💸 تكاليف التشغيل"):
    ship = st.number_input("تكلفة الشحن/وحدة", 0, 100, 10)
    tax = st.slider("الضريبة %", 0, 25, 15)
    op = st.slider("مصاريف إدارية %", 0, 50, 10)

final_df = advanced_analytics_engine(filtered_df, ship, tax, op)

# --- 5. لوحة القيادة و الـ KPIs المتقدمة ---
st.title("🚀 لوحة قيادة Nexus AI")

# ميزة 6: KPIs متقدمة
k1, k2, k3, k4 = st.columns(4)
gmv = final_df['GMV'].sum()
aov = gmv / len(final_df)
inventory_turnover = (final_df['تكلفة الوحدة'] * final_df['كمية المبيعات']).sum() / ((final_df['المخزون الحالي'] * final_df['تكلفة الوحدة']).mean() + 1)
net_profit = final_df['صافي الربح'].sum()

k1.metric("إجمالي GMV", f"${gmv:,.0f}")
k2.metric("متوسط الطلب AOV", f"${aov:,.1f}")
k3.metric("دوران المخزون", f"{inventory_turnover:.2f}x")
k4.metric("صافي الأرباح", f"${net_profit:,.0f}", delta=f"{ (net_profit/gmv*100):.1f}% Margin")

t1, t2, t3 = st.tabs(["📈 تحليل النمو والمرتجعات", "🔮 التنبؤ والذكاء الاصطناعي", "📦 تفاصيل المنتجات"])

with t1:
    col_a, col_b = st.columns(2)
    with col_a:
        # ميزة 1: تحليل السلاسل الزمنية
        daily_sales = final_df.groupby('تاريخ الطلب')['GMV'].sum().reset_index()
        fig_line = px.line(daily_sales, x='تاريخ الطلب', y='GMV', title="اتجاه المبيعات الزمني")
        st.plotly_chart(fig_line, use_container_width=True)
    with col_b:
        # ميزة 3: تحليل المرتجعات
        fig_ret = px.bar(final_df.nlargest(10, 'نسبة المرتجعات'), x='المنتج', y='نسبة المرتجعات', color='نسبة المرتجعات', title="أعلى 10 منتجات في معدل المرتجعات ⚠️")
        st.plotly_chart(fig_ret, use_container_width=True)

with t2:
    # ميزة 4: التنبؤ بنفاد المخزون
    st.subheader("🔮 تنبؤات AI لنفاد المخزون")
    final_df['أيام النفاذ المتوقعة'] = (final_df['المخزون الحالي'] / (final_df['كمية المبيعات']/30 + 0.1)).astype(int)
    risk_df = final_df[final_df['أيام النفاذ المتوقعة'] < 10].sort_values('أيام النفاذ المتوقعة')
    
    if not risk_df.empty:
        st.error(f"تحذير: هناك {len(risk_df)} منتجاً قد ينفد مخزونها خلال أقل من 10 أيام!")
        st.dataframe(risk_df[['المنتج', 'المخزون الحالي', 'أيام النفاذ المتوقعة', 'المورد']])
    else:
        st.success("جميع المنتجات في حالة مخزون آمنة.")

with t3:
    st.dataframe(final_df[['المنتج', 'التصنيف', 'أهمية المنتج', 'صافي الربح', 'نسبة المرتجعات']], use_container_width=True)

st.caption("Nexus AI Enterprise v4.0 - تم التطوير لذكاء المتاجر الإلكترونية 2026")
