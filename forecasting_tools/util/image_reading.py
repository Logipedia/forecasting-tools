import base64
import logging

import requests
from bs4 import BeautifulSoup, Tag

from forecasting_tools.ai_models.gpt4ovision import (
    Gpt4oVision,
    Gpt4VisionInput,
)
from forecasting_tools.util import async_batching

logger = logging.getLogger(__name__)


class ImageReader:
    IMAGE_DESCRIPTION_START_TAG = "[Image description start]"
    IMAGE_DESCRIPTION_END_TAG = "[Image description end]"

    @staticmethod
    def image_url_to_base64_str(image_url: str) -> str:
        response = requests.get(image_url)
        image_bytes = response.content
        base64_image = base64.b64encode(image_bytes).decode("utf-8")
        return base64_image

    @staticmethod
    async def replace_html_images_with_paragraph_descriptions(
        html: str,
    ) -> str:
        soup = BeautifulSoup(html, "html.parser")
        image_tags = soup.find_all("img")
        coroutines = [
            ImageReader.create_paragraph_tag_from_image_tag(soup, img_tag)
            for img_tag in image_tags
        ]
        paragraph_tags = async_batching.run_coroutines(coroutines)
        for img_tag, paragraph_tag in zip(image_tags, paragraph_tags):
            img_tag.replace_with(paragraph_tag)
        updated_html = str(soup)
        return updated_html

    @staticmethod
    async def create_paragraph_tag_from_image_tag(
        soup: BeautifulSoup, img_tag: Tag
    ) -> Tag:
        try:
            img_url: str | list[str] = img_tag["src"]

            if isinstance(img_url, list):
                logger.warning(f"Image tag had multiple srcs: {img_url}")
                img_url = img_url[0]

            base64_image = ImageReader.image_url_to_base64_str(img_url)

            vision_input = Gpt4VisionInput(
                prompt='Describe the image in the image tag. Make sure to include all the text in the image in quotes, but make other descriptions only a sentence. Say ```This is an image of [description] with the text "[image text]" on it.```.',
                b64_image=base64_image,
                image_resolution="low",
            )
            gpt_vision = Gpt4oVision(temperature=0)
            description: str = await gpt_vision.invoke(vision_input)
            description_with_tags: str = (
                f"{ImageReader.IMAGE_DESCRIPTION_START_TAG}{description}{ImageReader.IMAGE_DESCRIPTION_END_TAG}"
            )
            new_paragraph = soup.new_tag("p")
            new_paragraph.string = description_with_tags
        except Exception as e:
            logger.warning(
                f"Failed to create paragraph tag from image tag. Error: {e}"
            )
            new_paragraph = soup.new_tag("p")
            new_paragraph.string = f"{ImageReader.IMAGE_DESCRIPTION_START_TAG}ERROR: Failed to create description from image{ImageReader.IMAGE_DESCRIPTION_END_TAG}"
        return new_paragraph
