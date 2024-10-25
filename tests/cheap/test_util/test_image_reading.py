from src.util.image_reading import ImageReader
import asyncio

class TestImageElement:
    def __init__(self, image_element, text_snippets) -> None:
        self.image_element = image_element
        self.text_snippets = text_snippets


class ImageReadingTestInfo:
    EXAMPLE_IMAGE_ELEMENT_1 = "<img data-file-id=\"812824\" height=\"104\" src=\"https://mcusercontent.com/281c839c990f42b374467ae5f/images/15149c61-4ca2-96b2-d95c-35aa79106c63.png\" style=\"border: 0px initial;width: 200px;height: 104px;margin: 0px;outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;\" width=\"200\">"
    TEXT_SNIPPETS_FROM_EXAMPLE_IMAGE_1 = ["finance", "buzz"]

    EXAMPLE_IMAGE_ELEMENT_2 = "<img alt=\"\" height=\"auto\" src=\"https://braze-images.com/image_uploads/files/61a348e8e674911b27104b66/original.png?1638090984\" style=\"border-radius: 0; display: block; outline: none; text-decoration: none; height: auto; width: 100%; font-size: 13px; line-height: 100%; -ms-interpolation-mode: bicubic; border: 0;\" width=\"174\">"
    TEXT_SNIPPETS_FROM_EXAMPLE_IMAGE_2 = ["monday"]

    EXAMPLES = [
        TestImageElement(EXAMPLE_IMAGE_ELEMENT_1, TEXT_SNIPPETS_FROM_EXAMPLE_IMAGE_1),
        TestImageElement(EXAMPLE_IMAGE_ELEMENT_2, TEXT_SNIPPETS_FROM_EXAMPLE_IMAGE_2)
    ]


def test_html_images_successfully_replaced_with_descriptions() -> None:
    for example in ImageReadingTestInfo.EXAMPLES:
        html_content = f"<div><p>Other Paragraph with a unique wooorrrrddd</p>{example.image_element}{example.image_element}</div>"
        conversion_coroutine = ImageReader.replace_html_images_with_paragraph_descriptions(html_content)
        new_html_content = asyncio.run(conversion_coroutine)

        for text_snippet in example.text_snippets:
            assert text_snippet in new_html_content.lower(), "Image content was not identified"
        assert new_html_content.count(ImageReader.IMAGE_DESCRIPTION_START_TAG) == 2, "The image description start tag should appear exactly twice"
        assert new_html_content.count(ImageReader.IMAGE_DESCRIPTION_END_TAG) == 2, "The image description end tag should appear exactly twice"
        assert "<img" not in new_html_content, "Image tag was not removed"

        assert new_html_content.lower().count("<p") == 3, "There should be 3 paragraph tags"
        assert new_html_content.lower().count("</p>") == 3, "There should be 3 paragraph tags"
        assert "wooorrrrddd" in new_html_content.lower(), "Other elements were not preserved"
        assert "<div>" in new_html_content, "Div tag was removed"
        assert "</div>" in new_html_content, "Div tag was removed"


def test_nothing_changed_if_no_image_tags() -> None:
    html_content = "<div><p>Other Paragraph with a unique wooorrrrddd</p></div>"
    conversion_coroutine = ImageReader.replace_html_images_with_paragraph_descriptions(html_content)
    new_html_content = asyncio.run(conversion_coroutine)

    assert "finance" not in new_html_content.lower(), "Image content was identified"
    assert "buzz" not in new_html_content.lower(), "Image content was identified"
    assert "wooorrrrddd" in new_html_content.lower(), "Other elements were not preserved"
    assert "<p>" in new_html_content, "Paragraph tag was removed"
    assert "</p>" in new_html_content, "Paragraph tag was removed"
    assert "<div>" in new_html_content, "Div tag was removed"
    assert "</div>" in new_html_content, "Div tag was removed"
    assert "<img" not in new_html_content, "Image tag was not removed"
    assert "[Image description start]" not in new_html_content, "Image text start was added"
    assert "[Image description end]" not in new_html_content, "Image text end was added"