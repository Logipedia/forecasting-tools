from forecasting_tools.ai_models.gpt4o import Gpt4o
from forecasting_tools.ai_models.gpt4ovision import (
    Gpt4oVision,
    Gpt4VisionInput,
)
from forecasting_tools.ai_models.gpto1 import GptO1


class BasicLlm(Gpt4o):
    # NOTE: If need be, you can force an API key here through OpenAI Client class variable
    pass


class AdvancedLlm(GptO1):
    pass


class VisionLlm(Gpt4oVision):
    pass


class VisionData(Gpt4VisionInput):
    pass