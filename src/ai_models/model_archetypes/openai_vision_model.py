import logging
from abc import ABC

from src.ai_models.ai_utils.openai_utils import OpenAiUtils
from src.ai_models.model_archetypes.openai_text_model import (
    OpenAiTextToTextModel,
)

logger = logging.getLogger(__name__)
from src.ai_models.ai_utils.openai_utils import VisionMessageData
from src.ai_models.ai_utils.response_types import TextTokenCostResponse
from tests.cheap.test_ai_models.ai_mock_manager import AiModelMockManager


class OpenAiVisionToTextModel(OpenAiTextToTextModel, ABC):

    async def invoke(self, input: VisionMessageData) -> str:
        response: TextTokenCostResponse = (
            await self._invoke_with_request_cost_time_and_token_limits_and_retry(
                input
            )
        )
        return response.data

    async def _mockable_direct_call_to_model(
        self, input: VisionMessageData
    ) -> TextTokenCostResponse:
        self._everything_special_to_call_before_direct_call()
        messages = self.create_messages_from_input(input)
        prompt_tokens: int = self.input_to_tokens(input)
        max_tokens: int = prompt_tokens + 1000
        response: TextTokenCostResponse = (
            await self._call_online_model_using_api(
                messages, self.temperature, max_tokens
            )
        )
        return response

    @staticmethod
    def _get_cheap_input_for_invoke() -> VisionMessageData:
        return AiModelMockManager.CHEAP_IMAGE_MESSAGE_DATA

    def create_messages_from_input(self, input: VisionMessageData) -> list:
        if self.system_prompt is None:
            return OpenAiUtils.put_single_image_message_in_list_using_gpt_vision_input(
                input
            )
        else:
            return OpenAiUtils.create_system_and_image_message_from_prompt(
                input, self.system_prompt
            )

    def input_to_tokens(self, vision_input: VisionMessageData) -> int:
        messages = self.create_messages_from_input(vision_input)
        tokens = OpenAiUtils.messages_to_tokens(messages, self.MODEL_NAME)
        return tokens
