from src.ai_models.ai_utils.ai_misc import (
    clean_indents,  # Keep this import here for easier imports into other files # NOSONAR
)
from src.ai_models.gpt4o import Gpt4o
from src.ai_models.gpto1 import GptO1
from src.ai_models.metaculus4o import Gpt4oMetaculusProxy


class BaseRateProjectLlm(Gpt4o):
    # NOTE: If need be, you can force an API key here through OpenAI Client class variable
    pass


class BasicCompetitionLlm(Gpt4o):
    pass


class AdvancedCompetitionLlm(GptO1):
    pass
