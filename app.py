import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. إعدادات الهوية البصرية (Branding & UI) ---
st.set_page_config(
    page_title="Nexus Enterprise AI",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم الواجهة باستخدام CSS لضمان مظهر "Enterprise"
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* الخطوط والاتجاهات */
    html, body, [class*="css"] { 
        font-family: 'Cairo', sans-serif; 
        text-align: right; 
        direction: rtl;
    }
    
    /* الخلفية العامة */
    .main { background-color: #0f172a; }
    
    /* تصميم بطاقات المؤشرات (Metrics) */
    [data-testid="stMetricValue"] { font-size: 28px; color: #3b82f6; }
    .stMetric { 
        background: #1e293b; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #334155;
        border-bottom: 4px solid #3b82f6;
        transition: 0.3s;
    }
    .stMetric:hover { transform: translateY(-5px); border-color: #60a5fa; }
    
    /* تصميم القائمة الجانبية */
    section[data-testid="stSidebar"] { background-color: #1e293b !important; }
    
    /* أزرار الرفع والعمليات */
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background: linear-gradient(90deg, #3b82f6, #1d4ed8); 
        color: white; font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك العمليات الحسابية الذكي ---
def process_data(df_input):
    d = df_input.copy()
    
    # 1. حساب الربح إذا لم يكن موجوداً
    if 'إجمالي الربح' not in d.columns:
        # محاولة توقع أسماء الأعمدة بالإنجليزية أو العربية
        price_col = 'سعر البيع' if 'سعر البيع' in d.columns else 'Price'
        cost_col = 'تكلفة الوحدة' if 'تكلفة الوحدة' in d.columns else 'Cost'
        sales_col = 'المبيعات الشهرية' if 'المبيعات الشهرية' in d.columns else 'Sales'
        
        if all(col in d.columns for col in [price_col, cost_col, sales_col]):
            d['إجمالي الربح'] = (d[price_col] - d[cost_col]) * d[sales_col]
        else:
            d['إجمالي الربح'] = 0 # قيمة افتراضية في حال نقص البيانات
    
    # 2. تصنيف ABC الاحترافي
    d = d.sort_values(by='إجمالي الربح', ascending=False)
    d['Cumulative_Profit'] = d['إجمالي الربح'].cumsum()
    total_p = d['إجمالي الربح'].sum() if d['إجمالي الربح'].sum() != 0 else 1
    d['Profit_%'] = (d['Cumulative_Profit'] / total_p) * 100
    d['التصنيف'] = d['Profit_%'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))
    
    # 3. حساب EOQ (الكمية الاقتصادية)
    d['الكمية المثالية للطلب (EOQ)'] = np.sqrt(
        (2 * (d.get('المبيعات الشهرية', 100) * 12) * 150) / 
        (d.get('تكلفة الوحدة', 50) * 0.2 + 0.1)
    ).replace([np.inf, -np.inf], 0).fillna(0).astype(int)
    
    return d

# --- 3. توليد البيانات الافتراضية الفخمة ---
@st.cache_data
def get_demo_data():
    np.random.seed(42)
    data = {
        "المنتج": [f"منتج {i}" for i in range(1, 51)],
        "الفئة": [np.random.choice(["إلكترونيات", "أزياء", "عطور", "منزل"]) for _ in range(50)],
        "المخزون الحالي": np.random.randint(5, 500, 50),
        "المبيعات الشهرية": np.random.randint(50, 1000, 50),
        "تكلفة الوحدة": np.random.randint(20, 2000, 50),
        "سعر البيع": np.random.randint(50, 3000, 50),
        "زمن التوريد (أيام)": np.random.randint(3, 30, 50),
        "معدل المرتجعات (%)": np.random.uniform(1, 20, 50).round(1)
    }
    return pd.DataFrame(data)

# --- 4. هيكل التطبيق (The Interface) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
st.sidebar.title("🦅 Nexus Control")

# رفع الملفات
uploaded_file = st.sidebar.file_uploader("📥 ارفع بيانات متجرك (Excel/CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        raw_df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
        df = process_data(raw_df)
        st.sidebar.success("تم تحليل الملف بنجاح!")
    except:
        st.sidebar.error("خطأ في تنسيق الملف، تم العودة للبيانات الافتراضية.")
        df = process_data(get_demo_data())
else:
    df = process_data(get_demo_data())

# القائمة الرئيسية
menu = st.sidebar.selectbox("القسم الحالي", ["لوحة التحكم العامة", "تحليل المخزون والطلب", "رادار التسويق والربحية"])

# --- القسم الأول: لوحة التحكم ---
if menu == "لوحة التحكم العامة":
    st.title("🌐 Nexus AI Global Command")
    st.markdown("### إدارة الأداء اللوجستي والمالي")
    
    # بطاقات المؤشرات النشطة
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي المبيعات", f"{(df['المبيعات الشهرية'] * df['سعر البيع']).sum():,} ر.س")
    c2.metric("الأرباح المتوقعة", f"{int(df['إجمالي الربح'].sum()):,} ر.س")
    c3.metric("معدل المرتجعات", f"{df['معدل المرتجعات (%)'].mean():.1f}%")
    c4.metric("منتجات الفئة A", len(df[df['التصنيف'] == 'A (حيوي)']))

    st.markdown("---")
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("📊 توزيع الربحية حسب تصنيف ABC")
        fig_abc = px.pie(df, names='التصنيف', values='إجمالي الربح', hole=0.6, 
                         color_discrete_sequence=['#3b82f6', '#1e4ed8', '#1e293b'])
        fig_abc.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_abc, use_container_width=True)
        
    with col_b:
        st.subheader("🚨 تنبيهات المخزن")
        danger = df[df['المخزون الحالي'] < (df['المبيعات الشهرية'] / 4)]
        if not danger.empty:
            for _, row in danger.head(5).iterrows():
                st.warning(f"**نفاذ وشيك:** {row['المنتج']}")
        else:
            st.success("المخزون مستقر")

# --- القسم الثاني: المخزون ---
elif menu == "تحليل المخزون والطلب":
    st.title("📦 Smart Inventory Engine")
    st.dataframe(df[['المنتج', 'المخزون الحالي', 'الكمية المثالية للطلب (EOQ)', 'التصنيف']], use_container_width=True)
    
    fig_eoq = px.scatter(df, x="المخزون الحالي", y="الكمية المثالية للطلب (EOQ)", size="إجمالي الربح", 
                         color="التصنيف", hover_name="المنتج", template="plotly_dark")
    st.plotly_chart(fig_eoq, use_container_width=True)

# --- القسم الثالث: التسويق ---
elif menu == "رادار التسويق والربحية":
    st.title("🎯 Marketing & Profit Radar")
    st.info("💡 نصيحة: ركز ميزانيتك الإعلانية على المنتجات المصنفة (A) ذات المرتجعات المنخفضة.")
    
    fig_mkt = px.bar(df.head(15), x="المنتج", y="إجمالي الربح", color="معدل المرتجعات (%)", 
                     title="أكثر 15 منتجاً ربحية", template="plotly_dark")
    st.plotly_chart(fig_mkt, use_container_width=True)

# تذييل الصفحة
st.markdown("---")
with st.expander("📂 معاينة البيانات الخام"):
    st.write(df)

st.caption("Powered by Nexus AI Framework - الإصدار الاحترافي لمنى محمد")
