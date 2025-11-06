import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os
import numpy as np
# Load dataset
df = pd.read_csv("./dataset/A.csv")

# 1. Convert Date to datetime
df['Date'] = pd.to_datetime(df['Date'])

# 2. Remove duplicates
df = df.drop_duplicates(subset=['Date'])

# 3. Handle missing values
df = df.interpolate(method='linear') # nội suy tuyến tính theo thời gian

# 4. Remove outliers using IQR
Q1 = df['Close'].quantile(0.25)
Q3 = df['Close'].quantile(0.75)
IQR = Q3 - Q1
df = df[~((df['Close'] < (Q1 - 1.5 * IQR)) | (df['Close'] > (Q3 + 1.5 * IQR)))]

# 5. Remove invalid data
df = df[
    (df['Open'] > 0) &
    (df['High'] > 0) &
    (df['Low'] > 0) &
    (df['Close'] > 0) &
    (df['Volume'] > 0) &
    (df['High'] >= df['Low'])
]

# 6. Min-Max Normalize (exclude target 'Close')
scaler = MinMaxScaler()
df[['Open', 'High', 'Low', 'Volume']] = scaler.fit_transform(
    df[['Open', 'High', 'Low', 'Volume']]
)

# 7. Feature Engineering: add daily return
df['Return'] = df['Close'].pct_change() # tính biến thiên cột close của ngày hôm trước so với ngày hôm nay
df = df.replace([np.inf, -np.inf], np.nan)
df = df.dropna()
df = df.drop(columns=['Adj Close'])  # remove correlated column

# Save result
output_folder = "clean_data_set"
os.makedirs(output_folder, exist_ok=True)
output_path = os.path.join(output_folder, "cleaned_stock_data.csv")
df.to_csv(output_path, index=False)

print(f"✅ Cleaned dataset saved to: {output_path}")

