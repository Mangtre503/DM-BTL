"""
data_cleaner.py
Module chứa các hàm làm sạch và feature engineering cho dữ liệu cổ phiếu
"""

import pandas as pd
import numpy as np
import logging
from .config import *
from .utils import normalize_columns, ensure_price_columns


def clean_single_ticker(    
    df,
    ticker=None,
    fill_limit=FILL_LIMIT,
    reindex_bdays=True,
    outlier_return_threshold=OUTLIER_RETURN_THRESHOLD,
):
    """
    Làm sạch và bổ sung feature cho 1 ticker.

    Parameters
    ----------
    df : pd.DataFrame
        Dữ liệu thô của 1 mã cổ phiếu
    ticker : str
        Ký hiệu mã cổ phiếu (ví dụ AAPL)
    fill_limit : int
        Số ngày tối đa forward-fill khi reindex về business days
    reindex_bdays : bool
        Có chuẩn hóa index theo business days hay không
    outlier_return_threshold : float
        Ngưỡng nhận diện outlier cho daily return

    Returns
    -------
    cleaned_df : pd.DataFrame
    report : dict
    """
    df = df.copy()
    df = normalize_columns(df)
    df = ensure_price_columns(df)

    # Parse date
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    initial_count = len(df)

    # Drop rows không có date
    df = df[~df["date"].isna()].copy()
    df = df.sort_values("date").drop_duplicates(subset=["date"], keep="last")

    # Set index
    df = df.set_index("date").sort_index()

    # Convert numeric
    for col in ["open", "high", "low", "close", "adj_close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Điều chỉnh giá theo adj_close
    if df["adj_close"].notna().sum() > 0:
        df["adj_factor"] = df["adj_close"] / df["close"]
        df["adj_factor"] = df["adj_factor"].replace([np.inf, -np.inf], np.nan).ffill().bfill()
        for pcol in ["open", "high", "low", "close"]:
            df["adj_" + pcol] = df[pcol] * df["adj_factor"]
        price_col_for_returns = "adj_close"
    else:
        price_col_for_returns = "close"
        logging.debug(f"Không có adj_close cho {ticker}; sử dụng close để tính lợi nhuận")

    # Reindex về business days
    if reindex_bdays:
        bidx = pd.bdate_range(start=df.index.min(), end=df.index.max())
        df = df.reindex(bidx)
        if "symbol" in df.columns and df["symbol"].isna().all() and ticker:
            df["symbol"] = ticker
        df[["open", "high", "low", "close", "adj_close", "volume"]] = df[
            ["open", "high", "low", "close", "adj_close", "volume"]
        ].ffill(limit=fill_limit)

    # Daily return (lợi nhuận hằng ngày)
    df["daily_return"] = df[price_col_for_returns].pct_change(fill_method=None)

    # Log return (logarithmic return, hữu ích khi phân tích chuỗi thời gian)
    # Chỉ tính log cho giá trị > 0 để tránh warning
    price_positive = df[price_col_for_returns].where(df[price_col_for_returns] > 0)
    df["log_return"] = np.log(price_positive).diff()

    # Outlier detection
    df["abs_ret"] = df["daily_return"].abs()
    df["is_outlier"] = df["abs_ret"] > outlier_return_threshold

    # Loại bỏ giá không hợp lý (NaN, <= 0)
    plausible_mask = (df[price_col_for_returns] > 0) & (~df[price_col_for_returns].isna())
    df = df[plausible_mask].copy()

    # ---------- Feature Engineering bổ sung ----------
    # Moving Averages (MA ngắn hạn / trung hạn / dài hạn)
    for window in MA_WINDOWS:
        min_periods = max(1, window // 5)  # Tối thiểu 20% window size
        df[f"ma_{window}"] = df[price_col_for_returns].rolling(window=window, min_periods=min_periods).mean()

    # Volatility (biến động giá)
    for window in VOL_WINDOWS:
        df[f"vol_{window}"] = df["daily_return"].rolling(window=window).std()

    # Volume Change (% thay đổi khối lượng)
    df["volume_change"] = df["volume"].pct_change(fill_method=None)

    # RSI (Relative Strength Index)
    delta = df[price_col_for_returns].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain, index=df.index).rolling(window=RSI_PERIOD).mean()
    avg_loss = pd.Series(loss, index=df.index).rolling(window=RSI_PERIOD).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df[f"rsi_{RSI_PERIOD}"] = 100 - (100 / (1 + rs))

    # Báo cáo
    finished_count = len(df)
    report = {
        "initial_rows": int(initial_count),
        "final_rows": int(finished_count),
        "missing_ratio": float(df.isna().mean().mean()),
        "pct_outliers": float(df["is_outlier"].sum() / max(1, finished_count)),
    }
    return df, report