import unittest
from unittest.mock import patch, MagicMock
from src.app import app
import pandas as pd
import json

class AppTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Weather Forecasting API is running.", response.data)

    @patch("src.app.cities", new={"Athens": (37.98, 23.72), "London": (51.51, -0.13)})
    def test_list_cities(self):
        response = self.client.get("/cities")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("available_cities", data)
        self.assertSetEqual(set(data["available_cities"]), {"Athens", "London"})

    @patch("src.app.cities", {"Athens": (37.98, 23.72)})
    def test_forecast_city_not_found(self):
        response = self.client.get("/forecast?city=UnknownCity")
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["error"], "City not found")

    @patch("src.app.cities", {"Athens": (37.98, 23.72)})
    @patch("src.app.fetch_weather_data")
    @patch("src.app.preprocess_data")
    @patch("src.app.forecast")
    def test_forecast_success(self, mock_forecast, mock_preprocess, mock_fetch):
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=10, freq="H"),
            "temperature_2m": range(10),
            "relative_humidity_2m": range(10),
            "wind_speed_10m": range(10),
            "rain": range(10)
        })
        mock_fetch.return_value = df
        mock_preprocess.return_value = df
        mock_forecast.side_effect = lambda series, steps: pd.Series([1.0]*steps)

        response = self.client.get("/forecast?city=Athens&steps=3")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["city"], "Athens")
        self.assertEqual(data["forecast_steps"], 3)
        self.assertEqual(len(data["timestamps"]), 3)
        self.assertSetEqual(set(data["predictions"].keys()), {
            "temperature_2m", "relative_humidity_2m", "wind_speed_10m", "rain"
        })
        for preds in data["predictions"].values():
            self.assertEqual(preds, [1.0, 1.0, 1.0])

    @patch("src.app.cities", {"Athens": (37.98, 23.72)})
    @patch("src.app.fetch_weather_data")
    @patch("src.app.preprocess_data")
    @patch("src.app.forecast")
    def test_forecast_default_steps(self, mock_forecast, mock_preprocess, mock_fetch):
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=10, freq="H"),
            "temperature_2m": range(10),
            "relative_humidity_2m": range(10),
            "wind_speed_10m": range(10),
            "rain": range(10)
        })
        mock_fetch.return_value = df
        mock_preprocess.return_value = df
        mock_forecast.side_effect = lambda series, steps: pd.Series([2.0]*steps)

        response = self.client.get("/forecast?city=Athens")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["forecast_steps"], 24)
        self.assertEqual(len(data["timestamps"]), 24)
        for preds in data["predictions"].values():
            self.assertEqual(preds, [2.0]*24)

    @patch("src.app.cities", {"Athens": (37.98, 23.72)})
    @patch("src.app.fetch_weather_data")
    @patch("src.app.preprocess_data")
    @patch("src.app.forecast")
    def test_forecast_invalid_steps(self, mock_forecast, mock_preprocess, mock_fetch):
        # steps is not an integer
        response = self.client.get("/forecast?city=Athens&steps=abc")
        self.assertEqual(response.status_code, 400)  # ValueError, handled by Flask as 500

    @patch("src.app.cities", {"Athens": (37.98, 23.72)})
    @patch("src.app.fetch_weather_data")
    @patch("src.app.preprocess_data")
    @patch("src.app.forecast")
    def test_forecast_missing_city_param(self, mock_forecast, mock_preprocess, mock_fetch):
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=10, freq="H"),
            "temperature_2m": range(10),
            "relative_humidity_2m": range(10),
            "wind_speed_10m": range(10),
            "rain": range(10)
        })
        mock_fetch.return_value = df
        mock_preprocess.return_value = df
        mock_forecast.side_effect = lambda series, steps: pd.Series([3.0]*steps)

        response = self.client.get("/forecast")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["city"], "Athens")
        self.assertEqual(data["forecast_steps"], 24)
        for preds in data["predictions"].values():
            self.assertEqual(preds, [3.0]*24)

if __name__ == "__main__":
    unittest.main()