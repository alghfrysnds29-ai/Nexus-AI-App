import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. إعدادات النظام ---
st.set_page_config(page_title="Nexus AI - Supply Chain", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main { background-color: #0f172a; color: #f8fafc; }
    .stMetric { background: #1e293b; padding: 20px; border-radius: 15px; border: 1px solid #334155; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. دالة الحسابات الذكية (لضمان عدم حدوث خطأ عند رفع أي ملف) ---
def process_data(df_input):
    # توحيد أسماء الأعمدة لتجنب الأخطاء
    mapping = {
        'المنتج': 'المنتج', 'المخزون': 'المخزون الحالي', 'المبيعات': 'المبيعات الشهرية',
        'التكلفة': 'تكلفة الوحدة', 'السعر': 'سعر البيع', 'المرتجعات': 'معدل المرتجعات (%)'
    }
    # التأكد من وجود الأعمدة الأساسية للحسابات
    if 'إجمالي الربح' not in df_input.columns:
        df_input['إجمالي الربح'] = (df_input['سعر البيع'] - df_input['تكلفة الوحدة']) * df_input['المبيعات الشهرية']
    
    # تصنيف ABC
    df_input = df_input.sort_values(by='إجمالي الربح', ascending=False)
    df_input['Cumulative_Profit'] = df_input['إجمالي الربح'].cumsum()
    total_p = df_input['إجمالي الربح'].sum()
    df_input['Profit_%'] = (df_input['Cumulative_Profit'] / total_p) * 100
    df_input['التصنيف'] = df_input['Profit_%'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))
    
    # حساب EOQ (الكمية الاقتصادية)
    df_input['الكمية المثالية للطلب (EOQ)'] = np.sqrt((2 * (df_input['المبيعات الشهرية']*12) * 150) / (df_input['تكلفة الوحدة'] * 0.2)).replace([np.inf, -np.inf], 0).fillna(0).astype(int)
    
    return df_input

# --- 3. توليد البيانات الافتراضية ---
@st.cache_data
def load_massive_data():
    np.random.seed(42)
    data = {
        "المنتج": [f"منتج {i}" for i in range(1, 51)],
        "الفئة": [np.random.choice(["إلكترونيات", "أزياء", "منزل", "عطور"]) for _ in range(50)],
        "المخزون الحالي": np.random.randint(5, 500, 50),
        "المبيعات الشهرية": np.random.randint(50, 1000, 50),
        "تكلفة الوحدة": np.random.randint(20, 2000, 50),
        "سعر البيع": np.random.randint(50, 3000, 50),
        "زمن التوريد (أيام)": np.random.randint(3, 30, 50),
        "معدل المرتجعات (%)": np.random.uniform(1, 20, 50).round(1)
    }
    return process_data(pd.DataFrame(data))

# --- 4. إدارة البيانات المرفوعة ---
st.title("🌐 Nexus AI: Global Supply Chain Control")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)

uploaded_file = st.sidebar.file_uploader("ارفع ملف بيانات متجرك (Excel/CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        df = process_data(df) # معالجة الملف المرفوع فوراً
        st.sidebar.success("تم تحليل ملفك بنجاح!")
    except Exception as e:
        st.sidebar.error(f"خطأ في الملف: {e}")
        df = load_massive_data()
else:
    df = load_massive_data()

# --- 5. عرض الأقسام ---
menu = st.sidebar.selectbox("اختر القسم", ["لوحة التحكم العامة", "تحليل المخزون الذكي", "رادار التسويق والربحية"])

if menu == "لوحة التحكم العامة":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي قيمة المخزون", f"{int((df['المخزون الحالي'] * df['تكلفة الوحدة']).sum()):,} ر.س")
    c2.metric("الأرباح الشهرية", f"{int(df['إجمالي الربح'].sum()):,} ر.س")
    c3.metric("منتجات الفئة A", len(df[df['التصنيف'] == 'A (حيوي)']))
    c4.metric("متوسط المرتجعات", f"{df['معدل المرتجعات (%)'].mean():.1f}%")

    st.markdown("---")
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("📈 تحليل توزيع الأرباح (ABC Analysis)")
        fig_abc = px.pie(df, names='التصنيف', values='إجمالي الربح', hole=0.5)
        st.plotly_chart(fig_abc, use_container_width=True)
    
    with col_right:
        st.subheader("🚨 تنبيهات المخزن")
        stockouts = df[df['المخزون الحالي'] < (df['المبيعات الشهرية'] / 4)]
        if not stockouts.empty:
            for _, row in stockouts.head(5).iterrows():
                st.error(f"**نفاذ:** {row['المنتج']}")
        else:
            st.success("المخزون كافٍ لجميع المنتجات")

elif menu == "تحليل المخزون الذكي":
    st.subheader("📦 إدارة الطلب الاقتصادي (EOQ)")
    st.dataframe(df[['المنتج', 'المخزون الحالي', 'الكمية المثالية للطلب (EOQ)', 'التصنيف']], use_container_width=True)
    fig_eoq = px.scatter(df, x="المخزون الحالي", y="الكمية المثالية للطلب (EOQ)", color="التصنيف", size="إجمالي الربح")
    st.plotly_chart(fig_eoq, use_container_width=True)

# عرض البيانات بالأسفل دائماً للمعاينة
with st.expander("📂 عرض قاعدة البيانات الكاملة"):
    st.write(df)
