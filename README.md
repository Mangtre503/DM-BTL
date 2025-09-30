# 📊 Pipeline Làm Sạch và Phân Tích Dữ Liệu Cổ Phiếu

## 🎯 Tổng Quan

Đây là một pipeline hoàn chỉnh để làm sạch, xử lý và phân tích dữ liệu cổ phiếu từ các tệp CSV. Pipeline hỗ trợ nhiều chế độ chạy linh hoạt và tạo ra các chỉ số kỹ thuật quan trọng cho việc phân tích thị trường chứng khoán.

### ✨ Tính Năng Chính

- 🧹 **Làm sạch dữ liệu tự động**: Xử lý dữ liệu thiếu, outliers, và chuẩn hóa định dạng
- 📈 **Tạo chỉ số kỹ thuật**: Moving averages, RSI, volatility, và nhiều chỉ số khác
- 🔑 **Unique identifier linh hoạt**: Hỗ trợ nhiều định dạng ID khác nhau
- 🗂️ **Xuất dữ liệu đa dạng**: File riêng cho từng mã hoặc gom tất cả vào một file
- 💬 **Giao diện thân thiện**: Chế độ tương tác với hướng dẫn chi tiết
- ⚙️ **Cấu hình linh hoạt**: Tùy chỉnh tất cả thông số thông qua file config

## 🚀 Cài Đặt và Thiết Lập

### 1. Tạo môi trường ảo (Virtual Environment)
```bash
# Di chuyển đến thư mục dự án
cd "t:\251\data_mining\btl"

# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Kiểm tra môi trường đã kích hoạt (sẽ thấy (venv) ở đầu dòng lệnh)
```

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 3. Chuẩn bị dữ liệu
- Đặt các file CSV chứa dữ liệu cổ phiếu vào thư mục `datasets/`
- Mỗi file CSV nên chứa các cột: Date, Open, High, Low, Close, Volume
- Tên file sẽ được sử dụng làm symbol (ví dụ: `AAPL.csv` → symbol `AAPL`)

## 🎮 Cách Sử Dụng

### 1. 🎯 Chế Độ Tự Động (Khuyến nghị cho người mới)
```bash
python main.py
```
Chương trình sẽ hướng dẫn bạn chọn một trong ba chế độ:
- **1**: Nhập từng thông số (Chế độ tương tác)
- **2**: Sử dụng giá trị mặc định từ config
- **3**: Sử dụng command line arguments

### 2. 💬 Chế Độ Tương Tác (Interactive Mode)
```bash
python main.py --interactive
# hoặc
python main.py -i
```
Hệ thống sẽ hỏi từng thông số một cách chi tiết với validation tự động.

### 3. ⚙️ Chế Độ Mặc Định (Nhanh chóng)
```bash
python main.py --default
# hoặc
python main.py -d
```
Sử dụng tất cả cấu hình từ `config.py` mà không cần nhập gì thêm.

### 4. ⌨️ Chế Độ Command Line (Cho người dùng nâng cao)
```bash
# Cơ bản
python main.py --data_dir ./datasets --out_dir ./output

# Đầy đủ tùy chọn
python main.py \
    --data_dir "./nasdaq_data" \
    --out_dir "./cleaned_data" \
    --min_obs 150 \
    --missing_threshold 0.3 \
    --combine_all \
    --unique_id_format filename
```

## ⚙️ Tham Số Cấu Hình Chi Tiết

### 📋 Các Tham Số Chính

| Tham Số | Mô Tả | Giá Trị Mặc Định | Ví Dụ |
|----------|-------|-------------------|-------|
| `--data_dir` | Thư mục chứa dữ liệu CSV đầu vào | `./datasets` | `./nasdaq_data` |
| `--out_dir` | Thư mục lưu kết quả đã xử lý | `./clean_datasets` | `./output` |
| `--min_obs` | Số quan sát tối thiểu để giữ lại một mã | `100` | `150` |
| `--missing_threshold` | Ngưỡng dữ liệu thiếu cho phép (0-1) | `0.35` | `0.2` |
| `--median_volume_threshold` | Khối lượng giao dịch tối thiểu | `None` | `10000` |
| `--fill_limit` | Giới hạn forward-fill cho dữ liệu thiếu | `5` | `3` |
| `--combine_all` | Gom tất cả dữ liệu vào một file | `False` | - |
| `--unique_id_format` | Định dạng unique identifier | `filename` | `ticker` |

### 🔑 Định Dạng Unique ID

#### 1. `filename` (Mặc định - Khuyến nghị)
- Sử dụng tên file làm unique identifier
- **Ví dụ**: `AAPL.csv` → ID = `AAPL`
- **Xử lý trùng lặp**: Tự động thêm `_2`, `_3`, ... khi có file trùng tên
- **Cảnh báo**: Hệ thống sẽ thông báo khi phát hiện trùng lặp

