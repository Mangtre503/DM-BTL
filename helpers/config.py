"""
config.py
File cấu hình cho pipeline làm sạch dữ liệu cổ phiếu
"""

# ---------- Cấu hình chung ----------
DEFAULT_DATA_DIR = "./dataset"
DEFAULT_OUTPUT_DIR = "./clean_dataset"

# ---------- Cấu hình làm sạch dữ liệu ----------
MIN_OBSERVATIONS = 100
MISSING_THRESHOLD = 0.35
MEDIAN_VOLUME_THRESHOLD = None
FILL_LIMIT = 5

# ---------- Cấu hình memory và hiệu suất ----------
MAX_FILES_PROCESS = None  # None = xử lý tất cả, hoặc số nguyên để giới hạn
MEMORY_BATCH_SIZE = 100   # Số file xử lý cùng lúc (tránh memory overflow)
MAX_ROWS_FOR_SORT = 10_000_000  # Số dòng tối đa cho phép sort (tránh memory error)
CHUNK_SIZE_SAVE = 1_000_000     # Kích thước chunk khi lưu file lớn

# ---------- Cấu hình outlier detection ----------
OUTLIER_RETURN_THRESHOLD = 0.5

# ---------- Cấu hình xuất dữ liệu ----------
# Nếu True: Gom tất cả dữ liệu vào 1 file duy nhất với cột unique_id
# Nếu False: Tạo file riêng cho mỗi ticker + file combined
COMBINE_ALL_DATA = True

# Tên cột unique identifier cho mỗi stock/ETF
UNIQUE_ID_COLUMN = "stock_id"

# Xử lý trùng lặp unique_id
HANDLE_DUPLICATE_IDS = True
DUPLICATE_SUFFIX_FORMAT = "_{}"

# Định dạng unique_id: có thể là "ticker", "index", "hash", hoặc "filename"
# - "ticker": Sử dụng symbol làm unique_id
# - "index": Sử dụng số thứ tự (0, 1, 2, ...)
# - "hash": Sử dụng hash của ticker
# - "filename": Sử dụng tên file (không có extension) làm unique_id
UNIQUE_ID_FORMAT = "filename"

# ---------- Cấu hình feature engineering ----------
# Moving averages windows
MA_WINDOWS = [5, 20, 50, 200]

# Volatility windows
VOL_WINDOWS = [10, 20, 60]

# RSI period
RSI_PERIOD = 14

# ---------- Cấu hình file output ----------
COMBINED_FILENAME = "all_stocks_combined.csv"
INDIVIDUAL_FILE_SUFFIX = ".cleaned.csv"
SUMMARY_FILENAME = "clean_summary.json"

# ---------- Logging configuration ----------
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"

# ---------- Performance configuration ----------
# Có sử dụng multiprocessing không
USE_MULTIPROCESSING = False
MAX_WORKERS = 4

# Chunk size khi xử lý dữ liệu lớn
CHUNK_SIZE = 10000