# --- 1. إعدادات الهوية البصرية (اللون الفاتح الملكي) ---

st.set_page_config(page_title="Nexus SCM Pro | Store Edition", page_icon="📈", layout="wide")



st.markdown("""

    <style>

    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&display=swap');

    

    :root {

        --primary: #2563eb;

        --bg: #f8fafc;

        --text: #1e293b;

        --card-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);

    }

    

    html, body, [class*="css"] {

        font-family: 'IBM Plex Sans Arabic', sans-serif;

        direction: rtl; text-align: right;

        background-color: var(--bg);

        color: var(--text);

    }



    /* تصميم البطاقات المطور */

    .exec-card {

        background: white;

        border: 1px solid #e2e8f0;

        border-radius: 15px;

        padding: 20px;

        box-shadow: var(--card-shadow);

        transition: 0.3s;

    }

    .exec-card:hover {

        transform: translateY(-5px);

        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);

        border-color: var(--primary);

    }



    /* بنر الذكاء الاصطناعي */

    .ai-box {

        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);

        border-right: 5px solid var(--primary);

        padding: 20px;

        border-radius: 12px;

        margin-bottom: 25px;

        color: #1e3a8a;

    }



    /* التبويبات */

    .stTabs [data-baseweb="tab-list"] { gap: 10px; }

    .stTabs [data-baseweb="tab"] {

        background: white;

        border-radius: 10px 10px 0 0;

        border: 1px solid #e2e8f0;

        padding: 10px 30px;

    }

    .stTabs [aria-selected="true"] {

        background: var(--primary) !important;

        color: white !important;

    }



    /* إخفاء شعارات ستريم ليت الافتراضية */

    #MainMenu, footer, header {visibility: hidden;}

    </style>

    """, unsafe_allow_html=True)



# --- 2. محركات البيانات (Data Engines) ---

@st.cache_data

def load_all_data():

    # بيانات الإيرادات والمصاريف

    df_exec = pd.DataFrame({

        'الشهر': ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو"],

        'الإيرادات': [250000, 280000, 240000, 310000, 295000, 340000],

        'المصاريف': [180000, 190000, 175000, 210000, 205000, 220000]

    })

    

    # بيانات التنبؤ بالطلب (30 يوم قادم)

    dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]

    df_fore = pd.DataFrame({

        'التاريخ': dates, 

        'الطلب': [100 + (i*1.2) + np.random.randint(-10,10) for i in range(30)],

        'المخزون_المتوقع': [500 - (i*10) for i in range(30)]

    })

    

    # بيانات الموردين

    df_sup = pd.DataFrame({

        'المورد': ['مورد التقنية', 'مصنع الخليج', 'توريد آسيا'],

        'الجودة': [95, 80, 88],

        'زمن_الشحن': [5, 12, 7],

        'الالتزام': [98, 75, 90]

    })

    

    # بيانات المخزون التفصيلي (ABC)

    df_inv = pd.DataFrame({

        'المنتج': [f'منتج {i}' for i in range(1, 21)],

        'المبيعات': np.random.randint(1000, 50000, 20),

        'المخزون': np.random.randint(5, 100, 20)

    }).sort_values('المبيعات', ascending=False)

    

    return df_exec, df_fore, df_sup, df_inv



df_exec, df_fore, df_sup, df_inv = load_all_data()



# --- 3. الهيكل الرئيسي (Sidebar) ---

with st.sidebar:

    st.image("https://cdn-icons-png.flaticon.com/512/5968/5968204.png", width=50) 

    st.title("Nexus Store Pro")

    st.markdown("---")

    st.write("👤 **المدير:** منى محمد")

    st.success("🟢 حالة المتجر: متصل")

    st.markdown("---")

    st.write("🛠️ **إجراءات سريعة:**")

    if st.button("➕ إضافة طلب شراء"): st.toast("تم فتح نافذة المشتريات")

    if st.button("📄 تصدير تقرير اليوم"): st.balloons()

    st.markdown("---")

    st.button("🔴 تسجيل الخروج")



# --- 4. واجهة المستخدم (Main UI) ---

st.markdown("<h1 style='font-weight:800; color:#1e293b;'>🚀 لوحة تحكم متجري المتكاملة</h1>", unsafe_allow_html=True)



# بنر الذكاء الاصطناعي (AI Insight Box)

st.markdown("""

    <div class="ai-box">

        <h4 style="margin:0 0 10px 0;">🤖 رؤى Nexus AI لليوم:</h4>

        <p style="margin:0;">تحليل المبيعات يشير لارتفاع الطلب بنسبة <b>15%</b> الأسبوع القادم. 

        يُنصح بزيادة مخزون <b>"منتج 1"</b> و <b>"منتج 3"</b> لتفادي أي عجز محتمل.</p>

    </div>

""", unsafe_allow_html=True)



# التبويبات (Tabs)

tab1, tab2, tab3, tab4, tab5 = st.tabs([

    "🏢 برج المراقبة", "🔮 التنبؤ الذكي", "📦 إدارة المخزون", "🚚 الموردين", "🔄 المرتجعات"

])



