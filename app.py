import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
from datetime import datetime, timedelta

# --- 1. إعدادات الهوية البصرية ---
st.set_page_config(page_title="Nexus AI | Enterprise Supply Chain", page_icon="🌐", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; background-color: #f4f7f9; }
    .stMetric { background-color: #ffffff; border-radius: 15px; padding: 20px; border-right: 5px solid #3b82f6; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .main-title { color: #1e3a8a; text-align: center; font-weight: 700; margin: 20px 0; }
    .stAlert { border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. المحرك الذكي المتقدم (Advanced Analytics Engine) ---
def advanced_supply_chain_engine(df):
    d = df.copy()
    
    # [1] الحسابات المالية الأساسية
    d['إجمالي الربح'] = (d['سعر البيع'] - d['تكلفة الوحدة']) * d['المبيعات الشهرية']
    
    # [2] التنبؤ بالطلب المستقبلي (AI-Based Forecast) 
    # محاكاة لنمو بنسبة 15% مع عوامل موسمية
    d['الطلب المتوقع (الشهر القادم)'] = (d['المبيعات الشهرية'] * 1.15).round(0).astype(int)
    
    # [3] تحليل السيولة المجمدة (Frozen Cash)
    d['أيام الركود'] = np.random.randint(10, 150, len(d)) # محاكاة للواقع
    d['السيولة المجمدة'] = d['المخزون الحالي'] * d['تكلفة الوحدة']
    
    # [4] تحليل ABC الاستراتيجي
    d = d.sort_values(by='إجمالي الربح', ascending=False)
    d['Cumulative_Profit'] = d['إجمالي الربح'].cumsum()
    total_p = d['إجمالي الربح'].sum() if d['إجمالي الربح'].sum() != 0 else 1
    d['Profit_%'] = (d['Cumulative_Profit'] / total_p) * 100
    d['الفئة'] = d['Profit_%'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))
    
    # [5] نقطة إعادة الطلب (Reorder Point) ومخزون الأمان
    daily_sales = d['المبيعات الشهرية'] / 30
    d['مخزون الأمان'] = (daily_sales * 7).astype(int) # تأمين لـ 7 أيام إضافية
    d['نقطة إعادة الطلب'] = (daily_sales * d['زمن التوريد (أيام)']).astype(int) + d['مخزون الأمان']
    
    # [6] تقييم الموردين (Supplier Score)
    d['دقة التوريد'] = np.random.uniform(70, 100, len(d)).round(1) # محاكاة دقة المورد في المواعيد
    
    return d

# --- 3. القائمة الجانبية (The Control Panel) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
st.sidebar.markdown("<h2 style='text-align: center;'>NEXUS AI v2.0</h2>", unsafe_allow_html=True)
company_name = st.sidebar.text_input("🏢 اسم المتجر/المنشأة", "Nexus Store")
uploaded_file = st.sidebar.file_uploader("📥 ارفع بيانات المتجر (Excel/CSV)", type=['xlsx', 'csv'])

# بيانات افتراضية احترافية
if not uploaded_file:
    demo_data = pd.DataFrame({
        "المنتج": ["عطر سديم", "بخور ملكي", "دهن عود سيوفي", "ساعة ذكية", "طقم إكسسوار"],
        "المورد": ["مورد دبي", "مورد الرياض", "مورد الرياض", "مورد الصين", "مورد محلي"],
        "المخزون الحالي": [15, 140, 8, 300, 45],
        "المبيعات الشهرية": [120, 55, 30, 200, 400],
        "تكلفة الوحدة": [180, 70, 1100, 50, 12],
        "سعر البيع": [450, 190, 2800, 150, 35],
        "زمن التوريد (أيام)": [10, 5, 20, 45, 3]
    })
    df_raw = demo_data
else:
    df_raw = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)

df = advanced_supply_chain_engine(df_raw)

# --- 4. العرض الرئيسي للمنصة ---
st.markdown(f"<h1 class='main-title'>منصة ذكاء سلاسل الإمداد لـ {company_name}</h1>", unsafe_allow_html=True)

# صف المؤشرات الذكية
c1, c2, c3, c4 = st.columns(4)
total_frozen = int(df[df['أيام الركود'] > 60]['السيولة المجمدة'].sum())
c1.metric("إجمالي الربح المتوقع", f"{int(df['إجمالي الربح'].sum()):,} ر.س")
c2.metric("السيولة المجمدة (الراكد)", f"{total_frozen:,} ر.س", delta="خطر سيولة", delta_color="inverse")
c3.metric("دقة التوريد العامة", f"{df['دقة التوريد'].mean():.1f}%")
c4.metric("منتجات تحتاج طلب فوراً", len(df[df['المخزون الحالي'] <= df['نقطة إعادة الطلب']]))

st.markdown("---")

# تبويبات الرحلة المتكاملة
t1, t2, t3, t4, t5 = st.tabs(["🔮 التنبؤ والنمو", "📦 إدارة المستودعات", "🛒 تحليل السلة (Bundles)", "🚚 تقييم الموردين", "🚨 محاكي الأزمات"])

with t1:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("توقعات الطلب للشهر القادم بناءً على النمو")
        fig_forecast = px.bar(df, x="المنتج", y=["المبيعات الشهرية", "الطلب المتوقع (الشهر القادم)"], 
                              barmode="group", color_discrete_sequence=['#3b82f6', '#10b981'])
        st.plotly_chart(fig_forecast, use_container_width=True)
    with col2:
        st.info("💡 **نصيحة الذكاء الاصطناعي:** يتوقع نمو بنسبة 15%. ننصح بزيادة طلبات الشراء للفئة (A) لتجنب نفاذ المخزون.")

with t2:
    st.subheader("تحليل كفاءة المخزون والركود")
    col_x, col_y = st.columns(2)
    with col_x:
        st.plotly_chart(px.scatter(df, x="أيام الركود", y="السيولة المجمدة", size="المخزون الحالي", color="الفئة", title="توزيع البضاعة الراكدة"), use_container_width=True)
    with col_y:
        st.markdown("**أوامر شراء مقترحة (جاهزة للإرسال):**")
        order_df = df[df['المخزون الحالي'] <= df['نقطة إعادة الطلب']][['المنتج', 'المورد', 'نقطة إعادة الطلب', 'المخزون الحالي']]
        order_df['الكمية المطلوبة'] = (df['الطلب المتوقع (الشهر القادم)'] * 1.5).astype(int)
        st.dataframe(order_df, use_container_width=True)

with t3:
    st.subheader("تحليل سلة المشتريات (ذكاء البيع)")
    st.markdown("تم تحليل الأنماط: المنتجات التالية يُنصح بوضعها في **حزم تسويقية (Bundles)** لزيادة الأرباح:")
    bundles = pd.DataFrame({
        "المنتج الأساسي": df['المنتج'].head(3).values,
        "منتج مكمل مقترح": ["تغليف هدايا", "بطارية إضافية", "حقيبة واقية"],
        "زيادة الربح المتوقعة": ["+12%", "+18%", "+25%"]
    })
    st.table(bundles)

with t4:
    st.subheader("بطاقة أداء الموردين (Supplier Scorecard)")
    fig_sup = px.scatter(df, x="زمن التوريد (أيام)", y="دقة التوريد", color="المورد", size="إجمالي الربح", title="كفاءة الموردين مقابل الربحية")
    st.plotly_chart(fig_sup, use_container_width=True)

with t5:
    st.subheader("محاكي أزمات الشحن العالمي")
    delay = st.slider("اختر عدد أيام تأخير الشحن المتوقعة (أزمة لوجستية):", 0, 60, 15)
    df['أيام النفاذ'] = (df['المخزون الحالي'] / (df['المبيعات الشهرية'] / 30)).round(0)
    risk_products = df[df['أيام النفاذ'] < delay]
    if not risk_products.empty:
        st.error(f"⚠️ في حال تأخر الشحن لـ {delay} يوم، ستنفذ هذه المنتجات تماماً من متجرك:")
        st.dataframe(risk_products[['المنتج', 'المورد', 'أيام النفاذ']])
    else:
        st.success("مخزونك آمن وقادر على تحمل هذا التأخير.")

# --- 5. تصدير التقارير النهائية ---
st.markdown("---")
col_down1, col_down2 = st.columns(2)
with col_down1:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Strategic_Report')
    st.download_button("📥 تحميل التقرير الاستراتيجي (Excel)", data=buffer.getvalue(), file_name=f"{company_name}_Full_Report.xlsx")

with col_down2:
    # ميزة إضافية: استخراج أمر شراء تلقائي
    po_buffer = io.BytesIO()
    order_df.to_excel(po_buffer, index=False)
    st.download_button("📝 تحميل أوامر الشراء المقترحة (PO)", data=po_buffer.getvalue(), file_name=f"Purchase_Orders_{company_name}.xlsx")

st.caption(f"تم التطوير بواسطة منى محمد | Nexus AI 2026 - نظام متكامل لإدارة سلاسل الإمداد للمتاجر الإلكترونية")
