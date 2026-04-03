import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime, timedelta

# --- 1. إعدادات الهوية البصرية والوضع الداكن ---
st.set_page_config(page_title="Nexus AI | Enterprise BI", page_icon="💎", layout="wide")

# تصميم CSS احترافي يدعم التوجه RTL والجمالية العالية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #ffffff; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); border-top: 4px solid #2563eb; }
    .notification-badge { background-color: #ef4444; color: white; padding: 4px 8px; border-radius: 50%; font-size: 12px; vertical-align: top; }
    .nav-card { background: white; padding: 10px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك توليد البيانات الضخمة (Synthetic Big Data) ---
@st.cache_data
def generate_big_data(rows=10000):
    np.random.seed(42)
    categories = ['إلكترونيات', 'عطور', 'أزياء', 'مستلزمات منزلية', 'تجميل']
    suppliers = [f'مورد {i}' for i in range(1, 101)]
    
    data = {
        "المنتج": [f"منتج {i}" for i in range(1, rows + 1)],
        "الفئة": np.random.choice(categories, rows),
        "المورد": np.random.choice(suppliers, rows),
        "المخزون الحالي": np.random.randint(0, 500, rows),
        "المبيعات الشهرية": np.random.randint(10, 1000, rows),
        "تكلفة الوحدة": np.random.uniform(20, 1500, rows).round(2),
        "سعر البيع": np.random.uniform(50, 3000, rows).round(2),
        "زمن التوريد (أيام)": np.random.randint(3, 45, rows),
        "المرتجعات": np.random.randint(0, 20, rows)
    }
    df = pd.DataFrame(data)
    # ضمان أن سعر البيع أكبر من التكلفة
    df['سعر البيع'] = df[['تكلفة الوحدة', 'سعر البيع']].max(axis=1) + 10
    return df

# --- 3. محرك التحليل المتقدم (The Pro Engine) ---
def advanced_pro_engine(df, ship_cost, tax_pct, op_cost_pct):
    d = df.copy()
    
    # [أ] تحليل تكلفة الهبوط (Landed Cost)
    d['رسوم البوابة والضرائب'] = d['سعر البيع'] * (tax_pct / 100)
    d['التكلفة الكلية للقطعة'] = d['تكلفة الوحدة'] + ship_cost + d['رسوم البوابة والضرائب']
    
    # [ب] حسابات الربحية (Gross & Net)
    d['إجمالي الربح'] = (d['سعر البيع'] - d['التكلفة الكلية للقطعة']) * d['المبيعات الشهرية']
    d['صافي الربح الحقيقي'] = d['إجمالي الربح'] * (1 - op_cost_pct / 100)
    
    # [ج] مخزن الأمان الذكي (Safety Stock)
    # المعادلة: (أقصى مبيعات * أقصى زمن) - (المتوسط)
    avg_daily_sales = d['المبيعات الشهرية'] / 30
    d['مخزون الأمان'] = (avg_daily_sales * 1.5 * d['زمن التوريد (أيام)'] * 1.2 - (avg_daily_sales * d['زمن التوريد (أيام)'])).astype(int)
    d['نقطة إعادة الطلب'] = (avg_daily_sales * d['زمن التوريد (أيام)']).astype(int) + d['مخزون الأمان']
    
    # [د] تصنيف ABC
    d = d.sort_values(by='صافي الربح الحقيقي', ascending=False)
    d['Cum_Profit'] = d['صافي الربح الحقيقي'].cumsum()
    total_net = d['صافي الربح الحقيقي'].sum() if d['صافي الربح الحقيقي'].sum() != 0 else 1
    d['Profit_Pct'] = (d['Cum_Profit'] / total_net) * 100
    d['الفئة'] = d['Profit_Pct'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))
    
    return d

# --- 4. واجهة المستخدم والتحكم ---
st.sidebar.markdown("## ⚙️ إعدادات المتجر المتقدمة")
company_name = st.sidebar.text_input("اسم المتجر", "الماجد للعود - فرع الرياض")

# قسم إدخال التكاليف المخفية
with st.sidebar.expander("💰 محاكي تكلفة الهبوط والربح"):
    ship_cost = st.number_input("تكلفة الشحن لكل قطعة (ر.س)", 0.0, 500.0, 15.0)
    tax_pct = st.slider("الضرائب ورسوم البوابة (%)", 0, 30, 15)
    op_cost = st.slider("المصاريف التشغيلية/رواتب/إعلانات (%)", 0, 50, 20)

st.sidebar.markdown("---")
use_big_data = st.sidebar.checkbox("تفعيل قاعدة البيانات الضخمة (10,000 منتج)", value=True)
uploaded_file = st.sidebar.file_uploader("أو ارفع ملفك الخاص", type=['xlsx', 'csv'])

# جلب البيانات
if uploaded_file:
    raw_df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
else:
    raw_df = generate_big_data(10000 if use_big_data else 10)

df = advanced_pro_engine(raw_df, ship_cost, tax_pct, op_cost)

# --- 5. نظام التنبيهات الذكي (Notification Center) ---
critical_stock = df[df['المخزون الحالي'] <= df['نقطة إعادة الطلب']]
st.markdown(f"### 🔔 التنبيهات الذكية <span class='notification-badge'>{len(critical_stock.head(5))}</span>", unsafe_allow_html=True)
if not critical_stock.empty:
    with st.expander("عرض التنبيهات العاجلة"):
        for _, row in critical_stock.head(3).iterrows():
            st.error(f"تحذير: المنتج **{row['المنتج']}** قارب على النفاذ. المخزون الحالي: {row['المخزون الحالي']} | نقطة إعادة الطلب: {row['نقطة إعادة الطلب']}")

# --- 6. لوحة القيادة الاستراتيجية ---
st.title(f"🚀 لوحة تحكم ذكاء الأعمال: {company_name}")

m1, m2, m3, m4 = st.columns(4)
m1.metric("صافي الربح الحقيقي", f"{int(df['صافي الربح الحقيقي'].sum()):,} ر.س", "صافي")
m2.metric("قيمة رأس المال المخزني", f"{int((df['المخزون الحالي'] * df['تكلفة الوحدة']).sum()):,} ر.س")
m3.metric("دوران المخزون (متوسط)", f"{(df['المبيعات الشهرية'].sum() / df['المخزون الحالي'].sum()):.2f}x")
m4.metric("العائد على الاستثمار ROI", f"{((df['صافي الربح الحقيقي'].sum() / (df['تكلفة الوحدة'] * df['المبيعات الشهرية']).sum()) * 100):.1f}%")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📈 التحليل المالي", "📦 سلاسل الإمداد", "🤝 الموردين والشركاء", "⚙️ الربط والإعدادات"])

with tab1:
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.plotly_chart(px.pie(df, names='الفئة', values='صافي الربح الحقيقي', hole=0.5, title="توزيع صافي الأرباح حسب فئة المنتج (ABC)"), use_container_width=True)
    with col_f2:
        st.plotly_chart(px.histogram(df, x="الفئة", y="صافي الربح الحقيقي", color="الفئة", title="مساهمة الفئات في الدخل الصافي"), use_container_width=True)

with tab2:
    st.subheader("📦 إدارة المخزن والأمان الذكي")
    st.dataframe(df[['المنتج', 'المخزون الحالي', 'مخزون الأمان', 'نقطة إعادة الطلب', 'الفئة']].head(100), use_container_width=True)
    st.plotly_chart(px.scatter(df.head(500), x="المخزون الحالي", y="نقطة إعادة الطلب", size="المبيعات الشهرية", color="الفئة", hover_name="المنتج"), use_container_width=True)

with tab3:
    st.subheader("🚚 تحليل أداء الموردين (كشف المقصرين)")
    # تجميع البيانات حسب المورد
    sup_df = df.groupby('المورد').agg({'زمن التوريد (أيام)': 'mean', 'صافي الربح الحقيقي': 'sum', 'المنتج': 'count'}).reset_index()
    fig_sup = px.scatter(sup_df, x="زمن التوريد (أيام)", y="صافي الربح الحقيقي", size="المنتج", color="المورد", title="الموردين الأكثر ربحية مقابل سرعة التوريد")
    st.plotly_chart(fig_sup, use_container_width=True)

with tab4:
    st.subheader("🔌 الربط مع المنصات (API Integration)")
    st.info("سيتم تفعيل الربط المباشر قريباً لسحب البيانات لحظياً من منصاتك المفضلة.")
    c_api1, c_api2, c_api3 = st.columns(3)
    c_api1.image("https://cdn.iconscout.com/icon/free/png-256/free-shopify-226578.png", width=100)
    c_api2.markdown("### Salla / سلة")
    c_api3.markdown("### Zid / زد")
    st.markdown("---")
    st.markdown("🔒 **الأمان والخصوصية:** جميع البيانات تُعالج محلياً في متصفحك ولا يتم تخزين أي سجلات تجارية على خوادمنا.")

# --- 7. تصدير التقارير (White Label PDF & Excel) ---
st.markdown("---")
st.subheader("📑 تصدير التقارير الاستراتيجية")
c_down1, c_down2 = st.columns(2)
with c_down1:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Main_Report')
    st.download_button("📥 تحميل التقرير الختامي (Excel)", data=output.getvalue(), file_name=f"NexusAI_{company_name}.xlsx")
with c_down2:
    st.button("📄 تحميل تقرير الأداء الشهري (PDF) - قريباً", help="ميزة الفئة الاحترافية")

st.caption(f"تم التطوير بواسطة منى محمد | Nexus AI Enterprise 2026 - الإصدار 3.0")
