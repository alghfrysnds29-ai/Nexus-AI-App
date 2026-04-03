import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(
    page_title="Nexus AI | نظام تحليل البيانات الذكي",
    page_icon="💎",
    layout="wide"
)

# تصميم CSS لتصحيح التوجه RTL ودعم الخطوط العربية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Cairo', sans-serif; 
        text-align: right; 
        direction: rtl; 
    }
    .stMetric { 
        background-color: #ffffff; 
        border-radius: 12px; 
        padding: 20px; 
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); 
        border-top: 4px solid #2563eb; 
    }
    div[data-testid="stSidebarNav"] { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك توليد البيانات التجريبية (Demo Data) ---
@st.cache_data
def generate_demo_data(rows=1000):
    # استخدام مسافات بايثون القياسية لتجنب خطأ U+00A0
    np.random.seed(42)
    categories = ['إلكترونيات', 'أزياء', 'مستلزمات منزلية', 'أدوات تجميل', 'ألعاب أطفال']
    suppliers = [f'مورد معتمد {i}' for i in range(1, 11)]
    
    data = {
        "المنتج": [f"منتج ذكي {i}" for i in range(1, rows + 1)],
        "الفئة": np.random.choice(categories, rows),
        "المورد": np.random.choice(suppliers, rows),
        "المخزون الحالي": np.random.randint(5, 500, rows),
        "المبيعات الشهرية": np.random.randint(10, 1000, rows),
        "تكلفة الوحدة": np.random.uniform(30, 1500, rows).round(2),
        "سعر البيع": np.random.uniform(60, 3000, rows).round(2),
        "زمن التوريد (أيام)": np.random.randint(3, 25, rows)
    }
    df = pd.DataFrame(data)
    # ضمان وجود هامش ربح منطقي
    df['سعر البيع'] = df[['تكلفة الوحدة', 'سعر البيع']].max(axis=1) + 25
    return df

# --- 3. محرك التحليل المتقدم ---
def run_analytics_engine(df, shipping, tax_pct, ops_pct):
    d = df.copy()
    
    # حساب تكلفة الهبوط والضرائب
    d['ضريبة المبيعات'] = d['سعر البيع'] * (tax_pct / 100)
    d['التكلفة الإجمالية للقطعة'] = d['تكلفة الوحدة'] + shipping + d['ضريبة المبيعات']
    
    # حساب الأرباح
    d['إجمالي الربح'] = (d['سعر البيع'] - d['التكلفة الإجمالية للقطعة']) * d['المبيعات الشهرية']
    d['صافي الربح النهائي'] = d['إجمالي الربح'] * (1 - ops_pct / 100)
    
    # حسابات المخزون الذكي
    avg_daily_sales = d['المبيعات الشهرية'] / 30
    d['نقطة إعادة الطلب'] = (avg_daily_sales * d['زمن التوريد (أيام)'] * 1.3).astype(int)
    
    # تصنيف ABC حسب الربحية
    d = d.sort_values(by='صافي الربح النهائي', ascending=False)
    d['الربح التراكمي'] = d['صافي الربح النهائي'].cumsum()
    total_net = d['صافي الربح النهائي'].sum() if d['صافي الربح النهائي'].sum() != 0 else 1
    d['نسبة الربح %'] = (d['الربح التراكمي'] / total_net) * 100
    
    d['التصنيف'] = d['نسبة الربح %'].apply(
        lambda x: 'A (ممتاز)' if x <= 70 else ('B (جيد)' if x <= 90 else 'C (ضعيف)')
    )
    return d

# --- 4. الواجهة الجانبية ---
st.sidebar.title("⚙️ الإعدادات الذكية")
business_name = st.sidebar.text_input("اسم المؤسسة", "شركة المسار التجاري")

with st.sidebar.expander("💸 تكاليف إضافية"):
    ship_cost = st.number_input("شحن القطعة (ر.س)", 0.0, 500.0, 12.0)
    tax_rate = st.slider("الضريبة %", 0, 25, 15)
    ops_rate = st.slider("التكاليف التشغيلية %", 0, 50, 10)

# جلب البيانات
raw_df = generate_demo_data(1000)
df = run_analytics_engine(raw_df, ship_cost, tax_rate, ops_rate)

# --- 5. لوحة التحكم الرئيسية ---
st.title(f"🚀 لوحة ذكاء الأعمال: {business_name}")

# المؤشرات الرئيسية
m1, m2, m3, m4 = st.columns(4)
m1.metric("إجمالي صافي الربح", f"{df['صافي الربح النهائي'].sum():,.0f} ر.س")
m2.metric("قيمة المخزون", f"{(df['المخزون الحالي'] * df['تكلفة الوحدة']).sum():,.0f} ر.س")
m3.metric("معدل الدوران", f"{(df['المبيعات الشهرية'].sum() / df['المخزون الحالي'].sum()):.2f}x")
m4.metric("العائد ROI", f"{(df['صافي الربح النهائي'].sum() / (df['تكلفة الوحدة'] * df['المبيعات الشهرية']).sum() * 100):.1f}%")

st.divider()

# التبويبات
tab1, tab2, tab3 = st.tabs(["📊 تحليل الأرباح", "📦 إدارة المخزون", "📥 تصدير البيانات"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(df, names='التصنيف', values='صافي الربح النهائي', 
                         title="مساهمة فئات المنتجات في الربح (ABC)", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        fig_bar = px.histogram(df, x="الفئة", y="صافي الربح النهائي", color="الفئة",
                               title="صافي الربح حسب فئات المنتجات")
        st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.subheader("⚠️ تنبيهات المخزون الحرجة")
    low_stock = df[df['المخزون الحالي'] <= df['نقطة إعادة الطلب']]
    if not low_stock.empty:
        st.warning(f"يوجد {len(low_stock)} منتجاً وصلوا لنقطة إعادة الطلب.")
        st.dataframe(low_stock[['المنتج', 'المخزون الحالي', 'نقطة إعادة الطلب', 'المورد']].head(20), use_container_width=True)
    else:
        st.success("جميع المنتجات متوفرة بمخزون آمن.")

with tab3:
    st.subheader("تقرير البيانات الكامل")
    st.dataframe(df, use_container_width=True)
    
    # وظيفة التصدير
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='MainReport')
    
    st.download_button(
        label="📥 تحميل التقرير بصيغة Excel",
        data=output.getvalue(),
        file_name=f"Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.caption("Nexus AI Enterprise 2026 | تطوير م. منى محمد")
