import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from openai import OpenAI
import plotly.express as px

st.set_page_config(page_title="AI Spending Analyser", page_icon="💳", layout="wide")

# -------------------------
# Data generator 
# -------------------------
@st.cache_data
def generate_dummy_data(num=None, month=9):
    np.random.seed(40 + month)

    # Variable number of transactions
    if num is None:
        if month == 8:
            num = np.random.randint(42, 50)  
        elif month == 9:
            num = np.random.randint(30, 36)  
        else:
            num = np.random.randint(35, 41)

    # merchants and categories
    merchant_category_map = {
        'Tesco': 'Groceries',
        'M&S': 'Groceries',
        'Amazon': 'Shopping',
        'Costco': 'Shopping',
        'H&M': 'Clothing',
        'IKEA': 'Shopping',
        'Starbucks': 'Restaurants',
        'Pizza Hut': 'Restaurants',
        'Uber': 'Transport',
        'Shell': 'Transport',
        'Vue Cinema': 'Entertainment',
        'Arcade': 'Entertainment',
        'Boots': 'Health',
        'Holland & Barrett': 'Health',
    }

    # Extra holiday-style merchants for August to make it realistic 
    if month == 8:
        merchant_category_map.update({
            'Swimming Water Park': 'Entertainment',
            'Airbnb': 'Travel',
            'EasyJet Flights': 'Travel',
            'Local Museum': 'Entertainment',
            'Beachside Café': 'Restaurants'
        })

    merchants = list(merchant_category_map.keys())

    # Adjusted weights to reflect average spending patterns
    merchant_weights = {
        'Tesco': 0.15, 'M&S': 0.10,   
        'Amazon': 0.06, 'Costco': 0.05, 'H&M': 0.04, 'IKEA': 0.02,  
        'Starbucks': 0.06, 'Pizza Hut': 0.05, 'Beachside Café': 0.04 if month == 8 else 0,  
        'Uber': 0.06, 'Shell': 0.05,                                 
        'Vue Cinema': 0.05, 'Arcade': 0.04,                          
        'Boots': 0.02, 'Holland & Barrett': 0.02,                   
        # Seasonal additions (to make august more holiday focused)
        'Swimming Water Park': 0.05 if month == 8 else 0,
        'Airbnb': 0.05 if month == 8 else 0,
        'EasyJet Flights': 0.04 if month == 8 else 0,
        'Local Museum': 0.03 if month == 8 else 0,
    }

    weights = np.array([merchant_weights.get(m, 0) for m in merchants])
    weights /= weights.sum()

    year = datetime.today().year
    start = datetime(year, month, 1)

    rows = []
    for _ in range(num):
        merchant = np.random.choice(merchants, p=weights)
        category = merchant_category_map[merchant]

        # Spending ranges by category
        if category == 'Groceries':
            amount = np.random.uniform(15, 55)
        elif category == 'Restaurants':
            amount = np.random.uniform(12, 35)  
        elif category == 'Transport':
            amount = np.random.uniform(5, 25)
        elif category == 'Shopping':
            amount = np.random.uniform(15, 70)  
        elif category == 'Clothing':
            amount = np.random.uniform(20, 80)
        elif category == 'Entertainment':
            amount = np.random.uniform(15, 65)
        elif category == 'Health':
            amount = np.random.uniform(8, 40)
        elif category == 'Travel':
            amount = np.random.uniform(80, 250)  
        else:
            amount = np.random.uniform(5, 50)

        # Month-based adjustments
        if month == 8 and category in ["Restaurants", "Entertainment", "Travel"]:
            amount *= 1  
        if month == 9:
            amount *= 0.9  

        
        day_offset = np.random.randint(0, 30)
        day = start + timedelta(days=day_offset)
        if category in ['Restaurants', 'Entertainment'] and day.weekday() >= 5:
            amount *= 1.2

        # Time of day
        hour = np.random.randint(8, 22)
        minute = np.random.randint(0, 60)
        dt = day + timedelta(hours=hour, minutes=minute)

        rows.append({
            "Date": dt,
            "Category": category,
            "Amount": round(amount, 2),
            "Merchant": merchant
        })

    # Fixed monthly costs on the 2nd of each month for realism
    rows.append({
        "Date": start + timedelta(days=1, hours=9),
        "Category": "Rent & Utilities",
        "Amount": 600.00,
        "Merchant": "Monthly Rent"
    })
    rows.append({
        "Date": start + timedelta(days=1, hours=10),
        "Category": "Rent & Utilities",
        "Amount": 30.00,
        "Merchant": "Phone Bill"
    })

    return pd.DataFrame(rows)

