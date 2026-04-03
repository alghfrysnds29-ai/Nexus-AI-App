import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# --- 1. إعدادات الهوية البصرية ---
st.set_page_config(page_title="Nexus AI | Supply Chain Intelligence", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; background-color: #f4f7f9; }
    .stMetric { background-color: #ffffff; border-radius: 15px; padding: 20px; border-right: 5px solid #3b82f6; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .main-title { color: #1e3a8a; text-align: center; font-weight: 700; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك المعالجة الذكي (The Intelligence Engine) ---
def analyze_supply_chain(df):
    d = df.copy()
    
    # حساب المقاييس الأساسية (KPIs)
    # 1. الربحية
    d['إجمالي الربح'] = (d['سعر البيع'] - d['تكلفة الوحدة']) * d['المبيعات الشهرية']
    
    # 2. تحليل ABC (أهمية المنتج في سلاسل الإمداد)
    d = d.sort_values(by='إجمالي الربح', ascending=False)
    d['Cumulative_Profit'] = d['إجمالي الربح'].cumsum()
    total_p = d['إجمالي الربح'].sum() if d['إجمالي الربح'].sum() != 0 else 1
    d['Profit_%'] = (d['Cumulative_Profit'] / total_p) * 100
    d['التصنيف الاستراتيجي'] = d['Profit_%'].apply(lambda x: 'A (عالي القيمة)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (منخفض)'))
    
    # 3. كفاية المخزون (Inventory Coverage)
    # كم شهر سيكفي المخزون الحالي بناءً على المبيعات؟
    d['كفاية المخزون (شهور)'] = (d['المخزون الحالي'] / d['المبيعات الشهرية'].replace(0, 1)).round(1)
    
    # 4. نقطة إعادة الطلب (Reorder Point)
    # (المبيعات اليومية * زمن التوريد) + مخزون الأمان (عشوائي للمحاكاة)
    daily_sales = d['المبيعات الشهرية'] / 30
    d['نقطة إعادة الطلب'] = (daily_sales * d['زمن التوريد (أيام)']).astype(int) + 5
    
    return d

# --- 3. القائمة الجانبية والرفع (The Gateway) ---
st.sidebar.markdown("<h1 style='text-align: center;'>NEXUS AI</h1>", unsafe_allow_html=True)
company_name = st.sidebar.text_input("🏢 اسم المنشأة", "Nexus Enterprise")
uploaded_file = st.sidebar.file_uploader("📥 ارفع ملف بيانات سلاسل الإمداد (Excel/CSV)", type=['xlsx', 'csv'])

# بيانات افتراضية احترافية في حال عدم الرفع (للمعاينة)
if not uploaded_file:
    demo_data = pd.DataFrame({
        "المنتج": ["مجموعة عطور A", "بخور سوبر", "دهن عود فخم", "مبخرة كهربائية", "علب هدايا"],
        "المخزون الحالي": [120, 15, 5, 300, 50],
        "المبيعات الشهرية": [450, 60, 20, 180, 500],
        "تكلفة الوحدة": [85, 210, 1200, 45, 10],
        "سعر البيع": [280, 550, 3200, 140, 35],
        "زمن التوريد (أيام)": [14, 7, 21, 30, 5]
    })
    df_raw = demo_data
    st.info("💡 قمنا بتحميل بيانات تجريبية. ارفع ملفك الخاص للحصول على تقاريرك الحقيقية.")
else:
    if uploaded_file.name.endswith('xlsx'):
        df_raw = pd.read_excel(uploaded_file)
    else:
        df_raw = pd.read_csv(uploaded_file)
    st.sidebar.success(f"✅ تم استلام بيانات {company_name}")

# تشغيل التحليل
df_final = analyze_supply_chain(df_raw)

# --- 4. عرض التقارير (The Dashboard) ---
st.markdown(f"<h1 class='main-title'>تقرير سلاسل الإمداد الذكي لـ {company_name}</h1>", unsafe_allow_html=True)

# صف المؤشرات الرئيسية
m1, m2, m3, m4 = st.columns(4)
m1.metric("إجمالي القيمة المخزنية", f"{int((df_final['المخزون الحالي'] * df_final['تكلفة الوحدة']).sum()):,} ر.س")
m2.metric("أرباح الدورة الحالية", f"{int(df_final['إجمالي الربح'].sum()):,} ر.س")
m3.metric("المنتجات تحت خطر النفاذ", len(df_final[df_final['المخزون الحالي'] <= df_final['نقطة إعادة الطلب']]))
m4.metric("كفاءة التوريد", "88%", "2030 Vision")

st.markdown("---")

# تبويبات التقارير
tab1, tab2, tab3 = st.tabs(["🎯 تحليل المخزون الاستراتيجي", "📦 تخطيط المشتريات", "💰 تحليل الربحية والنمو"])

with tab1:
    col_a, col_b = st.columns([2, 1])
    with col_a:
        fig = px.bar(df_final, x="المنتج", y="كفاية المخزون (شهور)", color="التصنيف الاستراتيجي", 
                     title="كم شهراً سيكفي مخزونك الحالي؟", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.subheader("⚠️ منتجات تحتاج طلب فوراً")
        reorder_needed = df_final[df_final['المخزون الحالي'] <= df_final['نقطة إعادة الطلب']]
        if not reorder_needed.empty:
            for _, row in reorder_needed.iterrows():
                st.error(f"**{row['المنتج']}**: المخزون ({row['المخزون الحالي']}) وصل لنقطة الخطر.")
        else:
            st.success("جميع مستويات المخزون آمنة حالياً.")

with tab2:
    st.subheader("🚚 جدول مقترحات أوامر الشراء")
    df_final['الكمية المقترح طلبها'] = (df_final['المبيعات الشهرية'] * 1.5 - df_final['المخزون الحالي']).clip(lower=0).astype(int)
    st.table(df_final[['المنتج', 'المخزون الحالي', 'نقطة إعادة الطلب', 'الكمية المقترح طلبها', 'التصنيف الاستراتيجي']])

with tab3:
    st.subheader("💸 تحليل الأثر المالي لكل فئة")
    fig_pie = px.sunburst(df_final, path=['التصنيف الاستراتيجي', 'المنتج'], values='إجمالي الربح',
                          title="توزيع الأرباح حسب فئة المنتج ووزنه في السلسلة")
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 5. تصدير التقرير ---
st.markdown("---")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_final.to_excel(writer, index=False, sheet_name='Supply_Chain_Report')
st.download_button(label="📥 تحميل التقرير التحليلي كملف Excel", data=buffer.getvalue(), 
                   file_name=f"Supply_Chain_Report_{company_name}.xlsx", mime="application/vnd.ms-excel")

st.caption(f"تم التطوير بواسطة منى محمد | Nexus AI 2026 - جميع الحقوق محفوظة لـ {company_name}")
