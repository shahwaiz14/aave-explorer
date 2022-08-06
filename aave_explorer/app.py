import pandas as pd
import streamlit as st

from shroomdk import ShroomDK
from shroomDK.metrics import (
    get_aave_price,
    price_change_in_pct,
    get_market_cap,
    get_total_holders,
)
from shroomDK.recent_transactions import (
    get_aave_latest_transactions,
    get_aave_latest_withdrawals,
    get_aave_latest_deposits,
    get_transaction_details
)
from shroomDK.visualizations import (
    get_aave_price_hourly
)

# Initialize `ShroomDK` with your API Key
SDK = ShroomDK(st.secrets["FLIPSIDE_API_KEY"])


st.title("Aave Explorer")

# AAVE commone metrics, like price, total holders, and market cap
col1, col2, col3 = st.columns(3)
col1.metric(
    label="AAVE Price", value=get_aave_price(SDK), delta=round(price_change_in_pct(SDK), 2)
)
col2.metric(label="Total Holders", value=f"{get_total_holders(SDK):,}")
col3.metric(label="Market Cap", value=f"{get_market_cap(SDK):,}")


# AAVE latest transactions
tab1, tab2 = st.tabs(["Latest Withdrawals", "Latest Deposits"])
with tab1:
    st.header("Latest Withdrawals")
    st.dataframe(get_aave_latest_withdrawals(SDK))
with tab2:
    st.header("Latest Deposits")
    st.dataframe(get_aave_latest_deposits(SDK))

# AAVE Viz
price_df = get_aave_price_hourly(SDK)
st.line_chart(price_df.set_index("hour")["price"])

# AAVE Transaction Explorer
tx_hash = st.text_input("Enter tx hash")
st.dataframe(get_transaction_details(SDK, tx_hash))