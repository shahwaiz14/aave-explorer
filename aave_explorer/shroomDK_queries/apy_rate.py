import pandas as pd
import streamlit as st

from shroomdk import ShroomDK


@st.cache()
def get_top_pools_in_aave(sdk: ShroomDK) -> tuple:
    sql = f"""
        SELECT reserve_name,
            COUNT(lending_pool_add)
        FROM flipside_prod_db.aave.market_stats
        GROUP BY 1
        ORDER BY 2 DESC
        LIMIT 15;
        """
    result_set = sdk.query(sql)
    return tuple(i["reserve_name"] for i in result_set.records)


@st.cache()
def get_apy_rates(
    sdk: ShroomDK, option: str, asset: str, start_date: str, end_date: str
) -> tuple:
    sql = f"""
        SELECT block_hour::DATE AS date,
            aave_market,
            lending_pool_add,
            supply_rate,
            borrow_rate_stable,
            borrow_rate_variable
        FROM flipside_prod_db.aave.market_stats
        WHERE block_hour::DATE BETWEEN '{start_date}' AND '{end_date}'
            AND utilization_rate > 0
            AND reserve_name ILIKE '{asset}'
        LIMIT 100;
        """

    result_set = sdk.query(sql)
    df = pd.DataFrame(result_set.records)
    df = df.drop_duplicates(["date", "lending_pool_add"], keep="first")

    if df.empty:
        return (pd.DataFrame(), 0)
    else:
        filtered_df = (
            df[["date", "supply_rate"]]
            if option == "Lend"
            else df[["date", "borrow_rate_stable"]]
        )
        col_name = "supply_rate" if option == "Lend" else "borrow_rate_stable"
        return (filtered_df, filtered_df[col_name].mean())


def calculate_earning(amount: float, apy: int, time: int) -> float:
    # TODO: check if this is the correct way
    yield_ = amount * apy * (time / 12)
    return round(yield_, 5)
