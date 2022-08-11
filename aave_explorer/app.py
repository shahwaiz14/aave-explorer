from datetime import date, timedelta
import pandas as pd
import altair as alt
import streamlit as st
from PIL import Image

from shroomdk import ShroomDK

from shroomDK_queries.metrics import (
    get_aave_price,
    price_change_in_pct,
    get_market_cap,
    get_total_holders,
)

from shroomDK_queries.aave_price import get_aave_price_hourly, get_aave_price_daily

from shroomDK_queries.withdrawals_deposits_borrows import (
    get_aave_latest_withdrawals,
    get_hourly_withdrawals_today,
    get_top_assets_withdrawn,
    get_withdrawal_data_for_tx,
    get_aave_latest_deposits,
    get_top_deposits_today,
    get_top_borrowed_asset,
    get_deposit_data_for_tx,
    get_borrowed_data_for_tx,
)
from shroomDK_queries.aave_user_stats import (
    get_user_latest_lending_activity,
    get_user_total_lending_in_usd,
    get_user_top_lending_pools,
    get_user_latest_borrowing_activity,
    get_user_top_borrowed_pools,
    get_user_total_borrowed_in_usd,
)

from shroomDK_queries.apy_rate import get_apy_rates, get_top_pools_in_aave, calculate_earning

# Initialize `ShroomDK` with API Key
SDK = ShroomDK(st.secrets["FLIPSIDE_API_KEY"])

st.set_page_config(
    page_title="Aave Explorer", layout="centered", initial_sidebar_state="expanded"
)

st.title("Aave Explorer")
st.image(Image.open("aave.png"))

with st.expander("Currently Supported Markets"):
    st.write("Ethereum (Aave V1, V2, AMM)")


# AAVE commone metrics, like price, total holders, and market cap
col1, col2, col3 = st.columns([1.5, 1.5, 2.5])
col1.metric(
    label="AAVE Price",
    value=get_aave_price(SDK),
    delta=f"{round(price_change_in_pct(SDK), 2)}%",
)
col2.metric(label="Total Holders", value=f"{get_total_holders(SDK):,}")
col3.metric(label="Market Cap", value=f"{get_market_cap(SDK):,}")


# AAVE hourly and daily price charts
with st.container():
    price_option = st.selectbox("Aave Price", ("Daily (last 30 days)", "1 hr"))
    if price_option == "1 hr":
        df = get_aave_price_hourly(SDK)
        line_chart = (
            alt.Chart(df, height=400).mark_line().encode(x="hour (in utc)", y="price")
        )
        st.altair_chart(line_chart, use_container_width=True)
    else:
        df = get_aave_price_daily(SDK)
        line_chart = (
            alt.Chart(df, height=400)
            .mark_line()
            .encode(x="date", y="price")
            .configure_axisX(labelAngle=45)
        )
        st.altair_chart(line_chart, use_container_width=True)

st.markdown(
    f'<p style="color:#b7bfe4;font-size:40px;border-radius:2%;">Deposits, Withdrawals & Borrowals</p>',
    unsafe_allow_html=True,
)
# AAVE latest deposits, withdrawals, and borrows
option = st.selectbox(
    "Select Deposits, Withdrawals, or Borrows", ("Withdrawals", "Deposits", "Borrows")
)
if option == "Withdrawals":
    tab1, tab2, tab3 = st.tabs(
        ["Latest Withdrawals", "Top Assets Withdrawn Today", "Hourly Withdrawals"]
    )
    with tab1:
        st.subheader("Latest Withdrawals")
        st.dataframe(get_aave_latest_withdrawals(SDK))
    with tab2:
        st.subheader("Top Assets Withdrawn Today")
        st.table(get_top_assets_withdrawn(SDK))
    with tab3:
        st.subheader("Latest Hourly Withdrawals")
        withdrawal_df = get_hourly_withdrawals_today(SDK)
        st.bar_chart(
            withdrawal_df.set_index("hour")["total withdrawn in usd"],
            height=400,
            use_container_width=True,
        )

elif option == "Deposits":
    tab1, tab2 = st.tabs(["Latest Deposits", "Top Pools Today"])
    with tab1:
        st.subheader("Latest Deposits")
        st.dataframe(get_aave_latest_deposits(SDK))
    with tab2:
        st.subheader("Top Pools Today")
        deposits_df = get_top_deposits_today(SDK)
        st.dataframe(deposits_df)
        try:
            st.bar_chart(
                deposits_df.set_index("symbol")["total_deposited_in_usd"],
                height=400,
                use_container_width=True,
            )
        except:
            pass

elif option == "Borrows":
    st.subheader("Top Borrowed Assets for Today")
    st.dataframe(get_top_borrowed_asset(SDK))


# Txn hash
st.markdown(
    f'<p style="color:#b7bfe4;font-size:40px;border-radius:2%;">Transaction Explorer</p>',
    unsafe_allow_html=True,
)
st.info("Automatically detects if a txn includes lending, withdrawal, or borrowing.")

