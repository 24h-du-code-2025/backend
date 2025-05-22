from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from config import Config
from tools import get_tools
from utils import read_file, add_message
from datetime import date
import calendar
from flask_socketio import emit


my_date = date.today()
day = calendar.day_name[my_date.weekday()] + " " +  my_date.strftime('%d') + " " + calendar.month_name[my_date.month] + ", " + my_date.strftime('%Y')

if Config.LLM_MODEL == "CHATGPT":
    model_name = "gpt-4o-mini"
elif Config.LLM_MODEL == "CHATGPT_BLING":
    model_name = "gpt-4o"
else:
    raise ValueError(f"Unrecognized model: {Config.LLM_MODEL}")
model = ChatOpenAI(model=model_name, api_key=Config.OPENAI_API_KEY)


memory = MemorySaver()
sys_prompt = read_file('prompts/system_prompt.txt').replace('|DAY|', day)
graph = create_react_agent(model, tools=get_tools(), checkpointer=memory, prompt=sys_prompt)


def call_agent(user_input: str, session):
    emit('set_mood', "thinking")
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]},
                              {"configurable": {"thread_id": session["_id"]}}):
        for value in event.values():
            if value["messages"][-1].content == '__END__':
                return
            if type(value["messages"][-1]) == AIMessage and value["messages"][-1].content != '':
                emit('set_mood', "base")
                add_message("agent", value["messages"][-1].content)

