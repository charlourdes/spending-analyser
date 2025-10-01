import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from openai import OpenAI
import plotly.express as px

st.set_page_config(page_title="AI Spending Analyser", page_icon="💳", layout="wide")
st.title("Your spending analysis dashboard ")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif !important;
        background-color: #F0F4F8;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["openai_api_key"])

# -------------------------
# Data generator
# -------------------------
@st.cache_data
def generate_dummy_data(num=50, month=9):
    np.random.seed(40 + month)  # Different random seed per month

    merchant_category_map = {
        'Tesco': 'Groceries', 'Starbucks': 'Restaurants', 'Uber': 'Transport',
        'Vue Cinema': 'Entertainment', 'H&M': 'Clothing', 'Shell': 'Transport',
        'M&S': 'Groceries', 'Costco': 'Shopping', 'Amazon': 'Shopping',
        'Pizza Hut': 'Restaurants', 'Arcade': 'Entertainment', 'IKEA': 'Shopping',
        'Boots': 'Health', 'Holland & Barrett': 'Health',
    }
    merchants = list(merchant_category_map.keys())
    year = datetime.today().year
    start = datetime(year, month, 1)

    rows = []
    for _ in range(num):
        merchant = np.random.choice(merchants)
        category = merchant_category_map[merchant]

        if month == 8:
            amount = np.round(np.random.uniform(10, 75), 2)
        else:
            amount = np.round(np.random.uniform(5, 54), 2)

        day = start + timedelta(days=np.random.randint(0, 30))
        hour = np.random.randint(8, 22)
        minute = np.random.randint(0, 60)
        dt = day + timedelta(hours=hour, minutes=minute)
        rows.append({"Date": dt, "Category": category, "Amount": amount, "Merchant": merchant})
    return pd.DataFrame(rows)


# -------------------------
# Month selector
# -------------------------
col_month, _, _ = st.columns([1, 2, 2])
with col_month:
    month_choice = st.selectbox("Select Month", ["September", "August"], index=0)

if month_choice == "September":
    df = generate_dummy_data(50, month=9).sort_values("Date")
    month_name = "September"
else:
    df = generate_dummy_data(50, month=8).sort_values("Date")
    month_name = "August"

# -------------------------
# Copies for processing + display
# -------------------------
df_numeric = df.copy()
df_display = df.copy()
df_display["Date"] = pd.to_datetime(df_display["Date"]).dt.strftime("%d/%m/%Y %H:%M")
df_display["Amount"] = df_display["Amount"].apply(lambda x: f"£{x:.2f}")

# -------------------------
# KPI Cards (Top row)
# -------------------------
total_spending = df_numeric["Amount"].sum()
total_transactions = len(df_numeric)
avg_transaction = df_numeric["Amount"].mean()

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    k1 = st.container(border=True, height=120)
    with k1:
        st.metric(f"Total Spending ({month_name})", f"£{total_spending:.2f}")

with kpi2:
    k2 = st.container(border=True, height=120)
    with k2:
        st.metric("Total Transactions", f"{total_transactions}")

with kpi3:
    k3 = st.container(border=True, height=120)
    with k3:
        st.metric("Average Transaction", f"£{avg_transaction:.2f}")

# -------------------------
# Create Plotly figures
# -------------------------
cat_summary = df_numeric.groupby("Category")["Amount"].sum().reset_index()
fig_cat = px.bar(cat_summary, x="Category", y="Amount", text_auto=".2f", color="Category")
fig_cat.update_layout(showlegend=False, yaxis_title="Total Spending (£)", height=280,
                      margin=dict(t=10, l=40, r=10, b=40))

df_numeric["Day"] = pd.to_datetime(df_numeric["Date"]).dt.day
time_summary = df_numeric.groupby("Day")["Amount"].sum().reset_index()
fig_time = px.line(time_summary, x="Day", y="Amount", markers=True)
fig_time.update_layout(xaxis_title=f"Day in {month_name}", yaxis_title="Daily Spending (£)", height=280,
                       margin=dict(t=10, l=40, r=10, b=40))

# -------------------------
# Layout (2x2 grid, swapped order)
# -------------------------
col1, col2 = st.columns(2)

with col1:
    c1 = st.container(border=True, height=420)
    with c1:
        st.subheader(f":material/smart_toy: AI Spending Summary ({month_name})")

        if "summary_text" not in st.session_state:
            st.session_state["summary_text"] = {}

        if st.button(f"Generate Spending Summary", key=f"gen_summary_{month_name}"):
            cat_totals = df_numeric.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            top_merchants = df_numeric.groupby("Merchant")["Amount"].sum().sort_values(ascending=False).head(3)
            input_text = (
                f"Over the past {len(df_numeric)} transactions, "
                f"the highest spending was on {cat_totals.index[0]} (£{cat_totals.iloc[0]:.2f}). "
                f"Other major areas include {cat_totals.index[1]} and {cat_totals.index[2]}. "
                f"The most frequent merchants were {', '.join(top_merchants.index)}."
            )
            prompt = (
                f"You are a friendly financial assistant. Write a short, conversational summary of the customer's {month_name} spending. "
                "Highlight the biggest categories, point out any patterns (like weekends or frequent merchants), "
                "and mention a few specific merchants by name. Do not repeat the numbers exactly — explain insights naturally in 2–3 sentences.\n\n"
                f"Customer spending data:\n{input_text}"
            )
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful financial assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            st.session_state["summary_text"][month_name] = response.choices[0].message.content.strip()

        if month_name in st.session_state["summary_text"]:
            st.markdown(st.session_state["summary_text"][month_name])


with col2:
    c2 = st.container(border=True, height=420)
    with c2:
        st.subheader(f":material/receipt_long: {month_name} Transactions")
        st.dataframe(df_display, use_container_width=True, height=300)

col3, col4 = st.columns(2)

with col3:
    c3 = st.container(border=True, height=420)
    with c3:
        st.subheader(":material/category: Spending by Category")
        st.plotly_chart(fig_cat, use_container_width=True)

with col4:
    c4 = st.container(border=True, height=420)
    with c4:
        st.subheader(f":material/calendar_month: Daily {month_name} Spending")
        st.plotly_chart(fig_time, use_container_width=True)
