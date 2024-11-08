import logging
from datetime import datetime, timedelta

import pytest

from forecasting_tools.forecasting.forecast_reports.report_organizer import (
    ReportOrganizer,
)
from forecasting_tools.forecasting.metaculus_api import MetaculusApi
from forecasting_tools.forecasting.metaculus_question import (
    BinaryQuestion,
    DateQuestion,
    MetaculusQuestion,
    MultipleChoiceQuestion,
    NumericQuestion,
    QuestionState,
)
from tests.no_cost_expect_all_to_succeed.test_forecasting.forecasting_test_manager import (
    ForecastingTestManager,
)

logger = logging.getLogger(__name__)

# TODO:
# Can post numeric/date/multiple choice prediction
# Post binary prediction errors if given a non binary question id (and all other combinations of questions)
# Post numeric/date/multiple choice choice prediction errors if given a binary question id


def test_get_binary_question_type_from_id() -> None:
    question_id = ReportOrganizer.get_example_question_id_for_question_type(
        BinaryQuestion
    )
    question = MetaculusApi.get_question_by_id(question_id)
    assert isinstance(question, BinaryQuestion)
    assert question_id == question.question_id
    assert question.community_prediction_at_access_time is not None
    assert abs(question.community_prediction_at_access_time - 0.96) < 0.03
    assert question.state == QuestionState.OPEN
    assert_basic_question_attributes_not_none(question, question_id)


def test_get_numeric_question_type_from_id() -> None:
    question_id = ReportOrganizer.get_example_question_id_for_question_type(
        NumericQuestion
    )
    question = MetaculusApi.get_question_by_id(question_id)
    assert isinstance(question, NumericQuestion)
    assert question_id == question.question_id
    assert question.lower_bound == 0
    assert question.upper_bound == 100
    assert question.lower_bound_is_hard_limit
    assert question.upper_bound_is_hard_limit
    assert_basic_question_attributes_not_none(question, question_id)


def test_get_date_question_type_from_id() -> None:
    question_id = ReportOrganizer.get_example_question_id_for_question_type(
        DateQuestion
    )
    question = MetaculusApi.get_question_by_id(question_id)
    assert isinstance(question, DateQuestion)
    assert question_id == question.question_id
    assert question.lower_bound == datetime(2020, 8, 25)
    assert question.upper_bound == datetime(2199, 12, 25)
    assert question.lower_bound_is_hard_limit
    assert not question.upper_bound_is_hard_limit
    assert_basic_question_attributes_not_none(question, question_id)


def test_get_multiple_choice_question_type_from_id() -> None:
    question_id = ReportOrganizer.get_example_question_id_for_question_type(
        MultipleChoiceQuestion
    )
    question = MetaculusApi.get_question_by_id(question_id)
    assert isinstance(question, MultipleChoiceQuestion)
    assert question_id == question.question_id
    assert len(question.options) == 3
    assert "Russia" in question.options
    assert "Ukraine" in question.options
    assert "Neither" in question.options
    assert_basic_question_attributes_not_none(question, question_id)


def test_post_comment_on_question() -> None:
    question = ForecastingTestManager.get_question_safe_to_pull_and_push_to()
    MetaculusApi.post_question_comment(
        question.question_id, "This is a test comment"
    )
    # No assertion needed, just check that the request did not raise an exception


@pytest.mark.skip(reason="There are no safe questions to post predictions on")
def test_post_binary_prediction_on_question() -> None:
    question = ForecastingTestManager.get_question_safe_to_pull_and_push_to()
    assert isinstance(question, BinaryQuestion)
    question_id = question.question_id
    MetaculusApi.post_binary_question_prediction(question_id, 0.01)
    MetaculusApi.post_binary_question_prediction(question_id, 0.99)


def test_post_binary_prediction_error_when_out_of_range() -> None:
    question = ForecastingTestManager.get_question_safe_to_pull_and_push_to()
    question_id = question.question_id
    with pytest.raises(ValueError):
        MetaculusApi.post_binary_question_prediction(question_id, 0)
    with pytest.raises(ValueError):
        MetaculusApi.post_binary_question_prediction(question_id, 1)
    with pytest.raises(ValueError):
        MetaculusApi.post_binary_question_prediction(question_id, -0.01)
    with pytest.raises(ValueError):
        MetaculusApi.post_binary_question_prediction(question_id, 1.1)


