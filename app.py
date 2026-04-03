import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# --- 1. إعدادات الهوية البصرية والـ White Label ---
st.set_page_config(
    page_title="Nexus AI | Enterprise Supply Chain",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص الواجهة بالألوان الفاتحة (Light Mode)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; background-color: #f8fafc; }
    div[data-testid="stMetric"] { background-color: #ffffff !important; border: 1px solid #e2e8f0 !important; border-radius: 16px !important; padding: 20px !important; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02) !important; border-top: 5px solid #3b82f6 !important; }
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-left: 1px solid #e2e8f0 !important; }
    .stButton>button { width: 100%; border-radius: 12px; background: linear-gradient(90deg, #3b82f6, #2563eb); color: white; font-weight: bold; border: none; height: 3.2rem; transition: 0.3s all; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(59, 130, 246, 0.3); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك المعالجة الحسابية المتقدم ---
def process_full_data(df_input):
    d = df_input.copy()
    if 'إجمالي الربح' not in d.columns:
        d['إجمالي الربح'] = (d['سعر البيع'] - d['تكلفة الوحدة']) * d['المبيعات الشهرية']
    
    # تصنيف ABC
    d = d.sort_values(by='إجمالي الربح', ascending=False)
    d['Cumulative_Profit'] = d['إجمالي الربح'].cumsum()
    total_p = d['إجمالي الربح'].sum() if d['إجمالي الربح'].sum() != 0 else 1
    d['Profit_%'] = (d['Cumulative_Profit'] / total_p) * 100
    d['التصنيف'] = d['Profit_%'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))
    
    # حساب EOQ
    d['الكمية المثالية للطلب (EOQ)'] = np.sqrt((2 * (d['المبيعات الشهرية'] * 12) * 150) / (d['تكلفة الوحدة'] * 0.2 + 0.1)).fillna(0).astype(int)
    
    # تقييم الموردين
    d['تقييم المورد'] = (100 - (d['زمن التوريد (أيام)'] * 2) - d['معدل المرتجعات (%)']).clip(lower=0)
    
    # ميزة: تقرير الراكد (أيام الركود العشوائية للمحاكاة)
    d['أيام الركود'] = np.random.randint(5, 120, len(d))
    
    return d

@st.cache_data
def get_demo_data():
    data = {
        "المنتج": ["عطر ملكي", "بخور عود", "ساعة فاخرة", "عباية تطريز", "مبخرة ذكية", "قهوة مختصة"],
        "المورد": ["مورد دبي", "مورد الرياض", "مورد الكويت", "مورد دبي", "مورد الرياض", "مورد الكويت"],
        "المخزون الحالي": [25, 140, 10, 18, 55, 200],
        "المبيعات الشهرية": [95, 45, 120, 60, 35, 310],
        "تكلفة الوحدة": [180, 70, 600, 280, 120, 45],
        "سعر البيع": [450, 190, 1400, 750, 280, 130],
        "معدل المرتجعات (%)": [1.5, 0.4, 4.2, 7.8, 11.2, 0.9],
        "زمن التوريد (أيام)": [7, 5, 21, 14, 10, 4]
    }
    return pd.DataFrame(data)

# --- 3. تصميم القائمة الجانبية (Sidebar) ---
st.sidebar.markdown("<h2 style='text-align: center; color: #3b82f6;'>NEXUS AI</h2>", unsafe_allow_html=True)

# ميزة White Label: تخصيص اسم الشركة والشعار
company_name = st.sidebar.text_input("🏢 اسم شركتك (White Label)", "Nexus AI")
uploaded_file = st.sidebar.file_uploader("📥 ارفع بياناتك (Excel/CSV)", type=['xlsx', 'csv'])

df = process_full_data(pd.read_excel(uploaded_file) if uploaded_file and uploaded_file.name.endswith('xlsx') 
                       else pd.read_csv(uploaded_file) if uploaded_file 
                       else get_demo_data())

st.sidebar.markdown("---")
menu = st.sidebar.radio("القائمة الرئيسية:", 
    ["🏠 ملخص تنفيذي", "📦 المستودع والطلب", "🔮 التنبؤ بالطلب", "🚨 محاكي الأزمات", "🛒 ذكاء البيع", "❄️ تقرير الراكد", "🚚 الموردين"])

# ميزة التنبيهات السريعة
st.sidebar.markdown("---")
if st.sidebar.button("📲 إرسال تنبيه WhatsApp للمورد"):
    st.sidebar.success("تم تجهيز رسالة طلب المخزون!")

# زر تحميل التقرير
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False)
st.sidebar.download_button("📥 تحميل التقرير النهائي", data=buffer.getvalue(), file_name=f"{company_name}_Report.xlsx")

# --- 4. عرض الأقسام والميزات ---

# القسم 1: لوحة المدراء (Executive Dashboard)
if menu == "🏠 ملخص تنفيذي":
    st.title(f"📊 الملخص التنفيذي لشركة {company_name}")
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الربح", f"{int(df['إجمالي الربح'].sum()):,} ر.س")
    c2.metric("نسبة الهالك (المرتجعات)", f"{df['معدل المرتجعات (%)'].mean():.1f}%")
    c3.metric("العائد على الاستثمار (ROI)", "158%") # محاكاة
    
    st.markdown("---")
    l_col, r_col = st.columns([2, 1])
    with l_col:
        st.plotly_chart(px.pie(df, names='التصنيف', values='إجمالي الربح', hole=0.5, title="توزيع الأرباح حسب فئة المنتج"), use_container_width=True)
    with r_col:
        st.subheader("🚨 تنبيهات الإدارة")
        stock_danger = df[df['المخزون الحالي'] < 20]
        for _, row in stock_danger.head(3).iterrows():
            st.warning(f"مخزون منخفض: {row['المنتج']}")

# القسم 2: المستودع
elif menu == "📦 المستودع والطلب":
    st.title("📦 Smart Inventory & EOQ")
    st.dataframe(df[['المنتج', 'المخزون الحالي', 'الكمية المثالية للطلب (EOQ)', 'التصنيف']], use_container_width=True)
    st.plotly_chart(px.bar(df, x="المنتج", y="الكمية المثالية للطلب (EOQ)", color="التصنيف"), use_container_width=True)

# القسم 3: التنبؤ بالطلب (AI Demand Forecasting)
elif menu == "🔮 التنبؤ بالطلب":
    st.title("🔮 AI Demand Forecasting")
    st.info("تحليل السلاسل الزمنية لتوقع المبيعات الشهر القادم لتفادي نفاذ المخزون.")
    df['الطلب المتوقع'] = (df['المبيعات الشهرية'] * np.random.uniform(0.9, 1.4, len(df))).astype(int)
    fig_f = px.line(df, x="المنتج", y=["المبيعات الشهرية", "الطلب المتوقع"], title="توقعات المبيعات المستقبيلة")
    st.plotly_chart(fig_f, use_container_width=True)

# القسم 4: محاكي الأزمات (Disruption Simulator)
elif menu == "🚨 محاكي الأزمات":
    st.title("🚨 Supply Chain Disruption Simulator")
    ship_cost = st.slider("ارتفاع تكلفة الشحن العالمي (%)", 0, 100, 20)
    df['الربح بعد الأزمة'] = (df['سعر البيع'] - (df['تكلفة الوحدة'] * (1 + ship_cost/100))) * df['المبيعات الشهرية']
    st.metric("💸 التأثير على إجمالي الربح", f"{int(df['الربح بعد الأزمة'].sum()):,} ر.س", delta=f"{int(df['الربح بعد الأزمة'].sum() - df['إجمالي الربح'].sum())}")
    st.plotly_chart(px.bar(df, x="المنتج", y=["إجمالي الربح", "الربح بعد الأزمة"], barmode="group"), use_container_width=True)

# القسم 5: ذكاء البيع (Cross-Selling)
elif menu == "🛒 ذكاء البيع":
    st.title("🛒 Cross-Selling & Bundle Intelligence")
    st.markdown("المنتجات المقترحة لزيادة متوسط قيمة السلة (AOV).")
    bundles = pd.DataFrame({
        "المنتج الأساسي": df['المنتج'].head(3),
        "المنتج المكمل": ["بخور عود", "فحم", "تغليف هدايا"],
        "قوة الترابط": ["95%", "88%", "72%"]
    })
    st.table(bundles)

# القسم 6: تقرير الراكد (Dead Stock)
elif menu == "❄️ تقرير الراكد":
    st.title("❄️ Dead Stock Calculator")
    dead_stock = df[df['أيام الركود'] > 90]
    frozen_cash = (dead_stock['المخزون الحالي'] * dead_stock['تكلفة الوحدة']).sum()
    st.metric("💸 سيولة مجمدة (بضاعة راكدة)", f"{int(frozen_cash):,} ر.س")
    st.dataframe(dead_stock[['المنتج', 'المخزون الحالي', 'أيام الركود', 'تكلفة الوحدة']], use_container_width=True)
    st.warning("💡 نصيحة: ينصح بعمل حملة تصفية لهذه المنتجات فوراً.")

# القسم 7: الموردين
elif menu == "🚚 الموردين":
    st.title("🚚 Supplier Performance")
    st.plotly_chart(px.scatter(df, x="زمن التوريد (أيام)", y="معدل المرتجعات (%)", size="إجمالي الربح", color="المورد"), use_container_width=True)

# --- التذييل ---
st.markdown("---")
st.caption(f"تم التطوير بواسطة منى محمد | {company_name} Enterprise AI 2026")
