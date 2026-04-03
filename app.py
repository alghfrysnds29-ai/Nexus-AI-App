import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. إعدادات النظام الاحترافي ---
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

# --- 2. محرك توليد البيانات الضخمة (Big Data Engine) ---
@st.cache_data
def load_massive_data():
    # محاكاة لبيانات 50 منتجاً بمقاييس احترافية
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
        "تكلفة الطلب": [150] * 50, # تكلفة إرسال طلب جديد للمورد
        "تكلفة التخزين (%)": [0.2] * 50, # 20% من تكلفة المنتج سنوياً
        "معدل المرتجعات (%)": np.random.uniform(1, 20, 50).round(1)
    }
    df = pd.DataFrame(data)
    # حساب الربح الإجمالي لكل منتج
    df['إجمالي الربح'] = (df['سعر البيع'] - df['تكلفة الوحدة']) * df['المبيعات الشهرية']
    return df

df = load_massive_data()

# --- 3. الوظائف التحليلية المتقدمة ---

# أ. تصنيف ABC (الأكثر ربحية)
def abc_classification(d):
    d = d.sort_values(by='إجمالي الربح', ascending=False)
    d['Cumulative_Profit'] = d['إجمالي الربح'].cumsum()
    total_profit = d['إجمالي الربح'].sum()
    d['Profit_%'] = (d['Cumulative_Profit'] / total_profit) * 100
    d['التصنيف'] = d['Profit_%'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))
    return d

df = abc_classification(df)

# ب. حساب الكمية الاقتصادية للطلب (EOQ)
# القانون: sqrt(2 * المبيعات السنوية * تكلفة الطلب / تكلفة التخزين للوحدة)
df['الكمية المثالية للطلب (EOQ)'] = np.sqrt((2 * (df['المبيعات الشهرية']*12) * df['تكلفة الطلب']) / (df['تكلفة الوحدة'] * df['تكلفة التخزين (%)'])).astype(int)

# --- 4. واجهة المستخدم (Dashboard) ---
st.title("🌐 Nexus AI: Global Supply Chain Control")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
st.sidebar.title("إدارة العمليات")

# خيار رفع ملف
uploaded_file = st.sidebar.file_uploader("ارفع بيانات متجرك (Excel/CSV)", type=['xlsx', 'csv'])
if uploaded_file:
    df = pd.read_excel(uploaded_file) # تبسيط للقراءة

menu = st.sidebar.selectbox("اختر القسم", ["لوحة التحكم العامة", "تحليل المخزون الذكي", "رادار التسويق والربحية", "محاكي الموردين"])

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
        for _, row in stockouts.head(5).iterrows():
            st.error(f"**نفاذ وشيك:** {row['المنتج']} (باقي {row['المخزون الحالي']} قطعة)")

elif menu == "تحليل المخزون الذكي":
    st.subheader("📦 إدارة المستودعات والطلب الاقتصادي")
    st.write("هذا القسم يحدد لك بالظبط كم تطلب من كل منتج لتقليل مصاريف الشحن والتخزين.")
    
    st.dataframe(df[['المنتج', 'المخزون الحالي', 'الكمية المثالية للطلب (EOQ)', 'التصنيف', 'زمن التوريد (أيام)']], use_container_width=True)
    
    st.markdown("### 📊 التوازن بين التكلفة والكمية")
    fig_eoq = px.scatter(df, x="المخزون الحالي", y="الكمية المثالية للطلب (EOQ)", size="إجمالي الربح", color="التصنيف", hover_name="المنتج")
    st.plotly_chart(fig_eoq, use_container_width=True)

elif menu == "رادار التسويق والربحية":
    st.subheader("🎯 ربط التسويق بسلاسل الإمداد")
    st.info("نصيحة الذكاء الاصطناعي: لا تسوق لمنتجات الفئة C حتى لو كان هامش ربحها عالياً، ركز ميزانيتك على الفئة A.")
    
    # حساب عائد الإعلان الافتراضي ROAS
    df['ROAS المتوقع'] = (df['إجمالي الربح'] / (df['إجمالي الربح'] * 0.2)).round(2) # محاكاة
    
    fig_marketing = px.bar(df.head(15), x="المنتج", y="إجمالي الربح", color="معدل المرتجعات (%)", title="أكثر 15 منتجاً ربحية مقابل نسبة المرتجعات")
    st.plotly_chart(fig_marketing, use_container_width=True)
    
    st.warning("⚠️ **ملاحظة للمسوق:** المنتجات ذات اللون الأحمر الداكن تعاني من مرتجعات عالية، يفضل مراجعة جودتها قبل زيادة ميزانية الإعلانات.")

elif menu == "محاكي الموردين":
    st.subheader("🚚 إدارة الموردين والمخاطر")
    fig_risk = px.scatter(df, x="زمن التوريد (أيام)", y="معدل المرتجعات (%)", size="المخزون الحالي", color="التصنيف", title="خريطة مخاطر الموردين")
    st.plotly_chart(fig_risk, use_container_width=True)
    st.write("المنتجات في أعلى يمين الخريطة تمثل **خطراً كبيراً**: توريد بطيء ومرتجعات عالية.")

# عرض البيانات الخام في الأسفل
with st.expander("📂 معاينة قاعدة البيانات الكاملة"):
    st.write(df)
