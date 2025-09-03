import datetime as dt
import requests_cache
from retry_requests import retry
import openmeteo_requests
from typing import List, Dict
from .logging_config import get_logger

logger = get_logger(__name__)

class WeatherAPIError(Exception):
    """Raised when the weather API call fails."""


# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


def fetch_hourly_weather(
    lat: float, lon: float, start_date: dt.date, end_date: dt.date
) -> List[Dict]:
    """
    Fetch hourly weather data from Open-Meteo.

    Args:
        lat: Latitude
        lon: Longitude
        start_date: Start date (inclusive)
        end_date: End date (inclusive)

    Returns:
        List of readings where each is:
        {
            "time": datetime,
            "temp_c": float,
            "lat": float,
            "lon": float,
            "source": str
        }

    Raises:
        ValueError: If end_date < start_date
        WeatherAPIError: If API call fails or response malformed
    """
    if end_date < start_date:
        raise ValueError("end_date must be >= start_date")

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "hourly": "temperature_2m",
    }
    logger.info("Fetching weather from %s", url)
    try:
        responses = openmeteo.weather_api(url, params=params)
    except Exception as e:
        logger.error("API request failed: %s", e)
        raise WeatherAPIError("API request failed") from e

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    logger.info(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    logger.info(f"Elevation: {response.Elevation()} m asl")
    logger.info(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    readings = []
    for i, temp in enumerate(hourly_temperature_2m):
        timestamp = dt.datetime.fromtimestamp(hourly.Time() + i * hourly.Interval(), tz=dt.timezone.utc)
        readings.append(
            {
                "time": timestamp,
                "temp_c": float(temp),
                "lat": lat,
                "lon": lon,
                "source": "open-meteo",
            }
        )
    logger.info("Fetched %d readings", len(readings))
    return readings
