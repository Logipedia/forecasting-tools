from unittest.mock import Mock

import pytest

from front_end.helpers.tool_page import ToolPage
from front_end.Home import HomePage
from tests.no_cost_expect_all_to_succeed.test_frontend.front_end_test_utils import (
    FrontEndTestUtils,
)


@pytest.fixture
def mock_tool_functions(mocker: Mock) -> None:
    mocker.patch(
        "front_end.helpers.tool_page.ToolPage._run_tool", return_value=None
    )
    mocker.patch("front_end.helpers.tool_page.ToolPage._save_output_to_coda")
    mocker.patch(
        "front_end.helpers.tool_page.ToolPage._save_output_to_browser_storage"
    )


@pytest.mark.parametrize(
    "page_class",
    [page for page in HomePage.NON_HOME_PAGES if issubclass(page, ToolPage)],
)
async def test_tool_page_functionality(
    page_class: type[ToolPage], mock_tool_functions: None
) -> None:
    app_test = FrontEndTestUtils.convert_page_to_app_tester(page_class)

    # First run - no input
    app_test.run()
    assert not app_test.exception
    assert not app_test.error

    # Mock input and output
    mock_input = page_class.INPUT_TYPE()
    mock_output = page_class.OUTPUT_TYPE()

    # Patch the specific page methods
    with pytest.MonkeyPatch().context() as m:
        m.setattr(page_class, "_get_input", lambda cls: mock_input)
        m.setattr(page_class, "_run_tool", lambda cls, input: mock_output)

        # Second run - with input
        app_test.run()
        assert not app_test.exception
        assert not app_test.error

        # Verify something was displayed
        assert len(app_test.markdown) > 0 or len(app_test.text) > 0
