import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime as dt
import requests

# =========================
# إعدادات عامة + ثيم خليجي
# =========================
st.set_page_config(
    page_title="لوحة تحكم المتجر الخليجي",
    page_icon="🕌",
    layout="wide"
)

# ثيم Sand & Emerald عبر CSS
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f4e9d8 0%, #fdfaf5 40%, #f4e9d8 100%);
        color: #0f172a;
        font-family: "Cairo", sans-serif;
    }
    .css-1d391kg, .css-18e3th9, .css-1lcbmhc {
        background-color: transparent !important;
    }
    .stSidebar {
        background: linear-gradient(180deg, #0f766e 0%, #115e59 60%, #022c22 100%) !important;
        color: #ecfdf5 !important;
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar p, .stSidebar span, .stSidebar label {
        color: #ecfdf5 !important;
    }
    .stMetric {
        background-color: #ecfdf5 !important;
        border-radius: 12px;
        padding: 10px;
        border: 1px solid #a7f3d0;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    .kpi-title {
        font-weight: 700;
        color: #065f46;
    }
    .section-title {
        font-weight: 700;
        color: #064e3b;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# دوال توليد بيانات وهمية
# =========================
@st.cache_data
def generate_store_data():
    np.random.seed(42)
    dates = pd.date_range(end=dt.date.today(), periods=180)

    products = ["منتج A", "منتج B", "منتج C", "منتج D", "منتج E", "منتج F"]
    categories = ["إلكترونيات", "ملابس", "أدوات منزلية", "عطور", "مستلزمات شخصية"]

    gulf_cities = [
        "الرياض", "جدة", "الدمام",
        "دبي", "أبوظبي", "الشارقة",
        "الدوحة", "الكويت", "المنامة", "مسقط"
    ]

    customer_ids = [f"CUST-{i:04d}" for i in range(1, 801)]
    data = []

    for d in dates:
        for _ in range(np.random.randint(60, 160)):
            product = np.random.choice(products)
            category = np.random.choice(categories)
            city = np.random.choice(gulf_cities)
            customer_id = np.random.choice(customer_ids)

            price = np.random.randint(30, 700)
            quantity = np.random.randint(1, 6)
            cost = price * np.random.uniform(0.45, 0.75)

            data.append({
                "date": d,
                "product": product,
                "category": category,
                "city": city,
                "customer_id": customer_id,
                "price": price,
                "quantity": quantity,
                "revenue": price * quantity,
                "cost": cost * quantity,
            })

    df = pd.DataFrame(data)
    df["profit"] = df["revenue"] - df["cost"]
    return df


@st.cache_data
def generate_supply_chain_data():
    products = ["منتج A", "منتج B", "منتج C", "منتج D", "منتج E", "منتج F"]
    suppliers = ["مورد سعودي", "مورد إماراتي", "مورد قطري", "مورد كويتي", "مورد بحريني", "مورد عماني"]

    df = pd.DataFrame({
        "product": products,
        "supplier": np.random.choice(suppliers, size=len(products)),
        "lead_time_days": np.random.randint(3, 20, size=len(products)),
        "stock_level": np.random.randint(20, 500, size=len(products)),
        "reorder_point": np.random.randint(50, 220, size=len(products)),
    })

    df["risk_flag"] = np.where(df["stock_level"] < df["reorder_point"], "⚠️ خطر نفاد", "✔️ آمن")
    return df


@st.cache_data
def generate_suppliers_data():
    suppliers = ["مورد سعودي", "مورد إماراتي", "مورد قطري", "مورد كويتي", "مورد بحريني", "مورد عماني"]
    categories = ["إلكترونيات", "ملابس", "أدوات منزلية", "عطور"]

    df = pd.DataFrame({
        "supplier": suppliers,
        "category": np.random.choice(categories, size=len(suppliers)),
        "rating": np.round(np.random.uniform(2.5, 5.0, size=len(suppliers)), 2),
        "contracts_value": np.random.randint(20000, 150000, size=len(suppliers)),
        "active": np.random.choice([True, False], size=len(suppliers), p=[0.85, 0.15])
    })
    return df


@st.cache_data
def get_city_geo():
    data = {
        "city": ["الرياض", "جدة", "الدمام", "دبي", "أبوظبي", "الشارقة", "الدوحة", "الكويت", "المنامة", "مسقط"],
        "lat": [24.7136, 21.4858, 26.4207, 25.2048, 24.4539, 25.3463, 25.2854, 29.3759, 26.2235, 23.5880],
        "lon": [46.6753, 39.1925, 50.0888, 55.2708, 54.3773, 55.4209, 51.5310, 47.9774, 50.5876, 58.3829],
    }
    return pd.DataFrame(data)


# =========================
# تحميل البيانات
# =========================
store_df = generate_store_data()
supply_df = generate_supply_chain_data()
suppliers_df = generate_suppliers_data()
geo_df = get_city_geo()

# =========================
# الشريط الجانبي (مرتب حسب الأولوية)
# =========================
with st.sidebar:
    st.title("🕌 لوحة تحكم الخليج")

    page = st.radio(
        "اختر الصفحة:",
        (
            "📌 لوحة التحكم الرئيسية",
            "💰 التحليل المالي",
            "👥 تحليلات العملاء",
            "📈 التوقعات المستقبلية",
            "📍 التحليل الجغرافي",
            "🚚 سلاسل الإمداد",
            "🤝 الموردون والشركاء",
            "⭐ ملخص مؤشرات الأداء KPI",
            "🧠 تحليلات الذكاء الاصطناعي",
            "🔗 الربط مع API",
        )
    )

    st.markdown("---")
    st.caption("لوحة تحكم احترافية لمتاجر الخليج الإلكترونية")


# =========================
# 1) لوحة التحكم الرئيسية
# =========================
if page == "📌 لوحة التحكم الرئيسية":
    st.markdown("<h2 class='section-title'>📌 لوحة التحكم الرئيسية</h2>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        date_from = st.date_input("من تاريخ", store_df["date"].min().date())
    with col2:
        date_to = st.date_input("إلى تاريخ", store_df["date"].max().date())
    with col3:
        city_filter = st.multiselect(
            "اختر المدن",
            options=store_df["city"].unique().tolist(),
            default=store_df["city"].unique().tolist()
        )

    mask = (
        (store_df["date"] >= pd.to_datetime(date_from)) &
        (store_df["date"] <= pd.to_datetime(date_to)) &
        (store_df["city"].isin(city_filter))
    )
    filtered = store_df[mask]

    total_revenue = filtered["revenue"].sum()
    total_orders = len(filtered)
    top_city = filtered.groupby("city")["revenue"].sum().idxmax()
    top_product = filtered.groupby("product")["revenue"].sum().idxmax()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي المبيعات", f"{total_revenue:,.0f} ريال")
    c2.metric("عدد الطلبات", f"{total_orders:,}")
    c3.metric("أفضل مدينة مبيعًا", top_city)
    c4.metric("أكثر منتج مبيعًا", top_product)

    st.markdown("---")

    st.markdown("<p class='kpi-title'>المبيعات اليومية</p>", unsafe_allow_html=True)
    daily = filtered.groupby("date")["revenue"].sum().reset_index()
    fig_daily = px.line(
        daily,
        x="date",
        y="revenue",
        labels={"date": "التاريخ", "revenue": "المبيعات"},
        template="plotly_white",
    )
    fig_daily.update_traces(line_color="#0f766e")
    st.plotly_chart(fig_daily, use_container_width=True)

    st.markdown("<p class='kpi-title'>المنتجات الأكثر مبيعًا</p>", unsafe_allow_html=True)
    prod_rev = filtered.groupby("product")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
    fig_prod = px.bar(
        prod_rev,
        x="product",
        y="revenue",
        labels={"product": "المنتج", "revenue": "المبيعات"},
        template="plotly_white",
        color_discrete_sequence=["#0f766e"],
    )
    st.plotly_chart(fig_prod, use_container_width=True)


# =========================
# 2) التحليل المالي
# =========================
elif page == "💰 التحليل المالي":
    st.markdown("<h2 class='section-title'>💰 التحليل المالي</h2>", unsafe_allow_html=True)

    financial = store_df.groupby("date")[["revenue", "cost", "profit"]].sum().reset_index()

    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي الإيرادات", f"{financial['revenue'].sum():,.0f} ريال")
    col2.metric("إجمالي التكاليف", f"{financial['cost'].sum():,.0f} ريال")
    col3.metric("إجمالي الأرباح", f"{financial['profit'].sum():,.0f} ريال")

    st.markdown("---")

    st.markdown("<p class='kpi-title'>الإيرادات مقابل التكاليف</p>", unsafe_allow_html=True)
    fig_rev_cost = px.line(
        financial,
        x="date",
        y=["revenue", "cost"],
        labels={"value": "القيمة", "date": "التاريخ", "variable": "البند"},
        template="plotly_white",
    )
    fig_rev_cost.update_traces(line_width=3)
    st.plotly_chart(fig_rev_cost, use_container_width=True)

    st.markdown("<p class='kpi-title'>الأرباح اليومية</p>", unsafe_allow_html=True)
    fig_profit = px.area(
        financial,
        x="date",
        y="profit",
        labels={"date": "التاريخ", "profit": "الأرباح"},
        template="plotly_white",
    )
    fig_profit.update_traces(line_color="#0f766e", fillcolor="rgba(15,118,110,0.25)")
    st.plotly_chart(fig_profit, use_container_width=True)


# =========================
# 3) تحليلات العملاء
# =========================
elif page == "👥 تحليلات العملاء":
    st.markdown("<h2 class='section-title'>👥 تحليلات العملاء</h2>", unsafe_allow_html=True)

    cust = store_df.groupby("customer_id").agg(
        total_revenue=("revenue", "sum"),
        orders=("customer_id", "count"),
        first_purchase=("date", "min"),
        last_purchase=("date", "max"),
    ).reset_index()

    cust["days_since_last"] = (store_df["date"].max() - cust["last_purchase"]).dt.days

    st.markdown("<p class='kpi-title'>ملخص العملاء (أعلى 50 عميلًا)</p>", unsafe_allow_html=True)
    st.dataframe(cust.sort_values("total_revenue", ascending=False).head(50))

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p class='kpi-title'>توزيع قيمة العميل (CLV تقريبي)</p>", unsafe_allow_html=True)
        fig_clv = px.histogram(
            cust,
            x="total_revenue",
            nbins=30,
            labels={"total_revenue": "إجمالي إنفاق العميل"},
            template="plotly_white",
            color_discrete_sequence=["#0f766e"],
        )
        st.plotly_chart(fig_clv, use_container_width=True)

    with col2:
        st.markdown("<p class='kpi-title'>توزيع عدد الطلبات لكل عميل</p>", unsafe_allow_html=True)
        fig_orders = px.histogram(
            cust,
            x="orders",
            nbins=20,
            labels={"orders": "عدد الطلبات"},
            template="plotly_white",
            color_discrete_sequence=["#0f766e"],
        )
        st.plotly_chart(fig_orders, use_container_width=True)

    st.markdown("---")
    st.markdown("<p class='kpi-title'>شرائح العملاء حسب القيمة</p>", unsafe_allow_html=True)
    q_low = cust["total_revenue"].quantile(0.33)
    q_high = cust["total_revenue"].quantile(0.66)

    def segment(row):
        if row["total_revenue"] <= q_low:
            return "قيمة منخفضة"
        elif row["total_revenue"] <= q_high:
            return "قيمة متوسطة"
        else:
            return "قيمة عالية"

    cust["segment"] = cust.apply(segment, axis=1)
    seg_counts = cust["segment"].value_counts().reset_index()
    seg_counts.columns = ["segment", "count"]

    fig_seg = px.pie(
        seg_counts,
        names="segment",
        values="count",
        hole=0.4,
        template="plotly_white",
        color_discrete_sequence=["#a7f3d0", "#34d399", "#0f766e"],
    )
    st.plotly_chart(fig_seg, use_container_width=True)


# =========================
# 4) التوقعات المستقبلية
# =========================
elif page == "📈 التوقعات المستقبلية":
    st.markdown("<h2 class='section-title'>📈 التوقعات المستقبلية للمبيعات</h2>", unsafe_allow_html=True)

    daily = store_df.groupby("date")["revenue"].sum().reset_index()
    daily = daily.sort_values("date")
    daily["revenue_ma7"] = daily["revenue"].rolling(window=7).mean()

    last_date = daily["date"].max()
    future_days = 30
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=future_days)

    last_ma = daily["revenue_ma7"].dropna().iloc[-1]
    forecast_values = np.full(shape=future_days, fill_value=last_ma)
    forecast_df = pd.DataFrame({"date": future_dates, "forecast_revenue": forecast_values})

    fig_forecast = px.line(
        daily,
        x="date",
        y="revenue",
        labels={"date": "التاريخ", "revenue": "المبيعات"},
        template="plotly_white",
    )
    fig_forecast.update_traces(line_color="#0f766e", name="المبيعات الفعلية")

    fig_forecast.add_scatter(
        x=forecast_df["date"],
        y=forecast_df["forecast_revenue"],
        mode="lines",
        name="توقع المبيعات (تقريبي)",
        line=dict(color="#f97316", dash="dash"),
    )

    st.plotly_chart(fig_forecast, use_container_width=True)
    st.info("هذا نموذج توقع بسيط يعتمد على المتوسط المتحرك 7 أيام، ويمكن استبداله لاحقًا بنموذج ML حقيقي.")


# =========================
# 5) التحليل الجغرافي
# =========================
elif page == "📍 التحليل الجغرافي":
    st.markdown("<h2 class='section-title'>📍 التحليل الجغرافي للمبيعات</h2>", unsafe_allow_html=True)

    city_rev = store_df.groupby("city")["revenue"].sum().reset_index()
    city_rev = city_rev.merge(geo_df, on="city", how="left")

    st.markdown("<p class='kpi-title'>المبيعات حسب المدينة</p>", unsafe_allow_html=True)
    fig_city = px.bar(
        city_rev,
        x="city",
        y="revenue",
        labels={"city": "المدينة", "revenue": "المبيعات"},
        template="plotly_white",
        color_discrete_sequence=["#0f766e"],
    )
    st.plotly_chart(fig_city, use_container_width=True)

    st.markdown("<p class='kpi-title'>خريطة تقريبية لتوزيع المبيعات</p>", unsafe_allow_html=True)
    fig_geo = px.scatter_geo(
        city_rev,
        lat="lat",
        lon="lon",
        size="revenue",
        hover_name="city",
        projection="natural earth",
        template="plotly_white",
    )
    st.plotly_chart(fig_geo, use_container_width=True)


# =========================
# 6) سلاسل الإمداد
# =========================
elif page == "🚚 سلاسل الإمداد":
    st.markdown("<h2 class='section-title'>🚚 سلاسل الإمداد</h2>", unsafe_allow_html=True)

    st.markdown("<p class='kpi-title'>حالة المخزون</p>", unsafe_allow_html=True)
    st.dataframe(supply_df)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p class='kpi-title'>مستويات المخزون مقابل نقطة إعادة الطلب</p>", unsafe_allow_html=True)
        fig_stock = px.bar(
            supply_df,
            x="product",
            y=["stock_level", "reorder_point"],
            barmode="group",
            labels={"value": "الكمية", "product": "المنتج", "variable": "البند"},
            template="plotly_white",
        )
        st.plotly_chart(fig_stock, use_container_width=True)

    with col2:
        st.markdown("<p class='kpi-title'>أوقات التوريد حسب المورد</p>", unsafe_allow_html=True)
        fig_lead = px.bar(
            supply_df,
            x="product",
            y="lead_time_days",
            color="supplier",
            labels={"product": "المنتج", "lead_time_days": "أيام التوريد", "supplier": "المورد"},
            template="plotly_white",
        )
        st.plotly_chart(fig_lead, use_container_width=True)

    st.markdown("---")
    st.markdown("<p class='kpi-title'>تحليل المخاطر</p>", unsafe_allow_html=True)
    risk_counts = supply_df["risk_flag"].value_counts().reset_index()
    risk_counts.columns = ["status", "count"]
    fig_risk = px.pie(
        risk_counts,
        names="status",
        values="count",
        hole=0.4,
        template="plotly_white",
        color_discrete_sequence=["#f97316", "#22c55e"],
    )
    st.plotly_chart(fig_risk, use_container_width=True)


# =========================
# 7) الموردون والشركاء
# =========================
elif page == "🤝 الموردون والشركاء":
    st.markdown("<h2 class='section-title'>🤝 الموردون والشركاء</h2>", unsafe_allow_html=True)

    st.markdown("<p class='kpi-title'>قائمة الموردين</p>", unsafe_allow_html=True)
    st.dataframe(suppliers_df)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p class='kpi-title'>تقييم الموردين</p>", unsafe_allow_html=True)
        fig_rating = px.bar(
            suppliers_df,
            x="supplier",
            y="rating",
            color="category",
            range_y=[0, 5],
            labels={"supplier": "المورد", "rating": "التقييم", "category": "الفئة"},
            template="plotly_white",
        )
        st.plotly_chart(fig_rating, use_container_width=True)

    with col2:
        st.markdown("<p class='kpi-title'>قيمة العقود</p>", unsafe_allow_html=True)
        fig_contracts = px.bar(
            suppliers_df,
            x="supplier",
            y="contracts_value",
            labels={"supplier": "المورد", "contracts_value": "قيمة العقود"},
            template="plotly_white",
            color_discrete_sequence=["#0f766e"],
        )
        st.plotly_chart(fig_contracts, use_container_width=True)

    st.markdown("---")
    st.markdown("<p class='kpi-title'>فلترة الموردين</p>", unsafe_allow_html=True)
    min_rating = st.slider("أقل تقييم مقبول", 0.0, 5.0, 3.0, 0.1)
    active_only = st.checkbox("عرض الموردين النشطين فقط", value=True)

    filt = suppliers_df[suppliers_df["rating"] >= min_rating]
    if active_only:
        filt = filt[filt["active"]]

    st.write("الموردون المطابقون للمعايير:")
    st.dataframe(filt)


# =========================
# 8) ملخص مؤشرات الأداء KPI
# =========================
elif page == "⭐ ملخص مؤشرات الأداء KPI":
    st.markdown("<h2 class='section-title'>⭐ ملخص مؤشرات الأداء الرئيسية</h2>", unsafe_allow_html=True)

    today = store_df["date"].max()
    last_30 = store_df[store_df["date"] >= today - pd.Timedelta(days=30)]
    prev_30 = store_df[
        (store_df["date"] < today - pd.Timedelta(days=30)) &
        (store_df["date"] >= today - pd.Timedelta(days=60))
    ]

    def kpi_block(df):
        revenue = df["revenue"].sum()
        profit = df["profit"].sum()
        orders = len(df)
        return revenue, profit, orders

    rev_last, prof_last, ord_last = kpi_block(last_30)
    rev_prev, prof_prev, ord_prev = kpi_block(prev_30)

    col1, col2, col3 = st.columns(3)
    col1.metric("إيرادات آخر 30 يوم", f"{rev_last:,.0f} ريال", f"{rev_last - rev_prev:,.0f}")
    col2.metric("أرباح آخر 30 يوم", f"{prof_last:,.0f} ريال", f"{prof_last - prof_prev:,.0f}")
    col3.metric("عدد الطلبات (آخر 30 يوم)", f"{ord_last:,}", f"{ord_last - ord_prev:,}")

    st.markdown("---")
    st.markdown("<p class='kpi-title'>مقارنة شهرية مبسطة</p>", unsafe_allow_html=True)
    monthly = store_df.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
    monthly_kpi = monthly.groupby("month")[["revenue", "profit"]].sum().reset_index()

    fig_month = px.bar(
        monthly_kpi,
        x="month",
        y=["revenue", "profit"],
        barmode="group",
        labels={"month": "الشهر", "value": "القيمة", "variable": "البند"},
        template="plotly_white",
    )
    st.plotly_chart(fig_month, use_container_width=True)


# =========================
# 9) تحليلات الذكاء الاصطناعي (Insights)
# =========================
elif page == "🧠 تحليلات الذكاء الاصطناعي":
    st.markdown("<h2 class='section-title'>🧠 تحليلات ذكية (قواعد تحاكي AI)</h2>", unsafe_allow_html=True)

    prod_perf = store_df.groupby("product")["revenue"].sum().reset_index()
    best_product = prod_perf.sort_values("revenue", ascending=False).iloc[0]
    worst_product = prod_perf.sort_values("revenue", ascending=True).iloc[0]

    last_30 = store_df[store_df["date"] >= store_df["date"].max() - pd.Timedelta(days=30)]
    prev_30 = store_df[
        (store_df["date"] < store_df["date"].max() - pd.Timedelta(days=30)) &
        (store_df["date"] >= store_df["date"].max() - pd.Timedelta(days=60))
    ]

    city_last = last_30.groupby("city")["revenue"].sum()
    city_prev = prev_30.groupby("city")["revenue"].sum()
    growth = (city_last - city_prev).fillna(0)
    best_growth_city = growth.sort_values(ascending=False).index[0]

    st.markdown("### 🔍 رؤى مقترحة:")
    st.write(f"- **المنتج الأقوى أداءً:** {best_product['product']} بإجمالي مبيعات يقارب {best_product['revenue']:,.0f} ريال.")
    st.write(f"- **المنتج الأضعف أداءً:** {worst_product['product']}، يُنصح بمراجعته (سعر/تسويق/إلغاء).")
    st.write(f"- **أعلى مدينة نموًا في المبيعات خلال آخر 30 يومًا:** {best_growth_city}.")
    st.write("- **توصية:** ركّز الحملات التسويقية على المدن ذات النمو العالي، وأعد تقييم المنتجات ذات الأداء الضعيف.")


# =========================
# 10) الربط مع API
# =========================
elif page == "🔗 الربط مع API":
    st.markdown("<h2 class='section-title'>🔗 الربط مع API</h2>", unsafe_allow_html=True)

    st.write("مثال بسيط على جلب بيانات من API عام (JSONPlaceholder).")

    col1, col2 = st.columns(2)
    with col1:
        st.code(
            """
import requests

url = "https://jsonplaceholder.typicode.com/posts"
response = requests.get(url)
data = response.json()
            """,
            language="python",
        )

    with col2:
        try:
            url = "https://jsonplaceholder.typicode.com/posts"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()[:10]
                st.success("تم جلب البيانات بنجاح من الـ API 👌")
                st.dataframe(pd.DataFrame(data))
            else:
                st.error(f"فشل في الاتصال بالـ API. كود الاستجابة: {response.status_code}")
        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بالـ API: {e}")
