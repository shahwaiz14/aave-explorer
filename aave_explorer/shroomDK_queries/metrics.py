import pandas as pd
import streamlit as st

from shroomdk import ShroomDK


def get_aave_price(sdk: ShroomDK) -> float:
    sql = f"""
        SELECT * 
        FROM ethereum.core.fact_hourly_token_prices
        WHERE SYMBOL ILIKE 'aave'
            AND hour::DATE = CURRENT_DATE
        ORDER BY hour DESC
        LIMIT 1;
        """

    query_result_set = sdk.query(sql)
    return round(query_result_set.records[0]["price"], 2)


def price_change_in_pct(sdk: ShroomDK) -> float:
    sql = f"""
        WITH temp AS (
            SELECT *,
                LAG(PRICE, 1) OVER(ORDER BY hour) AS lag1,
                (price/lag1 - 1) * 100 AS pct_change
            FROM ethereum.core.fact_hourly_token_prices
            WHERE SYMBOL ILIKE 'aave'
                AND hour::DATE = CURRENT_DATE
            ORDER BY hour DESC
            LIMIT 1
            )
            SELECT pct_change
            FROM temp;
        """

    result = sdk.query(sql)
    if result.records[0]["pct_change"] == None:
        return 0
    else:
        return round(result.records[0]["pct_change"], 2)


def get_total_holders(sdk: ShroomDK) -> int:
    sql = f"""
    SELECT DISTINCT(COUNT(user_address)) AS number_of_holders
    FROM flipside_prod_db.ethereum.erc20_balances
    WHERE symbol ILIKE 'aave' 
        AND balance_date::DATE = CURRENT_DATE;
    """
    result = sdk.query(sql)
    return result.records[0]["number_of_holders"]


def get_market_cap(sdk: ShroomDK) -> float:
    aave_supply = 16_000_000
    return get_aave_price(sdk) * aave_supply
