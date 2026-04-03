import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# --- 1. إعدادات الصفحة والهوية ---
st.set_page_config(
    page_title="Visionary BI | ذكاء الأعمال للمتاجر",
    page_icon="📈",
    layout="wide"
)

# تصميم CSS احترافي (Modern UI)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    div[data-testid="stExpander"] {
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        background: white;
        border-radius: 10px;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك توليد البيانات التجريبية ---
@st.cache_data
def get_demo_data(rows=1000):
    np.random.seed(42)
    categories = ['إلكترونيات', 'أزياء', 'تجميل', 'مستلزمات منزلية']
    data = {
        "المنتج": [f"منتج ذكي {i}" for i in range(1, rows + 1)],
        "الفئة": np.random.choice(categories, rows),
        "المخزون": np.random.randint(10, 500, rows),
        "المبيعات_الشهرية": np.random.randint(5, 300, rows),
        "التكلفة": np.random.uniform(50, 1000, rows).round(2),
        "سعر_البيع": np.random.uniform(100, 2000, rows).round(2),
        "زمن_التوريد": np.random.randint(3, 20, rows)
    }
    df = pd.DataFrame(data)
    # التأكد أن سعر البيع دائماً أعلى من التكلفة لضمان منطقية البيانات
    df['سعر_البيع'] = df[['التكلفة', 'سعر_البيع']].max(axis=1) + 20
    return df

# --- 3. المحرك التحليلي ---
def process_analytics(df, ship_fee, tax_rate, op_ex):
    d = df.copy()
    
    # حسابات مالية
    d['إجمالي_التكلفة'] = d['التكلفة'] + ship_fee
    d['صافي_الربح_للقطعة'] = (d['سعر_البيع'] * (1 - tax_rate/100)) - d['إجمالي_التكلفة']
    d['إجمالي_صافي_الربح'] = d['صافي_الربح_للقطعة'] * d['المبيعات_الشهرية']
    d['الربح_النهائي'] = d['إجمالي_صافي_الربح'] * (1 - op_ex/100)
    
    # تحليل ABC (تصنيف المنتجات حسب الربحية)
    d = d.sort_values(by='الربح_النهائي', ascending=False)
    d['cum_profit'] = d['الربح_النهائي'].cumsum()
    total_p = d['الربح_النهائي'].sum()
    d['profit_pct'] = (d['cum_profit'] / total_p) * 100
    d['التصنيف'] = d['profit_pct'].apply(lambda x: '💎 الفئة A' if x <= 70 else ('⚡ الفئة B' if x <= 90 else '📦 الفئة C'))
    
    # إدارة المخزون
    d['نقطة_الطلب'] = ((d['المبيعات_الشهرية'] / 30) * d['زمن_التوريد'] * 1.5).astype(int)
    return d

# --- 4. واجهة التحكم الجانبية ---
with st.sidebar:
    st.markdown("### 🛠️ إعدادات المتجر")
    shop_name = st.text_input("اسم العلامة التجارية", "Visionary Store")
    
    with st.expander("💸 تكاليف التشغيل"):
        shipping = st.number_input("تكلفة الشحن (ر.س)", 0, 100, 25)
        tax = st.slider("الضرائب والرسوم (%)", 0, 25, 15)
        operating = st.slider("مصاريف التسويق والرواتب (%)", 0, 50, 10)
    
    st.markdown("---")
    st.write("✅ النظام يعمل ببيانات تجريبية احترافية")

# جلب ومعالجة البيانات
raw_df = get_demo_data()
df = process_analytics(raw_df, shipping, tax, operating)

# --- 5. لوحة المؤشرات (Dashboard) ---
st.markdown(f"<div class='main-header'>🚀 لوحة تحكم {shop_name}</div>", unsafe_allow_html=True)

# صف المؤشرات الرئيسية
m1, m2, m3, m4 = st.columns(4)
total_profit = df['الربح_النهائي'].sum()
total_sales = (df['سعر_البيع'] * df['المبيعات_الشهرية']).sum()

m1.metric("صافي الربح المتوقع", f"{total_profit:,.0f} ر.س")
m2.metric("إجمالي الإيرادات", f"{total_sales:,.0f} ر.س")
m3.metric("هامش الربح الصافي", f"{(total_profit/total_sales)*100:.1f}%")
m4.metric("المنتجات الحرجة", len(df[df['المخزون'] <= df['نقطة_الطلب']]))

st.markdown("---")

# --- 6. الأقسام التحليلية ---
t1, t2, t3 = st.tabs(["📊 تحليل الربحية", "📦 إدارة المخزون", "📥 تصدير البيانات"])

with t1:
    col_a, col_b = st.columns(2)
    with col_a:
        fig_pie = px.pie(df, names='التصنيف', values='الربح_النهائي', hole=0.5, 
                         title="توزيع الأرباح حسب فئة المنتج",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_b:
        category_perf = df.groupby('الفئة')['الربح_النهائي'].sum().reset_index()
        fig_bar = px.bar(category_perf, x='الفئة', y='الربح_النهائي', 
                         title="أداء الفئات (صافي الربح)",
                         color='الربح_النهائي', color_continuous_scale='Blues')
        st.plotly_chart(fig_bar, use_container_width=True)

with t2:
    st.subheader("⚠️ تنبيهات نفاذ المخزون")
    critical_items = df[df['المخزون'] <= df['نقطة_الطلب']].head(10)
    if not critical_items.empty:
        st.table(critical_items[['المنتج', 'المخزون', 'نقطة_الطلب', 'التصنيف']])
    else:
        st.success("المخزون في حالة ممتازة!")
    
    fig_scatter = px.scatter(df, x="المخزون", y="المبيعات_الشهرية", size="الربح_النهائي", 
                             color="التصنيف", hover_name="المنتج", title="تحليل كفاءة دوران المخزون")
    st.plotly_chart(fig_scatter, use_container_width=True)

with t3:
    st.subheader("📥 استخراج تقارير احترافية")
    st.write("يمكنك تحميل البيانات بصيغة CSV المتوافقة مع جميع برامج المحاسبة.")
    
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="تحميل التقرير الكامل (CSV)",
        data=csv,
        file_name=f'report_{shop_name}.csv',
        mime='text/csv',
    )

st.caption("تم التطوير بواسطة Visionary AI - الإصدار المستقر 2026")
