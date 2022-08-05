import pandas as pd
import streamlit as st

from shroomdk import ShroomDK

@st.cache()
def get_aave_price_hourly(sdk: ShroomDK) -> pd.DataFrame:
    sql = f"""
        SELECT hour AS timestamp,
            HOUR(hour) AS hour,
            symbol,
            price
            FROM ethereum.core.fact_hourly_token_prices
            WHERE symbol ILIKE 'aave'
                AND hour::DATE = CURRENT_DATE
            ORDER BY 1;
        """
    results = sdk.query(sql)
    return pd.DataFrame(results.records)

@st.cache()
def get_aave_price_daily(sdk: ShroomDK) -> pd.DataFrame:
    ...