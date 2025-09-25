from flask import Flask, request, jsonify
from cities import cities
from data_collect import fetch_weather_data, preprocess_data
from model import forecast
import pandas as pd

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Weather Forecasting API is running."

@app.route("/cities", methods=["GET"])
def list_cities():
    return jsonify({"available_cities": list(cities.keys())})
    
@app.route("/forecast", methods=["GET"])
def forecast_data():
    city = request.args.get("city", "Athens")          # default: Athens
    steps = int(request.args.get("steps", 24))         # default: 24h
    
    if city not in cities:
        return jsonify({"error": "City not found"}), 400
    
    lat, lon = cities[city]
    df = fetch_weather_data(lat, lon)
    df = preprocess_data(df)
    features = ["temperature_2m", "relative_humidity_2m", "wind_speed_10m", "rain"]
    
    # dictionary to hold forecasts for each feature
    forecasts = {}
    for feature in features:
        preds = forecast(df[feature], steps)
        forecasts[feature] = preds.tolist()

    start_time = df.iloc[-1].date + pd.Timedelta(hours=1)
    timestamps = pd.date_range(start=start_time, periods=steps, freq="H")
    
    return jsonify({
        "city": city,
        "forecast_steps": steps,
        "timestamps": timestamps.strftime("%Y-%m-%d %H:%M:%S").tolist(),
        "predictions": forecasts,
    })