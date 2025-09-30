import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from openai import OpenAI
import plotly.express as px

st.set_page_config(
    page_title="AI Spending Analyser",
    page_icon="💳",
    layout="wide"
)

st.title("AI Spending Analyser")

# Initialize OpenAI client 
client = OpenAI(api_key=st.secrets["openai_api_key"])

# Generate fake card transactions for September
@st.cache_data
def generate_dummy_data(num=100):
    np.random.seed(42)

    merchant_category_map = {
        'Tesco': 'Groceries',
        'Starbucks': 'Restaurants',
        'Uber': 'Transport',
        'Vue Cinema': 'Entertainment',
        'H&M': 'Clothing',
        'Shell': 'Transport',
        'M&S': 'Groceries',
        'Costco': 'Shopping',
        'Amazon': 'Shopping',
        'Pizza Hut': 'Restaurants',
        'Arcade': 'Entertainment',
        'IKEA': 'Shopping',
        'Boots': 'Health',
        'Holland & Barrett': 'Health',
    }

    merchants = list(merchant_category_map.keys())

    # September date range
    year = datetime.today().year
    start_date = datetime(year, 9, 1)

    data = []
    for _ in range(num):
        merchant = np.random.choice(merchants)
        category = merchant_category_map[merchant]
        amount = np.round(np.random.uniform(5, 54), 2)  # capped at £54

        # Random day/time in September
        random_day = start_date + timedelta(days=np.random.randint(0, 30))
        random_hour = np.random.randint(8, 22)
        random_minute = np.random.randint(0, 60)
        date = random_day + timedelta(hours=random_hour, minutes=random_minute)

        data.append({
            'Date': date,
            'Category': category,
            'Amount': amount,
            'Merchant': merchant
        })

    return pd.DataFrame(data)

# Load transactions
df = generate_dummy_data(50).sort_values('Date')
df_numeric = df.copy()

# Format Date + Amount for display
df['Date'] = pd.to_datetime(df['Date']).dt.strftime("%d/%m/%Y %H:%M")
df['Amount'] = df['Amount'].apply(lambda x: f"£{x:.2f}")

st.subheader("September Spending Transactions")
st.dataframe(df)

# ---- Plotly Visualisations ----
st.subheader("Spending by Category")
cat_summary = df_numeric.groupby('Category')['Amount'].sum().reset_index()
fig_cat = px.bar(
    cat_summary,
    x="Category",
    y="Amount",
    text_auto='.2f',
    title="Total Spending by Category (£)",
    color="Category"
)
fig_cat.update_layout(showlegend=False, yaxis_title="Total Spending (£)")
st.plotly_chart(fig_cat, use_container_width=True)

st.subheader("Spending Over Time")
df_numeric['Day'] = pd.to_datetime(df_numeric['Date']).dt.day
time_summary = df_numeric.groupby('Day')['Amount'].sum().reset_index()
fig_time = px.line(
    time_summary,
    x="Day",
    y="Amount",
    markers=True,
    title="Daily Spending in September (£)"
)
fig_time.update_layout(xaxis_title="Day in September", yaxis_title="Daily Spending (£)")
st.plotly_chart(fig_time, use_container_width=True)

# ---- AI-Powered Summary ----
def generate_summary(df):
    cat_totals = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
    top_merchants = df.groupby('Merchant')['Amount'].sum().sort_values(ascending=False).head(3)

    input_text = (
        f"Over the past {len(df)} transactions, "
        f"the highest spending was on {cat_totals.index[0]} (£{cat_totals.iloc[0]:.2f}). "
        f"Other major areas include {cat_totals.index[1]} and {cat_totals.index[2]}. "
        f"The most frequent merchants were {', '.join(top_merchants.index)}."
    )

    prompt = (
        "You are a friendly financial assistant. Write a short, conversational summary of the customer's September spending. "
        "Highlight the biggest categories, point out any patterns (like weekends or frequent merchants), "
        "and mention a few specific merchants by name. "
        "Do not repeat the numbers exactly — explain insights naturally in 2–3 sentences.\n\n"
        f"Customer spending data:\n{input_text}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful financial assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

st.subheader("AI Summary of Your Spending")
if st.button("Generate Spending Summary"):
    with st.spinner("Thinking..."):
        summary = generate_summary(df_numeric.head(20))
        st.success("Summary ready!")
        st.markdown(summary)
