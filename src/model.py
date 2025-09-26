from sktime.forecasting.trend import PolynomialTrendForecaster
from sktime.transformations.series.detrend import Detrender, Deseasonalizer
from sktime.forecasting.compose import TransformedTargetForecaster
from sktime.forecasting.arima import ARIMA
import numpy as np
import pandas as pd

def forecast(train, test):
    if len (train) < 2 * 24 * 7:
        sp = len(train) // 2
    else:
        sp = 168  # 24 hours * 7 days
    
    forecaster = TransformedTargetForecaster(
        [
            ("deseasonalize", Deseasonalizer(model="additive", sp=sp)),
            ("detrend", Detrender(forecaster=PolynomialTrendForecaster(degree=1))),
            ("forecast", ARIMA()),
        ]
    )

    fh = np.arange(1, test+1)

    forecaster.fit(train)
    pred = forecaster.predict(fh)

    return pred.round()