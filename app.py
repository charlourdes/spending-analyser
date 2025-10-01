import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from openai import OpenAI
import plotly.express as px

st.set_page_config(page_title="AI Spending Analyser", page_icon="💳", layout="wide")
st.title("Your spending analysis")

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
        # Title with SVG icon
        st.markdown(
            f"""
            <h3 style="display:flex; align-items:center; gap:8px; margin:0;">
                <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 30 30" fill="currentColor">
                    <path d="M14.217,19.707l-1.112,2.547c-0.427,0.979-1.782,0.979-2.21,0l-1.112-2.547c-0.99-2.267-2.771-4.071-4.993-5.057 L1.73,13.292c-0.973-0.432-0.973-1.848,0-2.28l2.965-1.316C6.974,8.684,8.787,6.813,9.76,4.47l1.126-2.714 c0.418-1.007,1.81-1.007,2.228,0L14.24,4.47c0.973,2.344,2.786,4.215,5.065,5.226l2.965,1.316c0.973,0.432,0.973,1.848,0,2.28 l-3.061,1.359C16.988,15.637,15.206,17.441,14.217,19.707z"></path>
                    <path d="M24.481,27.796l-0.339,0.777c-0.248,0.569-1.036,0.569-1.284,0l-0.339-0.777c-0.604-1.385-1.693-2.488-3.051-3.092 l-1.044-0.464c-0.565-0.251-0.565-1.072,0-1.323l0.986-0.438c1.393-0.619,2.501-1.763,3.095-3.195l0.348-0.84 c0.243-0.585,1.052-0.585,1.294,0l0.348,0.84c0.594,1.432,1.702,2.576,3.095,3.195l0.986,0.438c0.565,0.251,0.565,1.072,0,1.323 l-1.044,0.464C26.174,25.308,25.085,26.411,24.481,27.796z"></path>
                </svg>
                Your AI Spending Summary ({month_name})
            </h3>
            """,
            unsafe_allow_html=True
        )

        if "summary_text" not in st.session_state:
            st.session_state["summary_text"] = {}

        if st.button(f"Generate Spending Summary ({month_name})", key=f"gen_summary_{month_name}"):
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

        # Only show text if it exists, no grey placeholder
        if month_name in st.session_state["summary_text"]:
            st.markdown(st.session_state["summary_text"][month_name])


with col2:
    c2 = st.container(border=True, height=420)
    with c2:
        st.subheader(f"Your {month_name} Transactions")
        st.dataframe(df_display, use_container_width=True, height=300)

col3, col4 = st.columns(2)

with col3:
    c3 = st.container(border=True, height=420)
    with c3:
        st.subheader("Spending by Category")
        st.plotly_chart(fig_cat, use_container_width=True)

with col4:
    c4 = st.container(border=True, height=420)
    with c4:
        st.subheader(f"Daily {month_name} Spending")
        st.plotly_chart(fig_time, use_container_width=True)
