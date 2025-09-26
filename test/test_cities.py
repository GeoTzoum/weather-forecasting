import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np

from src.cities import cities

class TestCities(unittest.TestCase):
    def test_cities_is_dict(self):
        assert isinstance(cities, dict)

    def test_city_names_are_strings(self):
        for city in cities:
            assert isinstance(city, str)

    def test_coordinates_are_tuples_of_floats(self):
        for coords in cities.values():
            assert isinstance(coords, tuple)
            assert len(coords) == 2
            assert all(isinstance(x, float) for x in coords)

    def test_no_duplicate_cities(self):
        assert len(cities) == len(set(cities.keys()))

    def test_latitude_longitude_ranges(self):
        for lat, lon in cities.values():
            assert -90.0 <= lat <= 90.0
            assert -180.0 <= lon <= 180.0
