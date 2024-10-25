from pydantic import BaseModel
from typing import Any


class ModelResponse(BaseModel):
    data: Any


class TextTokenResponse(ModelResponse):
    data: str
    prompt_tokens_used: int
    completion_tokens_used: int
    total_tokens_used: int
    model: str


class TextTokenCostResponse(TextTokenResponse):
    cost: float
