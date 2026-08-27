# suitability_checker.py
import requests
import pandas as pd

def fetch_region_weather(center_lat, center_lon, buffer=0.9, start_date="2020-05-15", end_date="2020-06-17"):
    """
    Fetch weather for a square region: center ± buffer degrees in each direction.
    Open-Meteo doesn't support spatial averaging directly, but we can fetch the center point
    and use it as representative for the region.
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": center_lat,
        "longitude": center_lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "shortwave_radiation,temperature_2m,wind_speed_10m",
        "timezone": "Asia/Kolkata",
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()["hourly"]
    
    df = pd.DataFrame(data)
    df = df.rename(columns={
        "time": "timestamp",
        "shortwave_radiation": "ghi",
        "temperature_2m": "temp_c",
        "wind_speed_10m": "wind_speed_ms",
    })
    return df

def assess_suitability(center_lat, center_lon, buffer=0.9):
    """
    Check if a region is suitable for solar/wind farms.
    Returns suitability score and recommendation.
    """
    print(f"\n=== Assessing region: {center_lat}°N, {center_lon}°E (±{buffer}° square) ===\n")
    
    df = fetch_region_weather(center_lat, center_lon, buffer)
    
    # Calculate metrics (exclude nighttime zeros for cleaner averages)
    ghi_avg = df[df['ghi'] > 0]['ghi'].mean()
    ghi_max = df['ghi'].max()
    wind_avg = df['wind_speed_ms'].mean()
    wind_max = df['wind_speed_ms'].max()
    temp_avg = df['temp_c'].mean()
    
    print(f"Solar Irradiance (GHI):")
    print(f"  Average (daytime only): {ghi_avg:.1f} W/m²")
    print(f"  Peak:                   {ghi_max:.1f} W/m²")
    print(f"\nWind Speed:")
    print(f"  Average: {wind_avg:.2f} m/s")
    print(f"  Max:     {wind_max:.2f} m/s")
    print(f"\nTemperature: {temp_avg:.1f}°C\n")
    
    # Thresholds (adjust based on your region's standards)
    solar_good = ghi_avg >= 400        # daytime avg should be > 400 W/m²
    wind_good = wind_avg >= 4.0        # minimum 4 m/s average
    
    print("--- SUITABILITY ASSESSMENT ---")
    
    if solar_good and wind_good:
        print("✅ SUITABLE for hybrid solar+wind farm")
        score = "HIGH"
    elif solar_good and not wind_good:
        print("✅ SUITABLE for SOLAR farm (weak wind)")
        score = "MEDIUM"
    elif wind_good and not solar_good:
        print("✅ SUITABLE for WIND farm (moderate solar)")
        score = "MEDIUM"
    else:
        print("❌ NOT SUITABLE (weak solar and wind)")
        score = "LOW"
    
    print(f"\nSuitability Score: {score}")
    print(f"Solar Potential: {'✓' if solar_good else '✗'} (target ≥400 W/m²)")
    print(f"Wind Potential:  {'✓' if wind_good else '✗'} (target ≥4.0 m/s)")
    
    return score

if __name__ == "__main__":
    # Example: user provides center point
    center_lat = float(input("Enter latitude (e.g., 15.4): "))
    center_lon = float(input("Enter longitude (e.g., 77.0): "))
    buffer = 0.9  # fixed square radius
    
    assess_suitability(center_lat, center_lon, buffer)