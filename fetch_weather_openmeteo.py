# fetch_weather_openmeteo.py
import requests
import pandas as pd
import os
from datetime import datetime

def fetch_open_meteo(lat, lon, start_date, end_date, out_dir="data/raw"):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,relative_humidity_2m,cloud_cover,"
                  "wind_speed_10m,shortwave_radiation",
        "timezone": "Asia/Kolkata",
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()["hourly"]

    df = pd.DataFrame(data)
    df = df.rename(columns={
        "time": "timestamp",
        "temperature_2m": "temp_c",
        "relative_humidity_2m": "humidity_pct",
        "cloud_cover": "cloud_cover_pct",
        "wind_speed_10m": "wind_speed_ms",
        "shortwave_radiation": "ghi",
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # make sure the output folder exists, no matter where you run this from
    os.makedirs(out_dir, exist_ok=True)

    # tag the filename with when THIS fetch was run, so re-runs don't overwrite old data
    run_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(out_dir, f"openmeteo_weather_{run_tag}.csv")

    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows to {out_path}")
    print(f"Data covers: {df['timestamp'].min()} to {df['timestamp'].max()}")
    return df, out_path

if __name__ == "__main__":
    fetch_open_meteo(
        lat=15.4,
        lon=77.0,
        start_date="2020-05-15",
        end_date="2020-06-17",
    )