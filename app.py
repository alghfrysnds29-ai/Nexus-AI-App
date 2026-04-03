import streamlit as st
import pandas as pd

# --- 1. إعدادات الهوية البصرية (Nexus Digital Branding) ---
st.set_page_config(page_title="Nexus Digital | AI Supply Chain", layout="wide", initial_sidebar_state="expanded")

# تصميم واجهة احترافية باستخدام CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    .main { background-color: #f4f7f9; }
    .stButton>button { 
        width: 100%; border-radius: 12px; height: 3.5em; 
        background: linear-gradient(90deg, #007bff, #0056b3);
        color: white; font-weight: bold; border: none; box-shadow: 0 4px 15px rgba(0,123,255,0.3);
        transition: 0.3s; cursor: pointer;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,123,255,0.4); }
    .report-card { 
        background: white; padding: 25px; border-radius: 15px; 
        border-right: 8px solid #007bff; box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-top: 20px; direction: rtl;
    }
    .status-badge { padding: 5px 12px; border-radius: 20px; font-size: 0.8em; font-weight: bold; }
    </style>
    """, unsafe_allow_config=True)

# --- 2. محرك البيانات (Data Engine) ---
inventory_data = [
    {"المنتج": "MacBook Pro M3 14", "المخزون": 12, "المبيعات اليومية": 1.5, "التكلفة ($)": 1800, "السعر ($)": 2199, "الحالة": "مستقر"},
    {"المنتج": "iPhone 15 Pro Max", "المخزون": 8, "المبيعات اليومية": 4.2, "التكلفة ($)": 950, "السعر ($)": 1199, "الحالة": "خطر النفاذ"},
    {"المنتج": "Sony WH-1000XM5", "المخزون": 45, "المبيعات اليومية": 3.0, "التكلفة ($)": 280, "السعر ($)": 349, "الحالة": "مستقر"},
    {"المنتج": "Smart Watch Series 9", "المخزون": 150, "المبيعات اليومية": 1.2, "التكلفة ($)": 310, "السعر ($)": 399, "الحالة": "فائض كبير"},
    {"المنتج": "Gaming Chair Stealth", "المخزون": 5, "المبيعات اليومية": 0.8, "التكلفة ($)": 150, "السعر ($)": 299, "الحالة": "تأخر توريد"},
    {"المنتج": "USB-C Hub 7-in-1", "المخزون": 200, "المبيعات اليومية": 15.0, "التكلفة ($)": 10, "السعر ($)": 45, "الحالة": "حركة سريعة"}
]
df = pd.DataFrame(inventory_data)

# --- 3. بناء الواجهة (The Interface) ---
st.title("🛡️ Nexus Digital Store")
st.markdown("### نظام OptiChain AI لإدارة سلاسل الإمداد والتسويق")
st.info("مرحباً منى! النظام جاهز لتحليل بيانات المتجر وتقديم توصيات ذكية.")

# عرض الجدول بشكل احترافي
st.subheader("📊 نظرة عامة على المخزون الحالي")
st.dataframe(df, use_container_width=True)

st.markdown("---")
st.header("🤖 لوحة تحكم القرارات الذكية")
st.write("اضغطي على الخدمة المطلوبة للحصول على تقرير فوري:")

# توزيع الميزات الخمس على أزرار
col1, col2, col3, col4, col5 = st.columns(5)

report_title = ""
report_content = ""

with col1:
    if st.button("🚨 أمان الإعلانات"):
        report_title = "فحص توافق التسويق"
        report_content = "⚠️ **تحذير:** يجب إيقاف حملات 'iPhone 15' فوراً. المخزون الحالي (8 قطع) سينفد خلال 48 ساعة. توفير ميزانية الإعلانات وتوجيهها لمنتج 'USB-C Hub' الذي يمتلك فائضاً وحركة سريعة."

with col2:
    if st.button("🛡️ درع الأرباح"):
        report_title = "تحليل حماية الهوامش"
        report_content = "💰 **تحليل الربحية:** منتج 'Gaming Chair' يمتلك هامش ربح ممتاز، ولكن تكاليف التخزين الطويلة بدأت تأكل الربح. يُنصح بعمل خصم 5% لسرعة التدوير بدلاً من دفع تكاليف أرضية إضافية."

with col3:
    if st.button("📉 مخاطر الموردين"):
        report_title = "تقييم سلاسل الإمداد"
        report_content = "🚚 **تنبيه لوجستي:** مورد Apple Direct يعاني من تأخير. نوصي بتحويل طلبات 'الآيفون' القادمة لمورد محلي (حتى لو بسعر أعلى 5%) لضمان عدم انقطاع البيع في المواسم."

with col4:
    if st.button("🔥 محاكي الأزمات"):
        report_title = "اختبار تحمل (Stress Test)"
        report_content = "📈 **سيناريو نمو 40%:** في حال زيادة الطلب، سيعاني المتجر من فجوة سيولة بقيمة 12,000$. نوصي بتأمين خط ائتمان أو تقليل مشتريات المنتجات 'الفائضة' لتوفير الكاش."

with col5:
    if st.button("💰 تصفية الراكد"):
        report_title = "ذكاء التخلص من الفائض"
        report_content = "📦 **خطة التصفية:** الـ 'Smart Watch' لديها مبيعات منخفضة (1.2 قطعة/يوم). نقترح استراتيجية 'Bundle': (اشترِ ساعة واحصل على USB-C Hub بخصم 50%) لتفريغ المستودع فوراً."

# --- 4. منطقة عرض التقارير ---
if report_title:
    st.markdown(f"""
    <div class="report-card">
        <h2 style="color: #007bff;">📋 تقرير {report_title}</h2>
        <hr>
        <p style="font-size: 1.1em; line-height: 1.8;">{report_content}</p>
        <br>
        <small>تم التوليد بواسطة وحدة OptiChain الذكية لـ Nexus Digital</small>
    </div>
    """, unsafe_allow_config=True)
    st.balloons()
