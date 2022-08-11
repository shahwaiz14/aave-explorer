from time import time
import pandas as pd
import streamlit as st

from shroomdk import ShroomDK

########### LENDING QUERIES #############


@st.cache()
def get_user_latest_lending_activity(
    sdk: ShroomDK, user_id: str, time_interval: int
) -> pd.DataFrame:
    sql = f"""
        SELECT block_timestamp::DATE AS date,
            symbol,
            supplied_usd
        FROM flipside_prod_db.aave.deposits
        WHERE depositor_address ILIKE '{user_id}'
            AND block_timestamp::DATE >= CURRENT_DATE - {time_interval}
        ORDER BY 1 DESC
        LIMIT 25;
        """
    results = sdk.query(sql)
    return pd.DataFrame(results.records)


@st.cache()
def get_user_total_lending_in_usd(
    sdk: ShroomDK, user_id: str, time_interval: int
) -> float:
    sql = f"""
        SELECT SUM(supplied_usd) AS supplied_usd
        FROM flipside_prod_db.aave.deposits
        WHERE depositor_address ILIKE '{user_id}'
            AND block_timestamp::DATE >= CURRENT_DATE - {time_interval};
        """
    results = sdk.query(sql)
    return results.records[0]["supplied_usd"]


@st.cache()
def get_user_top_lending_pools(
    sdk: ShroomDK, user_id: str, time_interval: int
) -> pd.DataFrame:
    sql = f"""
        SELECT block_timestamp::DATE AS date,
            symbol,
            SUM(supplied_usd) AS supplied_usd
        FROM flipside_prod_db.aave.deposits
        WHERE depositor_address ILIKE '{user_id}'
            AND block_timestamp::DATE >= CURRENT_DATE - {time_interval}
            AND symbol IS NOT NULL
        GROUP BY 1, 2;
        """
    results = sdk.query(sql)
    return pd.DataFrame(results.records)


########### BORROWING QUERIES #############
@st.cache()
def get_user_latest_borrowing_activity(
    sdk: ShroomDK, user_id: str, time_interval: int
) -> pd.DataFrame:
    sql = f"""
        SELECT block_timestamp::DATE AS date,
            symbol,
            borrowed_usd
        FROM flipside_prod_db.aave.borrows
        WHERE borrower_address ILIKE '{user_id}'
            AND block_timestamp::DATE >= CURRENT_DATE - {time_interval}
        ORDER BY 1 DESC 
        LIMIT 25;
        """
    results = sdk.query(sql)
    return pd.DataFrame(results.records)


@st.cache()
def get_user_total_borrowed_in_usd(
    sdk: ShroomDK, user_id: str, time_interval: int
) -> float:
    sql = f"""
        SELECT SUM(borrowed_usd) AS borrowed_USD
        FROM flipside_prod_db.aave.borrows
        WHERE borrower_address ILIKE '{user_id}'
            AND block_timestamp::DATE >= CURRENT_DATE - {time_interval}
        """
    results = sdk.query(sql)
    return results.records[0]["borrowed_usd"]


@st.cache()
def get_user_top_borrowed_pools(
    sdk: ShroomDK, user_id: str, time_interval: int
) -> pd.DataFrame:
    sql = f"""
        SELECT block_timestamp::DATE AS date,
            symbol,
            SUM(borrowed_usd) AS borrowed_USD
        FROM flipside_prod_db.aave.borrows
        WHERE block_timestamp::DATE >= CURRENT_DATE - {time_interval}
            AND borrower_address ILIKE '{user_id}'
            AND symbol IS NOT NULL
        GROUP BY 1, 2
        """
    results = sdk.query(sql)
    return pd.DataFrame(results.records)
