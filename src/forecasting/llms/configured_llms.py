from src.ai_models.gpt4o import Gpt4o
from src.ai_models.gpto1 import GptO1


class BaseRateProjectLlm(Gpt4o):
    # NOTE: If need be, you can force an API key here through OpenAI Client class variable
    pass


class BasicCompetitionLlm(Gpt4o):
    pass


class AdvancedCompetitionLlm(GptO1):
    pass
