import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. إعدادات الهوية البصرية (Light & Professional Theme) ---
st.set_page_config(
    page_title="Nexus AI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed" # أفضل للجوال
)

# تصميم CSS للألوان الفاتحة وتوافق الجوال
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    /* الأساسيات والخط العربي */
    html, body, [class*="css"] { 
        font-family: 'Cairo', sans-serif; 
        text-align: right; 
        direction: rtl;
        background-color: #f8fafc;
        color: #1e293b;
    }

    /* تحسين الواجهة للجوال */
    @media (max-width: 640px) {
        .stMetric { margin-bottom: 10px; }
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    }

    /* تصميم بطاقات المؤشرات (Metrics) مودرن */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 15px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: 0.3s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #3b82f6;
        transform: translateY(-3px);
    }

    /* تصميم الأزرار */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: #3b82f6;
        color: white;
        font-weight: 600;
        border: none;
        height: 3rem;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: #2563eb;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    /* تصميم القائمة الجانبية الفاتحة */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-left: 1px solid #e2e8f0;
    }
    
    /* العناوين */
    h1, h2, h3 { color: #0f172a; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك البيانات والحسابات ---
def process_data(df_in):
    d = df_in.copy()
    # حساب الربح
    if 'إجمالي الربح' not in d.columns:
        d['إجمالي الربح'] = (d['سعر البيع'] - d['تكلفة الوحدة']) * d['المبيعات الشهرية']
    
    # تصنيف ABC
    d = d.sort_values(by='إجمالي الربح', ascending=False)
    d['Cumulative_Profit'] = d['إجمالي الربح'].cumsum()
    total_p = d['إجمالي الربح'].sum() if d['إجمالي الربح'].sum() != 0 else 1
    d['Profit_%'] = (d['Cumulative_Profit'] / total_p) * 100
    d['التصنيف'] = d['Profit_%'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))
    
    # حساب EOQ
    d['الكمية المثالية للطلب (EOQ)'] = np.sqrt(
        (2 * (d['المبيعات الشهرية'] * 12) * 150) / (d['تكلفة الوحدة'] * 0.2 + 0.1)
    ).fillna(0).astype(int)
    
    return d

@st.cache_data
def get_demo_data():
    data = {
        "المنتج": ["فستان سهرة", "طقم بخور", "ساعة ذكية", "عطر فرنسي", "عباية تطريز", "مبخرة مودرن"],
        "المخزون الحالي": [15, 120, 8, 45, 12, 60],
        "المبيعات الشهرية": [85, 40, 95, 110, 50, 30],
        "تكلفة الوحدة": [350, 80, 450, 180, 250, 110],
        "سعر البيع": [850, 220, 999, 450, 650, 280],
        "معدل المرتجعات (%)": [5.2, 0.5, 3.1, 1.2, 8.5, 12.0],
        "زمن التوريد (أيام)": [14, 7, 21, 10, 15, 12]
    }
    return pd.DataFrame(data)

# --- 3. واجهة المستخدم (Dashboard Body) ---
st.sidebar.markdown("<h2 style='text-align: center; color: #3b82f6;'>NEXUS AI</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف بياناتك", type=['xlsx', 'csv'])
if uploaded_file:
    try:
        raw_df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
        df = process_data(raw_df)
        st.sidebar.success("✅ تم تحديث البيانات")
    except:
        df = process_data(get_demo_data())
else:
    df = process_data(get_demo_data())

# القائمة
menu = st.sidebar.radio("القائمة الرئيسية:", ["🏠 لوحة التحكم", "📦 المستودع", "📈 التسويق"])

# --- القسم الأول: لوحة التحكم ---
if menu == "🏠 لوحة التحكم":
    st.title("🚀 لوحة التحكم الاستراتيجية")
    
    # صف المؤشرات (Metrics) - متوافق مع الجوال
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 إجمالي الأرباح", f"{int(df['إجمالي الربح'].sum()):,} ر.س")
    col2.metric("📉 نسبة المرتجعات", f"{df['معدل المرتجعات (%)'].mean():.1f}%")
    col3.metric("🏆 منتجات فئة A", len(df[df['التصنيف'] == 'A (حيوي)']))

    st.markdown("---")
    
    # الرسوم البيانية - تصميم فاتح
    c_left, c_right = st.columns([1, 1])
    with c_left:
        st.subheader("📊 توزيع الأرباح (ABC)")
        fig_abc = px.pie(df, names='التصنيف', values='إجمالي الربح', hole=0.5, 
                         color_discrete_sequence=['#3b82f6', '#93c5fd', '#e2e8f0'])
        fig_abc.update_layout(margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig_abc, use_container_width=True)
        
    with c_right:
        st.subheader("⚠️ تنبيهات عاجلة")
        danger = df[df['المخزون الحالي'] < 15]
        for _, row in danger.head(3).iterrows():
            st.warning(f"**{row['المنتج']}**: الكمية منخفضة ({row['المخزون الحالي']})")

# --- القسم الثاني: المستودع ---
elif menu == "📦 المستودع":
    st.title("📦 إدارة المخزون الذكي")
    st.info("يتم حساب الكمية المثالية (EOQ) لتقليل تكاليف التخزين.")
    
    st.dataframe(df[['المنتج', 'المخزون الحالي', 'الكمية المثالية للطلب (EOQ)', 'التصنيف']], use_container_width=True)
    
    fig_eoq = px.scatter(df, x="المخزون الحالي", y="الكمية المثالية للطلب (EOQ)", 
                         size="إجمالي الربح", color="التصنيف", hover_name="المنتج")
    fig_eoq.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig_eoq, use_container_width=True)

# --- القسم الثالث: التسويق ---
elif menu == "📈 التسويق":
    st.title("📈 رادار الأداء والربحية")
    fig_bar = px.bar(df.head(10), x="المنتج", y="إجمالي الربح", color="معدل المرتجعات (%)",
                     color_continuous_scale=px.colors.sequential.Blues)
    st.plotly_chart(fig_bar, use_container_width=True)

# تذييل الصفحة
st.markdown("---")
with st.expander("📂 عرض البيانات الخام"):
    st.dataframe(df)

st.caption("Nexus Enterprise AI - إصدار 2026 الخاص بمنى محمد")
