import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# --- 1. إعدادات الصفحة والهوية ---
st.set_page_config(page_title="Nexus AI | Enterprise BI", page_icon="💎", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .stMetric { background-color: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border-top: 4px solid #2563eb; }
    .notification-badge { background-color: #ef4444; color: white; padding: 4px 10px; border-radius: 50px; font-size: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات (Demo Data) ---
@st.cache_data
def generate_demo_data(rows=1000):
    np.random.seed(42)
    categories = ['الأجهزة الذكية', 'العطور والجمال', 'الأزياء والملابس', 'الأثاث المنزلي', 'الأدوات الرياضية']
    suppliers = [f'المورد {i}' for i in range(1, 21)]
    data = {
        "المنتج": [f"SKU-{1000 + i}" for i in range(1, rows + 1)],
        "الفئة": np.random.choice(categories, rows),
        "المورد": np.random.choice(suppliers, rows),
        "المخزون": np.random.randint(0, 300, rows),
        "المبيعات": np.random.randint(5, 500, rows),
        "التكلفة": np.random.uniform(50, 2000, rows).round(2),
        "السعر": np.random.uniform(100, 4000, rows).round(2),
        "زمن_التوريد": np.random.randint(2, 30, rows)
    }
    df = pd.DataFrame(data)
    df['السعر'] = df[['التكلفة', 'السعر']].max(axis=1) * 1.3
    return df

# --- 3. محرك التحليل (Intelligence Logic) ---
def apply_business_logic(df, ship_cost, tax_pct, op_cost_pct):
    d = df.copy()
    d['رسوم_التشغيل'] = d['السعر'] * (tax_pct / 100)
    d['التكلفة_الكلية'] = d['التكلفة'] + ship_cost + d['رسوم_التشغيل']
    d['صافي_الربح'] = d['السعر'] - d['التكلفة_الكلية']
    d['إجمالي_الربح'] = d['صافي_الربح'] * d['المبيعات']
    d['الربح_النهائي'] = d['إجمالي_الربح'] * (1 - op_cost_pct / 100)
    
    avg_daily_sales = d['المبيعات'] / 30
    d['نقطة_الطلب'] = ((avg_daily_sales * d['زمن_التوريد']) + 5).astype(int)
    
    d = d.sort_values(by='الربح_النهائي', ascending=False)
    d['Cum_Pct'] = 100 * d['الربح_النهائي'].cumsum() / (d['الربح_النهائي'].sum() if d['الربح_النهائي'].sum() != 0 else 1)
    d['التصنيف'] = d['Cum_Pct'].apply(lambda x: 'الفئة_A' if x <= 70 else ('الفئة_B' if x <= 90 else 'الفئة_C'))
    return d# تابع للكود السابق...
# --- 4. التحكم والواجهة ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.title("إعدادات النظام")
    store_name = st.text_input("اسم المتجر", "Nexus Demo Store")
    ship_cost = st.number_input("تكلفة الشحن", 0.0, 100.0, 10.0)
    tax_pct = st.slider("الضرائب (%)", 0, 25, 15)
    op_cost = st.slider("مصاريف تشغيل (%)", 0, 40, 10)
    rows_to_gen = st.slider("عدد المنتجات", 100, 3000, 1000)

df = apply_business_logic(generate_demo_data(rows_to_gen), ship_cost, tax_pct, op_cost)

st.title(f"🚀 لوحة تحكم: {store_name}")

# KPIs
k1, k2, k3 = st.columns(3)
k1.metric("صافي الربح", f"{int(df['الربح_النهائي'].sum()):,} ر.س")
k2.metric("قيمة المخزون", f"{int((df['المخزون'] * df['التكلفة']).sum()):,} ر.س")
k3.metric("نواقص المخزن", len(df[df['المخزون'] <= df['نقطة_الطلب']]))

# Tabs
t1, t2, t3 = st.tabs(["📊 التحليل", "📦 المخزن", "🚚 الموردين"])

with t1:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.pie(df, names='التصنيف', values='الربح_النهائي', title="تحليل ABC"), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(df.groupby('الفئة')['الربح_النهائي'].sum().reset_index(), x='الفئة', y='الربح_النهائي'), use_container_width=True)

with t2:
    st.dataframe(df[['المنتج', 'الفئة', 'المخزون', 'نقطة_الطلب', 'التصنيف']].head(100), use_container_width=True)

with t3:
    sup_df = df.groupby('المورد').agg({'زمن_التوريد': 'mean', 'الربح_النهائي': 'sum', 'المنتج': 'count'}).reset_index()
    fig_sup = px.scatter(sup_df, x="زمن_التوريد", y="الربح_النهائي", size="المنتج", color="المورد", title="أداء الموردين")
    st.plotly_chart(fig_sup, use_container_width=True)

# --- 5. تصدير التقارير (إصلاح AttributeError) ---
st.divider()
def convert_to_excel(df_to_save):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_to_save.to_excel(writer, index=False, sheet_name='Report')
    return output.getvalue()

try:
    excel_data = convert_to_excel(df)
    st.download_button("📥 تحميل تقرير Excel", data=excel_data, file_name="Nexus_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
except Exception as e:
    st.error(f"خطأ في التصدير: {e}")

st.caption("Nexus AI Enterprise 2026 | تطوير: منى محمد")
