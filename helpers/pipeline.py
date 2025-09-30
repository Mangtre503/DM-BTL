"""
pipeline.py
Module chứa pipeline chính để xử lý toàn bộ dataset
"""

import os
import json
import logging
import pandas as pd
from tqdm import tqdm

from .config import *
from .utils import (
    find_csv_files, read_csv_guess, normalize_columns, 
    generate_unique_id, handle_duplicate_unique_ids
)
from .data_cleaner import clean_single_ticker


def pipeline_clean_all(
    data_dir,
    out_dir,
    min_observations=MIN_OBSERVATIONS,
    missing_threshold=MISSING_THRESHOLD,
    median_volume_threshold=MEDIAN_VOLUME_THRESHOLD,
    fill_limit=FILL_LIMIT,
    combine_all_data=COMBINE_ALL_DATA,
    unique_id_format=UNIQUE_ID_FORMAT,
):
    """Pipeline làm sạch toàn bộ dataset nhiều ticker."""
    os.makedirs(out_dir, exist_ok=True)
    csvs = find_csv_files(data_dir)
    combined_rows, reports, used_tickers = [], {}, []
    used_unique_ids = set()  # Để theo dõi các unique_id đã sử dụng

    if not csvs:
        if os.path.isfile(data_dir) and data_dir.lower().endswith(".csv"):
            csvs = [data_dir]
        else:
            raise FileNotFoundError(f"Không tìm thấy file CSV nào trong {data_dir}")

    logging.info(f"Tìm thấy {len(csvs)} file CSV. Đang xử lý...")

    for idx, f in enumerate(tqdm(csvs)):
        try:
            df = read_csv_guess(f)
            df = normalize_columns(df)
            
            # Lấy tên file (không có extension) để làm filename
            filename = os.path.splitext(os.path.basename(f))[0].upper()
            
            ticker = (
                str(df["symbol"].dropna().iloc[0])
                if "symbol" in df.columns and df["symbol"].notna().any()
                else filename
            )
            cleaned_df, r = clean_single_ticker(df, ticker=ticker, fill_limit=fill_limit)

            if len(cleaned_df) < min_observations:
                reports[ticker] = {**r, "status": "dropped_too_few_obs"}
                continue

            miss_ratio = cleaned_df.isna().mean().mean()
            if miss_ratio > missing_threshold:
                reports[ticker] = {**r, "status": "dropped_missing_ratio", "missing_ratio": miss_ratio}
                continue

            if median_volume_threshold is not None:
                median_vol = float(cleaned_df["volume"].median(skipna=True) or 0.0)
                if median_vol < median_volume_threshold:
                    reports[ticker] = {**r, "status": "dropped_low_liquidity", "median_volume": median_vol}
                    continue

            if "symbol" not in cleaned_df.columns or cleaned_df["symbol"].isna().all():
                cleaned_df["symbol"] = ticker

            # Tạo unique_id cho ticker (sử dụng filename làm unique_id)
            base_unique_id = generate_unique_id(ticker, format_type=unique_id_format, index=idx, filename=filename)
            
            # Xử lý trùng lặp unique_id nếu cần
            if HANDLE_DUPLICATE_IDS:
                unique_id = handle_duplicate_unique_ids(base_unique_id, used_unique_ids)
            else:
                unique_id = base_unique_id
                used_unique_ids.add(unique_id)
            
            # Nếu không gom tất cả dữ liệu, lưu file riêng cho mỗi ticker
            if not combine_all_data:
                out_path = os.path.join(out_dir, f"{ticker}{INDIVIDUAL_FILE_SUFFIX}")
                cleaned_df.to_csv(out_path, index=True, header=True)
            
            used_tickers.append(ticker)
            reports[ticker] = {**r, "status": "kept", "final_rows": int(len(cleaned_df)), "unique_id": unique_id}

            # Chuẩn bị dữ liệu để gom chung
            tmp = cleaned_df.copy().reset_index().rename(columns={"index": "date"})
            tmp["symbol"] = ticker
            tmp[UNIQUE_ID_COLUMN] = unique_id
            combined_rows.append(tmp)
        except Exception as e:
            logging.exception(f"Xử lý thất bại cho file {f}: {e}")
            continue

    if combined_rows:
        logging.info(f"Đang gộp {len(combined_rows)} DataFrame với tổng cộng ~{sum(len(df) for df in combined_rows):,} dòng...")
        
        # Xử lý từng batch để tránh memory overflow
        combined_all = None
        
        for i in range(0, len(combined_rows), MEMORY_BATCH_SIZE):
            batch = combined_rows[i:i+MEMORY_BATCH_SIZE]
            logging.info(f"Xử lý batch {i//MEMORY_BATCH_SIZE + 1}/{(len(combined_rows)-1)//MEMORY_BATCH_SIZE + 1} ({len(batch)} files)")
            
            # Concat batch hiện tại
            batch_df = pd.concat(batch, axis=0, ignore_index=True)
            batch_df["date"] = pd.to_datetime(batch_df["date"], errors="coerce")
            
            # Tối ưu memory: chuyển về category cho string columns
            for col in batch_df.select_dtypes(include=['object']).columns:
                if batch_df[col].nunique() < len(batch_df) * 0.5:  # Nếu có nhiều giá trị trùng lặp
                    batch_df[col] = batch_df[col].astype('category')
            
            if combined_all is None:
                combined_all = batch_df
            else:
                combined_all = pd.concat([combined_all, batch_df], axis=0, ignore_index=True)
                
            # Dọn dẹp memory
            del batch_df
            import gc
            gc.collect()
        
        # Sort cuối cùng (nếu dataset không quá lớn)
        if len(combined_all) < MAX_ROWS_FOR_SORT:
            logging.info("Đang sắp xếp dữ liệu...")
            combined_all = combined_all.sort_values([UNIQUE_ID_COLUMN, "date"])
        else:
            logging.warning(f"Dataset quá lớn ({len(combined_all):,} dòng), bỏ qua việc sắp xếp để tránh memory error")
        
        # Đặt lại thứ tự cột với unique_id_column ở đầu
        cols = [UNIQUE_ID_COLUMN, "symbol", "date"] + [col for col in combined_all.columns if col not in [UNIQUE_ID_COLUMN, "symbol", "date"]]
        combined_all = combined_all[cols]
        
        if combine_all_data:
            # Nếu gom tất cả dữ liệu vào 1 file
            output_file = os.path.join(out_dir, COMBINED_FILENAME)
            logging.info(f"Đang lưu tất cả dữ liệu vào file duy nhất: {output_file}")
        else:
            # Nếu không, tạo file combined như trước
            output_file = os.path.join(out_dir, "cleaned_all.csv")
            logging.info(f"Đang lưu dữ liệu tổng hợp tới: {output_file}")
        
        # Lưu file với chunksize để tránh memory error
        if len(combined_all) > CHUNK_SIZE_SAVE * 5:  # Nếu > 5M dòng, lưu theo chunk
            logging.info(f"Dataset lớn ({len(combined_all):,} dòng), lưu theo chunk để tối ưu memory...")
            
            # Lưu chunk đầu tiên với header
            combined_all.iloc[:CHUNK_SIZE_SAVE].to_csv(output_file, index=False, mode='w')
            
            # Lưu các chunk còn lại không có header
            for i in range(CHUNK_SIZE_SAVE, len(combined_all), CHUNK_SIZE_SAVE):
                chunk = combined_all.iloc[i:i+CHUNK_SIZE_SAVE]
                chunk.to_csv(output_file, index=False, mode='a', header=False)
                logging.info(f"Đã lưu chunk {i//CHUNK_SIZE_SAVE + 1}/{(len(combined_all)-1)//CHUNK_SIZE_SAVE + 1}")
        else:
            combined_all.to_csv(output_file, index=False)
    else:
        combined_all = pd.DataFrame()

    summary = {
        "total_files": len(csvs),
        "tickers_kept": len(used_tickers),
        "tickers_dropped": len(reports) - len(used_tickers),
        "combine_all_data": combine_all_data,
        "unique_id_format": unique_id_format,
        "unique_id_column": UNIQUE_ID_COLUMN,
        "reports": reports,
    }
    with open(os.path.join(out_dir, SUMMARY_FILENAME), "w") as fh:
        json.dump(summary, fh, indent=2)

    logging.info("Pipeline làm sạch dữ liệu hoàn thành.")
    return summary