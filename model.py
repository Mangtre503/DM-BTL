import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor  
from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
import math


# 1️⃣ Load Cleaned Dataset
df = pd.read_csv("clean_data_set/cleaned_stock_data.csv")


# 2️⃣ Chọn đúng features và target để dự đoán Close ngày mai

feature_columns = [
    'Open', 'High', 'Low', 'Volume',
    'Return',
    'Close_lag1', 'Close_lag2', 'Close_lag3',
    'Volume_lag1',
    'MA5', 'MA10', 'MA20',
    'STD5', 'STD10',
    'ATR14', 'TR',
    'DayOfWeek'
]

X = df[feature_columns]
y = df['Target_Close']     # chính xác: giá Close của ngày mai


# 3️⃣ Chia train/test theo time-series (không shuffle)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, shuffle=False
)


# 4️⃣ Define Models
models = {
    "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
    "SVR": SVR(kernel='rbf'),
    "DecisionTree": DecisionTreeRegressor(random_state=42),
    "XGBoost": XGBRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
}


# 5️⃣ Create result folder
os.makedirs("result", exist_ok=True)


# 6️⃣ Train & Evaluate Models

results = []

for name, model in models.items():
    print(f"🔹 Training {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # --- Metrics ---
    mae = mean_absolute_error(y_test, y_pred)
    nmae = mae / np.mean(np.abs(y_test))
    rmse = math.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    # --- Save predictions ---
    pred_df = pd.DataFrame({
        'Actual': y_test.values,
        'Predicted': y_pred
    })
    pred_df.to_csv(f"result/{name}.csv", index=False)

    # --- Collect evaluation ---
    results.append({
        "Model": name,
        "MAE": mae,
        "NMAE": nmae,
        "RMSE": rmse,
        "R2": r2
    })


# 7️⃣ Save Evaluation Table

eval_df = pd.DataFrame(results)
eval_df.to_csv("result/evaluate_model.csv", index=False)

print("✅ All model results saved in folder: result/")
print(eval_df)
