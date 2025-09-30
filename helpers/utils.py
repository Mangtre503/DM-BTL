"""
utils.py
Các hàm tiện ích cho pipeline làm sạch dữ liệu cổ phiếu
"""

import os
import glob
import logging
import pandas as pd
import hashlib
from .config import *


def generate_unique_id(ticker, format_type="ticker", index=None, filename=None):
    """
    Tạo unique identifier cho mỗi stock/ETF
    
    Parameters
    ----------
    ticker : str
        Ký hiệu mã cổ phiếu
    format_type : str
        Loại format: "ticker", "index", "hash", "filename"
    index : int
        Số thứ tự (chỉ dùng khi format_type="index")
    filename : str
        Tên file (không có extension, chỉ dùng khi format_type="filename")
    
    Returns
    -------
    unique_id : str
    """
    if format_type == "ticker":
        return ticker
    elif format_type == "index":
        return str(index) if index is not None else "0"
    elif format_type == "hash":
        return hashlib.md5(ticker.encode()).hexdigest()[:8]
    elif format_type == "filename":
        return filename if filename is not None else ticker
    else:
        return ticker


def handle_duplicate_unique_ids(unique_id, used_ids, warn=True):
    """
    Xử lý trùng lặp unique_id bằng cách thêm suffix
    
    Parameters
    ----------
    unique_id : str
        Unique ID gốc
    used_ids : set
        Set chứa các ID đã sử dụng
    warn : bool
        Có hiển thị cảnh báo không
    
    Returns
    -------
    final_id : str
        Unique ID cuối cùng (có thể có suffix)
    """
    original_id = unique_id
    counter = 1
    
    while unique_id in used_ids:
        counter += 1
        unique_id = original_id + DUPLICATE_SUFFIX_FORMAT.format(counter)
        
        if warn and counter == 2:  # Chỉ cảnh báo lần đầu tiên
            logging.warning(f"Phát hiện trùng lặp unique_id: '{original_id}'. Sẽ đổi thành '{unique_id}'")
    
    used_ids.add(unique_id)
    return unique_id


def find_csv_files(data_dir):
    """Tìm tất cả file .csv trong thư mục (không đệ quy sâu)."""
    patterns = [os.path.join(data_dir, "*.csv"), os.path.join(data_dir, "*", "*.csv")]
    files = []
    for p in patterns:
        files.extend(glob.glob(p))
    return sorted(list(set(files)))


def read_csv_guess(path):
    """Đọc CSV với một vài thử parse options để tránh lỗi encoding/delimiter."""
    parse_dates = ["Date"]
    try:
        df = pd.read_csv(path, parse_dates=parse_dates, low_memory=False)
    except Exception as e:
        logging.warning(f"Đọc file CSV mặc định thất bại cho {path}: {e} — Thử lại với engine python")
        df = pd.read_csv(path, parse_dates=parse_dates, engine="python", low_memory=False)
    return df


def normalize_columns(df):
    """Chuẩn hoá tên cột về lower_case_with_underscore, map alias phổ biến."""
    df = df.rename(columns=lambda c: str(c).strip().lower().replace(" ", "_"))
    colmap = {}
    for c in df.columns:
        if c in ["adjclose", "adj_close", "adjusted_close", "adjusted close"]:
            colmap[c] = "adj_close"
        if c in ["close", "closing_price"]:
            colmap[c] = "close"
        if c in ["open"]:
            colmap[c] = "open"
        if c in ["high"]:
            colmap[c] = "high"
        if c in ["low"]:
            colmap[c] = "low"
        if c in ["volume", "vol"]:
            colmap[c] = "volume"
        if c in ["symbol", "ticker"]:
            colmap[c] = "symbol"
        if c in ["date"]:
            colmap[c] = "date"
    return df.rename(columns=colmap)


def ensure_price_columns(df):
    """Đảm bảo có các cột cần thiết (thiếu thì tạo NaN)."""
    import numpy as np
    for col in ["date", "open", "high", "low", "close", "adj_close", "volume", "symbol"]:
        if col not in df.columns:
            df[col] = np.nan
    return df