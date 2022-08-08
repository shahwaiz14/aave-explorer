import pandas as pd
import streamlit as st

from shroomdk import ShroomDK

@st.cache()
def get_aave_latest_withdrawals(sdk: ShroomDK) -> pd.DataFrame:
    sql = f"""
        SELECT tx_id,
            block_id,
            symbol,
            withdrawn_tokens,
            withdrawn_usd
        FROM flipside_prod_db.aave.withdraws
        WHERE symbol IS NOT NULL
        ORDER BY block_id DESC
        LIMIT 10;
        """
    result = sdk.query(sql)
    return pd.DataFrame(result.records)

@st.cache()
def get_top_assets_withdrawn(sdk: ShroomDK) -> pd.DataFrame:
    sql = f"""
        SELECT symbol AS Symbol,
            ROUND(SUM(withdrawn_usd)) AS "Total Withdrawn in USD"
        FROM flipside_prod_db.aave.withdraws
        WHERE block_timestamp::DATE = CURRENT_DATE - 3 
            AND symbol IS NOT NULL
        GROUP BY 1
        ORDER BY 2 DESC
        """
    results = sdk.query(sql)
    return pd.DataFrame(results.records)

@st.cache()
def get_hourly_withdrawals_today(sdk: ShroomDK) -> pd.DataFrame:
    sql = f"""
        SELECT HOUR(block_timestamp) AS Hour,
            COUNT(DISTINCT(tx_id)) AS "Total Transactions",
            ROUND(SUM(withdrawn_usd)) AS "Total Withdrawn in USD"
        FROM flipside_prod_db.aave.withdraws
        WHERE block_timestamp::DATE = CURRENT_DATE - 3
        AND symbol IS NOT NULL
        GROUP BY 1
        ORDER BY 1;
        """
    results = sdk.query(sql)
    return pd.DataFrame(results.records)

@st.cache()
def get_withdrawal_data_for_tx(sdk: ShroomDK, tx_id: str) -> pd.DataFrame:
    sql = f"""
        SELECT depositor_address,
            block_id,
            symbol,
            withdrawn_tokens,
            withdrawn_usd
        FROM flipside_prod_db.aave.withdraws
        WHERE tx_id ILIKE '{tx_id}'
        ORDER BY block_id DESC;
        """
    results = sdk.query(sql)
    return pd.DataFrame(results.records)

@st.cache()
def get_aave_latest_deposits(sdk: ShroomDK) -> pd.DataFrame:
    sql = f"""
        SELECT tx_id,
            block_id,
            block_timestamp,
            symbol,
            issued_tokens,
            supplied_usd,
            depositor_address
        FROM flipside_prod_db.aave.deposits
        ORDER BY block_timestamp DESC
        LIMIT 10;
        """
    results = sdk.query(sql)
    return pd.DataFrame(results.records)

@st.cache()
def get_top_deposits_today(sdk: ShroomDK) -> pd.DataFrame:
    sql = f"""
        SELECT symbol,
            SUM(supplied_usd) AS total_deposited_in_usd
            FROM flipside_prod_db.aave.deposits
            WHERE block_timestamp::DATE = CURRENT_DATE - 3
            GROUP BY symbol
            ORDER BY 2 DESC
            LIMIT 10;
        """
    results = sdk.query(sql)
    return pd.DataFrame(results.records)

@st.cache()
def get_top_borrowed_asset(sdk: ShroomDK) -> pd.DataFrame:
    sql = f"""
    SELECT symbol,
        SUM(borrowed_usd) AS total_borrowed_in_usd,
        SUM(borrowed_tokens) AS total_borrowed_tokens
    FROM flipside_prod_db.aave.borrows
    WHERE block_timestamp::DATE = CURRENT_DATE - 3
    GROUP BY symbol
    ORDER BY 2 DESC
    LIMIT 10;
    """
    result = sdk.query(sql)
    return pd.DataFrame(result.records)