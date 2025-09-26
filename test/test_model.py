import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np

from src.model import forecast

class TestModel(unittest.TestCase):
        
    def test_forecast_basic_output_length(self):
        # Generate a simple seasonal + trend time series
        periods = 200
        idx = pd.date_range("2023-01-01", periods=periods, freq="H")
        y = pd.Series(10 + 0.1 * np.arange(periods) + 5 * np.sin(2 * np.pi * np.arange(periods) / 24), index=idx)
        test_horizon = 10

        preds = forecast(y, test_horizon)
        assert len(preds) == test_horizon

    def test_forecast_returns_series(self):
        periods = 100
        idx = pd.date_range("2023-01-01", periods=periods, freq="H")
        y = pd.Series(np.random.randn(periods), index=idx)
        preds = forecast(y, 5)
        assert isinstance(preds, pd.Series)

    def test_forecast_works_with_short_series(self):
        periods = 20
        idx = pd.date_range("2023-01-01", periods=periods, freq="H")
        y = pd.Series(np.random.randn(periods), index=idx)
        preds = forecast(y, 3)
        assert len(preds) == 3

    def test_forecast_output_is_rounded(self):
        periods = 50
        idx = pd.date_range("2023-01-01", periods=periods, freq="H")
        y = pd.Series(np.linspace(0, 10, periods), index=idx)
        preds = forecast(y, 4)
        # All values should be integers after rounding
        assert np.all(preds == preds.round())

    def test_forecast_with_non_datetime_index(self):
        y = pd.Series(np.random.randn(30))
        preds = forecast(y, 5)
        assert len(preds) == 5