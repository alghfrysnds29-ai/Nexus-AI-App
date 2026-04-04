import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime as dt
import requests

# =========================
# إعدادات عامة للتطبيق
# =========================
st.set_page_config(
    page_title="لوحة تحكم المتجر الخليجي",
    page_icon="📊",
    layout="wide"
)

# =========================
# دوال توليد بيانات وهمية
# =========================

@st.cache_data
def generate_store_data():
    """توليد بيانات وهمية للمبيعات والطلبات والعملاء والمنتجات في مدن الخليج."""
    np.random.seed(42)
    dates = pd.date_range(end=dt.date.today(), periods=180)

    products = ["منتج A", "منتج B", "منتج C", "منتج D", "منتج E", "منتج F"]
    categories = ["إلكترونيات", "ملابس", "أدوات منزلية", "عطور", "مستلزمات شخصية"]

    gulf_cities = [
        "الرياض", "جدة", "الدمام",
        "دبي", "أبوظبي", "الشارقة",
        "الدوحة", "الكويت", "المنامة", "مسقط"
    ]

    data = []
    customer_ids = [f"CUST-{i:04d}" for i in range(1, 801)]

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
    """بيانات سلاسل الإمداد."""
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
    """بيانات الموردين والشركاء."""
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
    """إحداثيات تقريبية لمدن الخليج للخرائط."""
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
# الشريط الجانبي
# =========================
with st.sidebar:
    st.title("📊 لوحة تحكم الخليج")

    page = st.radio(
        "اختر الصفحة:",
        (
            "📌 لوحة التحكم الرئيسية",
            "💰 التحليل المالي",
            "🚚 سلاسل الإمداد",
            "🤝 الموردون والشركاء",
            "🔗 الربط مع API",
            "📈 التوقعات المستقبلية",
            "🧠 تحليلات الذكاء الاصطناعي",
            "📍 التحليل الجغرافي",
            "👥 تحليلات العملاء",
            "⭐ ملخص مؤشرات الأداء KPI"
        )
    )

    st.markdown("---")
    st.caption("مشروع تحليلي تجريبي لمدن الخليج")


# =========================
# الصفحة 1: لوحة التحكم
# =========================
if page == "📌 لوحة التحكم الرئيسية":
    st.title("📌 لوحة التحكم الرئيسية")

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

    st.subheader("المبيعات اليومية")
    daily = filtered.groupby("date")["revenue"].sum().reset_index()
    fig_daily = px.line(daily, x="date", y="revenue", labels={"date": "التاريخ", "revenue": "المبيعات"})
    st.plotly_chart(fig_daily, use_container_width=True)

    st.subheader("المنتجات الأكثر مبيعًا")
    prod_rev = filtered.groupby("product")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
    fig_prod = px.bar(prod_rev, x="product", y="revenue", labels={"product": "المنتج", "revenue": "المبيعات"})
    st.plotly_chart(fig_prod, use_container_width=True)


# =========================
# الصفحة 2: التحليل المالي
# =========================
elif page == "💰 التحليل المالي":
    st.title("💰 التحليل المالي")

    financial = store_df.groupby("date")[["revenue", "cost", "profit"]].sum().reset_index()

    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي الإيرادات", f"{financial['revenue'].sum():,.0f} ريال")
    col2.metric("إجمالي التكاليف", f"{financial['cost'].sum():,.0f} ريال")
    col3.metric("إجمالي الأرباح", f"{financial['profit'].sum():,.0f} ريال")

    st.markdown("---")

    st.subheader("الإيرادات مقابل التكاليف")
    fig_rev_cost = px.line(
        financial,
        x="date",
        y=["revenue", "cost"],
        labels={"value": "القيمة", "date": "التاريخ", "variable": "البند"}
    )
    st.plotly_chart(fig_rev_cost, use_container_width=True)

    st.subheader("الأرباح اليومية")
    fig_profit = px.area(financial, x="date", y="profit", labels={"date": "التاريخ", "profit": "الأرباح"})
    st.plotly_chart(fig_profit, use_container_width=True)


# =========================
# الصفحة 3: سلاسل الإمداد
# =========================
elif page == "🚚 سلاسل الإمداد":
    st.title("🚚 سلاسل الإمداد")

    st.subheader("حالة المخزون")
    st.dataframe(supply_df)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("مستويات المخزون مقابل نقطة إعادة الطلب")
        fig_stock = px.bar(
            supply_df,
            x="product",
            y=["stock_level", "reorder_point"],
            barmode="group",
            labels={"value": "الكمية", "product": "المنتج", "variable": "البند"}
        )
        st.plotly_chart(fig_stock, use_container_width=True)

    with col2:
        st.subheader("أوقات التوريد حسب المورد")
        fig_lead = px.bar(
            supply_df,
            x="product",
            y="lead_time_days",
            color="supplier",
            labels={"product": "المنتج", "lead_time_days": "أيام التوريد", "supplier": "المورد"}
        )
        st.plotly_chart(fig_lead, use_container_width=True)

    st.markdown("---")
    st.subheader("تحليل المخاطر")
    risk_counts = supply_df["risk_flag"].value_counts().reset_index()
    risk_counts.columns = ["status", "count"]
    fig_risk = px.pie(risk_counts, names="status", values="count", hole=0.4)
    st.plotly_chart(fig_risk, use_container_width=True)


