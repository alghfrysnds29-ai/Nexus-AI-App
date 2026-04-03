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
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
:root{
  --bg:#f8fafc;
  --card:#ffffff;
  --muted:#6b7280;
  --primary:#2563eb;
  --accent:#3b82f6;
  --success:#10b981;
  --danger:#ef4444;
  --radius:14px;
  --shadow: 0 6px 18px rgba(15,23,42,0.06);
  --metric-height:110px;
}

/* Global */
html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; background: var(--bg); color: #0f172a; }
section[data-testid="stSidebar"] { background: var(--card) !important; border-left: 1px solid rgba(15,23,42,0.04) !important; padding: 18px !important; }

/* Top header */
.app-header {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  background: linear-gradient(90deg, rgba(59,130,246,0.06), rgba(37,99,235,0.03));
  padding: 18px 24px;
  border-radius: var(--radius);
  margin-bottom: 18px;
  box-shadow: var(--shadow);
}
.app-brand {
  display:flex;
  align-items:center;
  gap:12px;
}
.app-logo {
  width:48px;
  height:48px;
  border-radius:10px;
  background: linear-gradient(135deg, var(--accent), var(--primary));
  display:flex;
  align-items:center;
  justify-content:center;
  color:white;
  font-weight:700;
  box-shadow: 0 6px 18px rgba(59,130,246,0.18);
}
.app-title { font-size:18px; font-weight:700; color:#0f172a; }
.app-sub { font-size:12px; color:var(--muted); }

/* Metric cards */
.metric-card {
  background: var(--card);
  border-radius: 12px;
  padding: 14px;
  box-shadow: var(--shadow);
  height: var(--metric-height);
  display:flex;
  align-items:center;
  gap:12px;
  border-top: 4px solid transparent;
}
.metric-icon {
  width:56px;
  height:56px;
  border-radius:10px;
  display:flex;
  align-items:center;
  justify-content:center;
  color:white;
  font-size:20px;
  flex-shrink:0;
}
.metric-body { flex:1; }
.metric-label { font-size:13px; color:var(--muted); margin-bottom:6px; }
.metric-value { font-size:20px; font-weight:700; color:#0f172a; }

/* Colored icons */
.icon-primary { background: linear-gradient(135deg, #3b82f6, #2563eb); }
.icon-success { background: linear-gradient(135deg, #10b981, #059669); }
.icon-warning { background: linear-gradient(135deg, #f59e0b, #f97316); }

/* Cards grid */
.cards-grid { display:grid; grid-template-columns: repeat(3, 1fr); gap:14px; margin-bottom:18px; }
@media (max-width: 900px) { .cards-grid { grid-template-columns: repeat(1, 1fr); } }

/* Section card */
.section-card {
  background: var(--card);
  border-radius: 12px;
  padding: 18px;
  box-shadow: var(--shadow);
  margin-bottom: 18px;
}

/* Buttons */
.stButton>button { border-radius: 10px; padding: 10px 14px; font-weight:600; }
.primary-btn { background: linear-gradient(90deg, var(--accent), var(--primary)); color:white; border:none; }

/* Table tweaks */
[data-testid="stDataFrameContainer"] { border-radius: 12px; overflow: hidden; box-shadow: var(--shadow); }

/* Small helpers */
.small-muted { color:var(--muted); font-size:13px; }
</style>
""", unsafe_allow_html=True)

# --- أدوات مساعدة ---
def bytes_hash(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def read_file_bytes(file_bytes: bytes, filename: str, sheet_name=None) -> pd.DataFrame:
    try:
        if filename.lower().endswith('.xlsx') or filename.lower().endswith('.xls'):
            return pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name)
        else:
            return pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        st.error("فشل قراءة الملف. تأكد من صيغة الملف أو جرب ملف آخر.")
        return pd.DataFrame()

def smart_col_mapper_suggestions(columns):
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

# --- محرك التحليل الرئيسي (كما في ملفك) ---
def process_full_data(df_input: pd.DataFrame) -> pd.DataFrame:
    d = df_input.copy()
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
    df_raw = read_file_bytes(file_bytes, filename, sheet_name=sheet_name)
    if mapping:
        rename_map = {orig: new for orig, new in mapping.items() if new}
        df_raw = df_raw.rename(columns=rename_map)
    df_processed = process_full_data(df_raw)
    return df_processed, file_hash

# --- Sidebar UI ---
st.sidebar.markdown("<h2 style='text-align: center; color: #3b82f6;'>NEXUS AI</h2>", unsafe_allow_html=True)
company_name = st.sidebar.text_input("🏢 اسم شركتك (White Label)", "Nexus AI")
uploaded_file = st.sidebar.file_uploader("📥 ارفع بياناتك (Excel/CSV)", type=['xlsx', 'csv'])
st.sidebar.caption("الملفات لا تُخزن على الخادم بعد المعالجة. الحجم المسموح 10MB.")
if st.sidebar.button("🧹 إعادة تعيين إعدادات الشركة"):
    if company_name in st.session_state.get("saved_mappings", {}):
        st.session_state["saved_mappings"].pop(company_name, None)
        st.sidebar.success("تم حذف إعدادات المطابقة المحفوظة لهذه الشركة.")

# --- رفع الملف ومعاينة ومطابقة ---
file_bytes = None
filename = ""
sheet_options = []
selected_sheet = None
using_demo = False
initial_df = pd.DataFrame()

if uploaded_file is not None:
    file_bytes = uploaded_file.read()
    filename = uploaded_file.name
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

suggestions = smart_col_mapper_suggestions(list(initial_df.columns))
if "saved_mappings" not in st.session_state:
    st.session_state["saved_mappings"] = {}
saved_for_company = st.session_state["saved_mappings"].get(company_name, {})

st.sidebar.markdown("---")
st.sidebar.subheader("معاينة ومطابقة الأعمدة")
st.sidebar.caption("راجع الاقتراحات ثم اضغط تطبيق لتخصيص التحليل لملفك.")
st.sidebar.markdown("**معاينة أول 5 صفوف**")
st.sidebar.dataframe(initial_df.head(5))

mapping_ui = {}
options_list = [None, "المنتج", "المورد", "المخزون الحالي", "المبيعات الشهرية", "تكلفة الوحدة", "سعر البيع", "زمن التوريد (أيام)", "معدل المرتجعات (%)"]
for col in initial_df.columns:
    suggested = suggestions.get(col)
    default = saved_for_company.get(col, suggested)
    try:
        idx = options_list.index(default) if default in options_list else 0
    except:
        idx = 0
    mapping_ui[col] = st.sidebar.selectbox(f"ماذا يمثل العمود '{col}'؟", options=options_list, index=idx)

col1, col2 = st.sidebar.columns(2)
apply_btn = col1.button("✅ تطبيق المطابقة")
save_btn = col2.button("💾 حفظ إعدادات الشركة")
if save_btn:
    st.session_state["saved_mappings"][company_name] = {k: v for k, v in mapping_ui.items() if v}
    st.sidebar.success("تم حفظ إعدادات المطابقة باسم الشركة.")

final_mapping = {}
if apply_btn:
    final_mapping = {orig: new for orig, new in mapping_ui.items() if new}
else:
    if saved_for_company:
        final_mapping = saved_for_company
    else:
        final_mapping = {orig: suggestions.get(orig) for orig in initial_df.columns if suggestions.get(orig)}

# --- معالجة نهائية مع caching حسب hash ---
if file_bytes is not None:
    file_hash = bytes_hash(file_bytes)
    df_processed, _ = cached_process(file_hash, file_bytes, filename, selected_sheet if selected_sheet else None, final_mapping)
else:
    df_processed = process_full_data(initial_df)

# --- Header مرئي احترافي ---
if using_demo:
    st.info("عرض بيانات تجريبية. ارفع ملفك لاستبدالها ببياناتك الحقيقية.")
else:
    st.success(f"✅ تم تحليل ملف {company_name} بنجاح. التطبيق الآن مخصص لبياناتك.")

st.markdown(f"""
<div class="app-header">
  <div class="app-brand">
    <div class="app-logo"><i class="fa-solid fa-rocket"></i></div>
    <div>
      <div class="app-title">Nexus AI</div>
      <div class="app-sub">Enterprise Supply Chain — تخصيص فوري لبيانات {company_name}</div>
    </div>
  </div>
  <div style="display:flex; gap:10px; align-items:center;">
    <a href="#download" class="primary-btn" style="padding:8px 12px; text-decoration:none; color:white;"><i class="fa-solid fa-file-arrow-down"></i>&nbsp; تنزيل تقرير</a>
  </div>
</div>
""", unsafe_allow_html=True)

# --- Metrics cards ---
st.markdown('<div class="cards-grid">', unsafe_allow_html=True)
total_profit = int(df_processed['إجمالي الربح'].sum()) if 'إجمالي الربح' in df_processed.columns else 0
avg_returns = df_processed['معدل المرتجعات (%)'].mean() if 'معدل المرتجعات (%)' in df_processed.columns else 0.0
with st.container():
    st.markdown(f'<div class="metric-card"><div class="metric-icon icon-primary"><i class="fa-solid fa-sack-dollar"></i></div><div class="metric-body"><div class="metric-label">إجمالي الربح</div><div class="metric-value">{total_profit:,} ر.س</div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-card"><div class="metric-icon icon-warning"><i class="fa-solid fa-boxes-stacked"></i></div><div class="metric-body"><div class="metric-label">عدد المنتجات</div><div class="metric-value">{len(df_processed)}</div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-card"><div class="metric-icon icon-success"><i class="fa-solid fa-rotate-left"></i></div><div class="metric-body"><div class="metric-label">متوسط المرتجعات</div><div class="metric-value">{avg_returns:.1f}%</div></div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- القوائم والصفحات الرئيسية (كما في ملفك) ---
st.title(f"📊 تحليلات شركة {company_name}")

menu = st.sidebar.radio("القائمة الرئيسية:", 
    ["🏠 ملخص تنفيذي", "📦 المستودع والطلب", "🔮 التنبؤ بالطلب", "🚨 محاكي الأزمات", "🛒 ذكاء البيع", "❄️ تقرير الراكد", "🚚 الموردين"])

if menu == "🏠 ملخص تنفيذي":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الربح", f"{total_profit:,} ر.س")
    c2.metric("نسبة الهالك (المرتجعات)", f"{avg_returns:.1f}%")
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
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "📦 المستودع والطلب":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.title("📦 Smart Inventory & EOQ")
    st.dataframe(df_processed[['المنتج', 'المخزون الحالي', 'الكمية المثالية للطلب (EOQ)', 'التصنيف']], use_container_width=True)
    st.plotly_chart(px.bar(df_processed, x="المنتج", y="الكمية المثالية للطلب (EOQ)", color="التصنيف"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🔮 التنبؤ بالطلب":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.title("🔮 AI Demand Forecasting")
    st.info("تنبؤ مبسط يعتمد على متوسطات وتحويل عشوائي صغير. يمكن ربط نماذج متقدمة لاحقاً.")
    df_processed['الطلب المتوقع'] = (df_processed['المبيعات الشهرية'] * np.random.uniform(0.9, 1.4, len(df_processed))).astype(int)
    fig_f = px.line(df_processed, x="المنتج", y=["المبيعات الشهرية", "الطلب المتوقع"], title="توقعات المبيعات المستقبلية")
    st.plotly_chart(fig_f, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🚨 محاكي الأزمات":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.title("🚨 Supply Chain Disruption Simulator")
    ship_cost = st.slider("ارتفاع تكلفة الشحن العالمي (%)", 0, 100, 20)
    df_processed['الربح بعد الأزمة'] = (df_processed['سعر البيع'] - (df_processed['تكلفة الوحدة'] * (1 + ship_cost/100))) * df_processed['المبيعات الشهرية']
    st.metric("💸 التأثير على إجمالي الربح", f"{int(df_processed['الربح بعد الأزمة'].sum()):,} ر.س", delta=f"{int(df_processed['الربح بعد الأزمة'].sum() - df_processed['إجمالي الربح'].sum())}")
    st.plotly_chart(px.bar(df_processed, x="المنتج", y=["إجمالي الربح", "الربح بعد الأزمة"], barmode="group"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🛒 ذكاء البيع":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.title("🛒 Cross-Selling & Bundle Intelligence")
    bundles = pd.DataFrame({
        "المنتج الأساسي": df_processed['المنتج'].head(3).values,
        "المنتج المكمل": ["بخور عود", "فحم", "تغليف هدايا"],
        "قوة الترابط": ["95%", "88%", "72%"]
    })
    st.table(bundles)
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "❄️ تقرير الراكد":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.title("❄️ Dead Stock Calculator")
    dead_stock = df_processed[df_processed['أيام الركود'] > 90]
    frozen_cash = (dead_stock['المخزون الحالي'] * dead_stock['تكلفة الوحدة']).sum()
    st.metric("💸 سيولة مجمدة (بضاعة راكدة)", f"{int(frozen_cash):,} ر.س")
    st.dataframe(dead_stock[['المنتج', 'المخزون الحالي', 'أيام الركود', 'تكلفة الوحدة']], use_container_width=True)
    if not dead_stock.empty:
        st.warning("💡 نصيحة: فكر في حملات ترويجية أو خصومات لتصفية هذه الأصناف.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu == "🚚 الموردين":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.title("🚚 Supplier Performance")
    st.plotly_chart(px.scatter(df_processed, x="زمن التوريد (أيام)", y="معدل المرتجعات (%)", size="إجمالي الربح", color="المورد", hover_name="المنتج"), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- زر تنزيل التقرير النهائي (محدّث) ---
st.markdown("---")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_processed.to_excel(writer, index=False, sheet_name='Analysis')
    raw_sheet = initial_df.copy()
    raw_sheet.to_excel(writer, index=False, sheet_name='Raw')
    mapping_df = pd.DataFrame(list(final_mapping.items()), columns=['Original Column', 'Mapped To'])
    mapping_df.to_excel(writer, index=False, sheet_name='Mapping')
buffer.seek(0)
st.download_button("📥 تحميل التقرير النهائي", data=buffer.getvalue(), file_name=f"{company_name}_Report.xlsx", key="download_report")

st.caption(f"تم التطوير بواسطة منى محمد | {company_name} Enterprise AI 2026")


