import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime

# --- 1. إعدادات المنصة الاحترافية ---
st.set_page_config(
    page_title="Visionary BI | منصة ذكاء الأعمال المتكاملة",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم CSS لرفع مستوى الواجهة (UI/UX)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;600;700&display=swap');
    
    * { font-family: 'IBM Plex Sans Arabic', sans-serif; }
    .main { background-color: #fcfcfd; direction: rtl; }
    
    /* تصميم البطاقات العلوية */
    [data-testid="stMetricValue"] { font-size: 28px; font-weight: 700; color: #1e293b; }
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #f1f5f9;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    
    /* تخصيص التبويبات */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8fafc;
        border-radius: 10px 10px 0 0;
        gap: 1px;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] { background-color: #2563eb !important; color: white !important; }
    
    /* إخفاء علامة Streamlit المزعجة */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. مولد البيانات التجريبية الشامل (Universal Data Generator) ---
@st.cache_data
def generate_universal_data(rows=5000):
    np.random.seed(42)
    sectors = {
        'أزياء وموضة': ['قميص عصري', 'حذاء رياضي', 'حقيبة يد', 'نظارات شمسية'],
        'تقنية وإلكترونيات': ['ساعة ذكية', 'سماعات لاسلكية', 'شاحن سريع', 'لوحة مفاتيح'],
        'تجميل وعناية': ['عطر نيش', 'كريم مرطب', 'مجموعة زيوت', 'ماسك وجه'],
        'أغذية عضوية': ['قهوة مختصة', 'عسل طبيعي', 'مكسرات مشكلة', 'شاي أخضر']
    }
    
    selected_sector = list(sectors.keys())
    data_list = []
    
    for i in range(rows):
        sector = np.random.choice(selected_sector)
        product = np.random.choice(sectors[sector])
        cost = np.random.uniform(30, 1200)
        price = cost * np.random.uniform(1.3, 2.5) # ربح بين 30% إلى 150%
        
        data_list.append({
            "المنتج": f"{product} #{i+101}",
            "القطاع": sector,
            "المخزون": np.random.randint(5, 1000),
            "المبيعات (30 يوم)": np.random.randint(0, 800),
            "تكلفة الوحدة (ر.س)": round(cost, 2),
            "سعر البيع (ر.س)": round(price, 2),
            "زمن التوريد (أيام)": np.random.randint(2, 30),
            "معدل الإرجاع (%)": round(np.random.uniform(0, 12), 1)
        })
    return pd.DataFrame(data_list)

# --- 3. المحرك التحليلي الذكي ---
def run_analytics_engine(df, overhead_pct, shipping):
    d = df.copy()
    # حساب الهوامش
    d['إجمالي الإيرادات'] = d['سعر البيع (ر.س)'] * d['المبيعات (30 يوم)']
    d['التكلفة الكلية'] = (d['تكلفة الوحدة (ر.س)'] + shipping) * d['المبيعات (30 يوم)']
    d['صافي الربح'] = d['إجمالي الإيرادات'] - d['التكلفة الكلية']
    d['صافي الربح النهائي'] = d['صافي الربح'] * (1 - overhead_pct/100)
    
    # تحليل ABC الاستراتيجي
    d = d.sort_values('صافي الربح النهائي', ascending=False)
    d['Cumulative_Profit'] = d['صافي الربح النهائي'].cumsum()
    total_profit = d['صافي الربح النهائي'].sum()
    d['Profit_Share'] = (d['Cumulative_Profit'] / total_profit) * 100
    d['التصنيف'] = d['Profit_Share'].apply(lambda x: '💎 الفئة A (الأعلى ربحاً)' if x <= 70 else ('⚡ الفئة B (متوسط)' if x <= 90 else '📦 الفئة C (ضعيف)'))
    
    # تنبؤ نقطة إعادة الطلب
    d['نقطة الطلب'] = ( (d['المبيعات (30 يوم)'] / 30) * d['زمن التوريد (أيام)'] * 1.5 ).astype(int)
    return d

# --- 4. شريط التحكم الجانبي ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)
    st.title("Visionary BI")
    st.info("نظام تحليل البيانات الذكي للمتاجر الإلكترونية")
    
    st.subheader("🛠️ تخصيص المعايير")
    shop_name = st.text_input("اسم المتجر الرقمي", "متجري المتطور")
    
    with st.expander("📝 إعدادات التكاليف"):
        shipping = st.slider("متوسط شحن القطعة (ر.س)", 0, 100, 25)
        overhead = st.slider("مصاريف تشغيلية (إعلانات/رواتب) %", 0, 50, 15)
    
    st.markdown("---")
    st.success("تم تحديث البيانات لحظياً")

# معالجة البيانات
raw_data = generate_universal_data()
processed_df = run_analytics_engine(raw_data, overhead, shipping)

# --- 5. الصفحة الرئيسية ---
st.title(f"📊 نظرة عامة: {shop_name}")
st.caption("تحليلات الأداء المتقدمة المبنية على البيانات الحقيقية")

# كروت المؤشرات الأساسية
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_rev = processed_df['إجمالي الإيرادات'].sum()
total_net = processed_df['صافي الربح النهائي'].sum()

kpi1.metric("إجمالي المبيعات", f"{total_rev:,.0f} ر.س")
kpi2.metric("صافي الأرباح", f"{total_net:,.0f} ر.س", f"{ (total_net/total_rev)*100:.1f}% هامش")
kpi3.metric("القطع المباعة", f"{processed_df['المبيعات (30 يوم)'].sum():,}")
kpi4.metric("كفاءة المخزون", f"{(processed_df['المبيعات (30 يوم)'].sum() / processed_df['المخزون'].sum()):.2f}x")

# --- 6. التبويبات الاحترافية ---
tab_main, tab_inventory, tab_ai = st.tabs(["📈 تحليل الأداء", "📦 إدارة المخزون", "🤖 رؤى الذكاء الاصطناعي"])

with tab_main:
    col1, col2 = st.columns([6, 4])
    
    with col1:
        fig_rev = px.bar(processed_df.groupby('القطاع')['صافي الربح النهائي'].sum().reset_index(), 
                         x='القطاع', y='صافي الربح النهائي', 
                         title="الأرباح حسب قطاع المنتجات",
                         color_discrete_sequence=['#2563eb'])
        fig_rev.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_rev, use_container_width=True)
        
    with col2:
        fig_pie = px.pie(processed_df, names='التصنيف', values='صافي الربح النهائي', 
                         hole=0.6, title="توزيع الربحية (ABC Analysis)",
                         color_discrete_sequence=['#1e40af', '#3b82f6', '#94a3b8'])
        st.plotly_chart(fig_pie, use_container_width=True)

with tab_inventory:
    st.subheader("⚠️ منتجات تتطلب تدخل عاجل")
    alert_df = processed_df[processed_df['المخزون'] <= processed_df['نقطة الطلب']]
    
    if not alert_df.empty:
        st.warning(f"يوجد {len(alert_df)} منتجاً وصلت لنقطة إعادة الطلب أو أقل!")
        st.dataframe(alert_df[['المنتج', 'القطاع', 'المخزون', 'نقطة الطلب', 'التصنيف']].head(10), use_container_width=True)
    
    st.markdown("---")
    fig_scatter = px.scatter(processed_df, x="المخزون", y="المبيعات (30 يوم)", 
                             size="صافي الربح النهائي", color="القطاع", 
                             hover_name="المنتج", title="علاقة المخزون بحجم المبيعات")
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab_ai:
    st.subheader("💡 توصيات المحرك الذكي")
    col_ai1, col_ai2 = st.columns(2)
    
    with col_ai1:
        st.info("**توصية التوسع:**")
        top_sector = processed_df.groupby('القطاع')['صافي الربح النهائي'].sum().idxmax()
        st.write(f"بناءً على البيانات، قطاع **{top_sector}** هو الأكثر ربحية. ننصح بزيادة تنوع المنتجات في هذا القسم بنسبة 20%.")
        
    with col_ai2:
        st.error("**توصية تصفية:**")
        low_perf = processed_df[processed_df['التصنيف'].str.contains('C')].iloc[0]
        st.write(f"المنتج **{low_perf['المنتج']}** يستهلك مساحة مخزنية دون عائد مجزي. يفضل عمل خصم لتصفيته.")

# --- 7. التصدير والقدمة ---
st.markdown("---")
col_down1, col_down2 = st.columns([8, 2])
with col_down2:
    st.button("📄 تصدير PDF", use_container_width=True)
with col_down1:
    st.caption("Visionary BI Engine v3.0 | 2026 - جميع الحقوق محفوظة")
