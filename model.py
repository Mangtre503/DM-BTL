import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor  
import math

# ===============================
# 1️⃣ Load Cleaned Dataset
# ===============================
df = pd.read_csv("clean_data_set/cleaned_stock_data.csv")

# Drop NaN caused by pct_change()
df = df.dropna()

# Chọn features và target
X = df[['Open', 'High', 'Low', 'Volume', 'Return']]
y = df['Close']

# Chia train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)


# Define Models

models = {
    "LinearRegression": LinearRegression(),
    "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
    "SVR": SVR(kernel='rbf'),
    "DecisionTree": DecisionTreeRegressor(random_state=42) 
}

# ===============================
# 3️⃣ Create result folder
# ===============================
os.makedirs("result", exist_ok=True)

# ===============================
# 4️⃣ Train & Evaluate Models
# ===============================
results = []

for name, model in models.items():
    print(f"🔹 Training {name}...")
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # --- Metrics ---
    mae = mean_absolute_error(y_test, y_pred)
    nmae = mae / np.mean(np.abs(y_test))  # normalized MAE
    rmse = math.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)

    # --- Save predictions ---
    pred_df = pd.DataFrame({
        'Date': df.iloc[y_test.index]['Date'],
        'Actual': y_test,
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

# ===============================
# 5️⃣ Save Evaluation Table
# ===============================
eval_df = pd.DataFrame(results)
eval_df.to_csv("result/evaluate_model.csv", index=False)

print("✅ All model results saved in folder: result/")
print(eval_df)