#### 2. `ticker`
- Sử dụng symbol từ dữ liệu hoặc tên file
- **Ví dụ**: Symbol trong CSV hoặc tên file

#### 3. `index`
- Sử dụng số thứ tự tự động
- **Ví dụ**: File đầu tiên → ID = `0`, thứ hai → ID = `1`

#### 4. `hash`
- Sử dụng mã hash MD5 (8 ký tự đầu)
- **Ví dụ**: `AAPL` → ID = `4f3b2a1c`

### 🗂️ Chế Độ Xuất Dữ Liệu

#### File Riêng (combine_all = False)
```
clean_datasets/
├── AAPL.cleaned.csv          # Dữ liệu riêng cho AAPL
├── GOOGL.cleaned.csv         # Dữ liệu riêng cho GOOGL
├── MSFT.cleaned.csv          # Dữ liệu riêng cho MSFT
├── cleaned_all.csv           # Tổng hợp tất cả dữ liệu
└── clean_summary.json        # Báo cáo chi tiết
```

#### Gom Tất Cả (combine_all = True)
```
clean_datasets/
├── all_stocks_combined.csv   # Dữ liệu tất cả mã trong một file
└── clean_summary.json        # Báo cáo chi tiết
```

## 📊 Dữ Liệu Đầu Ra và Các Biến Được Tạo

### 🔍 Cấu Trúc File CSV Kết Quả

Mỗi file CSV đầu ra sẽ chứa các cột sau:

#### **Cột Nhận Diện**
- `stock_id`: Unique identifier cho mỗi mã cổ phiếu
- `symbol`: Ký hiệu mã cổ phiếu (AAPL, GOOGL, ...)
- `date`: Ngày giao dịch (định dạng YYYY-MM-DD)

#### **Dữ Liệu Giá Gốc**
- `open`: Giá mở cửa
- `high`: Giá cao nhất trong ngày
- `low`: Giá thấp nhất trong ngày
- `close`: Giá đóng cửa
- `adj_close`: Giá đóng cửa điều chỉnh (theo chia cổ tức, split)
- `volume`: Khối lượng giao dịch

#### **Dữ Liệu Giá Điều Chỉnh**
- `adj_factor`: Hệ số điều chỉnh (adj_close/close)
- `adj_open`: Giá mở cửa điều chỉnh
- `adj_high`: Giá cao nhất điều chỉnh
- `adj_low`: Giá thấp nhất điều chỉnh

#### **Chỉ Số Lợi Nhuận**
- `daily_return`: Lợi nhuận hàng ngày (%) 
  - Công thức: `(Giá hôm nay - Giá hôm qua) / Giá hôm qua`
  - **Ý nghĩa**: Đo lường biến động giá theo ngày
  - **Ví dụ**: 0.02 = tăng 2% so với ngày hôm trước

- `log_return`: Lợi nhuận logarithmic
  - Công thức: `ln(Giá hôm nay / Giá hôm qua)`
  - **Ý nghĩa**: Phù hợp cho phân tích chuỗi thời gian, có tính chất cộng được
  - **Ưu điểm**: Symmetric, phân phối chuẩn hơn

#### **Moving Averages (Đường Trung Bình Động)**
- `ma_5`: Trung bình động 5 ngày
- `ma_20`: Trung bình động 20 ngày
- `ma_50`: Trung bình động 50 ngày
- `ma_200`: Trung bình động 200 ngày

**Ý nghĩa và Cách Sử Dụng:**
- **MA ngắn hạn (5, 20)**: Phản ánh xu hướng gần đây
- **MA trung hạn (50)**: Xu hướng trung hạn
- **MA dài hạn (200)**: Xu hướng dài hạn, phân biệt thị trường tăng/giảm
- **Golden Cross**: MA ngắn vượt lên MA dài → tín hiệu mua
- **Death Cross**: MA ngắn xuống dưới MA dài → tín hiệu bán

#### **Volatility (Độ Biến Động)**
- `vol_10`: Độ biến động 10 ngày (standard deviation của daily_return)
- `vol_20`: Độ biến động 20 ngày  
- `vol_60`: Độ biến động 60 ngày

**Ý nghĩa:**
- **Giá trị cao**: Cổ phiếu biến động mạnh, rủi ro cao, cơ hội lợi nhuận cao
- **Giá trị thấp**: Cổ phiếu ổn định, rủi ro thấp
- **Sử dụng**: Đánh giá rủi ro, xây dựng portfolio, tính toán VaR

