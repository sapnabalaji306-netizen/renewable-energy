# train_model.py
import pandas as pd, numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

df = pd.read_csv(r"C:\Users\Sapna\OneDrive\Documents\solar-wind-forecast\data\processed\merged_dataset.csv", parse_dates=["timestamp"])
df["hour_sin"] = np.sin(2 * np.pi * df["timestamp"].dt.hour / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["timestamp"].dt.hour / 24)

FEATURES = ["ghi", "temp_c", "humidity_pct", "cloud_cover_pct", "wind_speed_ms", "hour_sin", "hour_cos"]
X, y = df[FEATURES], df["solar_output_kw"]

split = int(len(df) * 0.8)  # chronological split -- no shuffling for time series
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

model = RandomForestRegressor(n_estimators=300, max_depth=12, min_samples_leaf=3, n_jobs=-1, random_state=42)
model.fit(X_train, y_train)
preds = np.clip(model.predict(X_test), 0, None)

print("RMSE:", round(mean_squared_error(y_test, preds) ** 0.5, 2))
print("MAE :", round(mean_absolute_error(y_test, preds), 2))
print("R2  :", round(r2_score(y_test, preds), 3))