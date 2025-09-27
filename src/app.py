from flask import Flask, request, jsonify
from src.cities import cities
from src.data_collect import fetch_weather_data, preprocess_data
from src.model import forecast
import pandas as pd

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "Weather Forecasting API is running."

@app.route("/cities", methods=["GET"])
def list_cities():
    return jsonify({"available_cities": list(cities.keys())})
    
@app.route("/forecast", methods=["GET"])
def forecast_data():
    city = request.args.get("city", "Athens")          # default: Athens
    try:
        steps = int(request.args.get("steps", 24))         # default: 24h
    except ValueError:
        return jsonify({"error": "Invalid steps parameter, must be an integer"}), 400
    
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

if __name__ == "__main__":
    app.run(debug=True)