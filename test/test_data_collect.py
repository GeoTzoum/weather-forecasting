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

    def test_preprocess_data(self):
        # Build DataFrame covering 2 days
        df = pd.DataFrame({
            "date": pd.date_range("2025-01-01 00:00", periods=6, freq="H"),
            "temperature_2m": [20, 21, 22, 23, 24, 25]
        })
        # last 2 rows are day 2025-01-01 05:00, still same date
        # add one from the next day
        df.loc[len(df)] = [pd.Timestamp("2025-01-02 00:00"), 26]

        # Preprocess
        processed = preprocess_data(df)

        # Should drop last day's rows (2025-01-02)
        self.assertTrue(all(processed["date"].dt.date < pd.to_datetime("2025-01-02").date()))
        self.assertEqual(len(processed), len(df) - 1)

if __name__ == "__main__":
    unittest.main()