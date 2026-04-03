import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# --- 1. إعدادات الهوية البصرية الاحترافية (Light Mode) ---
st.set_page_config(
    page_title="Nexus AI | Supply Chain Center",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Cairo', sans-serif; 
        text-align: right; 
        direction: rtl;
        background-color: #f8fafc;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02) !important;
        border-top: 5px solid #3b82f6 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-left: 1px solid #e2e8f0 !important;
    }

    .stButton>button {
        width: 100%; border-radius: 12px;
        background: linear-gradient(90deg, #3b82f6, #2563eb);
        color: white; font-weight: bold; border: none; height: 3.2rem;
        transition: 0.3s all;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(59, 130, 246, 0.3);
    }
    
    @media (max-width: 640px) {
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك المعالجة الحسابية ---
def process_data(df_input):
    d = df_input.copy()
    
    if 'إجمالي الربح' not in d.columns:
        d['إجمالي الربح'] = (d['سعر البيع'] - d['تكلفة الوحدة']) * d['المبيعات الشهرية']
    
    d = d.sort_values(by='إجمالي الربح', ascending=False)
    d['Cumulative_Profit'] = d['إجمالي الربح'].cumsum()
    total_p = d['إجمالي الربح'].sum() if d['إجمالي الربح'].sum() != 0 else 1
    d['Profit_%'] = (d['Cumulative_Profit'] / total_p) * 100
    d['التصنيف'] = d['Profit_%'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))
    
    d['الكمية المثالية للطلب (EOQ)'] = np.sqrt(
        (2 * (d['المبيعات الشهرية'] * 12) * 150) / (d['تكلفة الوحدة'] * 0.2 + 0.1)
    ).fillna(0).astype(int)
    
    d['تقييم المورد'] = (100 - (d['زمن التوريد (أيام)'] * 2) - d['معدل المرتجعات (%)']).clip(lower=0)
    
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

# --- 3. واجهة المستخدم ---
st.sidebar.markdown("<h2 style='text-align: center; color: #3b82f6;'>NEXUS AI</h2>", unsafe_allow_html=True)
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)

uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف بياناتك (Excel/CSV)", type=['xlsx', 'csv'])
if uploaded_file:
    try:
        raw_df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
        df = process_data(raw_df)
        st.sidebar.success("✅ تم تحديث البيانات بنجاح")
    except:
        df = process_data(get_demo_data())
else:
    df = process_data(get_demo_data())

st.sidebar.markdown("---")
st.sidebar.subheader("🛠️ محاكي الأرباح")
price_mod = st.sidebar.slider("تعديل سعر البيع (%)", -30, 30, 0)
total_sim_profit = df['إجمالي الربح'].sum() * (1 + price_mod/100)

# ميزة احترافية: زر تحميل التقرير
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False, sheet_name='Sheet1')
st.sidebar.download_button(label="📥 تحميل التقرير التنفيذي", data=buffer.getvalue(), file_name="Nexus_Report.xlsx", mime="application/vnd.ms-excel")

menu = st.sidebar.radio("انتقل إلى القسم:", ["🏠 لوحة التحكم", "📦 المستودع والطلب", "🎯 رادار التسويق", "🚚 محاكي الموردين"])

# --- الأقسام ---
if menu == "🏠 لوحة التحكم":
    st.title("🌐 Strategic Command Center")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 إجمالي الأرباح", f"{int(df['إجمالي الربح'].sum()):,} ر.س")
    col2.metric("🔮 ربح المحاكاة", f"{int(total_sim_profit):,} ر.س", delta=f"{price_mod}%")
    col3.metric("📉 المرتجعات", f"{df['معدل المرتجعات (%)'].mean():.1f}%")
    col4.metric("🏆 منتجات A", len(df[df['التصنيف'] == 'A (حيوي)']))

    st.markdown("---")
    left, right = st.columns([2, 1])
    with left:
        st.subheader("📊 تحليل ABC للربحية")
        fig_abc = px.pie(df, names='التصنيف', values='إجمالي الربح', hole=0.5, color_discrete_sequence=['#3b82f6', '#93c5fd', '#f1f5f9'])
        st.plotly_chart(fig_abc, use_container_width=True)
    with right:
        st.subheader("🚨 تنبيهات المخزون")
        danger = df[df['المخزون الحالي'] < 20]
        if not danger.empty:
            for _, row in danger.head(5).iterrows():
                st.error(f"**نفاذ:** {row['المنتج']} (باقي {row['المخزون الحالي']})")
        else: st.success("المخزون مستقر")

elif menu == "📦 المستودع والطلب":
    st.title("📦 Smart Inventory Engine")
    st.info("💡 نصيحة: اطلب الكمية المثالية (EOQ) لتقليل تكاليف الشحن والتخزين بنسبة تصل لـ 20%.")
    # تصحيح الخطأ المطبعي هنا
    st.dataframe(df[['المنتج', 'المخزون الحالي', 'الكمية المثالية للطلب (EOQ)', 'التصنيف']], use_container_width=True)
    st.plotly_chart(px.bar(df, x="المنتج", y="الكمية المثالية للطلب (EOQ)", color="التصنيف", template="plotly_white"), use_container_width=True)

elif menu == "🎯 رادار التسويق":
    st.title("🎯 Marketing ROI Radar")
    fig_mkt = px.bar(df.head(10), x="المنتج", y="إجمالي الربح", color="معدل المرتجعات (%)", title="أداء الربحية مقابل المرتجعات", color_continuous_scale="Blues")
    st.plotly_chart(fig_mkt, use_container_width=True)

elif menu == "🚚 محاكي الموردين":
    st.title("🚚 Supplier Risk Simulator")
    delay_sim = st.slider("محاكاة تأخير في التوريد (أيام إضافية)", 0, 20, 0)
    df['زمن التوريد الكلي'] = df['زمن التوريد (أيام)'] + delay_sim
    fig_sup = px.scatter(df, x="زمن التوريد الكلي", y="معدل المرتجعات (%)", size="إجمالي الربح", color="المورد", hover_name="المنتج", title="خريطة مخاطر الموردين", template="plotly_white")
    st.plotly_chart(fig_sup, use_container_width=True)
    st.subheader("📋 سجل تقييم الموردين")
    sup_eval = df.groupby('المورد').agg({'تقييم المورد': 'mean', 'زمن التوريد (أيام)': 'mean'}).reset_index()
    st.table(sup_eval.style.format({'تقييم المورد': '{:.1f}/100', 'زمن التوريد (أيام)': '{:.1f} يوم'}))

st.markdown("---")
# تصحيح الاسم في التذييل
st.caption(f"تم التطوير بواسطة منى محمد | Nexus Enterprise AI 2026")
