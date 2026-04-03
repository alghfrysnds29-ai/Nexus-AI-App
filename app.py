import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# ==========================================
# 1. إعدادات الهوية البصرية (Professional Light UI)
# ==========================================
def setup_ui():
    st.set_page_config(page_title="Nexus AI Enterprise", page_icon="📊", layout="wide")
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; background-color: #f8fafc; color: #1e293b; }
        .stMetric { background-color: white; border-radius: 16px; padding: 20px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .main-title { color: #1e3a8a; text-align: center; font-weight: 800; padding-bottom: 20px; }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. محرك البيانات (Data Engine)
# ==========================================
@st.cache_data
def load_data(rows=10000):
    np.random.seed(42)
    categories = ['Electronics', 'Beauty', 'Fashion', 'Home']
    data = {
        "SKU": [f"SKU-{i:05d}" for i in range(1, rows + 1)],
        "Product": [f"Universal Item {i}" for i in range(1, rows + 1)],
        "Category": np.random.choice(categories, rows),
        "Vendor": [f"Global Vendor {np.random.randint(1, 51)}" for _ in range(rows)],
        "Stock": np.random.randint(0, 1000, rows),
        "Monthly_Sales": np.random.randint(5, 2000, rows),
        "Cost": np.random.uniform(20, 3000, rows).round(2),
        "Price": np.random.uniform(50, 6000, rows).round(2),
        "Lead_Time": np.random.randint(2, 45, rows)
    }
    df = pd.DataFrame(data)
    df['Price'] = df[['Cost', 'Price']].max(axis=1) * 1.25
    return df

# ==========================================
# 3. محرك التحليل (Analytics Engine)
# ==========================================
def apply_analytics(df, ops_pct):
    d = df.copy()
    d['Total_Profit'] = (d['Price'] - d['Cost']) * d['Monthly_Sales']
    d['Net_Profit'] = d['Total_Profit'] * (1 - ops_pct/100)
    
    # Reorder Point Logic
    daily_sales = d['Monthly_Sales'] / 30
    d['Safety_Stock'] = (daily_sales * 5).astype(int)
    d['Reorder_Point'] = (daily_sales * d['Lead_Time']).astype(int) + d['Safety_Stock']
    
    # ABC Classification
    d = d.sort_values(by='Net_Profit', ascending=False)
    d['Cum_Profit'] = d['Net_Profit'].cumsum()
    total_p = d['Net_Profit'].sum() if d['Net_Profit'].sum() != 0 else 1
    d['Contrib_Pct'] = (d['Cum_Profit'] / total_p) * 100
    d['Strategy'] = d['Contrib_Pct'].apply(lambda x: 'A (High)' if x <= 70 else ('B (Med)' if x <= 90 else 'C (Low)'))
    return d

# ==========================================
# 4. وحدات العرض (Modular Features)
# ==========================================

def feature_metrics(df):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("صافي الأرباح", f"{int(df['Net_Profit'].sum()):,} ر.س")
    m2.metric("رأس المال المخزني", f"{int((df['Stock'] * df['Cost']).sum()):,} ر.س")
    m3.metric("تنبيهات الطلب", len(df[df['Stock'] <= df['Reorder_Point']]))
    m4.metric("كفاءة التوريد", "94%")

def feature_financial_charts(df):
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(px.pie(df, names='Strategy', values='Net_Profit', title="تحليل ABC للأرباح", color_discrete_sequence=px.colors.qualitative.Pastel), use_container_width=True)
    with c2:
        st.plotly_chart(px.bar(df.head(15), x="SKU", y="Net_Profit", title="أعلى 15 منتجاً ربحاً"), use_container_width=True)

def feature_inventory_table(df):
    st.subheader("📦 حالة المخازن الذكية")
    st.dataframe(df[['SKU', 'Product', 'Stock', 'Reorder_Point', 'Strategy']].head(100), use_container_width=True)

def feature_vendor_performance(df):
    st.subheader("🚚 تحليل أداء الموردين")
    # تصحيح الخطأ هنا: تم استخدام نفس اسم المتغير المجمع
    vendor_stats = df.groupby('Vendor').agg({'Net_Profit': 'sum', 'SKU': 'count'}).reset_index()
    vendor_stats.columns = ['Vendor', 'Total_Profit', 'Product_Count']
    st.plotly_chart(px.scatter(vendor_stats, x="Product_Count", y="Total_Profit", size="Total_Profit", color="Vendor", title="الموردين الأكثر ربحية"), use_container_width=True)

# ==========================================
# 5. الهيكل التنفيذي (The Main App)
# ==========================================
def main():
    setup_ui()
    
    # Sidebar
    st.sidebar.title("NEXUS AI v3.1")
    client = st.sidebar.text_input("اسم العميل", "منصة التجارة")
    ops_cost = st.sidebar.slider("المصاريف التشغيلية (%)", 0, 50, 15)
    
    # Load Data
    raw_df = load_data(10000)
    df = apply_analytics(raw_df, ops_cost)
    
    # Main Page
    st.markdown(f"<h1 class='main-title'>لوحة التحكم الإستراتيجية - {client}</h1>", unsafe_allow_html=True)
    
    feature_metrics(df)
    
    t1, t2, t3 = st.tabs(["💰 المالية", "📦 المخزون", "🚚 الموردين"])
    
    with t1:
        feature_financial_charts(df)
    with t2:
        feature_inventory_table(df)
    with t3:
        feature_vendor_performance(df) # تم إصلاح الخطأ هنا

    # التصدير
    st.sidebar.markdown("---")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.sidebar.download_button("📥 تحميل تقرير Excel", data=buffer.getvalue(), file_name="Nexus_Report.xlsx")

if __name__ == "__main__":
    main()
    
