import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import os

# ========= 1. Load Dataset =========
df = pd.read_csv("./dataset/A.csv")

# ========= 2. Basic Cleaning =========
df['Date'] = pd.to_datetime(df['Date'])
df = df.drop_duplicates(subset=['Date'])
df = df.interpolate(method='linear')

# Remove outliers (IQR on Close)
Q1 = df['Close'].quantile(0.25)
Q3 = df['Close'].quantile(0.75)
IQR = Q3 - Q1
df = df[~((df['Close'] < (Q1 - 1.5 * IQR)) | (df['Close'] > (Q3 + 1.5 * IQR)))]

# Remove invalid values
df = df[
    (df['Open'] > 0) &
    (df['High'] > 0) &
    (df['Low'] > 0) &
    (df['Close'] > 0) &
    (df['Volume'] > 0) &
    (df['High'] >= df['Low'])
]

# Drop correlated field
df = df.drop(columns=['Adj Close'], errors='ignore')

# ========= 3. Feature Engineering (tạo trước, scale sau) =========

# 3.1. Price returns
df["Return"] = df["Close"].pct_change()

# 3.2. Lag features (giúp dự đoán ngày mai bằng dữ liệu hôm qua)
df["Close_lag1"] = df["Close"].shift(1)
df["Close_lag2"] = df["Close"].shift(2)
df["Close_lag3"] = df["Close"].shift(3)

df["Volume_lag1"] = df["Volume"].shift(1)

# 3.3. Moving averages
df["MA5"] = df["Close"].rolling(window=5).mean()
df["MA10"] = df["Close"].rolling(window=10).mean()
df["MA20"] = df["Close"].rolling(window=20).mean()

# 3.4. Volatility features
df["STD5"] = df["Close"].rolling(window=5).std()
df["STD10"] = df["Close"].rolling(window=10).std()

# 3.5. True Range & ATR
df["Previous_Close"] = df["Close"].shift(1)
df["TR"] = df[["High", "Previous_Close"]].max(axis=1) - \
           df[["Low", "Previous_Close"]].min(axis=1)
df["ATR14"] = df["TR"].rolling(window=14).mean()

# 3.6. Day-of-week (categorical)
df["DayOfWeek"] = df["Date"].dt.weekday

# ========= 4. Create Target (Close ngày mai) =========
df["Target_Close"] = df["Close"].shift(-1)

# ========= 5. Remove nan/inf from feature engineering =========
df = df.replace([np.inf, -np.inf], np.nan)
df = df.dropna()

# ========= 6. SCALE FEATURES =========
features_to_scale = [
    'Open', 'High', 'Low', 'Volume',
    'Return',
    'Close_lag1', 'Close_lag2', 'Close_lag3',
    'Volume_lag1',
    'MA5', 'MA10', 'MA20',
    'STD5', 'STD10',
    'TR', 'ATR14'
]

scaler = MinMaxScaler()
df[features_to_scale] = scaler.fit_transform(df[features_to_scale])

# Không scale: DayOfWeek, Date, Target_Close

# ========= 7. Save Cleaned + Engineered Data =========
output_folder = "clean_data_set"
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, "cleaned_stock_data.csv")

df.to_csv(output_path, index=False)
print(f"✅ Cleaned + Feature Engineered dataset saved to: {output_path}")
