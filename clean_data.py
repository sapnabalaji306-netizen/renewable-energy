import pandas as pd
import numpy as np
import os

def load_kaggle_generation(gen_path):
    df = pd.read_csv(gen_path, parse_dates=["DATE_TIME"], dayfirst=True)  # DD-MM-YYYY format
    df = df.groupby("DATE_TIME").agg({"DC_POWER": "sum", "AC_POWER": "sum"}).reset_index()
    df = df.rename(columns={"DATE_TIME": "timestamp", "AC_POWER": "solar_output_kw"})
    return df[["timestamp", "solar_output_kw"]]

def load_kaggle_weather(weather_path):
    df = pd.read_csv(weather_path, parse_dates=["DATE_TIME"])  # YYYY-MM-DD format, no dayfirst needed
    df = df.rename(columns={
        "DATE_TIME": "timestamp",
        "IRRADIATION": "ghi",
        "AMBIENT_TEMPERATURE": "temp_c",
        "MODULE_TEMPERATURE": "module_temp_c",
    })
    return df[["timestamp", "ghi", "temp_c", "module_temp_c"]]

def load_openmeteo(path):
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df

def merge_all(generation_df, kaggle_weather_df, openmeteo_df):
    # Kaggle generation is 15-min resolution, Open-Meteo is hourly -> align to hourly
    generation_df = generation_df.set_index("timestamp").resample("h").mean().reset_index()

    df = generation_df.merge(kaggle_weather_df, on="timestamp", how="left")
    df = df.merge(openmeteo_df, on="timestamp", how="left", suffixes=("", "_om"))

    # fill gaps in on-site sensors using Open-Meteo as backup
    df["ghi"] = df["ghi"].fillna(df["ghi_om"])
    df["temp_c"] = df["temp_c"].fillna(df["temp_c_om"])

    keep = ["timestamp", "solar_output_kw", "ghi", "temp_c", "humidity_pct", "cloud_cover_pct", "wind_speed_ms"]
    df = df[[c for c in keep if c in df.columns]]
    df = df.sort_values("timestamp").reset_index(drop=True)

    fill_cols = [c for c in ["ghi", "temp_c", "humidity_pct", "cloud_cover_pct", "wind_speed_ms"] if c in df.columns]
    df[fill_cols] = df[fill_cols].interpolate().bfill().ffill()
    df = df.dropna(subset=["solar_output_kw"])
    return df

if __name__ == "__main__":
    gen = load_kaggle_generation("data/raw/Plant_1_Generation_Data.csv")
    weather = load_kaggle_weather("data/raw/Plant_1_Weather_Sensor_Data.csv")
    om = load_openmeteo("data/raw/openmeteo_weather_20260816_230353.csv")  # <- check this matches your actual filename

    merged = merge_all(gen, weather, om)

    os.makedirs("data/processed", exist_ok=True)
    merged.to_csv("data/processed/merged_dataset.csv", index=False)
    print(merged.shape)
    print(merged.isna().sum())