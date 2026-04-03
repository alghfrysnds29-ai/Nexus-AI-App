import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime, timedelta

# --- 1. إعدادات الهوية البصرية والواجهة ---
st.set_page_config(page_title="Nexus AI | Enterprise BI", page_icon="💎", layout="wide")

# تصميم CSS احترافي يدعم اللغة العربية والظلال العصرية
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
        padding: 4px 10px; 
        border-radius: 50px; 
        font-size: 12px; 
        font-weight: bold;
    }
    .status-online { color: #10b981; font-size: 14px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك توليد البيانات التجريبية (Demo Data Engine) ---
@st.cache_data
def generate_demo_data(rows=1000):
    np.random.seed(42)
    categories = ['الأجهزة الذكية', 'العطور والجمال', 'الأزياء والملابس', 'الأثاث المنزلي', 'الأدوات الرياضية']
    suppliers = [f'المورد العالمي {i}' for i in range(1, 21)]
    
    data = {
        "المنتج": [f"SKU-{1000 + i}" for i in range(1, rows + 1)],
        "الفئة": np.random.choice(categories, rows),
        "المورد": np.random.choice(suppliers, rows),
        "المخزون الحالي": np.random.randint(0, 300, rows),
        "المبيعات الشهرية": np.random.randint(5, 500, rows),
        "تكلفة الوحدة": np.random.uniform(50, 2000, rows).round(2),
        "سعر البيع": np.random.uniform(100, 4000, rows).round(2),
        "زمن التوريد (أيام)": np.random.randint(2, 30, rows),
        "معدل المرتجعات": np.random.randint(0, 15, rows)
    }
    df = pd.DataFrame(data)
    # التأكد منطقياً أن السعر > التكلفة
    df['سعر البيع'] = df[['تكلفة الوحدة', 'سعر البيع']].max(axis=1) * 1.3
    return df

# --- 3. محرك التحليل الذكي (The Intelligence Logic) ---
def apply_business_logic(df, ship_cost, tax_pct, op_cost_pct):
    d = df.copy()
    
    # حساب تكلفة الهبوط والضرائب
    d['رسوم التشغيل والضرائب'] = d['سعر البيع'] * (tax_pct / 100)
    d['التكلفة الكلية'] = d['تكلفة الوحدة'] + ship_cost + d['رسوم التشغيل والضرائب']
    
    # حسابات الربحية
    d['صافي الربح للقطعة'] = d['سعر البيع'] - d['التكلفة الكلية']
    d['إجمالي صافي الربح'] = d['صافي الربح للقطعة'] * d['المبيعات الشهرية']
    d['الربح الحقيقي بعد المصاريف'] = d['إجمالي صافي الربح'] * (1 - op_cost_pct / 100)
    
    # لوجيك سلاسل الإمداد (نقطة إعادة الطلب)
    avg_daily_sales = d['المبيعات الشهرية'] / 30
    d['مخزون الأمان'] = (avg_daily_sales * 7).astype(int) # أمان لمدة أسبوع
    d['نقطة إعادة الطلب'] = (avg_daily_sales * d['زمن التوريد (أيام)']).astype(int) + d['مخزون الأمان']
    
    # تصنيف ABC الاستراتيجي
    d = d.sort_values(by='إجمالي صافي الربح', ascending=False)
    d['Cum_Profit_Pct'] = 100 * d['إجمالي صافي الربح'].cumsum() / d['إجمالي صافي الربح'].sum()
    d['التصنيف'] = d['Cum_Profit_Pct'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))
    
    return d

