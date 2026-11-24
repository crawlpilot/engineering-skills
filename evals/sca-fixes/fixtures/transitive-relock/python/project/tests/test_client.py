from weather.client import forecast_url


def test_quotes_the_city():
    assert forecast_url("São Paulo") == "https://api.example.com/forecast/S%C3%A3o%20Paulo"
