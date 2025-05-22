from pydantic import BaseModel, Field

class IntentModel(BaseModel):
    title: str = Field(description="Label of the action to display to the user")
    prompt: str = Field(description="prompt that will be sent to the agent if the user choose this intent")