# -------------------------
# Title
# -------------------------
st.title("Your Spending Dashboard")

# -------------------------
# Month selector
# -------------------------
col_month, _ = st.columns([1, 3])
with col_month:
    month_choice = st.selectbox("Select Month", ["September", "August"], index=0, label_visibility="collapsed")

# -------------------------
# Apply selection
# -------------------------
if month_choice == "September":
    df = generate_dummy_data(month=9).sort_values("Date")
    month_name = "September"
else:
    df = generate_dummy_data(month=8).sort_values("Date")
    month_name = "August"

st.subheader(f"{month_name} Spending Analysis")

# -------------------------
# Copies for processing
# -------------------------
df_numeric = df.copy()
df_display = df.copy()
df_display["Date"] = pd.to_datetime(df_display["Date"]).dt.strftime("%d/%m/%Y %H:%M")
df_display["Amount"] = df_display["Amount"].apply(lambda x: f"£{x:.2f}")

# -------------------------
# Compare months
# -------------------------
df_aug = generate_dummy_data(month=8)
df_sep = generate_dummy_data(month=9)

aug_total_spending = df_aug["Amount"].sum()
sep_total_spending = df_sep["Amount"].sum()

if month_choice == "September":
    total_spending = sep_total_spending
    total_transactions = len(df_sep)
    avg_transaction = df_sep["Amount"].mean()
    delta_spending = sep_total_spending - aug_total_spending
    percent_change = ((sep_total_spending - aug_total_spending) / aug_total_spending) * 100
    delta_color = "inverse" if delta_spending < 0 else "normal"
else:
    total_spending = aug_total_spending
    total_transactions = len(df_aug)
    avg_transaction = df_aug["Amount"].mean()
    delta_spending = None
    percent_change = None
    delta_color = None

# -------------------------
# KPI cards
# -------------------------
kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    k1 = st.container(border=True, height=120)
    with k1:
        if month_choice == "September":
            col_left, col_right = st.columns([3, 1])
            with col_left:
                st.metric(
                    f"Total Spending ({month_name})",
                    f"£{total_spending:.2f}",
                    delta=f"{percent_change:.1f}%",
                    delta_color=delta_color
                )
            with col_right:
                if percent_change < 0:
                    st.caption(":material/trending_down: Spending down from last month")
                elif percent_change > 0:
                    st.caption(":material/trending_up: Spending up from last month")
        else:
            st.metric(f"Total Spending ({month_name})", f"£{total_spending:.2f}")

with kpi2:
    k2 = st.container(border=True, height=120)
    with k2:
        st.metric("Total Transactions", f"{total_transactions}")

with kpi3:
    k3 = st.container(border=True, height=120)
    with k3:
        st.metric("Average Transaction Cost", f"£{avg_transaction:.2f}")

# -------------------------
# Charts
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
# Layout
# -------------------------
col1, col2 = st.columns(2)

with col1:
    c1 = st.container(border=True, height=420)
    with c1:
        st.subheader(f":material/smart_toy: AI Spending Summary ({month_name})")

        if "summary_text" not in st.session_state:
            st.session_state["summary_text"] = {}

        summary_box = st.empty()

        if st.button(f"Generate AI Spending Summary", type="primary", key=f"gen_summary_{month_name}"):
            with st.spinner("🤖 Analysing your spending… please wait"):
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
                    "Highlight the biggest categories, point out any patterns, "
                    "look for changes in spending based on week or weekend, " "Based on this data, suggest one practical personalised budgeting tip or financial goals."
                    "look for themes of purchases, and a small comparison to last month if available, "
                    "and mention a few specific merchants by name. Do not repeat the numbers exactly — explain insights naturally in 3-4 sentences.\n\n"
                    f"Customer spending data:\n{input_text}"
                )

                response = OpenAI(api_key=st.secrets["openai_api_key"]).chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful financial assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                st.session_state["summary_text"][month_name] = response.choices[0].message.content.strip()

        if month_name in st.session_state["summary_text"]:
            summary_box.markdown(st.session_state["summary_text"][month_name])
        else:
            summary_box.markdown("_No summary generated yet for this month._")

with col2:
    c2 = st.container(border=True, height=420)
    with c2:
        st.subheader(f":material/receipt_long: Your Transactions in {month_name}")
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
        st.subheader(f":material/calendar_month: Daily Spending {month_name}")
        st.plotly_chart(fig_time, use_container_width=True)
