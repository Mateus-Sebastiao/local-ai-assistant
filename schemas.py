from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    user_prompt: str = Field(..., min_length=1, description="The message from the user")
