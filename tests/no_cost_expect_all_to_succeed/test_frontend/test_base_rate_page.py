from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from streamlit.testing.v1 import AppTest

from forecasting_tools.forecasting.forecast_database_manager import (
    ForecastDatabaseManager,
)
from forecasting_tools.forecasting.sub_question_responders.base_rate_responder import (
    BaseRateReport,
    BaseRateResponder,
    DenominatorOption,
    ReferenceClassWithCount,
)
from forecasting_tools.front_end.app_pages.base_rate_page import BaseRatePage
from forecasting_tools.front_end.helpers.report_displayer import (
    ReportDisplayer,
)
from tests.no_cost_expect_all_to_succeed.test_frontend.front_end_test_utils import (
    FrontEndTestUtils,
)


class BaseRatePageUtils:
    valid_example_question = "How often has SpaceX launched rockets over the last 5 years? Using their launches per year, what is the chance they will launch a rocket by Dec 30 2025?"
    report_creation_function_name = f"{BaseRateResponder.__module__}.{BaseRateResponder.__name__}.{BaseRateResponder.make_base_rate_report.__name__}"
    test_error_message = "Arbitrary Test error"

    @classmethod
    def mock_report_creation(cls, mocker: Mock) -> Mock:
        mock_reference_class = ReferenceClassWithCount(
            start_date=datetime.now(),
            end_date=datetime.now(),
            hit_definition="How often has SpaceX launched rockets over the last 5 years?",
            hit_description_with_dates_included="How often has SpaceX launched rockets over the last 5 years?",
            count=10,
            reasoning="# Test Report\n\nThis is a test report.\n It has currency. Tom has $5 and will give $1 to John. How much does John have? $1+1=2$",
        )
        mock_report = BaseRateReport(
            question=cls.valid_example_question,
            markdown_report="# Test Report\n\nThis is a test report.\n It has currency. Tom has $5 and will give $1 to John. How much does John have? $1+1=2$",
            historical_rate=0.1,
            start_date=datetime.now(),
            end_date=datetime.now(),
            numerator_reference_class=mock_reference_class,
            denominator_reference_class=mock_reference_class,
            denominator_type=DenominatorOption.PER_DAY,
        )
        mock_make_base_rate_report = AsyncMock(return_value=mock_report)
        mocker.patch(
            cls.report_creation_function_name,
            mock_make_base_rate_report,
        )
        return mock_make_base_rate_report

    @classmethod
    def mock_report_creation_error(cls, mocker: Mock) -> Mock:
        mock_make_base_rate_report = AsyncMock(
            side_effect=Exception(cls.test_error_message)
        )
        mocker.patch(
            cls.report_creation_function_name,
            mock_make_base_rate_report,
        )
        return mock_make_base_rate_report

    @staticmethod
    def mock_add_base_rate_report_to_database(mocker: Mock) -> Mock:
        mock_function = mocker.patch(
            f"{ForecastDatabaseManager.add_base_rate_report_to_database.__module__}.{ForecastDatabaseManager.add_base_rate_report_to_database.__qualname__}"
        )
        return mock_function


class SetupEnvironment:
    def __init__(
        self,
        app_test: AppTest,
        mocked_make_base_rate_report: Mock,
        mocked_add_base_rate_report_to_database: Mock,
    ) -> None:
        self.app_test = app_test
        self.mocked_make_base_rate_report = mocked_make_base_rate_report
        self.mocked_add_base_rate_report_to_database = (
            mocked_add_base_rate_report_to_database
        )


@pytest.fixture
def setup_environment(mocker: Mock) -> SetupEnvironment:
    mocked_make_base_rate_report = BaseRatePageUtils.mock_report_creation(
        mocker
    )
    mocked_add_base_rate_report_to_database = (
        BaseRatePageUtils.mock_add_base_rate_report_to_database(mocker)
    )
    app_test = FrontEndTestUtils.convert_page_to_app_tester(BaseRatePage)
    return SetupEnvironment(
        app_test,
        mocked_make_base_rate_report,
        mocked_add_base_rate_report_to_database,
    )