#### **RSI (Relative Strength Index)**
- `rsi_14`: Chỉ số sức mạnh tương đối 14 ngày

**Ý nghĩa và Cách Đọc:**
- **Thang đo**: 0-100
- **RSI > 70**: Vùng quá mua (overbought) → có thể sắp giảm
- **RSI < 30**: Vùng quá bán (oversold) → có thể sắp tăng
- **RSI 30-70**: Vùng trung tính
- **Divergence**: RSI và giá đi ngược chiều → tín hiệu đảo chiều

#### **Khối Lượng Giao Dịch**
- `volume_change`: Thay đổi khối lượng so với ngày trước (%)

**Ý nghĩa:**
- **Volume tăng + Giá tăng**: Xu hướng tăng mạnh
- **Volume tăng + Giá giảm**: Áp lực bán lớn
- **Volume thấp**: Thiếu quan tâm của nhà đầu tư

#### **Phát Hiện Bất Thường**
- `abs_ret`: Giá trị tuyệt đối của daily_return
- `is_outlier`: True/False - đánh dấu ngày có biến động bất thường

### 📋 Ví Dụ Dữ Liệu Thực Tế

```csv
stock_id,symbol,date,open,high,low,close,adj_close,volume,daily_return,log_return,ma_5,ma_20,ma_50,vol_10,vol_20,rsi_14,volume_change
AAPL,AAPL,2020-01-02,74.06,75.15,73.80,75.09,74.35,135480400,0.0089,0.0088,74.85,73.45,71.25,0.0245,0.0198,58.32,0.1245
AAPL,AAPL,2020-01-03,74.28,75.14,74.12,74.36,73.62,-0.0097,-0.0098,74.90,73.52,71.30,0.0251,0.0201,55.78,-0.0832
GOOGL,GOOGL,2020-01-02,1347.0,1368.0,1346.2,1367.4,1367.4,1621200,0.0151,0.0150,1365.2,1342.8,1298.5,0.0189,0.0156,61.45,0.0892
```

## 🧹 Quy Trình Làm Sạch Dữ Liệu

### 1. **Chuẩn Hóa Định Dạng**
- Chuyển tên cột về lowercase với dấu gạch dưới
- Xử lý các tên cột khác nhau: `adjclose` → `adj_close`, `vol` → `volume`
- Chuyển đổi kiểu dữ liệu: date → datetime, price → float

### 2. **Xử Lý Dữ Liệu Thiếu**
- Loại bỏ các hàng không có ngày tháng
- Forward-fill cho dữ liệu giá (tối đa `fill_limit` ngày)
- Báo cáo tỷ lệ dữ liệu thiếu cho mỗi mã

### 3. **Điều Chỉnh Giá**
- Tính toán adjustment factor từ `adj_close` và `close`
- Điều chỉnh tất cả giá theo corporate actions (chia cổ tức, split cổ phiếu)
- Đảm bảo tính nhất quán trong chuỗi giá

### 4. **Reindex Theo Business Days**
- Chuẩn hóa tất cả dữ liệu theo ngày làm việc
- Điền dữ liệu thiếu cho các ngày nghỉ lễ
- Đồng nhất timeline cho tất cả các mã

### 5. **Phát Hiện và Xử Lý Outliers**
- Tính toán daily return và log return
- Đánh dấu các ngày có biến động vượt ngưỡng (`outlier_return_threshold`)
- Loại bỏ dữ liệu không hợp lý (giá ≤ 0, NaN)

### 6. **Lọc Theo Tiêu Chí Chất Lượng**
- **Số quan sát tối thiểu**: Loại bỏ mã có ít hơn `min_observations` ngày
- **Tỷ lệ dữ liệu thiếu**: Loại bỏ mã có quá nhiều dữ liệu thiếu
- **Thanh khoản**: Loại bỏ mã có median volume thấp hơn ngưỡng

## 📈 Ứng Dụng Phân Tích

### 🔍 Phân Tích Kỹ Thuật
```python
# Tín hiệu Golden Cross
df['golden_cross'] = (df['ma_20'] > df['ma_50']) & (df['ma_20'].shift(1) <= df['ma_50'].shift(1))

# Xác định xu hướng
df['trend'] = np.where(df['close'] > df['ma_200'], 'Uptrend', 'Downtrend')

# Tín hiệu RSI
df['rsi_signal'] = np.where(df['rsi_14'] > 70, 'Sell', 
                   np.where(df['rsi_14'] < 30, 'Buy', 'Hold'))
```

