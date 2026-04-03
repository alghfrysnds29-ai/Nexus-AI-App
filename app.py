import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

# --- 1. إعدادات الهوية البصرية ---
st.set_page_config(page_title="Nexus AI | Enterprise", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    div[data-testid="stMetric"] { background-color: #ffffff !important; border-top: 5px solid #3b82f6 !important; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك الربط الذكي للأعمدة (Smart Column Mapper) ---
# هذه الدالة تضمن أن الموقع سيحلل ملف العميل مهما كانت مسميات الأعمدة لديه
def smart_col_mapper(df):
    mapping = {
        "المنتج": ["المنتج", "اسم المنتج", "Product", "Item", "Name"],
        "المورد": ["المورد", "Supplier", "Vendor"],
        "المخزون الحالي": ["المخزون", "Stock", "Inventory", "Qty"],
        "المبيعات الشهرية": ["المبيعات", "Sales", "Monthly Sales"],
        "تكلفة الوحدة": ["التكلفة", "Cost", "Unit Cost"],
        "سعر البيع": ["السعر", "Price", "Selling Price"],
        "زمن التوريد (أيام)": ["زمن التوريد", "Lead Time"],
        "معدل المرتجعات (%)": ["المرتجعات", "Returns"]
    }
    new_cols = {}
    for official_name, aliases in mapping.items():
        for col in df.columns:
            if col in aliases or col.lower() in [a.lower() for a in aliases]:
                new_cols[col] = official_name
                break
    return df.rename(columns=new_cols)

# --- 3. معالجة البيانات ---
def process_data(df):
    d = df.copy()
    # حسابات أساسية في حال عدم وجودها بالملف
    if 'إجمالي الربح' not in d.columns:
        d['إجمالي الربح'] = (d['سعر البيع'] - d['تكلفة الوحدة']) * d['المبيعات الشهرية']
    
    # تصنيف ABC
    d = d.sort_values(by='إجمالي الربح', ascending=False)
    d['Cumulative_Profit'] = d['إجمالي الربح'].cumsum()
    total_p = d['إجمالي الربح'].sum() if d['إجمالي الربح'].sum() != 0 else 1
    d['Profit_%'] = (d['Cumulative_Profit'] / total_p) * 100
    d['التصنيف'] = d['Profit_%'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))
    
    # حساب الكمية المثالية EOQ
    d['الكمية المثالية للطلب (EOQ)'] = np.sqrt((2 * (d['المبيعات الشهرية'] * 12) * 150) / (d['تكلفة الوحدة'] * 0.2 + 0.1)).fillna(0).astype(int)
    d['أيام الركود'] = np.random.randint(5, 120, len(d))
    return d

# --- 4. القائمة الجانبية وتحميل الملف ---
st.sidebar.header("NEXUS AI")
company_name = st.sidebar.text_input("🏢 اسم شركتك", "الماجد للعود")
uploaded_file = st.sidebar.file_uploader("📥 ارفع بيانات شركتك (Excel/CSV)", type=['xlsx', 'csv'])

# منطق التحليل: إذا رفع العميل ملفاً، نستخدمه، وإذا لم يرفع، نستخدم بيانات افتراضية (Demo)
@st.cache_data
def load_initial_data(file):
    if file is not None:
        df_raw = pd.read_excel(file) if file.name.endswith('xlsx') else pd.read_csv(file)
        df_mapped = smart_col_mapper(df_raw)
        return df_mapped
    else:
        # بيانات افتراضية للعرض فقط
        return pd.DataFrame({
            "المنتج": ["عطر ملكي", "بخور عود"], "المورد": ["مورد 1", "مورد 2"],
            "المخزون الحالي": [50, 100], "المبيعات الشهرية": [200, 80],
            "تكلفة الوحدة": [100, 50], "سعر البيع": [300, 150],
            "زمن التوريد (أيام)": [7, 10], "معدل المرتجعات (%)": [1.5, 0.5]
        })

raw_df = load_initial_data(uploaded_file)
df = process_data(raw_df)

if uploaded_file:
    st.sidebar.success(f"✅ تم تحليل بيانات {company_name} بنجاح")

menu = st.sidebar.radio("القائمة الرئيسية:", ["🏠 ملخص تنفيذي", "📦 المستودع والطلب", "🔮 التنبؤ بالطلب", "❄️ تقرير الراكد"])

# --- 5. عرض النتائج ---
st.title(f"📊 تحليلات شركة {company_name}")

if menu == "🏠 ملخص تنفيذي":
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الربح من ملفك", f"{int(df['إجمالي الربح'].sum()):,} ر.س")
    c2.metric("عدد المنتجات المحللة", len(df))
    c3.metric("متوسط المرتجعات", f"{df['معدل المرتجعات (%)'].mean():.1f}%")
    
    st.plotly_chart(px.pie(df, names='التصنيف', values='إجمالي الربح', hole=0.4, title="تحليل أرباح منتجاتك"), use_container_width=True)

elif menu == "📦 المستودع والطلب":
    st.subheader("📦 تحليل الكميات بناءً على بيانات العميل")
    st.dataframe(df[['المنتج', 'المخزون الحالي', 'الكمية المثالية للطلب (EOQ)', 'التصنيف']], use_container_width=True)
    st.plotly_chart(px.bar(df, x="المنتج", y="المخزون الحالي", color="التصنيف", title="توزيع المخزون الحالي"), use_container_width=True)

elif menu == "🔮 التنبؤ بالطلب":
    st.subheader("🔮 توقعات المبيعات المستقبلية")
    df['الطلب المتوقع'] = (df['المبيعات الشهرية'] * 1.2).astype(int)
    st.plotly_chart(px.line(df, x="المنتج", y=["المبيعات الشهرية", "الطلب المتوقع"], title="المبيعات الحالية مقابل المتوقعة"), use_container_width=True)

elif menu == "❄️ تقرير الراكد":
    st.subheader("❄️ تحليل البضاعة الراكدة")
    dead_stock = df[df['أيام الركود'] > 60]
    st.warning(f"وجدنا {len(dead_stock)} منتجات راكدة في ملفك.")
    st.table(dead_stock[['المنتج', 'المخزون الحالي', 'أيام الركود']])

st.markdown("---")
st.caption(f"تطوير منى محمد | تحليل ذكي لبيانات {company_name} 2026")
