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
def generate_dummy_data(num=50):
    np.random.seed(42)
    merchant_category_map = {
        'Tesco': 'Groceries', 'Starbucks': 'Restaurants', 'Uber': 'Transport',
        'Vue Cinema': 'Entertainment', 'H&M': 'Clothing', 'Shell': 'Transport',
        'M&S': 'Groceries', 'Costco': 'Shopping', 'Amazon': 'Shopping',
        'Pizza Hut': 'Restaurants', 'Arcade': 'Entertainment', 'IKEA': 'Shopping',
        'Boots': 'Health', 'Holland & Barrett': 'Health',
    }
    merchants = list(merchant_category_map.keys())
    year = datetime.today().year
    start = datetime(year, 9, 1)

    rows = []
    for _ in range(num):
        merchant = np.random.choice(merchants)
        category = merchant_category_map[merchant]
        amount = np.round(np.random.uniform(5, 54), 2)
        day = start + timedelta(days=np.random.randint(0, 30))
        hour = np.random.randint(8, 22)
        minute = np.random.randint(0, 60)
        dt = day + timedelta(hours=hour, minutes=minute)
        rows.append({"Date": dt, "Category": category, "Amount": amount, "Merchant": merchant})
    return pd.DataFrame(rows)

df = generate_dummy_data(50).sort_values("Date")
df_numeric = df.copy()

# Display formatting for table
df_display = df.copy()
df_display["Date"] = pd.to_datetime(df_display["Date"]).dt.strftime("%d/%m/%Y %H:%M")
df_display["Amount"] = df_display["Amount"].apply(lambda x: f"£{x:.2f}")


# -------------------------
# KPI summary cards (top row)
# -------------------------
total_spending = df_numeric["Amount"].sum()
num_transactions = len(df_numeric)
avg_transaction = df_numeric["Amount"].mean()

kpi_col1, kpi_col2, kpi_col3 = st.columns(3)

with kpi_col1:
    with st.container(border=True):
        st.subheader("💰 Total Spending")
        st.markdown(f"<h3 style='margin:0; font-family:Roboto'>£{total_spending:,.2f}</h3>", unsafe_allow_html=True)

with kpi_col2:
    with st.container(border=True):
        st.subheader("🧾 Transactions")
        st.markdown(f"<h3 style='margin:0; font-family:Roboto'>{num_transactions}</h3>", unsafe_allow_html=True)

with kpi_col3:
    with st.container(border=True):
        st.subheader("📊 Avg Transaction")
        st.markdown(f"<h3 style='margin:0; font-family:Roboto'>£{avg_transaction:,.2f}</h3>", unsafe_allow_html=True)


# -------------------------
# Helpers: card container WITH TITLE
# -------------------------
def card_container(title: str, height: int = 420):
    """Reusable card with a border and section title"""
    container = st.container(border=True, height=height)
    with container:
        st.subheader(title)
    return container

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
fig_time.update_layout(xaxis_title="Day in September", yaxis_title="Daily Spending (£)", height=280,
                       margin=dict(t=10, l=40, r=10, b=40))

# -------------------------
# Layout (2x2 grid)
# -------------------------
col1, col2 = st.columns(2)

# Top-left: Transactions table card
with col1:
    c1 = card_container("Your September Transactions")
    with c1:
        st.dataframe(df_display, use_container_width=True, height=300)

# Top-right: Category chart card
with col2:
    c2 = card_container("Spending by Category")
    with c2:
        st.plotly_chart(fig_cat, use_container_width=True)

# Bottom-left: Time chart card
col3, col4 = st.columns(2)
with col3:
    c3 = card_container("Spending over September")
    with c3:
        st.plotly_chart(fig_time, use_container_width=True)

# Bottom-right: AI summary card
with col4:
    c4 = card_container("Your AI Spending Summary")
    with c4:
        if "summary_text" not in st.session_state:
            st.session_state["summary_text"] = None

        if st.button("Generate Spending Summary", key="gen_summary"):
            cat_totals = df_numeric.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            top_merchants = df_numeric.groupby("Merchant")["Amount"].sum().sort_values(ascending=False).head(3)
            input_text = (
                f"Over the past {len(df_numeric.head(20))} transactions, "
                f"the highest spending was on {cat_totals.index[0]} (£{cat_totals.iloc[0]:.2f}). "
                f"Other major areas include {cat_totals.index[1]} and {cat_totals.index[2]}. "
                f"The most frequent merchants were {', '.join(top_merchants.index)}."
            )
            prompt = (
                "You are a friendly financial assistant. Write a short, conversational summary of the customer's September spending. "
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
            st.session_state["summary_text"] = response.choices[0].message.content.strip()

        if st.session_state["summary_text"]:
            st.markdown(st.session_state["summary_text"])
        else:
            st.markdown("<p style='color:#666'>Click the button to generate an AI summary of the displayed transactions.</p>", unsafe_allow_html=True)