# =========================
# الصفحة 4: الموردون والشركاء
# =========================
elif page == "🤝 الموردون والشركاء":
    st.title("🤝 الموردون والشركاء")

    st.subheader("قائمة الموردين")
    st.dataframe(suppliers_df)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("تقييم الموردين")
        fig_rating = px.bar(
            suppliers_df,
            x="supplier",
            y="rating",
            color="category",
            range_y=[0, 5],
            labels={"supplier": "المورد", "rating": "التقييم", "category": "الفئة"}
        )
        st.plotly_chart(fig_rating, use_container_width=True)

    with col2:
        st.subheader("قيمة العقود")
        fig_contracts = px.bar(
            suppliers_df,
            x="supplier",
            y="contracts_value",
            labels={"supplier": "المورد", "contracts_value": "قيمة العقود"}
        )
        st.plotly_chart(fig_contracts, use_container_width=True)

    st.markdown("---")
    st.subheader("فلترة الموردين")
    min_rating = st.slider("أقل تقييم مقبول", 0.0, 5.0, 3.0, 0.1)
    active_only = st.checkbox("عرض الموردين النشطين فقط", value=True)

    filt = suppliers_df[suppliers_df["rating"] >= min_rating]
    if active_only:
        filt = filt[filt["active"]]

    st.write("الموردون المطابقون للمعايير:")
    st.dataframe(filt)


# =========================
# الصفحة 5: الربط مع API
# =========================
elif page == "🔗 الربط مع API":
    st.title("🔗 الربط مع API")

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


# =========================
# الصفحة 6: التوقعات المستقبلية
# =========================
elif page == "📈 التوقعات المستقبلية":
    st.title("📈 التوقعات المستقبلية للمبيعات")

    daily = store_df.groupby("date")["revenue"].sum().reset_index()
    daily = daily.sort_values("date")

    # متوسط متحرك بسيط كـ Forecast تجريبي
    daily["revenue_ma7"] = daily["revenue"].rolling(window=7).mean()

    last_date = daily["date"].max()
    future_days = 30
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=future_days)

    last_ma = daily["revenue_ma7"].dropna().iloc[-1]
    forecast_values = np.full(shape=future_days, fill_value=last_ma)

    forecast_df = pd.DataFrame({"date": future_dates, "forecast_revenue": forecast_values})

    st.subheader("المبيعات التاريخية والتوقعات")
    fig_forecast = px.line(
        daily,
        x="date",
        y="revenue",
        labels={"date": "التاريخ", "revenue": "المبيعات"},
        title="المبيعات التاريخية"
    )
    fig_forecast.add_scatter(
        x=forecast_df["date"],
        y=forecast_df["forecast_revenue"],
        mode="lines",
        name="توقع المبيعات (تقريبي)"
    )
    st.plotly_chart(fig_forecast, use_container_width=True)

    st.markdown("**ملاحظة:** هذا نموذج توقع بسيط (متوسط متحرك)، ويمكن استبداله لاحقًا بنموذج ML حقيقي.")


# =========================
# الصفحة 7: تحليلات الذكاء الاصطناعي (Insights)
# =========================
elif page == "🧠 تحليلات الذكاء الاصطناعي":
    st.title("🧠 تحليلات ذكية (قواعد بسيطة تحاكي AI)")

    st.write("هذه الصفحة تعرض رؤى (Insights) مبنية على قواعد تحليلية بسيطة، ويمكن لاحقًا استبدالها بنموذج ذكاء اصطناعي حقيقي.")

    # أفضل منتج
    prod_perf = store_df.groupby("product")["revenue"].sum().reset_index()
    best_product = prod_perf.sort_values("revenue", ascending=False).iloc[0]

    # أسوأ منتج
    worst_product = prod_perf.sort_values("revenue", ascending=True).iloc[0]

    # أفضل مدينة نموًا (آخر 30 يوم مقابل 30 قبلها)
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
    st.write(f"- **المنتج الأكثر مساهمة في الإيرادات:** {best_product['product']} بإجمالي مبيعات يقارب {best_product['revenue']:,.0f} ريال.")
    st.write(f"- **المنتج الأضعف أداءً حاليًا:** {worst_product['product']}، قد يحتاج إلى عروض أو إعادة تسعير.")
    st.write(f"- **أعلى مدينة نموًا في المبيعات خلال آخر 30 يومًا:** {best_growth_city}.")
    st.write("- **توصية:** ركّز الحملات التسويقية على المدن ذات النمو العالي، وأعد تقييم المنتجات ذات الأداء الضعيف.")


