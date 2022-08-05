import os
from dotenv import load_dotenv

import pandas as pd
import streamlit as st

from shroomdk import ShroomDK
from shroomDK.metrics import (
    get_aave_price,
    price_change_in_pct,
    get_market_cap,
    get_total_holders,
)
from shroomDK.recent_transactions import get_aave_latest_transactions

load_dotenv()

# Initialize `ShroomDK` with your API Key
SDK = ShroomDK(os.getenv("FLIPSIDE_API_KEY"))


st.title("Aave Explorer")

# AAVE commone metrics, like price, total holders, and market cap

col1, col2, col3 = st.columns(3)
col1.metric(
    label="AAVE Price", value=get_aave_price(SDK), delta=price_change_in_pct(SDK)
)
col2.metric(label="Total Holders", value=f"{get_total_holders(SDK):,}", delta=0)
col3.metric(label="Market Cap", value=f"{get_market_cap(SDK):,}", delta=0)


# AAVE latest transactions
title = st.text_input('Transaction hash')
st.dataframe(get_aave_latest_transactions(SDK))