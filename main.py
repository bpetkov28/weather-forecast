import openmeteo_requests

import requests_cache
import pandas as pd
from retry_requests import retry
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
from datetime import datetime


def get_lat_long(city_name, retries=3):
    geolocator = Nominatim(user_agent="your_app_name")
    try:
        location = geolocator.geocode(city_name, timeout=2)
        if location:
            return (location.latitude, location.longitude)
        else:
            return None
    except GeocoderTimedOut:
        if retries > 0:
            time.sleep(1)  # wait for a second before retrying
            return get_lat_long(city_name, retries - 1)
        else:
            return None

is_valid = False

while not is_valid:
    city = str(input("Please enter a valid city name "))
    coordinates = get_lat_long(city)

    if coordinates != None:
        is_valid = True

        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Make sure all required weather variables are listed here
        # The order of variables in hourly or daily is important to assign them correctly below
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
	        "latitude": coordinates[0],
	        "longitude": coordinates[1],
            "current": ["temperature_2m", "precipitation", "relative_humidity_2m", "weather_code", "wind_speed_10m"],
            "hourly": ["temperature_2m", "weather_code", "cloud_cover", "wind_speed_10m", "uv_index"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "weather_code",
              "uv_index_max", "precipitation_probability_max"],
            "timezone": "auto",
            "forecast_hours": 24
        }
        responses = openmeteo.weather_api(url, params=params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation {response.Elevation()} m asl")
        print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")

        # Current values. The order of variables needs to be the same as requested.
        current = response.Current()
        current_temperature_2m = current.Variables(0).Value()
        current_relative_humidity_2m = current.Variables(1).Value()
        current_weather_code = current.Variables(2).Value()
        current_wind_speed_10m = current.Variables(3).Value()

        current_timestamp = current.Time()
        date_object = datetime.fromtimestamp(current_timestamp)

        print(f"Last update {date_object}")
        print(f"Temperature {round(current_temperature_2m)}°C")
        print(f"Humidity {round(current_relative_humidity_2m)}%")
        print(f"Weather code {current_weather_code}")
        print(f"Wind speed {round(current_wind_speed_10m,2)}km/h")

        user_request = input("Do you want to see the forecast by hours? ")
        user_request2 = input("Do you want to see the forecast for the next 7 days? ")

        if user_request.lower() == 'yes':
        # Process hourly data. The order of variables needs to be the same as requested.
            hourly = response.Hourly()
            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
            hourly_weather_code = hourly.Variables(1).ValuesAsNumpy()
            hourly_cloud_cover = hourly.Variables(2).ValuesAsNumpy()
            hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()
            hourly_uv_index = hourly.Variables(4).ValuesAsNumpy()


            hourly_data = {"date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )}


            hourly_data["temperature"] = hourly_temperature_2m
            hourly_data["weather_code"] = hourly_weather_code
            hourly_data["cloud_cover"] = hourly_cloud_cover
            hourly_data["wind_speed"] = hourly_wind_speed_10m
            hourly_data["uv_index"] = hourly_uv_index

            hourly_dataframe = pd.DataFrame(data=hourly_data)
            print(hourly_dataframe.to_string())

        if user_request2.lower() == 'yes':
            # Process daily data. The order of variables needs to be the same as requested.
            daily = response.Daily()
            daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
            daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
            daily_weather_code = daily.Variables(2).ValuesAsNumpy()
            daily_uv_index_max = daily.Variables(3).ValuesAsNumpy()
            daily_precipitation_probability_max = daily.Variables(4).ValuesAsNumpy()

            daily_data = {"date": pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            )}

            daily_data["temperature_max"] = daily_temperature_2m_max
            daily_data["temperature_min"] = daily_temperature_2m_min
            daily_data["weather_code"] = daily_weather_code
            daily_data["uv_index_max"] = daily_uv_index_max
            daily_data["precipitation_probability_max"] = daily_precipitation_probability_max

            daily_dataframe = pd.DataFrame(data=daily_data)
            print(daily_dataframe.to_string())
