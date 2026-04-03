import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(
    page_title="Nexus AI | نظام تحليل البيانات الاحترافي", 
    page_icon="📊", 
    layout="wide"
)

# تصميم CSS احترافي يدعم التوجه RTL وتنسيق الواجهة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main { background-color: #f8fafc; }
    .stMetric { 
        background-color: #ffffff; 
        border-radius: 12px; 
        padding: 20px; 
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); 
        border-top: 4px solid #2563eb; 
    }
    .notification-badge { 
        background-color: #ef4444; 
        color: white; 
        padding: 4px 8px; 
        border-radius: 50%; 
        font-size: 12px; 
        vertical-align: top; 
    }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك توليد البيانات التجريبية (Synthetic Data Engine) ---
@st.cache_data
def generate_demo_data(rows=1000):
    np.random.seed(42)
    categories = ['الأجهزة الإلكترونية', 'الملابس والأزياء', 'الأثاث المنزلي', 'المنتجات الغذائية', 'أدوات التجميل']
    suppliers = [f'المورد العالمي {i}' for i in range(1, 21)]
    
    data = {
        "المنتج": [f"منتج تجريبي {i}" for i in range(1, rows + 1)],
        "الفئة": np.random.choice(categories, rows),
        "المورد": np.random.choice(suppliers, rows),
        "المخزون الحالي": np.random.randint(5, 1000, rows),
        "المبيعات الشهرية": np.random.randint(20, 1500, rows),
        "تكلفة الوحدة": np.random.uniform(50, 2000, rows).round(2),
        "سعر البيع": np.random.uniform(100, 4000, rows).round(2),
        "زمن التوريد (أيام)": np.random.randint(2, 30, rows),
        "نسبة المرتجعات (%)": np.random.uniform(0, 5, rows).round(1)
    }
    df = pd.DataFrame(data)
    # التأكد من منطقية السعر (سعر البيع > التكلفة)
    df['سعر البيع'] = df[['تكلفة الوحدة', 'سعر البيع']].max(axis=1) * 1.3
    return df

# --- 3. محرك التحليل المتقدم (The Analytics Engine) ---
def process_analytics(df, ship_cost, tax_pct, op_cost_pct):
    d = df.copy()
    
    # [أ] حساب تكاليف الهبوط والربحية
    d['الضرائب والرسوم'] = d['سعر البيع'] * (tax_pct / 100)
    d['التكلفة التشغيلية للقطعة'] = d['تكلفة الوحدة'] + ship_cost + d['الضرائب والرسوم']
    
    # [ب] إجمالي وصافي الربح
    d['إجمالي الربح'] = (d['سعر البيع'] - d['التكلفة التشغيلية للقطعة']) * d['المبيعات الشهرية']
    d['صافي الربح'] = d['إجمالي الربح'] * (1 - op_cost_pct / 100)
    
    # [ج] لوجستيات المخزون
    avg_daily_sales = d['المبيعات الشهرية'] / 30
    d['مخزون الأمان'] = (avg_daily_sales * 1.5 * d['زمن التوريد (أيام)'] * 0.2).astype(int)
    d['نقطة إعادة الطلب'] = (avg_daily_sales * d['زمن التوريد (أيام)']).astype(int) + d['مخزون الأمان']
    
    # [د] تصنيف ABC (حسب المساهمة في الربح)
    d = d.sort_values(by='صافي الربح', ascending=False)
    d['Cumulative_Profit'] = d['صافي الربح'].cumsum()
    total_net = d['صافي الربح'].sum() if d['صافي الربح'].sum() != 0 else 1
    d['Profit_Percentage'] = (d['Cumulative_Profit'] / total_net) * 100
    d['تصنيف المنتج'] = d['Profit_Percentage'].apply(
        lambda x: 'A (قيمة عالية)' if x <= 70 else ('B (قيمة متوسطة)' if x <= 90 else 'C (منتج ثانوي)')
    )
    
    return d

# --- 4. شريط التحكم الجانبي (Sidebar Control) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1541/1541411.png", width=100)
st.sidebar.markdown("## ⚙️ إعدادات النموذج التحليلي")
store_name = st.sidebar.text_input("اسم المؤسسة/المتجر", "شركة النخبة للتجارة")

with st.sidebar.expander("💰 مدخلات التكاليف والضرائب"):
    ship_cost = st.number_input("متوسط شحن القطعة (ر.س)", 0.0, 1000.0, 10.0)
    tax_pct = st.slider("نسبة الضريبة والرسوم (%)", 0, 100, 15)
    op_cost = st.slider("المصاريف الإدارية والتشغيلية (%)", 0, 100, 10)

