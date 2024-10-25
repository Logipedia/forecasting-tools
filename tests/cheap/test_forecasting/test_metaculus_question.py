from src.forecasting.metaculus_question import BinaryQuestion
from tests.cheap.test_forecasting.forecasting_test_manager import ForecastingTestManager
from tests.utilities_for_tests import jsonable_assertations


def test_metaculus_question_is_jsonable() -> None:
    temp_writing_path = "temp/temp_metaculus_question.json"
    read_report_path = (
        "tests/cheap/test_forecasting/forecasting_test_data/metaculus_questions.json"
    )
    jsonable_assertations.assert_reading_and_printing_from_file_works(
        BinaryQuestion, read_report_path, temp_writing_path
    )