# =========================
# الصفحة 8: التحليل الجغرافي
# =========================
elif page == "📍 التحليل الجغرافي":
    st.title("📍 التحليل الجغرافي للمبيعات في مدن الخليج")

    city_rev = store_df.groupby("city")["revenue"].sum().reset_index()
    city_rev = city_rev.merge(geo_df, on="city", how="left")

    st.subheader("المبيعات حسب المدينة")
    fig_city = px.bar(
        city_rev,
        x="city",
        y="revenue",
        labels={"city": "المدينة", "revenue": "المبيعات"},
    )
    st.plotly_chart(fig_city, use_container_width=True)

    st.subheader("خريطة المبيعات (تقريبية)")
    fig_geo = px.scatter_geo(
        city_rev,
        lat="lat",
        lon="lon",
        size="revenue",
        hover_name="city",
        projection="natural earth",
        labels={"revenue": "المبيعات"},
    )
    st.plotly_chart(fig_geo, use_container_width=True)


# =========================
# الصفحة 9: تحليلات العملاء
# =========================
elif page == "👥 تحليلات العملاء":
    st.title("👥 تحليلات العملاء")

    cust = store_df.groupby("customer_id").agg(
        total_revenue=("revenue", "sum"),
        orders=("customer_id", "count"),
        first_purchase=("date", "min"),
        last_purchase=("date", "max"),
    ).reset_index()

    cust["days_since_last"] = (store_df["date"].max() - cust["last_purchase"]).dt.days

    st.subheader("ملخص العملاء")
    st.dataframe(cust.head(50))

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("توزيع قيمة العميل (CLV تقريبي)")
        fig_clv = px.histogram(cust, x="total_revenue", nbins=30, labels={"total_revenue": "إجمالي إنفاق العميل"})
        st.plotly_chart(fig_clv, use_container_width=True)

    with col2:
        st.subheader("توزيع عدد الطلبات لكل عميل")
        fig_orders = px.histogram(cust, x="orders", nbins=20, labels={"orders": "عدد الطلبات"})
        st.plotly_chart(fig_orders, use_container_width=True)

    st.markdown("---")
    st.subheader("شرائح العملاء حسب القيمة")
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

    fig_seg = px.pie(seg_counts, names="segment", values="count", hole=0.4)
    st.plotly_chart(fig_seg, use_container_width=True)


# =========================
# الصفحة 10: ملخص مؤشرات الأداء KPI
# =========================
elif page == "⭐ ملخص مؤشرات الأداء KPI":
    st.title("⭐ ملخص مؤشرات الأداء الرئيسية (KPI)")

    today = store_df["date"].max()
    last_30 = store_df[store_df["date"] >= today - pd.Timedelta(days=30)]
    prev_30 = store_df[
        (store_df["date"] < today - pd.Timedelta(days=30)) &
        (store_df["date"] >= today - pd.Timedelta(days=60))
    ]

    def kpi_block(df, label):
        revenue = df["revenue"].sum()
        profit = df["profit"].sum()
        orders = len(df)
        return revenue, profit, orders

    rev_last, prof_last, ord_last = kpi_block(last_30, "آخر 30 يوم")
    rev_prev, prof_prev, ord_prev = kpi_block(prev_30, "الـ 30 يوم السابقة")

    col1, col2, col3 = st.columns(3)
    col1.metric("إيرادات آخر 30 يوم", f"{rev_last:,.0f} ريال", f"{rev_last - rev_prev:,.0f}")
    col2.metric("أرباح آخر 30 يوم", f"{prof_last:,.0f} ريال", f"{prof_last - prof_prev:,.0f}")
    col3.metric("عدد الطلبات (آخر 30 يوم)", f"{ord_last:,}", f"{ord_last - ord_prev:,}")

    st.markdown("---")

    st.subheader("مقارنة شهرية مبسطة")
    monthly = store_df.copy()
    monthly["month"] = monthly["date"].dt.to_period("M").astype(str)
    monthly_kpi = monthly.groupby("month")[["revenue", "profit"]].sum().reset_index()

    fig_month = px.bar(
        monthly_kpi,
        x="month",
        y=["revenue", "profit"],
        barmode="group",
        labels={"month": "الشهر", "value": "القيمة", "variable": "البند"},
    )
    st.plotly_chart(fig_month, use_container_width=True)

    st.markdown("هذه الصفحة موجهة للإدارة العليا لعرض أهم المؤشرات في نظرة واحدة.")
