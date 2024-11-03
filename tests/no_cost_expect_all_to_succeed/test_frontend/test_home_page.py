import logging

from front_end.helpers.app_page import AppPage
from front_end.Home import HomePage
from tests.no_cost_expect_all_to_succeed.test_frontend.front_end_test_utils import (
    FrontEndTestUtils,
)

logger = logging.getLogger(__name__)
import pytest


@pytest.mark.parametrize("page", HomePage.NON_HOME_PAGES)
def test_home_page(page: type[AppPage]) -> None:
    at = FrontEndTestUtils.convert_page_to_app_tester(HomePage)
    at.run()
    assert not at.exception, f"Exception occurred: {at.exception}"
    button = at.button(key=page.PAGE_DISPLAY_NAME)
    button.click()
    at.run()
    assert not at.exception, f"Exception occurred: {at.exception}"
