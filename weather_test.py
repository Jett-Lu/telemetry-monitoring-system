from api.openweather_client import OpenWeatherClient

client = OpenWeatherClient()
result = client.fetch_weather("Toronto")

if result.get("error"):
    print("API request failed:", result)
else:
    print("Temperature:", result["temperature"])
    print("Humidity:", result["humidity"])
    print("Description:", result["description"])
