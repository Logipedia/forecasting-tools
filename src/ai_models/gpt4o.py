import logging
from typing import Any, Final

from src.ai_models.ai_utils.ai_misc import (
    clean_indents,  # Keep this import here for easier imports into other files so prompts can keep proper indentation levels in code # NOSONAR
)
from src.ai_models.model_archetypes.openai_text_model import OpenAiTextToTextModel

logger = logging.getLogger(__name__)


class Gpt4o(OpenAiTextToTextModel):
    # See OpenAI Limit on the account dashboard for most up-to-date limit
    MODEL_NAME: Final[str] = "gpt-4o"
    REQUESTS_PER_PERIOD_LIMIT: Final[int] = 8_000
    REQUEST_PERIOD_IN_SECONDS: Final[int] = 60
    TIMEOUT_TIME: Final[int] = 40
    TOKENS_PER_PERIOD_LIMIT: Final[int] = 8_000_000
    TOKEN_PERIOD_IN_SECONDS: Final[int] = 60
