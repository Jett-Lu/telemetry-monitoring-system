from api.openweather_client import OpenWeatherClient

class WeatherService:
    def __init__(self):
        self.client = OpenWeatherClient()

    def get_weather(self, city="Toronto"):
        return self.client.fetch_weather(city)
