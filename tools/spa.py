from langchain_core.tools import tool
import requests
from typing import List

from config import Config
from model import SpaModel
from utils import add_structured_message
from utils.utils_database import database
from flask_socketio import emit
from flask import request

API_HEADERS = Config.API_HEADERS
HOTEL_API_URL = Config.HOTEL_API_URL


@tool
def get_spas():
    """list all available spas arround the hotel"""
    return requests.get(HOTEL_API_URL+"/api/spas/", headers=API_HEADERS).text


@tool
def display_spa_data(
        spa: SpaModel
):
    """When the user ask details about a spa and there is only one spa to display or if the information about a spa must be displayed, always respond using this tool"""
    session = database.sessions.find_one({"sid": request.sid})
    print(session["token"])
    add_structured_message("spa_details", spa)
    emit('set_mood', "spa")

    return "__END__"



@tool
def display_spa_list(
        spas: List[SpaModel]
):
    """When the user ask about spas and there is a list to display or if the information about a list of spas must be displayed, always respond using this tool"""
    session = database.sessions.find_one({"sid": request.sid})
    print(session["token"])
    add_structured_message("spa_list", spas)
    emit('set_mood', "spa")
    return "__END__"