# --- القسم 1: برج المراقبة ---

with tab1:

    m1, m2, m3 = st.columns(3)

    with m1:

        st.markdown('<div class="exec-card">', unsafe_allow_html=True)

        st.metric("إجمالي السيولة", "340,000 ر.س", "12%")

        st.markdown('</div>', unsafe_allow_html=True)

    with m2:

        st.markdown('<div class="exec-card">', unsafe_allow_html=True)

        st.metric("رأس مال المخزون", "1.2M ر.س", "-4%")

        st.markdown('</div>', unsafe_allow_html=True)

    with m3:

        st.markdown('<div class="exec-card">', unsafe_allow_html=True)

        st.metric("دقة التوصيل", "96.5%", "1.2%")

        st.markdown('</div>', unsafe_allow_html=True)

    

    st.markdown("<br>", unsafe_allow_html=True)

    fig_exec = go.Figure()

    fig_exec.add_trace(go.Scatter(x=df_exec['الشهر'], y=df_exec['الإيرادات'], name='الإيرادات', line=dict(color='#2563eb', width=4), fill='tozeroy'))

    fig_exec.add_trace(go.Scatter(x=df_exec['الشهر'], y=df_exec['المصاريف'], name='المصاريف', line=dict(color='#ef4444', width=2)))

    fig_exec.update_layout(title="تحليل التدفق النقدي (الستة أشهر الماضية)", plot_bgcolor='white')

    st.plotly_chart(fig_exec, use_container_width=True)



# --- القسم 2: التنبؤ الذكي ---

with tab2:

    st.subheader("🔮 توقعات الطلب لـ 30 يوماً القادمة")

    c_f1, c_f2 = st.columns([7, 3])

    

    with c_f1:

        fig_f = px.line(df_fore, x='التاريخ', y='الطلب', markers=True, title="منحنى الطلب المتوقع")

        fig_f.update_traces(line_color='#2563eb')

        st.plotly_chart(fig_f, use_container_width=True)

    

    with c_f2:

        st.markdown("""<div class='exec-card' style='border-right: 5px solid #f59e0b;'>

            <h4>⚠️ تنبيه نفاذ مخزون</h4>

            <p>منتج <b>SKU-55</b> مرشح للنفاذ بتاريخ <b>12 إبريل</b>.</p>

            <button style='width:100%; padding:10px; background:#2563eb; color:white; border:none; border-radius:5px;'>طلب بضاعة الآن</button>

        </div>""", unsafe_allow_html=True)



# --- القسم 3: إدارة المخزون (ABC Analysis) ---

with tab3:

    st.subheader("📦 تحليل ABC وتصنيف المنتجات")

    col_abc1, col_abc2 = st.columns(2)

    

    with col_abc1:

        # حساب ABC وهمي سريع

        df_inv['النسبة'] = (df_inv['المبيعات'] / df_inv['المبيعات'].sum()) * 100

        fig_pie = px.pie(names=['الفئة A (حيوي)', 'الفئة B (متوسط)', 'الفئة C (ثانوي)'], values=[70, 20, 10], 

                         hole=0.5, title="توزيع قيمة المخزون", color_discrete_sequence=['#1e40af', '#3b82f6', '#94a3b8'])

        st.plotly_chart(fig_pie, use_container_width=True)

        

    with col_abc2:

        st.write("🔍 **أكثر المنتجات ربحية (Top Tier):**")

        st.dataframe(df_inv[['المنتج', 'المبيعات', 'المخزون']].head(5), use_container_width=True)



# --- القسم 4: الموردين والشحن ---

with tab4:

    st.subheader("🚚 تقييم الموردين واللوجستيات")

    st.table(df_sup)

    

    fig_sup = px.scatter(df_sup, x='زمن_الشحن', y='الجودة', size='الالتزام', color='المورد', 

                         title="مصفوفة أداء الموردين", text='المورد')

    fig_sup.update_layout(plot_bgcolor='white')

    st.plotly_chart(fig_sup, use_container_width=True)



# --- القسم 5: المرتجعات والتقارير ---

with tab5:

    st.subheader("🔄 إدارة المرتجعات والهدر المالي")

    col_r1, col_r2 = st.columns(2)

    

    with col_r1:

        st.bar_chart({'عيب مصنعي': 20, 'مقاس خاطئ': 50, 'تأخر شحن': 15, 'لم يعجب العميل': 10})

        

    with col_r2:

        st.markdown("""<div class='exec-card'>

            <h4>📑 مركز التقارير الجاهزة</h4>

            <p>يمكنك تحميل ملخص العمليات الشهري بصيغة PDF.</p>

            <hr>

            <p>✅ تقرير المخزون جاهز</p>

            <p>✅ تقرير الموردين جاهز</p>

        </div>""", unsafe_allow_html=True)

        st.button("📥 تحميل التقرير النهائي (Full Report)")



# --- التذييل ---

st.markdown("---")

st.caption(f"Nexus BI Solution v3.0 | جميع الحقوق محفوظة لـ {STORE_NAME if 'STORE_NAME' in locals() else 'متجري'} 2026")