# --- 4. الشريط الجانبي والتحكم (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.title("إعدادات النظام")
    store_name = st.text_input("اسم النظام / المتجر", "Nexus Demo Store")
    st.markdown(f"<span class='status-online'>● النظام متصل بالبيانات</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("💸 محاكي التكاليف"):
        ship_cost = st.number_input("تكلفة الشحن (لكل قطعة)", 0.0, 100.0, 10.0)
        tax_pct = st.slider("الضرائب والرسوم (%)", 0, 25, 15)
        op_cost = st.slider("مصاريف تشغيلية عامة (%)", 0, 40, 10)
    
    st.markdown("---")
    rows_to_gen = st.slider("عدد المنتجات للتجربة", 100, 5000, 1000)
    st.caption("Nexus AI Enterprise v3.0")

# معالجة البيانات
raw_data = generate_demo_data(rows_to_gen)
df = apply_business_logic(raw_data, ship_cost, tax_pct, op_cost)

# --- 5. لوحة القيادة المركزية ---
st.title(f"🚀 لوحة تحكم ذكاء الأعمال: {store_name}")

# صف المؤشرات الرئيسية (KPIs)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("صافي الربح المتوقع", f"{int(df['الربح الحقيقي بعد المصاريف'].sum()):,} ر.س", "+5.2%")
kpi2.metric("إجمالي قيمة المخزون", f"{int((df['المخزون الحالي'] * df['تكلفة الوحدة']).sum()):,} ر.س")
kpi3.metric("معدل دوران المخزون", f"{(df['المبيعات الشهرية'].sum() / df['المخزون الحالي'].sum()):.2f}x")
kpi4.metric("العائد على التكلفة", f"{((df['الربح الحقيقي بعد المصاريف'].sum() / (df['تكلفة الوحدة'] * df['المبيعات الشهرية']).sum()) * 100):.1f}%")

st.markdown("---")

# نظام التنبيهات
critical_items = df[df['المخزون الحالي'] <= df['نقطة إعادة الطلب']]
if not critical_items.empty:
    st.markdown(f"### 🔔 منتجات تتطلب إجراءً فورياً <span class='notification-badge'>{len(critical_items)}</span>", unsafe_allow_html=True)
    with st.expander("عرض تفاصيل النواقص المحتملة"):
        st.warning("هذه المنتجات وصلت إلى نقطة إعادة الطلب بناءً على سرعة البيع وزمن التوريد.")
        st.dataframe(critical_items[['المنتج', 'المخزون الحالي', 'نقطة إعادة الطلب', 'المورد']].head(10), use_container_width=True)

# التبويبات الرئيسية
tab1, tab2, tab3 = st.tabs(["📊 التحليل الاستراتيجي", "📦 إدارة المخزون", "🚚 أداء الموردين"])

with tab1:
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        # توزيع الأرباح حسب التصنيف ABC
        fig_abc = px.pie(df, names='التصنيف', values='إجمالي صافي الربح', hole=0.4, 
                         title="تحليل ABC: مساهمة الفئات في الربح",
                         color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig_abc, use_container_width=True)
    
    with col_chart2:
        # أداء الفئات المختلفة
        fig_cat = px.bar(df.groupby('الفئة')['الربح الحقيقي بعد المصاريف'].sum().reset_index(), 
                         x='الفئة', y='الربح الحقيقي بعد المصاريف', color='الفئة',
                         title="صافي الربح حسب فئة المنتج")
        st.plotly_chart(fig_cat, use_container_width=True)

with tab2:
    st.subheader("📦 مستويات الأمان والمخزن")
    st.plotly_chart(px.scatter(df.head(200), x="المخزون الحالي", y="نقطة إعادة الطلب", 
                               size="المبيعات الشهرية", color="التصنيف", 
                               hover_name="المنتج", title="علاقة المخزون الحالي بنقطة إعادة الطلب (أول 200 منتج)"), use_container_width=True)
    st.dataframe(df[['المنتج', 'الفئة', 'المخزون الحالي', 'مخزون الأمان', 'نقطة إعادة الطلب']].head(50), use_container_width=True)

with tab3:
    st.subheader("🚚 تقييم الموردين واللوجستيات")
    sup_analysis = df.groupby('المورد').agg({
        'زمن التوريد (أيام)': 'mean',
        'الربح الحقيقي بعد المصاريف': 'sum',
        'المنتج': 'count'
    }).reset_index().rename(columns={'المنتج': 'عدد الأصناف'})
    
    fig_sup = px.bubble(sup_analysis, x="زمن التوريد (أيام)", y="الربح الحقيقي بعد المصاريف",
                        size="عدد الأصناف", color="المورد", title="الموردون: السرعة مقابل الربحية")
    st.plotly_chart(fig_sup, use_container_width=True)

# --- 6. تصدير التقارير ---
st.markdown("---")
st.subheader("📑 مركز التقارير")
col_ex1, col_ex2 = st.columns(2)
with col_ex1:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Strategic_Report')
    st.download_button("📥 تحميل التقرير الشامل (Excel)", data=output.getvalue(), 
                       file_name=f"{store_name}_Analysis.xlsx", mime="application/vnd.ms-excel")

with col_ex2:
    st.info("💡 نصيحة احترافية: المنتجات من الفئة **A** هي التي تولد 70% من أرباحك، تأكد من عدم نفاذ مخزونها أبداً.")

st.caption(f"تطوير: منى محمد | Nexus AI Enterprise 2026 - جميع الحقوق محفوظة")
