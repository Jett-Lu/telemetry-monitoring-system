import requests

API_KEY = "5747e1b6e4add1a3316b577fca2b7d88"
city = "Toronto"

url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

response = requests.get(url, timeout=15)
print("Status:", response.status_code)

data = response.json()
print(data)

if response.status_code == 200 and "main" in data:
    print("Temperature:", data["main"]["temp"])
    print("Humidity:", data["main"]["humidity"])
else:
    print("API request failed.")