def test_questions_returned_from_list_questions() -> None:
    ai_tournament_id = (
        ForecastingTestManager.TOURNAMENT_WITH_MIXTURE_OF_OPEN_AND_NOT_OPEN
    )
    questions = MetaculusApi.get_all_questions_from_tournament(
        ai_tournament_id
    )
    assert len(questions) > 0
    for question in questions:
        assert isinstance(question, BinaryQuestion)


def test_open_filter_works_for_questions() -> None:
    ai_tournament_id = (
        ForecastingTestManager.TOURNAMENT_WITH_MIXTURE_OF_OPEN_AND_NOT_OPEN
    )
    questions_without_filter = MetaculusApi.get_all_questions_from_tournament(
        ai_tournament_id
    )
    questions_with_filter = MetaculusApi.get_all_questions_from_tournament(
        ai_tournament_id, filter_by_open=True
    )
    assert len(questions_without_filter) > len(
        questions_with_filter
    ), "Expected more questions without filter than with filter"
    for question in questions_with_filter:
        assert (
            question.state == QuestionState.OPEN
        ), f"Expected question to be open, but got {question.state}"


@pytest.mark.parametrize("num_questions_to_get", [30, 100])
def test_get_benchmark_questions(num_questions_to_get: int) -> None:
    if ForecastingTestManager.quarterly_cup_is_not_active():
        pytest.skip("Quarterly cup is not active")

    random_seed = 42
    questions = MetaculusApi.get_benchmark_questions(
        num_questions_to_get, random_seed
    )

    assert (
        len(questions) == num_questions_to_get
    ), f"Expected {num_questions_to_get} questions to be returned"
    for question in questions:
        assert isinstance(question, BinaryQuestion)
        assert question.date_accessed.date() == datetime.now().date()
        assert isinstance(question.num_forecasters, int)
        assert isinstance(question.num_predictions, int)
        assert isinstance(question.close_time, datetime)
        assert isinstance(question.scheduled_resolution_time, datetime)
        assert (
            question.num_predictions >= 40
        ), "Need to have critical mass of predictions to be confident in the results"
        assert (
            question.num_forecasters >= 40
        ), "Need to have critical mass of forecasters to be confident in the results"
        assert isinstance(question, BinaryQuestion)
        three_months_from_now = datetime.now() + timedelta(days=90)
        assert question.close_time < three_months_from_now
        assert question.scheduled_resolution_time < three_months_from_now
        assert question.state == QuestionState.OPEN
        assert question.community_prediction_at_access_time is not None
        logger.info(f"Found question: {question.question_text}")
    question_ids = [question.question_id for question in questions]
    assert len(question_ids) == len(
        set(question_ids)
    ), "Not all questions are unique"

    questions2 = MetaculusApi.get_benchmark_questions(
        num_questions_to_get, random_seed
    )
    question_ids1 = [q.question_id for q in questions]
    question_ids2 = [q.question_id for q in questions2]
    assert (
        question_ids1 == question_ids2
    ), "Questions retrieved with same random seed should return same IDs"


def test_get_questions_from_current_quartely_cup() -> None:
    expected_question_text = "Will BirdCast report 1 billion birds flying over the United States at any point before January 1, 2025?"
    questions = (
        MetaculusApi._get_open_binary_questions_from_current_quarterly_cup()
    )

    if ForecastingTestManager.quarterly_cup_is_not_active():
        assert len(questions) == 0
    else:
        assert len(questions) > 0
        assert any(
            question.question_text == expected_question_text
            for question in questions
        )


def assert_basic_question_attributes_not_none(
    question: MetaculusQuestion, question_id: int
) -> None:
    assert question.resolution_criteria is not None
    assert question.fine_print is not None
    assert question.background_info is not None
    assert question.question_text is not None
    assert question.close_time is not None
    assert question.scheduled_resolution_time is not None
    assert isinstance(question.state, QuestionState)
    assert isinstance(question.page_url, str)
    assert (
        question.page_url
        == f"https://www.metaculus.com/questions/{question_id}"
    )
    assert isinstance(question.num_forecasters, int)
    assert isinstance(question.num_predictions, int)
    assert question.actual_resolution_time is None or isinstance(
        question.actual_resolution_time, datetime
    )
    assert isinstance(question.api_json, dict)
    assert question.close_time > datetime.now()
    if question.scheduled_resolution_time:
        assert question.scheduled_resolution_time >= question.close_time