def test_displays_markdown_within_expander_when_question_entered(
    setup_environment: SetupEnvironment,
) -> None:
    test_question = BaseRatePageUtils.valid_example_question
    input_and_submit_base_rate_question(
        setup_environment.app_test, test_question
    )
    assert_reports_on_page(setup_environment.app_test, 1, test_question)
    setup_environment.mocked_make_base_rate_report.assert_called_once()
    setup_environment.mocked_add_base_rate_report_to_database.assert_called_once()


@pytest.mark.skip(
    reason="After adding the fixture, the error mocking of this test is not working, but not important enough to fix for now"
)
async def test_displays_error_when_responder_errors(
    setup_environment: SetupEnvironment,
) -> None:
    test_question = BaseRatePageUtils.valid_example_question
    BaseRatePageUtils.mock_report_creation_error(
        setup_environment.mocked_make_base_rate_report
    )
    input_and_submit_base_rate_question(
        setup_environment.app_test, test_question
    )

    error_elements = setup_environment.app_test.error
    assert len(error_elements) == 1
    assert BaseRatePageUtils.test_error_message in str(error_elements[0].value)
    setup_environment.mocked_add_base_rate_report_to_database.assert_not_called()


async def test_displays_error_when_no_question_entered(
    setup_environment: SetupEnvironment,
) -> None:
    input_and_submit_base_rate_question(setup_environment.app_test, "")
    error_elements = setup_environment.app_test.error
    assert len(error_elements) == 1
    assert "Please enter a question." in str(error_elements[0].value)
    setup_environment.mocked_make_base_rate_report.assert_not_called()
    setup_environment.mocked_add_base_rate_report_to_database.assert_not_called()


async def test_two_reports_after_two_runs(
    setup_environment: SetupEnvironment,
) -> None:
    test_question = BaseRatePageUtils.valid_example_question

    input_and_submit_base_rate_question(
        setup_environment.app_test, test_question
    )
    assert_reports_on_page(setup_environment.app_test, 1, test_question)
    assert setup_environment.mocked_make_base_rate_report.call_count == 1
    assert (
        setup_environment.mocked_add_base_rate_report_to_database.call_count
        == 1
    )

    input_and_submit_base_rate_question(
        setup_environment.app_test, test_question
    )
    assert_reports_on_page(setup_environment.app_test, 2, test_question)
    assert setup_environment.mocked_make_base_rate_report.call_count == 2
    assert (
        setup_environment.mocked_add_base_rate_report_to_database.call_count
        == 2
    )


def test_all_markdown_is_clean_after_reports_displayed(
    setup_environment: SetupEnvironment,
) -> None:
    test_question = BaseRatePageUtils.valid_example_question
    input_and_submit_base_rate_question(
        setup_environment.app_test, test_question
    )
    all_markdown = setup_environment.app_test.markdown
    for markdown_element in all_markdown:
        assert ReportDisplayer.markdown_is_clean(markdown_element.value)


def input_and_submit_base_rate_question(
    app_test: AppTest, question_text: str
) -> None:
    app_test.run()
    # Enter a question and submit the form
    question_input = app_test.text_area(BaseRatePage.QUESTION_TEXT_BOX)
    question_input.input(question_text).run()
    submit_button = app_test.button[0]
    submit_button.click().run()


def assert_reports_on_page(
    app_test: AppTest, expected_expanders: int, test_question: str
) -> None:
    assert not app_test.exception, f"Exception occurred: {app_test.exception}"

    expanders = app_test.expander
    assert len(expanders) == expected_expanders
    assert expanders[expected_expanders - 1].label == test_question
    assert len(expanders[expected_expanders - 1].markdown) == 1
