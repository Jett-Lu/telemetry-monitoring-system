
import requests

API_KEY = "5747e1b6e4add1a3316b577fca2b7d88"

url = f"https://api.openweathermap.org/data/2.5/weather?q=Toronto&appid={API_KEY}&units=metric"

response = requests.get(url)
data = response.json()

print("Status:", response.status_code)
print(data)

if response.status_code == 200:
    print("Temperature:", data["main"]["temp"])
    print("Humidity:", data["main"]["humidity"])
