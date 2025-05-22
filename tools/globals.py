from typing import List, Dict, Optional, Literal
from langchain_core.tools import tool
from flask_socketio import emit
from model.intent import IntentModel
from utils import add_structured_message


@tool
def send_intents(intents: List[IntentModel]):
    """Generate personalized prompt suggestions when users don't provide a specific question. This tool proactively offers a list of conversation starters, helping overcome the blank page problem and encouraging meaningful interactions."""
    print("send_intents")
    add_structured_message("propose_intents", [intent.dict() for intent in intents])
    return "__END__"

@tool
def stop_session():
    """Session Termination Tool: Ends the active session when all user requests have been successfully addressed, or when the user explicitly signals a desire to conclude the interaction through farewell messages, explicit end commands, or natural conversation closing signals. This tool ensures proper session closure, saving state when appropriate, and delivering a courteous final response to maintain a positive user experience."""
    emit('end_session')
