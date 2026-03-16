import os
import requests

DEFAULT_OPENWEATHER_API_KEY = "5747e1b6e4add1a3316b577fca2b7d88"

class OpenWeatherClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY", DEFAULT_OPENWEATHER_API_KEY)

    def fetch_weather(self, city="Toronto"):
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={self.api_key}&units=metric"
        )

        response = requests.get(url, timeout=15)
        data = response.json()

        if response.status_code == 200:
            return {
                "city": data.get("name"),
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
            }

        return {
            "error": True,
            "status_code": response.status_code,
            "response": data,
        }
