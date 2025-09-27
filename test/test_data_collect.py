import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.data_collect import fetch_weather_data, preprocess_data


class TestDataCollect(unittest.TestCase):

    @patch("src.data_collect.openmeteo.weather_api")
    def test_fetch_weather_data(self, mock_weather_api):
        # --- Setup fake hourly object ---
        fake_hourly = MagicMock()
        fake_hourly.Time.return_value = 0  # epoch
        fake_hourly.TimeEnd.return_value = 3600 * 3  # 3 hours later
        fake_hourly.Interval.return_value = 3600  # 1-hour interval

        # Fake Variables
        fake_var_temp = MagicMock()
        fake_var_temp.ValuesAsNumpy.return_value = [20, 21, 22]
        fake_var_hum = MagicMock()
        fake_var_hum.ValuesAsNumpy.return_value = [60, 61, 62]
        fake_var_wind = MagicMock()
        fake_var_wind.ValuesAsNumpy.return_value = [3.0, 3.2, 3.1]
        fake_var_rain = MagicMock()
        fake_var_rain.ValuesAsNumpy.return_value = [0.0, 0.1, 0.0]

        fake_hourly.Variables.side_effect = [
            fake_var_temp, fake_var_hum, fake_var_wind, fake_var_rain
        ]

        # --- Setup fake response ---
        fake_response = MagicMock()
        fake_response.Hourly.return_value = fake_hourly
        mock_weather_api.return_value = [fake_response]

        # --- Call function ---
        df = fetch_weather_data(10, 20, days=1)

        # --- Assertions ---
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 3)
        self.assertListEqual(
            list(df.columns),
            ["date", "temperature_2m", "relative_humidity_2m", "wind_speed_10m", "rain"]
        )
        self.assertTrue((df["temperature_2m"] == [20, 21, 22]).all())
        self.assertTrue((df["relative_humidity_2m"] == [60, 61, 62]).all())
        self.assertTrue((df["wind_speed_10m"] == [3.0, 3.2, 3.1]).all())
        self.assertTrue((df["rain"] == [0.0, 0.1, 0.0]).all())
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(df["date"]))

    def test_preprocess_data(self):
        # Create a sample dataframe
        data = {
            "date": pd.date_range(start="2023-01-01", periods=5, freq="H"),
            "temperature_2m": [20, 21, 22, 23, 24],
            "relative_humidity_2m": [60, 61, 62, 63, 64],
            "wind_speed_10m": [3.0, 3.2, 3.1, 3.3, 3.4],
            "rain": [0.0, 0.1, 0.0, 0.2, 0.0],
        }
        df = pd.DataFrame(data)

        # Add future dates
        future_dates = pd.date_range(start="2023-01-01 05:00", periods=5, freq="H")
        future_data = {
            "date": future_dates,
            "temperature_2m": [25, 26, 27, 28, 29],
            "relative_humidity_2m": [65, 66, 67, 68, 69],
            "wind_speed_10m": [3.5, 3.6, 3.7, 3.8, 3.9],
            "rain": [0.1, 0.0, 0.2, 0.1, 0.0],
        }
        df_future = pd.DataFrame(future_data)
        df = pd.concat([df, df_future], ignore_index=True)

        # Preprocess the data
        df_processed = preprocess_data(df)

        # Assertions
        self.assertIsInstance(df_processed, pd.DataFrame)
        self.assertTrue((df_processed['date'] <= str(pd.Timestamp.now())).all())
        self.assertTrue(all(col in df_processed.columns for col in data.keys()))

if __name__ == "__main__":
    unittest.main()