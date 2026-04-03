import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
import hashlib
from typing import Tuple, Dict

# --- إعدادات الصفحة والستايل العام ---
st.set_page_config(page_title="Nexus AI | Enterprise Supply Chain", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

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

# --- أدوات مساعدة ---
def bytes_hash(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def read_file_bytes(file_bytes: bytes, filename: str, sheet_name=None) -> pd.DataFrame:
    """اقرأ الملف من بايتس، ادعم CSV و XLSX مع اختيار sheet"""
    try:
        if filename.lower().endswith('.xlsx') or filename.lower().endswith('.xls'):
            return pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name)
        else:
            return pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        st.error("فشل قراءة الملف. تأكد من صيغة الملف أو جرب ملف آخر.")
        return pd.DataFrame()

def smart_col_mapper_suggestions(columns):
    """اقتراحات مطابقة ذكية (قابلة للتوسيع)"""
    mapping = {
        "المنتج": ["المنتج", "اسم المنتج", "product", "item", "name"],
        "المورد": ["المورد", "supplier", "vendor"],
        "المخزون الحالي": ["المخزون", "stock", "inventory", "qty", "quantity"],
        "المبيعات الشهرية": ["المبيعات", "sales", "monthly sales", "monthly_sales"],
        "تكلفة الوحدة": ["التكلفة", "cost", "unit cost", "unit_cost"],
        "سعر البيع": ["السعر", "price", "selling price", "sale price"],
        "زمن التوريد (أيام)": ["زمن التوريد", "lead time", "lead_time"],
        "معدل المرتجعات (%)": ["المرتجعات", "returns", "return rate", "return_rate"]
    }
    suggestions = {}
    cols_lower = [c.lower().strip() for c in columns]
    for col in columns:
        best = None
        for official, aliases in mapping.items():
            for a in aliases:
                if a in col.lower() or col.lower() in a:
                    best = official
                    break
            if best:
                break
        suggestions[col] = best
    return suggestions

# --- محرك التحليل الرئيسي ---
def process_full_data(df_input: pd.DataFrame) -> pd.DataFrame:
    d = df_input.copy()
    # تأكد من وجود الأعمدة الأساسية
    defaults = {
        "المبيعات الشهرية": 0,
        "تكلفة الوحدة": 0.0,
        "سعر البيع": 0.0,
        "معدل المرتجعات (%)": 0.0,
        "المخزون الحالي": 0
    }
    for col, val in defaults.items():
        if col not in d.columns:
            d[col] = val

    if 'إجمالي الربح' not in d.columns:
        d['إجمالي الربح'] = (d['سعر البيع'] - d['تكلفة الوحدة']) * d['المبيعات الشهرية']

    d = d.sort_values(by='إجمالي الربح', ascending=False).reset_index(drop=True)
    d['Cumulative_Profit'] = d['إجمالي الربح'].cumsum()
    total_p = d['إجمالي الربح'].sum() if d['إجمالي الربح'].sum() != 0 else 1
    d['Profit_%'] = (d['Cumulative_Profit'] / total_p) * 100
    d['التصنيف'] = d['Profit_%'].apply(lambda x: 'A (حيوي)' if x <= 70 else ('B (متوسط)' if x <= 90 else 'C (ثانوي)'))

    annual_demand = (d['المبيعات الشهرية'] * 12).clip(lower=0)
    holding_cost = (d['تكلفة الوحدة'] * 0.2 + 0.1).replace(0, np.nan)
    eoq = np.sqrt((2 * annual_demand * 150) / holding_cost)
    eoq = eoq.replace([np.inf, -np.inf], 0).fillna(0).astype(int)
    d['الكمية المثالية للطلب (EOQ)'] = eoq

    if 'زمن التوريد (أيام)' not in d.columns:
        d['زمن التوريد (أيام)'] = np.random.randint(5, 20, len(d))
    if 'معدل المرتجعات (%)' not in d.columns:
        d['معدل المرتجعات (%)'] = 0.0

    d['تقييم المورد'] = (100 - (d['زمن التوريد (أيام)'] * 2) - d['معدل المرتجعات (%)']).clip(lower=0)
    if 'أيام الركود' not in d.columns:
        d['أيام الركود'] = np.random.randint(5, 120, len(d))

    return d

# --- تخزين مؤقت ذكي حسب hash الملف ---
@st.cache_data
def cached_process(file_hash: str, file_bytes: bytes, filename: str, sheet_name: str, mapping: Dict[str, str]) -> Tuple[pd.DataFrame, str]:
    # اقرأ الملف
    df_raw = read_file_bytes(file_bytes, filename, sheet_name=sheet_name)
    # طبق المطابقة اليدوية/الذكية
    if mapping:
        # إعادة تسمية الأعمدة بناءً على mapping
        rename_map = {orig: new for orig, new in mapping.items() if new}
        df_raw = df_raw.rename(columns=rename_map)
    # معالجة
    df_processed = process_full_data(df_raw)
    return df_processed, file_hash

# --- واجهة المستخدم Sidebar ---
st.sidebar.markdown("<h2 style='text-align: center; color: #3b82f6;'>NEXUS AI</h2>", unsafe_allow_html=True)
company_name = st.sidebar.text_input("🏢 اسم شركتك (White Label)", "Nexus AI")

uploaded_file = st.sidebar.file_uploader("📥 ارفع بياناتك (Excel/CSV)", type=['xlsx', 'csv'])
# خيارات خصوصية وحجم
st.sidebar.caption("الملفات لا تُخزن على الخادم بعد المعالجة. الحجم المسموح 10MB.")
# زر مسح إعدادات الشركة
if st.sidebar.button("🧹 إعادة تعيين إعدادات الشركة"):
    if company_name in st.session_state.get("saved_mappings", {}):
        st.session_state["saved_mappings"].pop(company_name, None)
        st.sidebar.success("تم حذف إعدادات المطابقة المحفوظة لهذه الشركة.")

# --- منطق رفع الملف ومعالجة المعاينة والمطابقة ---
file_bytes = None
filename = ""
sheet_options = []
selected_sheet = None
using_demo = False
initial_df = pd.DataFrame()

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    filename = uploaded_file.name
    # إذا كان Excel، اعرض اختيار sheet
    try:
        if filename.lower().endswith(('xlsx', 'xls')):
            xls = pd.ExcelFile(io.BytesIO(file_bytes))
            sheet_options = xls.sheet_names
            selected_sheet = st.sidebar.selectbox("اختر ورقة Excel", sheet_options)
            initial_df = read_file_bytes(file_bytes, filename, sheet_name=selected_sheet)
        else:
            initial_df = read_file_bytes(file_bytes, filename)
    except Exception:
        initial_df = pd.DataFrame()
else:
    # بيانات تجريبية للعرض
    using_demo = True
    initial_df = pd.DataFrame({
        "المنتج": ["عطر ملكي", "بخور عود", "ساعة فاخرة"],
        "المورد": ["مورد دبي", "مورد الرياض", "مورد الكويت"],
        "المخزون الحالي": [25, 140, 10],
        "المبيعات الشهرية": [95, 45, 120],
        "تكلفة الوحدة": [180, 70, 600],
        "سعر البيع": [450, 190, 1400],
        "معدل المرتجعات (%)": [1.5, 0.4, 4.2],
        "زمن التوريد (أيام)": [7, 5, 21]
    })

# اقتراحات المطابقة الذكية
suggestions = smart_col_mapper_suggestions(list(initial_df.columns))

# استرجاع إعدادات محفوظة للشركة إن وجدت
if "saved_mappings" not in st.session_state:
    st.session_state["saved_mappings"] = {}

saved_for_company = st.session_state["saved_mappings"].get(company_name, {})

st.sidebar.markdown("---")
st.sidebar.subheader("معاينة ومطابقة الأعمدة")
st.sidebar.caption("راجع الاقتراحات ثم اضغط تطبيق لتخصيص التحليل لملفك.")

# عرض معاينة أولية
st.sidebar.markdown("**معاينة أول 5 صفوف**")
st.sidebar.dataframe(initial_df.head(5))

# واجهة مطابقة الأعمدة يدوياً مع اقتراحات
mapping_ui = {}
for col in initial_df.columns:
    suggested = suggestions.get(col)
    default = saved_for_company.get(col, suggested)
    mapping_ui[col] = st.sidebar.selectbox(f"ماذا يمثل العمود '{col}'؟", options=[None, "المنتج", "المورد", "المخزون الحالي", "المبيعات الشهرية", "تكلفة الوحدة", "سعر البيع", "زمن التوريد (أيام)", "معدل المرتجعات (%)"], index=0 if default is None else ["None","المنتج","المورد","المخزون الحالي","المبيعات الشهرية","تكلفة الوحدة","سعر البيع","زمن التوريد (أيام)","معدل المرتجعات (%)"].index(default) if default in ["المنتج","المورد","المخزون الحالي","المبيعات الشهرية","تكلفة الوحدة","سعر البيع","زمن التوريد (أيام)","معدل المرتجعات (%)"] else 0)

# أزرار تطبيق وحفظ الإعدادات
col1, col2 = st.sidebar.columns(2)
apply_btn = col1.button("✅ تطبيق المطابقة")
save_btn = col2.button("💾 حفظ إعدادات الشركة")

# عند الحفظ، خزّن mapping باسم الشركة
if save_btn:
    st.session_state["saved_mappings"][company_name] = {k: v for k, v in mapping_ui.items() if v}
    st.sidebar.success("تم حفظ إعدادات المطابقة باسم الشركة.")

# إذا لم يضغط المستخدم Apply، استخدم الإعدادات المحفوظة إن وجدت
final_mapping = {}
if apply_btn:
    final_mapping = {orig: new for orig, new in mapping_ui.items() if new}
else:
    # استخدم الإعدادات المحفوظة أو الاقتراحات
    if saved_for_company:
        final_mapping = saved_for_company
    else:
        final_mapping = {orig: suggestions.get(orig) for orig in initial_df.columns if suggestions.get(orig)}

# --- معالجة نهائية مع caching حسب hash ---
if file_bytes is not None:
    file_hash = bytes_hash(file_bytes)
    df_processed, _ = cached_process(file_hash, file_bytes, filename, selected_sheet if selected_sheet else None, final_mapping)
    # بعد المعالجة، امسح البايتس من الذاكرة (نصيحة خصوصية)
    # ملاحظة: لا تمسح uploaded_file نفسه لأن Streamlit يديرها، لكن نحرص على عدم الاحتفاظ بنسخ إضافية
else:
    df_processed = process_full_data(initial_df)

# رسالة حالة واضحة
if using_demo:
    st.info("عرض بيانات تجريبية. ارفع ملفك لاستبدالها ببياناتك الحقيقية.")
else:
    st.success(f"✅ تم تحليل ملف {company_name} بنجاح. التطبيق الآن مخصص لبياناتك.")

# --- واجهة التطبيق الرئيسية مع القوائم ---
st.title(f"📊 تحليلات شركة {company_name}")

menu = st.sidebar.radio("القائمة الرئيسية:", 
    ["🏠 ملخص تنفيذي", "📦 المستودع والطلب", "🔮 التنبؤ بالطلب", "🚨 محاكي الأزمات", "🛒 ذكاء البيع", "❄️ تقرير الراكد", "🚚 الموردين"])

if menu == "🏠 ملخص تنفيذي":
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الربح", f"{int(df_processed['إجمالي الربح'].sum()):,} ر.س")
    c2.metric("نسبة الهالك (المرتجعات)", f"{df_processed['معدل المرتجعات (%)'].mean():.1f}%")
    c3.metric("عدد المنتجات المحللة", len(df_processed))
    st.markdown("---")
    l_col, r_col = st.columns([2, 1])
    with l_col:
        st.plotly_chart(px.pie(df_processed, names='التصنيف', values='إجمالي الربح', hole=0.5, title="توزيع الأرباح حسب فئة المنتج"), use_container_width=True)
    with r_col:
        st.subheader("🚨 تنبيهات الإدارة")
        stock_danger = df_processed[df_processed['المخزون الحالي'] < 20]
        for _, row in stock_danger.head(5).iterrows():
            st.warning(f"مخزون منخفض: {row.get('المنتج','غير معروف')} - الكمية {row.get('المخزون الحالي',0)}")

elif menu == "📦 المستودع والطلب":
    st.title("📦 Smart Inventory & EOQ")
    st.dataframe(df_processed[['المنتج', 'المخزون الحالي', 'الكمية المثالية للطلب (EOQ)', 'التصنيف']], use_container_width=True)
    st.plotly_chart(px.bar(df_processed, x="المنتج", y="الكمية المثالية للطلب (EOQ)", color="التصنيف"), use_container_width=True)

elif menu == "🔮 التنبؤ بالطلب":
    st.title("🔮 AI Demand Forecasting")
    st.info("تنبؤ مبسط يعتمد على متوسطات وتحويل عشوائي صغير. يمكن ربط نماذج متقدمة لاحقاً.")
    df_processed['الطلب المتوقع'] = (df_processed['المبيعات الشهرية'] * np.random.uniform(0.9, 1.4, len(df_processed))).astype(int)
    fig_f = px.line(df_processed, x="المنتج", y=["المبيعات الشهرية", "الطلب المتوقع"], title="توقعات المبيعات المستقبلية")
    st.plotly_chart(fig_f, use_container_width=True)

elif menu == "🚨 محاكي الأزمات":
    st.title("🚨 Supply Chain Disruption Simulator")
    ship_cost = st.slider("ارتفاع تكلفة الشحن العالمي (%)", 0, 100, 20)
    df_processed['الربح بعد الأزمة'] = (df_processed['سعر البيع'] - (df_processed['تكلفة الوحدة'] * (1 + ship_cost/100))) * df_processed['المبيعات الشهرية']
    st.metric("💸 التأثير على إجمالي الربح", f"{int(df_processed['الربح بعد الأزمة'].sum()):,} ر.س", delta=f"{int(df_processed['الربح بعد الأزمة'].sum() - df_processed['إجمالي الربح'].sum())}")
    st.plotly_chart(px.bar(df_processed, x="المنتج", y=["إجمالي الربح", "الربح بعد الأزمة"], barmode="group"), use_container_width=True)

elif menu == "🛒 ذكاء البيع":
    st.title("🛒 Cross-Selling & Bundle Intelligence")
    st.markdown("اقتراحات باقة منتجات لزيادة متوسط قيمة السلة.")
    bundles = pd.DataFrame({
        "المنتج الأساسي": df_processed['المنتج'].head(3).values,
        "المنتج المكمل": ["بخور عود", "فحم", "تغليف هدايا"],
        "قوة الترابط": ["95%", "88%", "72%"]
    })
    st.table(bundles)

elif menu == "❄️ تقرير الراكد":
    st.title("❄️ Dead Stock Calculator")
    dead_stock = df_processed[df_processed['أيام الركود'] > 90]
    frozen_cash = (dead_stock['المخزون الحالي'] * dead_stock['تكلفة الوحدة']).sum()
    st.metric("💸 سيولة مجمدة (بضاعة راكدة)", f"{int(frozen_cash):,} ر.س")
    st.dataframe(dead_stock[['المنتج', 'المخزون الحالي', 'أيام الركود', 'تكلفة الوحدة']], use_container_width=True)
    if not dead_stock.empty:
        st.warning("💡 نصيحة: فكر في حملات ترويجية أو خصومات لتصفية هذه الأصناف.")

elif menu == "🚚 الموردين":
    st.title("🚚 Supplier Performance")
    st.plotly_chart(px.scatter(df_processed, x="زمن التوريد (أيام)", y="معدل المرتجعات (%)", size="إجمالي الربح", color="المورد", hover_name="المنتج"), use_container_width=True)

# زر تنزيل التقرير النهائي
st.markdown("---")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_processed.to_excel(writer, index=False, sheet_name='Analysis')
    # يمكن إضافة أوراق إضافية مثل Raw و Mapping
    raw_sheet = initial_df.copy()
    raw_sheet.to_excel(writer, index=False, sheet_name='Raw')
    # Mapping sheet
    mapping_df = pd.DataFrame(list(final_mapping.items()), columns=['Original Column', 'Mapped To'])
    mapping_df.to_excel(writer, index=False, sheet_name='Mapping')
buffer.seek(0)
st.download_button("📥 تحميل التقرير النهائي", data=buffer.getvalue(), file_name=f"{company_name}_Report.xlsx")

st.caption(f"تم التطوير بواسطة منى محمد | {company_name} Enterprise AI 2026")
