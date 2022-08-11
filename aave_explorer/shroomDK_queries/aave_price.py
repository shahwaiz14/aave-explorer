import pandas as pd
import streamlit as st

from shroomdk import ShroomDK


def get_aave_price_hourly(sdk: ShroomDK) -> pd.DataFrame:
    sql = f"""
        SELECT hour AS timestamp,
            HOUR(hour) AS "hour (in utc)",
            symbol,
            price
            FROM ethereum.core.fact_hourly_token_prices
            WHERE symbol ILIKE 'aave'
                AND hour::DATE = CURRENT_DATE
            ORDER BY 1;
        """
    results = sdk.query(sql)
    return pd.DataFrame(results.records)


def get_aave_price_daily(sdk: ShroomDK) -> pd.DataFrame:
    sql = f"""
    SELECT hour::DATE AS date,
        price
        FROM ethereum.core.fact_hourly_token_prices
        WHERE symbol ILIKE 'aave'
            AND HOUR(hour) = 23
            AND hour::DATE >= CURRENT_DATE - 30
        ORDER BY 1;
    """
    results = sdk.query(sql)
    return pd.DataFrame(results.records)
