import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="Nexus SCM | Executive Dashboard", page_icon="📈", layout="wide")

# --- 2. التصميم الفاتح المودرن (CSS Custom Design) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-main: #f8fafc;
        --card-bg: #ffffff;
        --primary-blue: #2563eb;
        --text-main: #1e293b;
        --text-sub: #64748b;
        --border-color: #e2e8f0;
    }
    
    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans Arabic', sans-serif;
        direction: rtl; text-align: right;
        background-color: var(--bg-main);
        color: var(--text-main);
    }

    /* تصميم البطاقات الاحترافي */
    .st-emotion-cache-12w0qpk { background-color: var(--bg-main); } /* سحب خلفية ستريم ليت */

    .executive-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease-in-out;
    }
    .executive-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: var(--primary-blue);
    }

    .kpi-label { font-size: 0.9rem; color: var(--text-sub); font-weight: 500; margin-bottom: 5px; }
    .kpi-value { font-size: 1.8rem; font-weight: 700; color: var(--text-main); }
    .trend-badge {
        font-size: 0.8rem; padding: 4px 10px; border-radius: 50px; font-weight: 600;
    }
    .up { background: #dcfce7; color: #166534; }
    .down { background: #fee2e2; color: #991b1b; }

    /* صندوق رؤى الذكاء الاصطناعي الفاتح */
    .ai-banner {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-right: 5px solid var(--primary-blue);
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 25px;
        color: #1e3a8a;
    }

    /* تعديل التبويبات */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border: 1px solid var(--border-color);
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: var(--text-sub);
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-blue) !important;
        color: white !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. محرك البيانات ---
@st.cache_data
def get_data():
    months = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"]
    return pd.DataFrame({
        'الشهر': months,
        'الإيرادات': [250000, 280000, 240000, 310000, 295000, 340000],
        'المصاريف': [180000, 190000, 175000, 210000, 205000, 220000],
        'الكفاءة': [92, 94, 91, 95, 93, 97]
    })

df = get_data()

# --- 4. العرض (UI Layout) ---

# الهيدر
st.markdown("<h1 style='color: #1e293b; font-weight: 800;'>📊 ملخص العمليات التنفيذي</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #64748b; margin-top:-15px;'>Nexus SCM v3.0 | نظام إدارة سلسلة الإمداد المتكامل</p>", unsafe_allow_html=True)

# بنر الذكاء الاصطناعي
st.markdown("""
    <div class="ai-banner">
        <h4 style="margin:0 0 10px 0;">🤖 تحليل Nexus AI اليومي:</h4>
        <p style="margin:0; font-size:1rem;">
            أداء الموردين مستقر بنسبة <b>97%</b>. يوجد فرصة لتحسين التدفق النقدي عبر تقليل مخزون 
            الأزياء الصيفية بنسبة <b>10%</b> قبل نهاية الشهر الحالي.
        </p>
    </div>
""", unsafe_allow_html=True)

# صف الـ KPIs
k1, k2, k3, k4 = st.columns(4)

def kpi_box(col, label, value, trend, is_up):
    t_class = "up" if is_up else "down"
    t_icon = "↑" if is_up else "↓"
    col.markdown(f"""
        <div class="executive-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div style="margin-top:10px;">
                <span class="trend-badge {t_class}">{t_icon} {trend}</span>
                <span style="color:#94a3b8; font-size:0.8rem; margin-right:5px;">عن الشهر الماضي</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

kpi_box(k1, "إجمالي الإيرادات", "340,000 ر.س", "12.5%", True)
kpi_box(k2, "رأس المال المخزني", "1.2M ر.س", "3.2%", False)
kpi_box(k3, "دقة التنبؤ بالطلب", "94.8%", "1.2%", True)
kpi_box(k4, "صافي الربح التشغيلي", "120,000 ر.س", "8.4%", True)

st.markdown("<br>", unsafe_allow_html=True)

# الرسوم البيانية (Charts)
c1, c2 = st.columns([6, 4])

with c1:
    st.markdown("<h4 style='padding-right:10px;'>📈 اتجاهات النمو والسيولة</h4>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['الشهر'], y=df['الإيرادات'], name='الإيرادات', marker_color='#3b82f6', borderround=5))
    fig.add_trace(go.Scatter(x=df['الشهر'], y=df['المصاريف'], name='تكاليف العمليات', line=dict(color='#ef4444', width=3)))
    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("<h4 style='padding-right:10px;'>🎯 كفاءة التوصيل (Fulfillment)</h4>", unsafe_allow_html=True)
    fig_radial = px.line(df, x='الشهر', y='الكفاءة', markers=True, text='الكفاءة')
    fig_radial.update_traces(line_color='#2563eb', fill='tozeroy')
    fig_radial.update_layout(plot_bgcolor='white', yaxis=dict(range=[80, 100]))
    st.plotly_chart(fig_radial, use_container_width=True)

# تذييل بسيط
st.markdown("---")
st.caption("مركز التحكم في سلسلة الإمداد - جميع البيانات مُحدثة بتاريخ اليوم")
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. محرك التنبؤ التخيلي (AI Forecasting Engine) ---
@st.cache_data
def get_forecast_data():
    # إنشاء بيانات لـ 30 يوم قادم
    last_date = datetime.now()
    dates = [(last_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
    
    # محاكاة تنبؤ ذكي (اتجاه صاعد مع بعض العشوائية)
    forecast_sales = [100 + (i * 1.5) + np.random.randint(-10, 10) for i in range(30)]
    actual_stock = [500 - (sum(forecast_sales[:i]) * 0.8) for i in range(30)]
    
    return pd.DataFrame({
        'التاريخ': dates,
        'الطلب_المتوقع': forecast_sales,
        'المخزون_الاحتياطي': actual_stock
    })

df_forecast = get_forecast_data()

# --- 2. واجهة المستخدم للقسم الثاني ---
st.markdown("---")
st.markdown("<h2 style='color: #1e293b;'>🔮 مركز التنبؤ الذكي (AI Forecasting)</h2>", unsafe_allow_html=True)
st.caption("تحليل الأنماط الموسمية وتوقعات الطلب لـ 30 يوماً القادمة")

# صف التنبيهات الذكية (Smart Insights)
col_ai1, col_ai2 = st.columns(2)

with col_ai1:
    st.markdown(f"""
        <div style="background-color: #fff7ed; border-right: 5px solid #f97316; padding: 20px; border-radius: 10px;">
            <h4 style="color: #9a3412; margin:0;">⚠️ تنبيه نفاذ مخزون وشيك</h4>
            <p style="color: #c2410c; margin: 10px 0 0 0;">
                بناءً على معدل الطلب المتزايد، المنتج <b>"ساعة Ultra"</b> سينفد خلال <b>8 أيام</b>. 
                نقترح عمل أمر شراء بـ 200 قطعة الآن لتجنب خسارة مبيعات بقيمة 15,400 ر.س.
            </p>
        </div>
    """, unsafe_allow_html=True)

with col_ai2:
    st.markdown("""
        <div style="background-color: #f0fdf4; border-right: 5px solid #22c55e; padding: 20px; border-radius: 10px;">
            <h4 style="color: #166534; margin:0;">✅ فرصة تحسين الطلب</h4>
            <p style="color: #15803d; margin: 10px 0 0 0;">
                نتوقع زيادة في الطلب بنسبة <b>22%</b> على قسم "العطور" خلال عطلة نهاية الأسبوع القادمة. 
                تم تجهيز خطة التوزيع اللوجستي لتغطية هذه الزيادة تلقائياً.
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# الرسم البياني للتنبؤ
st.markdown("<div class='executive-card'>", unsafe_allow_html=True)
st.subheader("📈 محاكاة حركة الطلب vs المخزون المتاح")

fig_forecast = go.Figure()

# خط الطلب المتوقع
fig_forecast.add_trace(go.Scatter(
    x=df_forecast['التاريخ'], y=df_forecast['الطلب_المتوقع'],
    name='الطلب المتوقع (وحدة)',
    line=dict(color='#2563eb', width=4, dash='dot')
))

# خط المخزون المتاح
fig_forecast.add_trace(go.Scatter(
    x=df_forecast['التاريخ'], y=df_forecast['المخزون_الاحتياطي'],
    name='المخزون المتوفر',
    fill='tozeroy',
    line=dict(color='#94a3b8', width=1)
))

# إضافة خط "نقطة الخطر"
fig_forecast.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="نقطة إعادة الطلب الحرجة")

fig_forecast.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='rgba(0,0,0,0)',
    hovermode="x unified",
    margin=dict(l=20, r=20, t=30, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_forecast, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# جدول التوصيات الشرائية
st.markdown("<br>", unsafe_allow_html=True)
st.subheader("📋 أوامر الشراء المقترحة من النظام")

# بيانات وهمية للجدول
procurement_data = pd.DataFrame({
    "المنتج": ["ساعة Ultra", "عطر العود", "سماعة Pro", "حقيبة جيم"],
    "المورد": ["مورد الصين الأساسي", "شركة العود العالمية", "التقنية الحديثة", "مصنع الجلود"],
    "الكمية المقترحة": [250, 100, 150, 50],
    "التكلفة التقديرية": ["45,000 ر.س", "12,000 ر.س", "22,500 ر.س", "3,000 ر.س"],
    "الأولوية": ["🔴 عاجلة جداً", "🟠 متوسطة", "🟡 عادية", "🟢 منخفضة"]
})

st.table(procurement_data)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. محرك تصنيف المخزون المتقدم (ABC Logic) ---
@st.cache_data
def get_inventory_analysis():
    np.random.seed(42)
    n_products = 1000  # محاكاة لعدد كبير من المنتجات
    products = [f"منتج SKU-{i}" for i in range(1, n_products + 1)]
    categories = ['إلكترونيات', 'أزياء', 'منزل', 'عناية']
    
    data = pd.DataFrame({
        'المنتج': products,
        'الفئة': np.random.choice(categories, n_products),
        'المبيعات_السنوية': np.random.exponential(scale=100, size=n_products) * 100,
        'المخزون_الحالي': np.random.randint(0, 1000, n_products),
        'تكلفة_الوحدة': np.random.uniform(10, 500, n_products)
    })
    
    # حساب القيمة الإجمالية للمبيعات لكل منتج
    data['قيمة_المبيعات'] = data['المبيعات_السنوية'] * data['تكلفة_الوحدة']
    data = data.sort_values(by='قيمة_المبيعات', ascending=False)
    
    # تصنيف ABC بناءً على المساهمة في الإيرادات
    data['النسبة_التراكمية'] = 100 * data['قيمة_المبيعات'].cumsum() / data['قيمة_المبيعات'].sum()
    data['تصنيف_ABC'] = pd.cut(data['النسبة_التراكمية'], 
                               bins=[0, 70, 90, 100], 
                               labels=['💎 الفئة A (حيوي)', '⚡ الفئة B (متوسط)', '📦 الفئة C (ثانوي)'])
    
    return data

df_inv = get_inventory_analysis()

# --- 2. واجهة المستخدم للقسم الثالث ---
st.markdown("---")
st.markdown("<h2 style='color: #1e293b;'>📦 إدارة المخزون الاستراتيجية (ABC)</h2>", unsafe_allow_html=True)
st.caption("تحليل توزيع الاستثمار المخزني وتحديد الأولويات الشرائية")

# بطاقات ملخصة للقسم
i1, i2, i3 = st.columns(3)

with i1:
    st.markdown(f"""
        <div class="executive-card" style="border-right: 5px solid #1d4ed8;">
            <div style="color: #64748b;">قيمة المخزون في الفئة (A)</div>
            <div style="font-size: 1.5rem; font-weight: 700;">{df_inv[df_inv['تصنيف_ABC'].str.contains('A')]['قيمة_المبيعات'].sum():,.0f} ر.س</div>
            <p style="font-size: 0.8rem; color: #1e40af;">تمثل 70% من إجمالي مبيعاتك</p>
        </div>
    """, unsafe_allow_html=True)

with i2:
    st.markdown("""
        <div class="executive-card" style="border-right: 5px solid #f59e0b;">
            <div style="color: #64748b;">مخزون راكد (Dead Stock)</div>
            <div style="font-size: 1.5rem; font-weight: 700;">185 قطعة</div>
            <p style="font-size: 0.8rem; color: #b45309;">لم تتحرك منذ 90 يوماً</p>
        </div>
    """, unsafe_allow_html=True)

with i3:
    st.markdown("""
        <div class="executive-card" style="border-right: 5px solid #ef4444;">
            <div style="color: #64748b;">عجز متوقع (Out of Stock)</div>
            <div style="font-size: 1.5rem; font-weight: 700;">12 منتجاً</div>
            <p style="font-size: 0.8rem; color: #991b1b;">يجب إعادة الطلب خلال 48 ساعة</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# الرسوم البيانية للقسم الثالث
col_inv1, col_inv2 = st.columns([4, 6])

with col_inv1:
    # توزيع المنتجات في التصنيف
    fig_abc_pie = px.pie(df_inv, names='تصنيف_ABC', values='قيمة_المبيعات', 
                         title="تحليل باريتو (توزيع الربحية)",
                         color_discrete_map={'💎 الفئة A (حيوي)':'#1d4ed8', 
                                             '⚡ الفئة B (متوسط)':'#f59e0b', 
                                             '📦 الفئة C (ثانوي)':'#94a3b8'},
                         hole=0.4)
    fig_abc_pie.update_layout(showlegend=False)
    st.plotly_chart(fig_abc_pie, use_container_width=True)

with col_inv2:
    # مصفوفة المخزون vs المبيعات
    fig_matrix = px.scatter(df_inv.head(100), x="المبيعات_السنوية", y="المخزون_الحالي",
                            size="تكلفة_الوحدة", color="تصنيف_ABC",
                            hover_name="المنتج", title="مصفوفة كفاءة المخزون (أفضل 100 منتج)",
                            color_discrete_map={'💎 الفئة A (حيوي)':'#1d4ed8', 
                                             '⚡ الفئة B (متوسط)':'#f59e0b', 
                                             '📦 الفئة C (ثانوي)':'#94a3b8'})
    st.plotly_chart(fig_matrix, use_container_width=True)

# البحث الفلترة المتقدمة
st.subheader("🔍 استكشاف سجل المنتجات")
search_term = st.text_input("ابحث عن منتج بالاسم أو الـ SKU...")
filtered_df = df_inv[df_inv['المنتج'].str.contains(search_term, case=False)]

st.dataframe(filtered_df[['المنتج', 'الفئة', 'المخزون_الحالي', 'قيمة_المبيعات', 'تصنيف_ABC']].head(50), 
             use_container_width=True)
# --- 1. محرك بيانات الموردين واللوجستيات ---
@st.cache_data
def get_logistics_data():
    suppliers = ['مورد التقنية العالمي', 'مصنع الخليج العربي', 'شركة توريد آسيا', 'منسوجات أوروبا']
    data = pd.DataFrame({
        'المورد': suppliers,
        'جودة_المنتجات': [98, 85, 92, 89],
        'الالتزام_بالمواعيد': [95, 70, 88, 91],
        'متوسط_زمن_الشحن': [5, 14, 10, 7],
        'تكلفة_الشحن_المتوسطة': [45, 120, 85, 110]
    })
    return data

df_log = get_logistics_data()

# --- 2. واجهة المستخدم للجزء الرابع ---
with tab4:
    st.markdown("<h2 style='color: #1e293b;'>🚚 كفاءة الموردين والعمليات اللوجستية</h2>", unsafe_allow_html=True)
    st.caption("مراقبة أداء شركاء النجاح وتتبع سلاسل الإمداد الدولية")

    # صف الرسوم البيانية للموردين
    l_col1, l_col2 = st.columns([5, 5])

    with l_col1:
        st.markdown("#### 📊 مقارنة أداء الموردين (الجودة vs الوقت)")
        fig_sup = px.scatter(df_log, x="متوسط_زمن_الشحن", y="جودة_المنتجات",
                             size="الالتزام_بالمواعيد", color="المورد",
                             text="المورد", title="مصفوفة اختيار المورد الأفضل")
        fig_sup.update_layout(plot_bgcolor='white', showlegend=False)
        st.plotly_chart(fig_sup, use_container_width=True)

    with l_col2:
        st.markdown("#### 📉 الالتزام بمواعيد التسليم (%)")
        fig_time = px.bar(df_log, x='المورد', y='الالتزام_بالمواعيد', 
                          color='الالتزام_بالمواعيد', color_continuous_scale='RdYlGn')
        fig_time.update_layout(plot_bgcolor='white')
        st.plotly_chart(fig_time, use_container_width=True)

    # قسم تتبع الشحنات القادمة (Inbound Tracking)
    st.markdown("---")
    st.subheader("🚢 تتبع الشحنات الدولية القادمة")
    
    shipments = pd.DataFrame({
        "رقم الشحنة": ["SHP-9901", "SHP-8823", "SHP-7712"],
        "المورد": ["مورد التقنية", "مصنع الخليج", "شركة توريد آسيا"],
        "الحالة": ["🚢 في البحر", "🛃 في الجمارك", "🏭 قيد التصنيع"],
        "التوصيل المتوقع": ["5 إبريل", "2 إبريل", "15 إبريل"],
        "مستوى الخطورة": ["🟢 منخفض", "🟡 متوسط", "🔵 مستقر"]
    })
    
    st.table(shipments)

    # نصيحة لوجستية من AI
    st.info("💡 **نصيحة Nexus AI:** نلاحظ تأخراً متكرراً من 'مصنع الخليج' في الجمارك؛ نقترح تحديث أوراق التخليص مسبقاً أو تجربة الشحن الجوي لتفادي النقص في المخزون.")
    # --- 1. محرك بيانات المرتجعات (Reverse Logistics) ---
@st.cache_data
def get_returns_data():
    return pd.DataFrame({
        'السبب': ['عيب مصنعي', 'مقاس خاطئ', 'تأخر التوصيل', 'لم يعجب العميل', 'تلف في الشحن'],
        'النسبة': [15, 45, 10, 20, 10],
        'التكلفة_التقديرية': [5000, 12000, 2000, 8000, 3000]
    })

df_returns = get_returns_data()

# إضافة التبويب الخامس للأقسام السابقة
with st.sidebar:
    st.markdown("---")
    st.write("✅ **حالة النظام:** متصل بسلة / زد")
    st.write("📊 **آخر تحديث:** منذ دقيقتين")

# --- 2. واجهة المستخدم للجزء الخامس (تضاف داخل st.tabs) ---
# لنفترض أننا أضفنا tab5 في تعريف التبويبات سابقا
with tab5: 
    st.markdown("<h2 style='color: #1e293b;'>🔄 اللوجستيات العكسية وتحليل المرتجعات</h2>", unsafe_allow_html=True)
    st.caption("تحليل أسباب الاسترجاع وتقليل الهدر المالي")

    r_col1, r_col2 = st.columns([6, 4])

    with r_col1:
        st.markdown("#### 📉 أسباب المرتجعات (تأثيرها على الأرباح)")
        fig_returns = px.bar(df_returns, x='السبب', y='التكلفة_التقديرية', 
                             color='السبب', title="التكلفة المالية لكل سبب استرجاع",
                             color_discrete_sequence=px.colors.sequential.Reds_r)
        fig_returns.update_layout(plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_returns, use_container_width=True)

    with r_col2:
        st.markdown("#### 🎯 توزيع أسباب الاسترجاع (%)")
        fig_pie_ret = px.pie(df_returns, names='السبب', values='النسبة', 
                             hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie_ret, use_container_width=True)

    # قسم التقارير الجاهزة (Report Center)
    st.markdown("---")
    st.markdown("### 📄 مركز التقارير الذكية")
    
    rep_c1, rep_c2, rep_c3 = st.columns(3)
    
    with rep_c1:
        st.markdown("""
            <div style="border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; text-align: center;">
                <p style="margin:0; font-weight:600;">تقرير الأداء الشهري</p>
                <small style="color: #64748b;">PDF • 2.4 MB</small><br><br>
                <button style="background:#2563eb; color:white; border:none; padding:5px 15px; border-radius:5px;">تحميل</button>
            </div>
        """, unsafe_allow_html=True)

    with rep_c2:
        st.markdown("""
            <div style="border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; text-align: center;">
                <p style="margin:0; font-weight:600;">جرد المخزون السنوي</p>
                <small style="color: #64748b;">XLSX • 1.1 MB</small><br><br>
                <button style="background:#2563eb; color:white; border:none; padding:5px 15px; border-radius:5px;">تحميل</button>
            </div>
        """, unsafe_allow_html=True)

    with rep_c3:
        st.markdown("""
            <div style="border: 1px solid #e2e8f0; padding: 15px; border-radius: 10px; text-align: center;">
                <p style="margin:0; font-weight:600;">تحليل الموردين</p>
                <small style="color: #64748b;">CSV • 0.8 MB</small><br><br>
                <button style="background:#2563eb; color:white; border:none; padding:5px 15px; border-radius:5px;">تحميل</button>
            </div>
        """, unsafe_allow_html=True)

# --- تذييل الصفحة النهائي ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: #94a3b8; padding: 20px; border-top: 1px solid #e2e8f0;">
        Nexus SCM Pro Edition © 2026 | تطوير منى محمد - منصة ذكاء الأعمال المتكاملة
    </div>
""", unsafe_allow_html=True)
