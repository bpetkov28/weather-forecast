# Weather Forecast Console Application
## Overview
This is a Python console application that provides current weather data, a 24-hour forecast, and a 7-day forecast. The app updates weather information every 15 minutes and displays the forecast in a user-friendly format using pandas DataFrame. Users can access extended forecasts by typing "yes" twice when prompted.

## Features
- Current Weather: Get real-time weather data, updated every 15 minutes.
- 24-Hour Forecast: View the hourly forecast for the next 24 hours.
- 7-Day Forecast: Check the daily weather forecast for the next 7 days.
- Geolocation Support: Automatically fetch weather data for your current location using geopy.
## Prerequisites
- Python 3.x
- Install the following Python packages:
  - openmeteo_requests (for weather data)
  - geopy (for geolocation)
  - pandas (for displaying data in a table)
Install these libraries using pip:
```bash
pip install openmeteo_requests geopy pandas
```

## How It Works
- Current Weather: The user should start the program and type a city name. The app displays the current weather forecast.
- Extended Forecast: The app will ask the user for 7-day forecast and for 24-hour forecast. If the user types "yes" two times, the app will display both the 7-day and 24-hour forecasts in pandas DataFrame format.
  
## Usage
- Run the application using Python: 

```bash
python weather_app.py
```

- Follow the console prompts to view weather data and request extended forecasts.
