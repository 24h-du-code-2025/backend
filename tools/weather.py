from typing import Literal

from flask_socketio import emit
from langchain_core.tools import tool

from config import Config
from utils import add_structured_message
from utils.utils_weather import get_weather_info


@tool
def get_weather(city):
    """Use this to predict weather information for a given city"""
    return get_weather_info(Config.OPEN_WEATHER_API_KEY, city)


@tool
def display_weather(
        city: str,
        weather_type: Literal["sunny", "cloudy", "rain", "storm"],
        temperature: str,
        humidity: str,
        wind: str,

):
    """Use this to display the weather to the user"""
    add_structured_message("meteo", {
        "city": city,
        "weather_type": weather_type,
        "temperature": temperature,
        "humidity": humidity,
        "wind": wind,
    })
    emit('set_mood', "meteo")

    return "__END__"