st.sidebar.markdown("---")
data_size = st.sidebar.select_slider("حجم البيانات للتجربة", options=[100, 1000, 5000, 10000], value=1000)
uploaded_file = st.sidebar.file_uploader("رفع ملف مبيعات (Excel/CSV)", type=['xlsx', 'csv'])

# جلب ومعالجة البيانات
if uploaded_file:
    raw_df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
else:
    raw_df = generate_demo_data(data_size)

df = process_analytics(raw_df, ship_cost, tax_pct, op_cost)

# --- 5. نظام التنبيهات الذكي ---
critical_items = df[df['المخزون الحالي'] <= df['نقطة إعادة الطلب']]
st.markdown(f"### 🔔 مركز التنبيهات الذكي <span class='notification-badge'>{len(critical_items)}</span>", unsafe_allow_html=True)

if not critical_items.empty:
    with st.expander("⚠️ منتجات تحتاج لإعادة طلب فورية"):
        st.warning(f"يوجد {len(critical_items)} منتجاً تحت خط الأمان للمخزون.")
        st.table(critical_items[['المنتج', 'المخزون الحالي', 'نقطة إعادة الطلب']].head(5))

# --- 6. واجهة العرض الرئيسية ---
st.title(f"📊 لوحة ذكاء الأعمال الاستراتيجية: {store_name}")

# المؤشرات الرئيسية (KPIs)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("صافي الربح المتوقع", f"{df['صافي الربح'].sum():,.0f} ر.س", "شهرياً")
with kpi2:
    capital = (df['المخزون الحالي'] * df['تكلفة الوحدة']).sum()
    st.metric("رأس المال المخزني", f"{capital:,.0f} ر.س")
with kpi3:
    turnover = df['المبيعات الشهرية'].sum() / df['المخزون الحالي'].sum()
    st.metric("معدل دوران المخزون", f"{turnover:.2f}x")
with kpi4:
    roi = (df['صافي الربح'].sum() / capital) * 100 if capital != 0 else 0
    st.metric("العائد على الاستثمار", f"{roi:.1f}%")

st.markdown("---")

# التبويبات التحليلية
tab1, tab2, tab3 = st.tabs(["📈 التحليل المالي", "📦 اللوجستيات والمخزون", "🏬 أداء الموردين"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        fig_pie = px.pie(df, names='تصنيف المنتج', values='صافي الربح', 
                         title="توزيع الأرباح حسب تصنيف ABC", 
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
    with col2:
        fig_bar = px.bar(df.groupby('الفئة')['صافي الربح'].sum().reset_index(), 
                         x='الفئة', y='صافي الربح', title="الأرباح حسب فئة المنتج",
                         color='الفئة', text_auto='.2s')
        st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.subheader("تحليل فجوات المخزون")
    fig_scatter = px.scatter(df, x="المخزون الحالي", y="المبيعات الشهرية", 
                             size="صافي الربح", color="تصنيف المنتج",
                             hover_name="المنتج", title="العلاقة بين المخزون والمبيعات والربحية")
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.dataframe(df[['المنتج', 'الفئة', 'المخزون الحالي', 'نقطة إعادة الطلب', 'تصنيف المنتج']].head(50), use_container_width=True)

with tab3:
    st.subheader("تقييم كفاءة الموردين")
    supplier_stats = df.groupby('المورد').agg({
        'صافي الربح': 'sum',
        'زمن التوريد (أيام)': 'mean',
        'نسبة المرتجعات (%)': 'mean'
    }).reset_index()
    
    fig_sup = px.scatter(supplier_stats, x="زمن التوريد (أيام)", y="صافي الربح", 
                         size="نسبة المرتجعات (%)", color="المورد", 
                         title="قوة الموردين: الربحية مقابل سرعة التوريد (حجم الدائرة = نسبة المرتجعات)")
    st.plotly_chart(fig_sup, use_container_width=True)

# --- 7. تصدير التقارير ---
st.markdown("---")
st.subheader("📑 تصدير البيانات النهائية")
col_ex1, col_ex2 = st.columns(2)

with col_ex1:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data_Report')
    st.download_button(
        label="📥 تحميل التقرير الشامل (Excel)",
        data=output.getvalue(),
        file_name=f"Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

with col_ex2:
    st.info("💡 نصيحة: المنتجات من الفئة 'A' هي المحرك الرئيسي لأرباحك، تأكد من عدم نفاذ مخزونها أبداً.")

st.divider()
st.caption(f"تم التطوير بواسطة م. منى محمد | Nexus AI BI Suite 2026 | نظام تجريبي آمن 100%")
