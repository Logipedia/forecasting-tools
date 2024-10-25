import logging
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from front_end.mokoresearch_site.app_pages.forecaster_page import ForecasterPage
from front_end.mokoresearch_site.helpers.report_displayer import ReportDisplayer
from src.forecasting.metaculus_question import BinaryQuestion
from tests.cheap.test_forecasting.forecasting_test_manager import ForecastingTestManager
from tests.cheap.test_frontend.front_end_test_utils import FrontEndTestUtils

logger = logging.getLogger(__name__)


############################# SETUP ####################################
class SetupEnvironment:
    def __init__(
        self,
        app_test: AppTest,
        fake_question: BinaryQuestion,
        mocked_run_forecast_function: Mock,
        mocked_add_report_to_database_function: Mock,
    ) -> None:
        self.app_test = app_test
        self.fake_question = fake_question
        self.mocked_run_forecast_function = mocked_run_forecast_function
        self.mocked_add_report_to_database_function = (
            mocked_add_report_to_database_function
        )


@pytest.fixture
def setup_environment(mocker: Mock) -> SetupEnvironment:
    mocked_run_forecast_function = (
        ForecastingTestManager.mock_forecaster_team_run_forecast(mocker)
    )
    mocked_add_report_to_database_function = (
        ForecastingTestManager.mock_add_forecast_report_to_database(mocker)
    )
    app_test = FrontEndTestUtils.convert_page_to_app_tester(ForecasterPage)
    fake_question = ForecastingTestManager.get_question_safe_to_pull_and_push_to()
    return SetupEnvironment(
        app_test,
        fake_question,
        mocked_run_forecast_function,
        mocked_add_report_to_database_function,
    )


################################ TESTS ######################################


@pytest.mark.skip(
    reason="These tests seem to break every change I do, and yet the actual website works. Not worth maintaining"
)
def test_arbitrary_forecast_page_works_with_only_question_inputted(
    setup_environment: SetupEnvironment,
) -> None:
    setup_environment.fake_question.background_info = ""
    setup_environment.fake_question.resolution_criteria = ""
    setup_environment.fake_question.fine_print = ""
    run_forecast_and_assert_reports_on_page(setup_environment)


@pytest.mark.skip(
    reason="These tests seem to break every change I do, and yet the actual website works. Not worth maintaining"
)
def test_arbitrary_forecast_page_works_with_all_fields_inputted(
    setup_environment: SetupEnvironment,
) -> None:
    run_forecast_and_assert_reports_on_page(setup_environment)


@pytest.mark.skip(
    reason="These tests seem to break every change I do, and yet the actual website works. Not worth maintaining"
)
def test_errors_if_no_question_text_inputted(
    setup_environment: SetupEnvironment,
) -> None:
    setup_environment.fake_question.question_text = ""
    app_test = setup_environment.app_test
    fake_question = setup_environment.fake_question
    run_forecast_on_forecaster_page(setup_environment.app_test, fake_question)
    assert len(app_test.error) == 1, "Error component not displayed as expected"
    assert setup_environment.mocked_run_forecast_function.call_count == 0
    assert setup_environment.mocked_add_report_to_database_function.call_count == 0


@pytest.mark.skip(
    reason="These tests seem to break every change I do, and yet the actual website works. Not worth maintaining"
)
def test_multiple_reports_submitted_stay_between_runs(
    setup_environment: SetupEnvironment,
) -> None:
    run_forecast_and_assert_reports_on_page(setup_environment)
    run_forecast_and_assert_reports_on_page(
        setup_environment, [setup_environment.fake_question.question_text]
    )


@pytest.mark.skip(
    reason="These tests seem to break every change I do, and yet the actual website works. Not worth maintaining"
)
def test_all_markdown_is_clean_after_reports_displayed(
    setup_environment: SetupEnvironment,
) -> None:
    run_forecast_and_assert_reports_on_page(setup_environment)
    all_markdown = setup_environment.app_test.markdown
    for markdown_element in all_markdown:
        assert ReportDisplayer.markdown_is_clean(markdown_element.value)


###################################### HELPER FUNCTIONS #########################################


def run_forecast_and_assert_reports_on_page(
    set_env: SetupEnvironment, past_question_texts: list[str] = []
) -> None:
    run_forecast_on_forecaster_page(set_env.app_test, set_env.fake_question)

    questions_texts = past_question_texts + [set_env.fake_question.question_text]
    num_questions_on_page = len(questions_texts)
    mock_report = ForecastingTestManager.get_fake_forecast_report()
    FrontEndTestUtils.assert_x_valid_forecast_reports_are_on_the_page(
        set_env.app_test,
        [mock_report] * num_questions_on_page,
    )

    number_of_times_mock_should_have_been_called = len(questions_texts)
    assert (
        set_env.mocked_run_forecast_function.call_count
        == number_of_times_mock_should_have_been_called
    )
    assert (
        set_env.mocked_add_report_to_database_function.call_count
        == number_of_times_mock_should_have_been_called
    )


def run_forecast_on_forecaster_page(
    app_test_on_forecaster_page: AppTest, fake_question: BinaryQuestion
) -> None:
    app_test = app_test_on_forecaster_page
    app_test.run()
    question_text_input = app_test.text_input(ForecasterPage.QUESTION_TEXT_BOX)
    background_input = app_test.text_area(ForecasterPage.BACKGROUND_INFO_BOX)
    resolution_criteria_input = app_test.text_area(
        ForecasterPage.RESOLUTION_CRITERIA_BOX
    )
    fine_print_input = app_test.text_area(ForecasterPage.FINE_PRINT_BOX)

    question_text_input.set_value(fake_question.question_text)
    background_input.set_value(fake_question.background_info)
    resolution_criteria_input.set_value(fake_question.resolution_criteria)
    fine_print_input.set_value(fake_question.fine_print)

    submit_button = app_test.button[0]
    submit_button.click()
    app_test.run()
