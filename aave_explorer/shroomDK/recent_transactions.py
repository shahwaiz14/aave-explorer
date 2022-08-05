import pandas as pd
import streamlit as st

from shroomdk import ShroomDK

@st.cache()
def get_aave_latest_transactions(sdk: ShroomDK) -> pd.DataFrame:
    sql = f"""
        SELECT *
        FROM ethereum.core.fact_event_logs
        WHERE contract_address ILIKE '0x80fB784B7eD66730e8b1DBd9820aFD29931aab03'
            AND tx_status = 'SUCCESS'
        ORDER BY block_number DESC
        LIMIT 10;
    """
    # query_result_set = sdk.query(sql)
    # return pd.DataFrame(query_result_set.records)
    return pd.DataFrame({"a":23})

@st.cache()
def get_aave_latest_withdrawals(sdk: ShroomDK) -> pd.DataFrame:
    sql = f"""
        SELECT tx_id,
            block_id,
            symbol,
            withdrawn_tokens,
            withdrawn_usd
        FROM flipside_prod_db.aave.withdraws
        ORDER BY block_id DESC
        LIMIT 10;
        """
    result = sdk.query(sql)
    return pd.DataFrame(result.records)

@st.cache()
def get_aave_latest_deposits(sdk: ShroomDK) -> pd.DataFrame:
    sql = f"""
        SELECT tx_id,
            block_id,
            symbol,
            withdrawn_tokens,
            withdrawn_usd
        FROM flipside_prod_db.aave.withdraws
        ORDER BY block_id DESC
        LIMIT 10;
        """
    result = sdk.query(sql)
    return pd.DataFrame(result.records)
