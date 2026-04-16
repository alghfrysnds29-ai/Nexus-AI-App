import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime as dt
import requests

# =========================
# إعدادات عامة + ثيم iOS Light
# =========================
st.set_page_config(
    page_title="لوحة تحكم المتجر ",
    page_icon=None,
    layout="wide"
)

# =========================
# هوية بصرية احترافية (Brand Kit)
# =========================
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
    }

    .stApp {
        background-color: #f5f7fa !important;
        color: #111827 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e5e7eb !important;
    }

    h1, h2, h3 {
        color: #004aad !important;
        font-weight: 700 !important;
    }

    .stButton>button {
        background-color: #004aad !important;
        color: #fff !important;
        border-radius: 8px !important;
        padding: 0.6em 1.2em !important;
        font-weight: bold !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #00a86b !important;
        color: #fff !important;
    }

    .stMetric {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        padding: 12px !important;
        border: 1px solid #e5e7eb !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }

    .stDataFrame, .stTable {
        background-color: #ffffff !important;
        border-radius: 12px !important;
        padding: 8px !important;
        border: 1px solid #e5e7eb !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 999px !important;
        padding: 6px 14px !important;
        background-color: #f3f4f6 !important;
        color: #374151 !important;
        font-weight: 500 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #004aad !important;
        color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)

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

    df["risk_flag"] = np.where(df["stock_level"] < df["reorder_point"], "خطر نفاد", "آمن")
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
    df["score"] = (
        (df["rating"] / 5) * 0.6 +
        (df["contracts_value"] / df["contracts_value"].max()) * 0.4
    ) * 100
    df["score"] = df["score"].round(1)
    return df


@st.cache_data
def get_city_geo():
    data = {
        "city": ["الرياض", "جدة", "الدمام", "دبي", "أبوظبي", "الشارقة", "الدوحة", "الكويت", "المنامة", "مسقط"],
        "lat": [24.7136, 21.4858, 26.4207, 25.2048, 24.4539, 25.3463, 25.2854, 29.3759, 26.2235, 23.5880],
        "lon": [46.6753, 39.1925, 50.0888, 55.2708, 54.3773, 55.4209, 51.5310, 47.9774, 50.5876, 58.3829],
    }
    geo = pd.DataFrame(data)
    np.random.seed(10)
    geo["avg_shipping_cost"] = np.random.randint(15, 45, size=len(geo))
    geo["avg_delivery_days"] = np.random.uniform(1.5, 4.5, size=len(geo)).round(1)
    return geo


# =========================
# تحميل البيانات
# =========================
store_df = generate_store_data()
supply_df = generate_supply_chain_data()
suppliers_df = generate_suppliers_data()
geo_df = get_city_geo()

# =========================
# الشريط الجانبي
# =========================
with st.sidebar:
    st.title("لوحة تحكم المتجر الخليجي")

    page = st.radio(
        "اختر الصفحة:",
        (
            "لوحة التحكم الرئيسية",
            "التحليل المالي",
            "تحليلات العملاء",
            "التوقعات المستقبلية",
            "التحليل الجغرافي",
            "سلاسل الإمداد",
            "الموردون والشركاء",
            "ملخص مؤشرات الأداء",
            "تحليلات ذكية",
            "الربط مع API",
        )
    )

    st.markdown("---")
    st.caption("لوحة تحكم احترافية لمتاجر الخليج الإلكترونية")


# =========================
# 1) لوحة التحكم الرئيسية
# =========================
if page == "لوحة التحكم الرئيسية":
    st.markdown("<h2 class='section-title'>لوحة التحكم الرئيسية</h2>", unsafe_allow_html=True)

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
    total_customers = filtered["customer_id"].nunique()
    top_city = filtered.groupby("city")["revenue"].sum().idxmax()
    top_product = filtered.groupby("product")["revenue"].sum().idxmax()

    monthly = filtered.copy()
    monthly["month"] = monthly["date"].dt.to_period("M")
    monthly_kpi = monthly.groupby("month")["revenue"].sum().reset_index()
    monthly_kpi["month"] = monthly_kpi["month"].astype(str)
    if len(monthly_kpi) >= 2:
        last_rev = monthly_kpi["revenue"].iloc[-1]
        prev_rev = monthly_kpi["revenue"].iloc[-2]
        growth_month = ((last_rev - prev_rev) / prev_rev * 100) if prev_rev != 0 else 0
    else:
        growth_month = 0

    estimated_sessions = total_orders * 5
    conversion_rate = (total_orders / estimated_sessions * 100) if estimated_sessions > 0 else 0
    aov = (total_revenue / total_orders) if total_orders > 0 else 0
    marketing_spend = total_revenue * 0.1
    cac = (marketing_spend / total_customers) if total_customers > 0 else 0

    cust_orders = filtered.groupby("customer_id")["date"].count()
    returning_customers = (cust_orders > 1).sum()
    returning_rate = (returning_customers / total_customers * 100) if total_customers > 0 else 0

    top_low_stock = supply_df.sort_values("stock_level").head(5)

    ceo_mode = st.checkbox("تفعيل وضع المدير التنفيذي", value=False)

    if ceo_mode:
        today = store_df["date"].max()
        today_df = store_df[store_df["date"] == today]
        rev_today = today_df["revenue"].sum()
        ord_today = len(today_df)
        prof_today = today_df["profit"].sum()
        if len(today_df) > 0:
            best_city_today = today_df.groupby("city")["revenue"].sum().idxmax()
        else:
            best_city_today = "-"

        st.markdown("### مؤشرات سريعة للمدير التنفيذي")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("مبيعات اليوم", f"{rev_today:,.0f} ريال")
        c2.metric("طلبات اليوم", f"{ord_today:,}")
        c3.metric("أرباح اليوم", f"{prof_today:,.0f} ريال")
        c4.metric("أفضل مدينة اليوم", best_city_today)

        st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إجمالي المبيعات", f"{total_revenue:,.0f} ريال", f"{growth_month:.1f}% شهريًا")
    c2.metric("عدد الطلبات", f"{total_orders:,}")
    c3.metric("متوسط قيمة السلة", f"{aov:,.1f} ريال")
    c4.metric("معدل التحويل", f"{conversion_rate:.1f}%")

    c5, c6, c7 = st.columns(3)
    c5.metric("CAC تقديري", f"{cac:,.1f} ريال/عميل")
    c6.metric("نسبة العملاء العائدين", f"{returning_rate:.1f}%")
    c7.metric("أفضل مدينة مبيعًا", top_city)

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
    fig_daily.update_traces(line_color="#111827")
    st.plotly_chart(fig_daily, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<p class='kpi-title'>المنتجات الأكثر مبيعًا</p>", unsafe_allow_html=True)
        prod_rev = filtered.groupby("product")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
        fig_prod = px.bar(
            prod_rev,
            x="product",
            y="revenue",
            labels={"product": "المنتج", "revenue": "المبيعات"},
            template="plotly_white",
            color_discrete_sequence=["#111827"],
        )
        st.plotly_chart(fig_prod, use_container_width=True)

    with col_b:
        st.markdown("<p class='kpi-title'>أعلى 5 منتجات قريبة من النفاد</p>", unsafe_allow_html=True)
        st.dataframe(top_low_stock[["product", "stock_level", "reorder_point", "risk_flag"]])


# =========================
# 2) التحليل المالي
# =========================
elif page == "التحليل المالي":
    st.markdown("<h2 class='section-title'>التحليل المالي</h2>", unsafe_allow_html=True)

    financial = store_df.groupby("date")[["revenue", "cost", "profit"]].sum().reset_index()

    total_rev = financial["revenue"].sum()
    total_cost = financial["cost"].sum()
    total_profit = financial["profit"].sum()
    gross_margin = (total_profit / total_rev * 100) if total_rev > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("إجمالي الإيرادات", f"{total_rev:,.0f} ريال")
    col2.metric("إجمالي التكاليف", f"{total_cost:,.0f} ريال")
    col3.metric("إجمالي الأرباح", f"{total_profit:,.0f} ريال")
    col4.metric("هامش الربح الإجمالي", f"{gross_margin:.1f}%")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["إيرادات وتكاليف", "ربحية المدن", "ربحية الفئات", "محاكاة مالية"])

    with tab1:
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
        fig_profit.update_traces(line_color="#111827", fillcolor="rgba(17,24,39,0.15)")
        st.plotly_chart(fig_profit, use_container_width=True)

    with tab2:
        st.markdown("<p class='kpi-title'>تحليل الربحية حسب المدينة</p>", unsafe_allow_html=True)
        city_fin = store_df.groupby("city")[["revenue", "profit"]].sum().reset_index()
        fig_city_fin = px.bar(
            city_fin,
            x="city",
            y=["revenue", "profit"],
            barmode="group",
            template="plotly_white",
            labels={"city": "المدينة", "value": "القيمة", "variable": "البند"},
        )
        st.plotly_chart(fig_city_fin, use_container_width=True)

    with tab3:
        st.markdown("<p class='kpi-title'>تحليل الربحية حسب الفئة</p>", unsafe_allow_html=True)
        cat_fin = store_df.groupby("category")[["revenue", "profit"]].sum().reset_index()
        fig_cat_fin = px.bar(
            cat_fin,
            x="category",
            y=["revenue", "profit"],
            barmode="group",
            template="plotly_white",
            labels={"category": "الفئة", "value": "القيمة", "variable": "البند"},
        )
        st.plotly_chart(fig_cat_fin, use_container_width=True)

    with tab4:
        st.markdown("<p class='kpi-title'>محاكاة مالية (What‑If)</p>", unsafe_allow_html=True)
        products = store_df["product"].unique().tolist()
        selected_product = st.selectbox("اختر منتجًا", products)
        price_change = st.slider("نسبة تغيير السعر (%)", -30, 30, 10)

        prod_df = store_df[store_df["product"] == selected_product]
        base_rev = prod_df["revenue"].sum()
        base_profit = prod_df["profit"].sum()

        qty_factor = 1 - (price_change / 10) * 0.05
        qty_factor = max(qty_factor, 0.2)

        new_rev = base_rev * (1 + price_change / 100) * qty_factor
        new_profit = base_profit * (1 + price_change / 100) * qty_factor

        c1, c2 = st.columns(2)
        c1.metric("إيرادات المنتج الحالية", f"{base_rev:,.0f} ريال")
        c2.metric(
            "إيرادات المنتج بعد التعديل",
            f"{new_rev:,.0f} ريال",
            f"{(new_rev-base_rev)/base_rev*100 if base_rev>0 else 0:.1f}%"
        )

        c3, c4 = st.columns(2)
        c3.metric("أرباح المنتج الحالية", f"{base_profit:,.0f} ريال")
        c4.metric(
            "أرباح المنتج بعد التعديل",
            f"{new_profit:,.0f} ريال",
            f"{(new_profit-base_profit)/base_profit*100 if base_profit>0 else 0:.1f}%"
        )


# =========================
# 3) تحليلات العملاء
# =========================
elif page == "تحليلات العملاء":
    st.markdown("<h2 class='section-title'>تحليلات العملاء</h2>", unsafe_allow_html=True)

    cust = store_df.groupby("customer_id").agg(
        total_revenue=("revenue", "sum"),
        orders=("customer_id", "count"),
        first_purchase=("date", "min"),
        last_purchase=("date", "max"),
    ).reset_index()

    cust["days_since_last"] = (store_df["date"].max() - cust["last_purchase"]).dt.days

    today = store_df["date"].max()
    cust["R"] = cust["days_since_last"]
    cust["F"] = cust["orders"]
    cust["M"] = cust["total_revenue"]

    r_q = cust["R"].quantile([0.33, 0.66])
    f_q = cust["F"].quantile([0.33, 0.66])
    m_q = cust["M"].quantile([0.33, 0.66])

    def rfm_segment(row):
        seg = ""
        seg += "R1" if row["R"] <= r_q.iloc[0] else ("R2" if row["R"] <= r_q.iloc[1] else "R3")
        seg += "F1" if row["F"] <= f_q.iloc[0] else ("F2" if row["F"] <= f_q.iloc[1] else "F3")
        seg += "M1" if row["M"] <= m_q.iloc[0] else ("M2" if row["M"] <= m_q.iloc[1] else "M3")
        return seg

    cust["RFM"] = cust.apply(rfm_segment, axis=1)

    vip_threshold = cust["total_revenue"].quantile(0.9)
    cust["VIP"] = cust["total_revenue"] >= vip_threshold

    last_30 = store_df[store_df["date"] >= today - pd.Timedelta(days=30)]
    new_customers = last_30["customer_id"].unique()
    cust["is_new_last_30"] = cust["customer_id"].isin(new_customers) & (cust["first_purchase"] >= today - pd.Timedelta(days=30))

    cust["churn_risk"] = cust["days_since_last"] >= 60

    st.markdown("<p class='kpi-title'>ملخص العملاء (أعلى 50 عميلًا حسب القيمة)</p>", unsafe_allow_html=True)
    st.dataframe(cust.sort_values("total_revenue", ascending=False).head(50))

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["القيمة والطلبات", "شرائح RFM", "جدد مقابل عائدين", "VIP والتسرب"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<p class='kpi-title'>توزيع قيمة العميل</p>", unsafe_allow_html=True)
            fig_clv = px.histogram(
                cust,
                x="total_revenue",
                nbins=30,
                labels={"total_revenue": "إجمالي إنفاق العميل"},
                template="plotly_white",
                color_discrete_sequence=["#111827"],
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
                color_discrete_sequence=["#111827"],
            )
            st.plotly_chart(fig_orders, use_container_width=True)

    with tab2:
        st.markdown("<p class='kpi-title'>شرائح RFM</p>", unsafe_allow_html=True)
        rfm_counts = cust["RFM"].value_counts().reset_index()
        rfm_counts.columns = ["RFM", "count"]
        fig_rfm = px.bar(
            rfm_counts.head(20),
            x="RFM",
            y="count",
            template="plotly_white",
            labels={"RFM": "القطاع", "count": "عدد العملاء"},
        )
        st.plotly_chart(fig_rfm, use_container_width=True)

    with tab3:
        st.markdown("<p class='kpi-title'>العملاء الجدد مقابل العائدين (آخر 30 يوم)</p>", unsafe_allow_html=True)
        new_count = cust["is_new_last_30"].sum()
        returning_count = len(new_customers) - new_count if len(new_customers) > 0 else 0
        df_new_ret = pd.DataFrame({
            "type": ["جدد", "عائدين"],
            "count": [new_count, returning_count]
        })
        fig_new_ret = px.pie(
            df_new_ret,
            names="type",
            values="count",
            template="plotly_white",
            color_discrete_sequence=["#e5e7eb", "#111827"],
        )
        st.plotly_chart(fig_new_ret, use_container_width=True)

    with tab4:
        st.markdown("<p class='kpi-title'>العملاء VIP والعملاء المعرضون للتسرب</p>", unsafe_allow_html=True)
        vip_df = cust[cust["VIP"]]
        churn_df = cust[cust["churn_risk"]]

        col1, col2 = st.columns(2)
        with col1:
            st.write("العملاء VIP (أعلى 10%):")
            st.dataframe(vip_df[["customer_id", "total_revenue", "orders", "last_purchase"]].head(30))

        with col2:
            st.write("العملاء المعرضون للتسرب (لم يشتروا منذ 60 يومًا أو أكثر):")
            st.dataframe(churn_df[["customer_id", "total_revenue", "orders", "last_purchase", "days_since_last"]].head(30))


# =========================
# 4) التوقعات المستقبلية
# =========================
elif page == "التوقعات المستقبلية":
    st.markdown("<h2 class='section-title'>التوقعات المستقبلية للمبيعات</h2>", unsafe_allow_html=True)

    daily = store_df.groupby("date")[["revenue", "profit"]].sum().reset_index()
    daily = daily.sort_values("date")
    daily["revenue_ma7"] = daily["revenue"].rolling(window=7).mean()
    daily["profit_ma7"] = daily["profit"].rolling(window=7).mean()

    last_date = daily["date"].max()
    future_days = 30
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=future_days)

    last_rev_ma = daily["revenue_ma7"].dropna().iloc[-1]
    last_prof_ma = daily["profit_ma7"].dropna().iloc[-1]
    forecast_rev = np.full(shape=future_days, fill_value=last_rev_ma)
    forecast_prof = np.full(shape=future_days, fill_value=last_prof_ma)

    forecast_df = pd.DataFrame({
        "date": future_dates,
        "forecast_revenue": forecast_rev,
        "forecast_profit": forecast_prof
    })

    tab1, tab2, tab3 = st.tabs(["إجمالي المبيعات", "حسب الفئة", "حسب المدينة"])

    with tab1:
        fig_forecast = px.line(
            daily,
            x="date",
            y="revenue",
            labels={"date": "التاريخ", "revenue": "المبيعات"},
            template="plotly_white",
        )
        fig_forecast.update_traces(line_color="#111827", name="المبيعات الفعلية")

        fig_forecast.add_scatter(
            x=forecast_df["date"],
            y=forecast_df["forecast_revenue"],
            mode="lines",
            name="توقع المبيعات (تقريبي)",
            line=dict(color="#9ca3af", dash="dash"),
        )
        st.plotly_chart(fig_forecast, use_container_width=True)

        fig_prof = px.line(
            daily,
            x="date",
            y="profit",
            labels={"date": "التاريخ", "profit": "الأرباح"},
            template="plotly_white",
        )
        fig_prof.update_traces(line_color="#4b5563", name="الأرباح الفعلية")
        fig_prof.add_scatter(
            x=forecast_df["date"],
            y=forecast_df["forecast_profit"],
            mode="lines",
            name="توقع الأرباح (تقريبي)",
            line=dict(color="#9ca3af", dash="dot"),
        )
        st.plotly_chart(fig_prof, use_container_width=True)

    with tab2:
        st.markdown("<p class='kpi-title'>توقعات تقريبية حسب الفئة</p>", unsafe_allow_html=True)
        cat_daily = store_df.groupby(["date", "category"])["revenue"].sum().reset_index()
        cat_daily = cat_daily.sort_values("date")
        fig_cat = px.line(
            cat_daily,
            x="date",
            y="revenue",
            color="category",
            template="plotly_white",
            labels={"date": "التاريخ", "revenue": "المبيعات", "category": "الفئة"},
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with tab3:
        st.markdown("<p class='kpi-title'>توقعات تقريبية حسب المدينة</p>", unsafe_allow_html=True)
        city_daily = store_df.groupby(["date", "city"])["revenue"].sum().reset_index()
        city_daily = city_daily.sort_values("date")
        fig_city = px.line(
            city_daily,
            x="date",
            y="revenue",
            color="city",
            template="plotly_white",
            labels={"date": "التاريخ", "revenue": "المبيعات", "city": "المدينة"},
        )
        st.plotly_chart(fig_city, use_container_width=True)

    st.info("النماذج الحالية تعتمد على متوسطات متحركة كتقريب، ويمكن لاحقًا استبدالها بنماذج تعلم آلي مثل Prophet أو ARIMA.")


# =========================
# 5) التحليل الجغرافي
# =========================
elif page == "التحليل الجغرافي":
    st.markdown("<h2 class='section-title'>التحليل الجغرافي للمبيعات</h2>", unsafe_allow_html=True)

    city_rev = store_df.groupby("city")["revenue"].sum().reset_index()
    city_rev = city_rev.merge(geo_df, on="city", how="left")

    tab1, tab2, tab3 = st.tabs(["مبيعات المدن", "خريطة حرارة", "الشحن والتوصيل"])

    with tab1:
        st.markdown("<p class='kpi-title'>المبيعات حسب المدينة</p>", unsafe_allow_html=True)
        fig_city = px.bar(
            city_rev,
            x="city",
            y="revenue",
            labels={"city": "المدينة", "revenue": "المبيعات"},
            template="plotly_white",
            color_discrete_sequence=["#111827"],
        )
        st.plotly_chart(fig_city, use_container_width=True)

    with tab2:
        st.markdown("<p class='kpi-title'>خريطة حرارة تقريبية للمبيعات</p>", unsafe_allow_html=True)
        fig_geo = px.density_mapbox(
            city_rev,
            lat="lat",
            lon="lon",
            z="revenue",
            radius=40,
            center=dict(lat=24, lon=45),
            zoom=3.5,
            mapbox_style="carto-positron",
        )
        st.plotly_chart(fig_geo, use_container_width=True)

    with tab3:
        st.markdown("<p class='kpi-title'>تحليل تكلفة الشحن وسرعة التوصيل</p>", unsafe_allow_html=True)
        fig_ship = px.scatter(
            geo_df,
            x="avg_shipping_cost",
            y="avg_delivery_days",
            text="city",
            template="plotly_white",
            labels={"avg_shipping_cost": "متوسط تكلفة الشحن", "avg_delivery_days": "متوسط أيام التوصيل"},
        )
        fig_ship.update_traces(textposition="top center")
        st.plotly_chart(fig_ship, use_container_width=True)

        st.write("بيانات الشحن والتوصيل هنا تقريبية ويمكن ربطها لاحقًا ببيانات حقيقية من شركات الشحن.")


# =========================
# 6) سلاسل الإمداد
# =========================
elif page == "سلاسل الإمداد":
    st.markdown("<h2 class='section-title'>سلاسل الإمداد</h2>", unsafe_allow_html=True)

    prod_fin = store_df.groupby("product")[["revenue", "cost", "quantity"]].sum().reset_index()
    merged = supply_df.merge(prod_fin, on="product", how="left")
    merged["inventory_turnover"] = merged["cost"] / ((merged["stock_level"] + merged["reorder_point"]) / 2)
    merged["inventory_turnover"] = merged["inventory_turnover"].replace([np.inf, -np.inf], np.nan).fillna(0).round(2)

    merged["slow_moving"] = merged["quantity"] < merged["quantity"].median()

    merged["days_to_stockout"] = np.where(
        merged["quantity"] > 0,
        (merged["stock_level"] / (merged["quantity"] / len(store_df["date"].unique()))).round(1),
        np.nan
    )

    st.markdown("<p class='kpi-title'>حالة المخزون وسلاسل الإمداد</p>", unsafe_allow_html=True)
    st.dataframe(merged[["product", "supplier", "stock_level", "reorder_point", "lead_time_days", "inventory_turnover", "risk_flag", "days_to_stockout"]])

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p class='kpi-title'>مستويات المخزون مقابل نقطة إعادة الطلب</p>", unsafe_allow_html=True)
        fig_stock = px.bar(
            merged,
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
            merged,
            x="product",
            y="lead_time_days",
            color="supplier",
            labels={"product": "المنتج", "lead_time_days": "أيام التوريد", "supplier": "المورد"},
            template="plotly_white",
        )
        st.plotly_chart(fig_lead, use_container_width=True)

    st.markdown("---")
    st.markdown("<p class='kpi-title'>تحليل دوران المخزون والمنتجات الراكدة</p>", unsafe_allow_html=True)
    fig_turn = px.bar(
        merged,
        x="product",
        y="inventory_turnover",
        color="slow_moving",
        template="plotly_white",
        labels={"inventory_turnover": "دوران المخزون", "slow_moving": "منتج راكد؟"},
    )
    st.plotly_chart(fig_turn, use_container_width=True)

    st.markdown("<p class='kpi-title'>تنبيهات ذكية</p>", unsafe_allow_html=True)
    alerts = merged[(merged["risk_flag"] == "خطر نفاد") | (merged["days_to_stockout"] <= 7)]
    st.write("المنتجات التي قد تنفد خلال 7 أيام أو أقل (تقديريًا):")
    st.dataframe(alerts[["product", "stock_level", "reorder_point", "days_to_stockout", "risk_flag"]])


# =========================
# 7) الموردون والشركاء
# =========================
elif page == "الموردون والشركاء":
    st.markdown("<h2 class='section-title'>الموردون والشركاء</h2>", unsafe_allow_html=True)

    st.markdown("<p class='kpi-title'>قائمة الموردين ودرجة الأداء</p>", unsafe_allow_html=True)
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
            color_discrete_sequence=["#111827"],
        )
        st.plotly_chart(fig_contracts, use_container_width=True)

    st.markdown("---")
    st.markdown("<p class='kpi-title'>درجة المورد (Supplier Scorecard)</p>", unsafe_allow_html=True)
    fig_score = px.bar(
        suppliers_df,
        x="supplier",
        y="score",
        template="plotly_white",
        labels={"supplier": "المورد", "score": "الدرجة"},
        color_discrete_sequence=["#4ade80"],
    )
    st.plotly_chart(fig_score, use_container_width=True)

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
elif page == "ملخص مؤشرات الأداء":
    st.markdown("<h2 class='section-title'>ملخص مؤشرات الأداء الرئيسية</h2>", unsafe_allow_html=True)

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
    st.markdown("<p class='kpi-title'>مقارنة شهرية (MoM)</p>", unsafe_allow_html=True)
    st.plotly_chart(fig_month, use_container_width=True)

    st.markdown("---")
    st.markdown("<p class='kpi-title'>مؤشرات النمو والمخاطر</p>", unsafe_allow_html=True)
    if len(monthly_kpi) >= 2:
        last_row = monthly_kpi.iloc[-1]
        prev_row = monthly_kpi.iloc[-2]
        rev_growth = (last_row["revenue"] - prev_row["revenue"]) / prev_row["revenue"] * 100 if prev_row["revenue"] > 0 else 0
        prof_growth = (last_row["profit"] - prev_row["profit"]) / prev_row["profit"] * 100 if prev_row["profit"] > 0 else 0
    else:
        rev_growth = prof_growth = 0

    colg1, colg2 = st.columns(2)
    colg1.metric("نمو الإيرادات شهريًا", f"{rev_growth:.1f}%")
    colg2.metric("نمو الأرباح شهريًا", f"{prof_growth:.1f}%")

    total_rev = store_df["revenue"].sum()
    total_prof = store_df["profit"].sum()
    gm = (total_prof / total_rev * 100) if total_rev > 0 else 0
    if gm < 20:
        st.warning(f"هامش الربح الإجمالي منخفض ({gm:.1f}%) – قد تحتاج لمراجعة التسعير أو التكاليف.")
    else:
        st.success(f"هامش الربح الإجمالي جيد ({gm:.1f}%).")


# =========================
# 9) تحليلات الذكاء الاصطناعي (Insights)
# =========================
elif page == "تحليلات ذكية":
    st.markdown("<h2 class='section-title'>تحليلات ذكية</h2>", unsafe_allow_html=True)

    prod_perf = store_df.groupby("product").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        quantity=("quantity", "sum")
    ).reset_index()
    prod_perf["margin"] = (prod_perf["profit"] / prod_perf["revenue"] * 100).replace([np.inf, -np.inf], np.nan).fillna(0)

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
    best_growth_city = growth.sort_values(ascending=False).index[0] if len(growth) > 0 else "-"

    pricing_candidates = prod_perf[(prod_perf["revenue"] > prod_perf["revenue"].median()) & (prod_perf["margin"] < 20)]
    discount_candidates = prod_perf[(prod_perf["revenue"] < prod_perf["revenue"].median()) & (prod_perf["margin"] > 30)]

    stock_risk = supply_df[supply_df["risk_flag"] == "خطر نفاد"]

    cust = store_df.groupby("customer_id").agg(
        total_revenue=("revenue", "sum"),
        orders=("customer_id", "count"),
        last_purchase=("date", "max"),
    ).reset_index()
    cust["days_since_last"] = (store_df["date"].max() - cust["last_purchase"]).dt.days
    churn_customers = cust[cust["days_since_last"] >= 60].sort_values("total_revenue", ascending=False)

    st.markdown("### رؤى عامة")
    st.write(f"- المنتج الأقوى أداءً: {best_product['product']} بإجمالي مبيعات يقارب {best_product['revenue']:,.0f} ريال.")
    st.write(f"- المنتج الأضعف أداءً: {worst_product['product']}، يُنصح بمراجعته من حيث السعر أو التسويق أو الاستبدال.")
    st.write(f"- أعلى مدينة نموًا في المبيعات خلال آخر 30 يومًا: {best_growth_city}.")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### توصيات تسعير")
        st.write("منتجات مبيعاتها عالية وهامش ربحها منخفض – يمكن رفع السعر تدريجيًا:")
        st.dataframe(pricing_candidates[["product", "revenue", "profit", "margin"]])

    with col2:
        st.markdown("#### توصيات عروض وخصومات")
        st.write("منتجات مبيعاتها ضعيفة وهامش ربحها عالي – يمكن عمل عروض عليها:")
        st.dataframe(discount_candidates[["product", "revenue", "profit", "margin"]])

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("#### منتجات معرضة للنفاد")
        st.dataframe(stock_risk[["product", "stock_level", "reorder_point", "risk_flag"]])

    with col4:
        st.markdown("#### عملاء معرضون للتسرب")
        st.dataframe(churn_customers[["customer_id", "total_revenue", "orders", "last_purchase", "days_since_last"]].head(30))

    st.info("يمكن لاحقًا ربط هذه الصفحة بنموذج ذكاء اصطناعي حقيقي أو مساعد تفاعلي يجيب على أسئلة الإدارة.")


# =========================
# 10) الربط مع API
# =========================
elif page == "الربط مع API":
    st.markdown("<h2 class='section-title'>الربط مع API</h2>", unsafe_allow_html=True)

    st.write("هذه الصفحة مثال لمركز تكامل مع أنظمة خارجية.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### أمثلة على تكاملات محتملة:")
        st.markdown("- Shopify (متاجر إلكترونية)")
        st.markdown("- Odoo (نظام ERP وإدارة مخزون)")
        st.markdown("- Zoho Inventory")
        st.markdown("- Google Analytics (تحليل زيارات)")
        st.markdown("- بوابات دفع خليجية: STC Pay, Mada, Benefit, KNET")

        st.markdown("### مثال كود استهلاك API بسيط:")
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
        st.markdown("### تجربة جلب بيانات من API عام")
        try:
            url = "https://jsonplaceholder.typicode.com/posts"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()[:10]
                st.success("تم جلب البيانات بنجاح من واجهة البرمجة.")
                st.dataframe(pd.DataFrame(data))
            else:
                st.error(f"فشل في الاتصال بواجهة البرمجة. كود الاستجابة: {response.status_code}")
        except Exception as e:
            st.error(f"حدث خطأ أثناء الاتصال بواجهة البرمجة: {e}")

