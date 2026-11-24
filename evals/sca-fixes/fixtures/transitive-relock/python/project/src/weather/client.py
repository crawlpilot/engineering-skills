"""Weather client."""

import requests

BASE_URL = "https://api.example.com"


def forecast_url(city: str) -> str:
    return f"{BASE_URL}/forecast/{requests.utils.quote(city)}"


def fetch_forecast(city: str, session: requests.Session | None = None) -> dict:
    response = (session or requests.Session()).get(forecast_url(city), timeout=10)
    response.raise_for_status()
    return response.json()
