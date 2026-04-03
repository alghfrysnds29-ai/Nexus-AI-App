import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. إعدادات النظام الاحترافي والهوية البصرية ---
st.set_page_config(page_title="Nexus AI - Supply Chain Command Center", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main { background-color: #0f172a; color: #f8fafc; }
    .stMetric { background: #1e293b; padding: 20px; border-radius: 15px; border: 1px solid #334155; }
    .sidebar .sidebar-content { background: #1e293b; }
    .report-card { background: #1e293b; padding: 20px; border-radius: 12px; border-left: 5px solid #3b82f6; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك العمليات الحسابية (المعالج الذكي) ---
def process_supply_chain_data(df_input):
    """تقوم هذه الدالة بإجراء كافة الحسابات التقنية على البيانات"""
    d = df_input.copy()
    
    # تأكيد وجود الأعمدة الأساسية أو حسابها
    if 'إجمالي الربح' not in d.columns:
        d['إجمالي الربح'] = (d['سعر البيع'] - d['تكلفة الوحدة']) * d['المبيعات الشهرية']
    
    # أ. تصنيف ABC (الأكثر ربحية)
    d = d.sort_values(by='إجمالي الربح', ascending=False)
    d['Cumulative_Profit'] = d['إجمالي الربح'].cumsum()
    total_profit = d['إجمالي الربح'].sum()
    d['Profit_%'] = (d['Cumulative_Profit'] / total_profit) * 100
    d['التصنيف'] = d['Profit_%'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))
    
    # ب. حساب الكمية الاقتصادية للطلب (EOQ)
    # نستخدم قيم افتراضية للتكاليف إذا لم تكن موجودة في الملف المرفوع
    cost_per_order = 150
    holding_cost_pct = 0.2
    d['الكمية المثالية للطلب (EOQ)'] = np.sqrt(
        (2 * (d['المبيعات الشهرية'] * 12) * cost_per_order) / 
        (d['تكلفة الوحدة'] * holding_cost_pct)
    ).replace([np.inf, -np.inf], 0).fillna(0).astype(int)
    
    return d

# --- 3. توليد البيانات الافتراضية (Demo Data) ---
@st.cache_data
def get_default_data():
    np.random.seed(42)
    products = [f"منتج {i}" for i in range(1, 51)]
    categories = ["إلكترونيات", "أزياء", "منزل", "عطور", "ألعاب"]
    data = {
        "المنتج": products,
        "الفئة": [np.random.choice(categories) for _ in range(50)],
        "المخزون الحالي": np.random.randint(5, 500, 50),
        "المبيعات الشهرية": np.random.randint(50, 1000, 50),
        "تكلفة الوحدة": np.random.randint(20, 2000, 50),
        "سعر البيع": np.random.randint(50, 3000, 50),
        "زمن التوريد (أيام)": np.random.randint(3, 30, 50),
        "معدل المرتجعات (%)": np.random.uniform(1, 20, 50).round(1)
    }
    return pd.DataFrame(data)

# --- 4. واجهة المستخدم والتحكم بالبيانات ---
st.title("🌐 Nexus AI: Global Supply Chain Control")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
st.sidebar.title("إدارة العمليات")

uploaded_file = st.sidebar.file_uploader("ارفع بيانات متجرك (Excel/CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('xlsx'):
            raw_df = pd.read_excel(uploaded_file)
        else:
            raw_df = pd.read_csv(uploaded_file)
        df = process_supply_chain_data(raw_df)
        st.sidebar.success("✅ تم تحميل ومعالجة ملفك بنجاح")
    except Exception as e:
        st.sidebar.error(f"❌ خطأ في قراءة الملف: {e}")
        df = process_supply_chain_data(get_default_data())
else:
    df = process_supply_chain_data(get_default_data())

# القائمة الرئيسية
menu = st.sidebar.selectbox("اختر القسم", ["لوحة التحكم العامة", "تحليل المخزون الذكي", "رادار التسويق والربحية", "محاكي الموردين"])

# --- 5. الأقسام التحليلية ---

if menu == "لوحة التحكم العامة":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي قيمة المخزون", f"{int((df['المخزون الحالي'] * df['تكلفة الوحدة']).sum()):,} ر.س")
    c2.metric("الأرباح الشهرية المتوقعة", f"{int(df['إجمالي الربح'].sum()):,} ر.س")
    c3.metric("منتجات الفئة A", len(df[df['التصنيف'] == 'A (حيوي)']))
    c4.metric("متوسط المرتجعات", f"{df['معدل المرتجعات (%)'].mean():.1f}%")

    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("📈 تحليل توزيع الأرباح (ABC Analysis)")
        fig_abc = px.pie(df, names='التصنيف', values='إجمالي الربح', hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_abc, use_container_width=True)
    
    with col_right:
        st.subheader("🚨 تنبيهات فورية")
        stockouts = df[df['المخزون الحالي'] < (df['المبيعات الشهرية'] / 4)]
        if not stockouts.empty:
            for _, row in stockouts.head(5).iterrows():
                st.error(f"**نفاذ وشيك:** {row['المنتج']} (باقي {row['المخزون الحالي']} قطعة)")
        else:
            st.success("المخزون في مستويات آمنة")

elif menu == "تحليل المخزون الذكي":
    st.subheader("📦 إدارة المستودعات والطلب الاقتصادي")
    st.write("يساعدك هذا القسم في تحديد الكمية المثالية للطلب لتقليل تكاليف التخزين.")
    
    st.dataframe(df[['المنتج', 'المخزون الحالي', 'الكمية المثالية للطلب (EOQ)', 'التصنيف']], use_container_width=True)
    
    fig_eoq = px.scatter(df, x="المخزون الحالي", y="الكمية المثالية للطلب (EOQ)", size="إجمالي الربح", color="التصنيف", hover_name="المنتج", title="التوازن بين التكلفة والكمية")
    st.plotly_chart(fig_eoq, use_container_width=True)

elif menu == "رادار التسويق والربحية":
    st.subheader("🎯 ربط التسويق بسلاسل الإمداد")
    st.info("💡 نصيحة: ركز ميزانيتك الإعلانية على فئة A لضمان أعلى عائد على الإنفاق.")
    
    fig_marketing = px.bar(df.head(15), x="المنتج", y="إجمالي الربح", color="معدل المرتجعات (%)", title="أكثر 15 منتجاً ربحية")
    st.plotly_chart(fig_marketing, use_container_width=True)
    
    st.warning("⚠️ انتبه للمنتجات ذات اللون الأحمر؛ المرتجعات العالية قد تلتهم أرباحك الإعلانية.")

elif menu == "محاكي الموردين":
    st.subheader("🚚 إدارة الموردين والمخاطر")
    fig_risk = px.scatter(df, x="زمن التوريد (أيام)", y="معدل المرتجعات (%)", size="المخزون الحالي", color="التصنيف", title="خريطة مخاطر الموردين")
    st.plotly_chart(fig_risk, use_container_width=True)

# عرض البيانات الخام
with st.expander("📂 معاينة قاعدة البيانات الكاملة"):
    st.write(df)

st.caption("Nexus AI Framework - تم التطوير لخدمة قطاع الأعمال")
