import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from streamlit_lottie import st_lottie
import requests

# --- 1. إعدادات الصفحة والهوية البصرية ---
st.set_page_config(page_title="Nexus SCM Pro | Global Edition", page_icon="🌐", layout="wide")

# دالة لتحميل رسوم Lottie
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_ai = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_gssu2dkm.json") # AI animation
lottie_success = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_pqnfmone.json") # Success check

# حقن الـ CSS المطور
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl; text-align: right;
        background-color: #f0f2f6;
    }

    /* تصميم البطاقات العالمية */
    .metric-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #2563eb;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }

    /* تحسين الهيدر */
    .stHeader { background: rgba(255,255,255,0); }
    
    /* تخصيص التنبيهات */
    .ai-insight-box {
        background: linear-gradient(90deg, #ffffff 0%, #f1f5f9 100%);
        border-right: 5px solid #8b5cf6;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. محركات البيانات ---
@st.cache_data
def get_data():
    df_exec = pd.DataFrame({
        'الشهر': ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"],
        'الإيرادات': [250000, 280000, 240000, 310000, 295000, 340000],
        'المصاريف': [180000, 190000, 175000, 210000, 205000, 220000]
    })
    
    df_inv = pd.DataFrame({
        'المنتج': [f'منتج {i}' for i in range(1, 11)],
        'الفئة': np.random.choice(['A', 'B', 'C'], 10),
        'المخزون': np.random.randint(2, 100, 10),
        'السعر': np.random.randint(50, 500, 10),
        'الحالة': 'مستقر'
    })
    # تحديد المنتجات الحرجة
    df_inv.loc[df_inv['المخزون'] < 10, 'الحالة'] = 'حرِج'
    
    return df_exec, df_inv

df_exec, df_inv = get_data()

# --- 3. شريط التنقل العلوي (Navigation) ---
selected = option_menu(
    menu_title=None,
    options=["الرئيسية", "المخزون الذكي", "التقارير", "الإعدادات"],
    icons=["house", "box-seam", "graph-up", "gear"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#ffffff", "border-radius": "0px"},
        "icon": {"color": "#2563eb", "font-size": "18px"}, 
        "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#2563eb"},
    }
)

# --- 4. محتوى الصفحات ---

if selected == "الرئيسية":
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grid Layout: نظام الأعمدة المتقدم للبطاقات
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card">
            <p style='color:#64748b; font-size:14px; margin-bottom:5px;'>إجمالي المبيعات</p>
            <h2 style='margin:0; color:#1e293b;'>340,000 ر.س</h2>
            <span style='color:#10b981; font-size:12px;'>▲ +12% من الشهر الماضي</span>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card" style='border-left-color: #f59e0b;'>
            <p style='color:#64748b; font-size:14px; margin-bottom:5px;'>قيمة المخزون</p>
            <h2 style='margin:0; color:#1e293b;'>1.2M ر.س</h2>
            <span style='color:#ef4444; font-size:12px;'>▼ -4.2% تنظيف مخزون</span>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card" style='border-left-color: #10b981;'>
            <p style='color:#64748b; font-size:14px; margin-bottom:5px;'>طلبات قيد التنفيذ</p>
            <h2 style='margin:0; color:#1e293b;'>85 طلب</h2>
            <span style='color:#10b981; font-size:12px;'>📦 جاهز للشحن</span>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card" style='border-left-color: #8b5cf6;'>
            <p style='color:#64748b; font-size:14px; margin-bottom:5px;'>دقة التنبؤ</p>
            <h2 style='margin:0; color:#1e293b;'>94%</h2>
            <span style='color:#2563eb; font-size:12px;'>مدعوم بـ Nexus AI</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # القسم السفلي: الرسم البياني وتنبيهات AI
    c1, c2 = st.columns([7, 3])
    
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_exec['الشهر'], y=df_exec['الإيرادات'], name='المبيعات', fill='tozeroy', line_color='#2563eb'))
        fig.update_layout(title="الأداء المالي السنوي", template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.markdown("<div class='ai-insight-box'>", unsafe_allow_html=True)
        st_lottie(lottie_ai, height=100, key="ai_icon")
        st.subheader("رؤى الذكاء الاصطناعي")
        st.info("هناك فرصة لزيادة المبيعات بنسبة 10% إذا تم توفير منتج 'أ' بكميات أكبر.")
        st.markdown("</div>", unsafe_allow_html=True)

elif selected == "المخزون الذكي":
    st.subheader("📦 إدارة المخزون المتقدمة")
    
    # استخدام AgGrid بدلاً من جداول ستريم ليت العادية
    gb = GridOptionsBuilder.from_dataframe(df_inv)
    gb.configure_pagination(paginationAutoPageSize=True) # تفعيل الترقيم
    gb.configure_side_bar() # تفعيل الفلاتر الجانبية
    gb.configure_selection('multiple', use_checkbox=True)
    
    # تلوين الخلايا (تنبيه المخزون المنخفض)
    cellsytle_jscode = """
    function(params) {
        if (params.value < 10) {
            return { 'color': 'white', 'backgroundColor': '#ef4444' };
        }
    }
    """
    gb.configure_column("المخزون", cellStyle=cellsytle_jscode)
    grid_options = gb.build()
    
    AgGrid(
        df_inv, 
        gridOptions=grid_options,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
        theme='balham', # ثيم احترافي
    )
    
    if st.button("تحديث المخزون"):
        with st.spinner("جاري المزامنة..."):
            st_lottie(lottie_success, height=150)
            st.success("تم تحديث البيانات بنجاح!")

# --- التذييل (Footer) ---
st.markdown("---")
st.caption(f"Nexus SCM Pro v3.0 | 2026 Edition | تم التصميم بواسطة منى محمد")
