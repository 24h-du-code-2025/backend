from langchain_core.tools import tool
from typing import List


from model import EventModel
from utils import add_structured_message, extract_events
from flask_socketio import emit


@tool
def display_events(
        events: List[EventModel]
):
    """When the user ask details about upcoming events or news in Le Mans, always respond using this tool"""
    print("show_events")
    add_structured_message("events_list", events)
    emit('set_mood', "tourism")
    return "__END__"



@tool
def get_events():
    """List upcoming events and news in Le Mans"""
    print("get_events")
    return extract_events()
