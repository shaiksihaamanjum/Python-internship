"""
Weather Forecast App - Project 3
Uses OpenWeatherMap API to fetch live weather data.
Concepts: API integration, requests module, JSON parsing, CLI
"""

import requests
import sys
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIG — paste your free API key here
#  Get one at: https://openweathermap.org/api
# ─────────────────────────────────────────────
API_KEY = "db5874d61b6b5d588514831d2c3e8daa"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city: str, units: str = "metric") -> dict:
    """
    Fetch current weather for a city from OpenWeatherMap.
    
    Args:
        city   : Name of the city (e.g. "London")
        units  : "metric" (°C) | "imperial" (°F) | "standard" (K)
    
    Returns:
        Parsed JSON dict from the API
    
    Raises:
        ValueError  : City not found (404)
        RuntimeError: Network / API errors
    """
    params = {
        "q":     city,
        "appid": API_KEY,
        "units": units,
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No internet connection. Please check your network.")
    except requests.exceptions.Timeout:
        raise RuntimeError("Request timed out. Try again later.")

    if response.status_code == 401:
        raise RuntimeError("Invalid API key. Get a free key at openweathermap.org")
    if response.status_code == 404:
        raise ValueError(f"City '{city}' not found. Check the spelling and try again.")
    if response.status_code != 200:
        raise RuntimeError(f"API error {response.status_code}: {response.text}")

    return response.json()   # ← JSON parsing


def parse_weather(data: dict, units: str = "metric") -> dict:
    """Extract the fields we care about from the raw JSON."""
    unit_symbol = {"metric": "°C", "imperial": "°F", "standard": "K"}[units]

    return {
        "city":        data["name"],
        "country":     data["sys"]["country"],
        "condition":   data["weather"][0]["description"].title(),
        "temp":        data["main"]["temp"],
        "feels_like":  data["main"]["feels_like"],
        "temp_min":    data["main"]["temp_min"],
        "temp_max":    data["main"]["temp_max"],
        "humidity":    data["main"]["humidity"],
        "pressure":    data["main"]["pressure"],
        "wind_speed":  data["wind"]["speed"],
        "wind_dir":    data["wind"].get("deg", "N/A"),
        "visibility":  data.get("visibility", "N/A"),
        "unit":        unit_symbol,
        "timestamp":   datetime.utcfromtimestamp(data["dt"]).strftime("%Y-%m-%d %H:%M UTC"),
    }


def display_weather(w: dict) -> None:
    """Pretty-print the weather report to the terminal."""
    border = "─" * 45
    print(f"\n┌{border}")
    print(f"│{'  🌤  WEATHER FORECAST':^45}")
    print(f"├{border}")
    print(f"│  📍  {w['city']}, {w['country']:<37}")
    print(f"│  🕐  {w['timestamp']:<39}")
    print(f"├{border}")
    print(f"│  ☁️   Condition  : {w['condition']:<25}")
    print(f"│  🌡️   Temperature: {w['temp']}{w['unit']} (feels {w['feels_like']}{w['unit']}){'':<6}")
    print(f"│  🔺  High / Low : {w['temp_max']}{w['unit']} / {w['temp_min']}{w['unit']:<19}")
    print(f"│  💧  Humidity   : {w['humidity']}%{'':<26}")
    print(f"│  🌬️   Wind Speed : {w['wind_speed']} m/s @ {w['wind_dir']}°{'':<14}")
    print(f"│  👁️   Visibility : {str(w['visibility']) + ' m':<26}")
    print(f"│  🔵  Pressure   : {w['pressure']} hPa{'':<23}")
    print(f"└{border}\n")


def main():
    """Entry point — supports CLI arguments or interactive prompt."""
    # ── accept city from command line: python weather_app.py "New York"
    if len(sys.argv) >= 2:
        city  = " ".join(sys.argv[1:])
        units = "metric"
    else:
        city  = input("Enter city name: ").strip()
        unit_choice = input("Units? (1) Celsius  (2) Fahrenheit  [default: 1]: ").strip()
        units = "imperial" if unit_choice == "2" else "metric"

    if not city:
        print("❌  No city provided. Exiting.")
        sys.exit(1)

    print(f"\n⏳  Fetching weather for '{city}'…")

    try:
        raw_data     = fetch_weather(city, units)      # API call
        weather_info = parse_weather(raw_data, units)  # JSON parsing
        display_weather(weather_info)                  # output
    except ValueError as e:
        print(f"❌  {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"⚠️   {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()