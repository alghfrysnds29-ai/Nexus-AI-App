import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

st.set_page_config(page_title="Nexus AI | Enterprise", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    div[data-testid="stMetric"] { background-color: #ffffff !important; border-top: 5px solid #3b82f6 !important; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# محسّن: Smart Column Mapper يدعم تطابق جزئي وحالة أحرف مختلفة
def smart_col_mapper(df):
    mapping = {
        "المنتج": ["المنتج", "اسم المنتج", "Product", "Item", "Name"],
        "المورد": ["المورد", "Supplier", "Vendor"],
        "المخزون الحالي": ["المخزون", "Stock", "Inventory", "Qty", "Quantity"],
        "المبيعات الشهرية": ["المبيعات", "Sales", "Monthly Sales", "Monthly_Sales"],
        "تكلفة الوحدة": ["التكلفة", "Cost", "Unit Cost", "Unit_Cost"],
        "سعر البيع": ["السعر", "Price", "Selling Price", "Sale Price"],
        "زمن التوريد (أيام)": ["زمن التوريد", "Lead Time", "Lead_Time"],
        "معدل المرتجعات (%)": ["المرتجعات", "Returns", "Return Rate", "Return_Rate"]
    }
    new_cols = {}
    cols_lower = {c: c.lower().strip() for c in df.columns}
    for official_name, aliases in mapping.items():
        alias_lowers = [a.lower() for a in aliases]
        found = False
        for col, col_lower in cols_lower.items():
            # تطابق كامل أو تطابق جزئي للكلمة الأساسية
            if col_lower in alias_lowers or any(a in col_lower for a in alias_lowers):
                new_cols[col] = official_name
                found = True
                break
        # لا نكسر إذا لم نجد العمود؛ سننشئه لاحقاً في المعالجة
    return df.rename(columns=new_cols)

# معالجة بيانات أكثر مرونة
def process_data(df):
    d = df.copy()

    # تأكد من وجود الأعمدة الأساسية، وإن لم تكن موجودة أنشئها بقيم افتراضية مع تحذير غير متطفل
    required_cols = {
        "المبيعات الشهرية": 0,
        "تكلفة الوحدة": 0.0,
        "سعر البيع": 0.0,
        "معدل المرتجعات (%)": 0.0,
        "المخزون الحالي": 0
    }
    for col, default in required_cols.items():
        if col not in d.columns:
            d[col] = default

    # إجمالي الربح
    if 'إجمالي الربح' not in d.columns:
        d['إجمالي الربح'] = (d['سعر البيع'] - d['تكلفة الوحدة']) * d['المبيعات الشهرية']

    # ABC classification
    d = d.sort_values(by='إجمالي الربح', ascending=False).reset_index(drop=True)
    d['Cumulative_Profit'] = d['إجمالي الربح'].cumsum()
    total_p = d['إجمالي الربح'].sum() if d['إجمالي الربح'].sum() != 0 else 1
    d['Profit_%'] = (d['Cumulative_Profit'] / total_p) * 100
    d['التصنيف'] = d['Profit_%'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))

    # EOQ مع حماية من القسمة على صفر والقيم السالبة
    annual_demand = (d['المبيعات الشهرية'] * 12).clip(lower=0)
    holding_cost = (d['تكلفة الوحدة'] * 0.2 + 0.1).replace(0, np.nan)
    eoq = np.sqrt((2 * annual_demand * 150) / holding_cost)
    eoq = eoq.replace([np.inf, -np.inf], 0).fillna(0).astype(int)
    d['الكمية المثالية للطلب (EOQ)'] = eoq

    # أيام الركود عشوائية إن لم تكن موجودة
    if 'أيام الركود' not in d.columns:
        d['أيام الركود'] = np.random.randint(5, 120, len(d))

    return d

# قراءة الملف مع استخدام بايتس لمنع بقاء البيانات الافتراضية بعد الرفع
@st.cache_data
def load_initial_data(file_bytes, filename):
    if file_bytes is not None:
        try:
            if filename.lower().endswith('xlsx'):
                df_raw = pd.read_excel(io.BytesIO(file_bytes))
            else:
                df_raw = pd.read_csv(io.BytesIO(file_bytes))
            df_mapped = smart_col_mapper(df_raw)
            return df_mapped, False
        except Exception as e:
            # في حال فشل القراءة، نعيد None مع العلم أننا لسنا في وضع العرض التجريبي
            return pd.DataFrame(), False
    else:
        demo = pd.DataFrame({
            "المنتج": ["عطر ملكي", "بخور عود"],
            "المورد": ["مورد 1", "مورد 2"],
            "المخزون الحالي": [50, 100],
            "المبيعات الشهرية": [200, 80],
            "تكلفة الوحدة": [100, 50],
            "سعر البيع": [300, 150],
            "زمن التوريد (أيام)": [7, 10],
            "معدل المرتجعات (%)": [1.5, 0.5]
        })
        return demo, True

# Sidebar
st.sidebar.header("NEXUS AI")
company_name = st.sidebar.text_input("🏢 اسم شركتك", "الماجد للعود")
uploaded_file = st.sidebar.file_uploader("📥 ارفع بيانات شركتك (Excel/CSV)", type=['xlsx', 'csv'])

# اقرأ الملف كبايتس ثم مرره إلى الدالة المخبأة
file_bytes = None
filename = ""
if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    filename = uploaded_file.name
    # أعد مؤشر الملف إن احتجنا لقراءته لاحقاً
    try:
        uploaded_file.seek(0)
    except:
        pass

raw_df, using_demo = load_initial_data(file_bytes if file_bytes is not None else None, filename)

# إذا كانت القراءة فشلت وأعدنا DataFrame فارغ، نعرض تحذيراً ونعود للعرض التجريبي
if raw_df.empty and not using_demo:
    st.sidebar.error("حدث خطأ في قراءة الملف. تأكد من صيغة الملف وحاول مرة أخرى.")
    raw_df, using_demo = load_initial_data(None, "")

df = process_data(raw_df)

if not using_demo:
    st.sidebar.success(f"✅ تم تحليل بيانات {company_name} بنجاح")
else:
    st.sidebar.info("عرض بيانات تجريبية. ارفع ملفك لاستبدالها ببياناتك الحقيقية.")

menu = st.sidebar.radio("القائمة الرئيسية:", ["🏠 ملخص تنفيذي", "📦 المستودع والطلب", "🔮 التنبؤ بالطلب", "❄️ تقرير الراكد"])

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
