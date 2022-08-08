import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

from shroomdk import ShroomDK

from shroomDK.metrics import (
    get_aave_price,
    price_change_in_pct,
    get_market_cap,
    get_total_holders,
)

from shroomDK.visualizations import get_aave_price_hourly, get_aave_price_daily

from shroomDK.withdrawals import (
    get_aave_latest_withdrawals,
    get_hourly_withdrawals_today,
    get_top_assets_withdrawn,
    get_withdrawal_data_for_tx,
    get_aave_latest_deposits,
    get_top_deposits_today,
    get_top_borrowed_asset,
)
from shroomDK.aave_user_stats import (
    get_user_latest_lending_activity,
    get_user_total_lending_in_usd,
    get_user_top_lending_pools,
    get_user_latest_borrowing_activity,
    get_user_top_borrowed_pool,
    get_user_total_borrowed_in_usd
)

# Initialize `ShroomDK` with API Key
SDK = ShroomDK(st.secrets["FLIPSIDE_API_KEY"])

st.set_page_config(
    page_title="Aave Explorer", layout="wide", initial_sidebar_state="expanded"
)

st.title("Aave Explorer")

# AAVE commone metrics, like price, total holders, and market cap
col1, col2, col3 = st.columns(3)
col1.metric(
    label="AAVE Price",
    value=get_aave_price(SDK),
    delta=f"{round(price_change_in_pct(SDK), 2)}%",
)
col2.metric(label="Total Holders", value=f"{get_total_holders(SDK):,}")
col3.metric(label="Market Cap", value=f"{get_market_cap(SDK):,}")

price_option = st.selectbox("Aave Price", ("Daily", "1 hr"))
if price_option == "1 hr":
    df = get_aave_price_hourly(SDK)
    fig = plt.figure(figsize=(10, 4))
    g = sns.lineplot(x = "hour", y = "price", data = df)
    g.set_xticklabels(rotation=30)
    st.line_chart(fig)
else:
    df = get_aave_price_daily(SDK)
    st.line_chart(df.set_index("date")["price"])


option = st.selectbox(
    "Select Deposits, Withdrawals, or Borrows", ("Withdrawals", "Deposits", "Borrows")
)
if option == "Withdrawals":
    tab1, tab2, tab3 = st.tabs(
        ["Latest Withdrawals", "Top Assets Withdrawn Today", "Hourly Withdrawals"]
    )
    with tab1:
        st.subheader("Latest Withdrawals")
        st.dataframe(get_aave_latest_deposits(SDK))
    with tab2:
        st.subheader("Top Assets Withdrawn Today")
        st.dataframe(get_top_assets_withdrawn(SDK))
    with tab3:
        st.subheader("Hourly Withdrawals")
        withdrawal_df = get_hourly_withdrawals_today(SDK)
        st.bar_chart(withdrawal_df)
elif option == "Deposits":
    tab1, tab2 = st.tabs(["Latest Deposits", "Top Pools Today"])
    with tab1:
        st.subheader("Latest Deposits")
        st.dataframe(get_aave_latest_deposits(SDK))
    with tab2:
        st.subheader("Top Pools Today")
        st.dataframe(get_top_deposits_today(SDK))
elif option == "Borrows":
    tab1, tab2 = st.tabs(["Top Borrowed Asset", "test"])
    with tab1:
        st.subheader("Top Borrowed Asset")
        st.dataframe(get_top_borrowed_asset(SDK))


tx_id = st.text_area("Enter tx id")
if tx_id:
    with st.spinner("Retreiving..."):
        df = get_withdrawal_data_for_tx(SDK, tx_id)
    if df.shape[0] == 0:
        st.info(f"No info found for {tx_id}")
    else:
        col1, col2 = st.columns(2)
        col3, col4, col5 = st.columns(3)

        col1.metric("BLOCK ID:", df["block_id"].squeeze())
        col2.metric("USER ID:", df["depositor_address"].squeeze())
        col3.metric("SYMBOL:", df["symbol"].squeeze())
        col4.metric("WITHDRAWN TOKEN:", round(df["withdrawn_tokens"].squeeze(), 2))
        col5.metric("WITHDRAWN USD:", round(df["withdrawn_usd"].squeeze(), 2))

user_id = st.text_area("Enter user id")
if user_id:
    time_interval = st.selectbox(
        "Select Time Interval (in days)", (1, 3, 5, 7, 9, 11, 13, 15)
    )
    df = get_user_latest_lending_activity(SDK, user_id, time_interval)
    if df.shape[0] == 0:
        st.info(f"No info found for {user_id}")
    else:
        st.write(f"Most Recent Lending Activity for the last {time_interval} days")
        st.dataframe(df)

        st.metric(
            "Total USD Supplied",
            round(get_user_total_lending_in_usd(SDK, user_id, time_interval)),
        )
        # st.bar_chart(
        #     get_user_top_lending_pools(SDK, user_id, time_interval).set_index(
        #         ["date", "symbol"]
        #     )["supplied_usd"]
        # )

    df = get_user_latest_borrowing_activity(SDK, user_id, time_interval)
    if df.shape[0] == 0:
        st.info(f"No info found for {user_id}")
    else:
        st.write(f"Most Recent Borrowing Activity for the last {time_interval} days")
        st.dataframe(df)

        st.metric(
            "Total USD Borrowed",
            get_user_total_borrowed_in_usd(SDK, user_id, time_interval),
        )

