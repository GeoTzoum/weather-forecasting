import os
import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests

# ---------- Setup API Client ----------
cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# ---------- Weather Fetch Function ----------
def fetch_weather_data(lat: float, lon: float, days: int = 60) -> pd.DataFrame:
    """Fetch past weather + forecast data for a city."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "rain"],
        "past_days": days,
        "forecast_days": 1,
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        ),
        "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
        "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
        "wind_speed_10m": hourly.Variables(2).ValuesAsNumpy(),
        "rain": hourly.Variables(3).ValuesAsNumpy(),
    }

    return pd.DataFrame(hourly_data)

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'])

    # Find the last date (without time)
    last_day = df['date'].dt.date.max()

    # Filter out rows from the last day
    df = df[df['date'].dt.date != last_day]
    return df