### 📊 Phân Tích Rủi Ro
```python
# Tính VaR (Value at Risk) 95%
var_95 = df['daily_return'].quantile(0.05)

# Sharpe Ratio (giả sử risk-free rate = 2% năm)
risk_free_daily = 0.02 / 252
sharpe_ratio = (df['daily_return'].mean() - risk_free_daily) / df['daily_return'].std()

# Maximum Drawdown
cumulative_returns = (1 + df['daily_return']).cumprod()
running_max = cumulative_returns.expanding().max()
drawdown = (cumulative_returns - running_max) / running_max
max_drawdown = drawdown.min()
```

### 🔄 Backtesting Strategies
```python
# Simple Moving Average Strategy
df['position'] = np.where(df['ma_5'] > df['ma_20'], 1, -1)
df['strategy_return'] = df['position'].shift(1) * df['daily_return']
df['cumulative_strategy'] = (1 + df['strategy_return']).cumprod()
```

## ⚙️ Tùy Chỉnh Cấu Hình (config.py)

### 📁 Đường Dẫn Mặc Định
```python
DEFAULT_DATA_DIR = "./datasets"           # Thư mục dữ liệu đầu vào
DEFAULT_OUTPUT_DIR = "./clean_datasets"   # Thư mục kết quả
```

### 🧹 Thông Số Làm Sạch
```python
MIN_OBSERVATIONS = 100          # Số quan sát tối thiểu
MISSING_THRESHOLD = 0.35        # Ngưỡng dữ liệu thiếu (35%)
FILL_LIMIT = 5                 # Giới hạn forward-fill
OUTLIER_RETURN_THRESHOLD = 0.5  # Ngưỡng phát hiện outlier (50%)
```

### 📊 Cấu Hình Feature Engineering
```python
MA_WINDOWS = [5, 20, 50, 200]   # Các cửa sổ Moving Average
VOL_WINDOWS = [10, 20, 60]      # Các cửa sổ Volatility  
RSI_PERIOD = 14                 # Chu kỳ tính RSI
```

### 🔑 Unique ID và Xuất File
```python
COMBINE_ALL_DATA = False                    # Gom dữ liệu vào 1 file
UNIQUE_ID_FORMAT = "filename"               # Định dạng unique ID
UNIQUE_ID_COLUMN = "stock_id"              # Tên cột ID
HANDLE_DUPLICATE_IDS = True                 # Xử lý trùng lặp
DUPLICATE_SUFFIX_FORMAT = "_{}"            # Format suffix: _2, _3...
```

## 📋 Báo Cáo Kết Quả (clean_summary.json)

```json
{
  "total_files": 150,
  "tickers_kept": 120,
  "tickers_dropped": 30,
  "combine_all_data": true,
  "unique_id_format": "filename",
  "unique_id_column": "stock_id",
  "reports": {
    "AAPL": {
      "initial_rows": 2520,
      "final_rows": 2500,
      "missing_ratio": 0.02,
      "pct_outliers": 0.015,
      "status": "kept",
      "unique_id": "AAPL"
    },
    "LOWVOL": {
      "status": "dropped_low_liquidity",
      "median_volume": 5000,
      "initial_rows": 1200
    }
  }
}
```

### 📊 Các Trạng Thái Ticker
- **`kept`**: Được giữ lại và xử lý thành công
- **`dropped_too_few_obs`**: Loại bỏ do quá ít quan sát
- **`dropped_missing_ratio`**: Loại bỏ do quá nhiều dữ liệu thiếu
- **`dropped_low_liquidity`**: Loại bỏ do thanh khoản thấp

## 🚨 Xử Lý Lỗi và Cảnh Báo

### ⚠️ Cảnh Báo Thường Gặp
```
WARNING: Phát hiện trùng lặp unique_id: 'AAPL'. Sẽ đổi thành 'AAPL_2'
WARNING: Ticker ABC có 45% dữ liệu thiếu, vượt ngưỡng 35%
INFO: Đã loại bỏ 15 ngày có biến động bất thường (>50%) cho ticker XYZ
```

### 🔧 Khắc Phục Lỗi Phổ Biến

#### Lỗi: "Không tìm thấy file CSV"
```bash
# Giải pháp: Kiểm tra đường dẫn và tạo thư mục
mkdir datasets
# Đặt file CSV vào thư mục datasets/
```

#### Lỗi: "Cột Date không tồn tại"
```bash
# Giải pháp: Đảm bảo CSV có cột Date hoặc date
# Các định dạng được chấp nhận: Date, date, DATE
```

#### Lỗi: "Không đủ dữ liệu để tính Moving Average"
```bash
# Giải pháp: Giảm MIN_OBSERVATIONS hoặc tăng dữ liệu đầu vào
python main.py --min_obs 50
```

---

<div align="center">

*Được phát triển với QuangTrucSieuCapDepTrai*

</div>