tx_id = st.text_area(
    "Enter Transaction Hash (Try entering: 0x322a2a183c1fac541ffc109a6e75a6a55a9a521d7dab600d7323c99b40fbea4f)",
    placeholder="(Type tx hash and press ⌘ + Enter to see the results)",
)
if tx_id:
    txn = ""
    if not get_withdrawal_data_for_tx(SDK, tx_id).empty:
        txn = "withdrawn"
        df = get_withdrawal_data_for_tx(SDK, tx_id)
    elif not get_deposit_data_for_tx(SDK, tx_id).empty:
        txn = "deposit"
        df = get_deposit_data_for_tx(SDK, tx_id)
    elif not get_borrowed_data_for_tx(SDK, tx_id).empty:
        txn = "borrowed"
        df = get_borrowed_data_for_tx(SDK, tx_id)

    if txn == "":
        st.info(f"No info found for {tx_id}")
    else:
        col2, col3, col4, col5 = st.columns(4)

        col2.metric("BLOCK ID:", df["block_id"].squeeze())
        col3.metric("SYMBOL:", df["symbol"].squeeze())
        col4.metric(f"{txn.upper()} TOKEN:", round(df[f"{txn}_tokens"].squeeze(), 2))
        col5.metric(f"{txn.upper()} USD:", round(df[f"{txn}_usd"].squeeze(), 2))
        st.text(f"USER ID: {df['address'].squeeze()}")


# User Id Lending and Borrowing Stats
st.markdown(
    f'<p style="color:#b7bfe4;font-size:40px;border-radius:2%;">User Activity Explorer</p>',
    unsafe_allow_html=True,
)
st.caption("Enter user id and get their lending and borrowing activity")
user_id = st.text_area(
    "Enter User Id (Try entering: 0x540f45337b548824438a25734f429e4b4095476a)",
    placeholder="(Press ⌘ + Enter to see the results)",
)
if user_id:
    time_interval = st.selectbox(
        "Select Time Interval (in days)", (1, 3, 5, 7, 9, 11, 13, 15), index=6
    )
    df = get_user_latest_lending_activity(SDK, user_id, time_interval)
    st.subheader("Lending Activity")
    if df.shape[0] == 0:
        st.info(
            f"No lending activity found for {user_id} for the last {time_interval} days"
        )
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"Most Recent Lending Activity for the last {time_interval} days")
            st.dataframe(df)
        with col2:
            st.metric(
                f"Total USD Supplied in the last {time_interval} days",
                f"{round(get_user_total_lending_in_usd(SDK, user_id, time_interval)):,}",
            )
        try:
            bar_chart = (
                alt.Chart(
                    get_user_top_lending_pools(SDK, user_id, time_interval), height=400
                )
                .mark_bar()
                .encode(x="date", y="supplied_usd", color="symbol")
                .configure_axisX(labelAngle=45)
            )

            st.altair_chart(bar_chart, use_container_width=True)
        except:
            pass

    df = get_user_latest_borrowing_activity(SDK, user_id, time_interval)
    st.subheader("Borrowing Activity")
    if df.shape[0] == 0:
        st.info(
            f"No borrowing activity found for {user_id} for the last {time_interval} days"
        )
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.write(
                f"Most Recent Borrowing Activity for the last {time_interval} days"
            )
            st.dataframe(df)
        with col2:
            st.metric(
                f"Total USD Borrowed in the last {time_interval} days",
                f"{round(get_user_total_borrowed_in_usd(SDK, user_id, time_interval)):,}",
            )

        try:
            bar_chart = (
                alt.Chart(
                    get_user_top_borrowed_pools(SDK, user_id, time_interval), height=400
                )
                .mark_bar()
                .encode(x="date", y="borrowed_usd", color="symbol")
                .configure_axisX(labelAngle=45)
            )

            st.altair_chart(bar_chart, use_container_width=True)
        except:
            pass


# Historical APY Lending and Borrowing
st.markdown(
    f'<p style="color:#b7bfe4;font-size:40px;border-radius:2%;">Historical APY Search</p>',
    unsafe_allow_html=True,
)
with st.expander("Details"):
    st.write("""
    This tool allows you to pick an asset from the drop down list and see its
    historical APY for both lending and borrowing over a chosen date range. You
    can also input the amount you would like to lend or borrow and it will show 
    you the estimated amount you will earn or owe by the end of that time period.
    """)

asset = st.selectbox("Pick one of the Assets", get_top_pools_in_aave(SDK))
option = st.selectbox(
    f"Are you looking to borrow or lend your {asset}?", ("Lend", "Borrow")
)
if option:
    start_date = st.date_input("Start date:", value=date.today() - timedelta(10), max_value=date.today())
    end_date = st.date_input("End date:", max_value=date.today())
    if end_date < start_date:
        st.warning("Please pick the right date")

df, average_apy = get_apy_rates(SDK, option, asset, str(start_date), str(end_date))
if df.empty:
    st.info(f"No rates found for {asset} between {start_date} and {end_date}")

st.subheader(f"Historical APY for {option.lower()}ing {asset}")
st.table(df.sort_values("date", ascending=False))
try:
    col_name = "supply_rate" if option == "Lend" else "borrow_rate_stable"
    bar_chart = (
                alt.Chart(df, height=400)
                .mark_bar()
                .encode(x="date", y=col_name)
                .configure_axisX(labelAngle=45)
                )

    st.altair_chart(bar_chart, use_container_width=True)
except:
    pass

st.metric(f"Average Rate for {option}ing {asset}:", round(average_apy, 3))
amount = st.number_input(f"How much are you willing to {option.lower()} {asset}", min_value=0, value=100)
if amount:
    t = st.slider("Select time frame in months", min_value=0, max_value=12)
    if t:
        f = "earn" if option == "Lend" else "pay"
        st.metric(
            f"Total amount you will {f} with {round(average_apy, 3)}% rate in {t} months is:",
            f"{calculate_earning(amount, average_apy, t)} {asset}"
            )


##About
with st.container():
    """ """
    st.subheader("ABOUT:")
    st.caption("Author: Shahwaiz")
    st.caption("Github: https://github.com/shahwaiz14/aave-explorer")
    st.caption("Data provided by Flipside Crypto")
