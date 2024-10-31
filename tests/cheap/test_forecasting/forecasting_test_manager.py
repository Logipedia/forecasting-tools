import textwrap
from datetime import datetime
from typing import TypeVar
from unittest.mock import Mock

from src.forecasting.forecast_database_manager import ForecastDatabaseManager
from src.forecasting.forecast_reports.binary_report import BinaryReport
from src.forecasting.forecast_team.forecast_team import ForecastTeam
from src.forecasting.metaculus_api import MetaculusApi
from src.forecasting.metaculus_question import (
    BinaryQuestion,
    MetaculusQuestion,
)

T = TypeVar("T", bound=MetaculusQuestion)


class ForecastingTestManager:
    TOURNAMENT_SAFE_TO_PULL_AND_PUSH_TO = MetaculusApi.AI_WARMUP_TOURNAMENT_ID
    TOURNAMENT_WITH_MIXTURE_OF_OPEN_AND_NOT_OPEN = (
        MetaculusApi.AI_COMPETITION_ID_Q4
    )
    TOURNAMENT_WITH_MIX_OF_QUESTION_TYPES = MetaculusApi.Q4_2024_QUARTERLY_CUP

    @classmethod
    def get_question_safe_to_pull_and_push_to(cls) -> BinaryQuestion:
        questions = MetaculusApi.get_all_questions_from_tournament(
            cls.TOURNAMENT_SAFE_TO_PULL_AND_PUSH_TO
        )
        assert len(questions) > 0
        question = questions[0]
        assert isinstance(question, BinaryQuestion)
        question.community_prediction_at_access_time = (
            0  # Some tests need a value to manipulate
        )
        return question

    @staticmethod
    def get_fake_forecast_report() -> BinaryReport:
        return BinaryReport(
            question=ForecastingTestManager.get_question_safe_to_pull_and_push_to(),
            prediction=0.5,
            explanation=textwrap.dedent(
                """
                # Summary
                This is a test explanation

                ## Analysis
                ### Analysis 1
                This is a test analysis

                ### Analysis 2
                This is a test analysis
                #### Analysis 2.1
                This is a test analysis
                #### Analysis 2.2
                This is a test analysis
                - Conclusion 1
                - Conclusion 2

                # Conclusion
                This is a test conclusion
                - Conclusion 1
                - Conclusion 2
                """
            ),
            other_notes=None,
        )

    @staticmethod
    def mock_forecaster_team_run_forecast(mocker: Mock) -> Mock:
        test_binary_question = (
            ForecastingTestManager.get_question_safe_to_pull_and_push_to()
        )
        mock_function = mocker.patch(
            f"{ForecastTeam.run_forecast.__module__}.{ForecastTeam.run_forecast.__qualname__}"
        )
        assert isinstance(test_binary_question, BinaryQuestion)
        mock_function.return_value = (
            ForecastingTestManager.get_fake_forecast_report()
        )
        return mock_function

    @staticmethod
    def mock_add_forecast_report_to_database(mocker: Mock) -> Mock:
        mock_function = mocker.patch(
            f"{ForecastDatabaseManager.add_forecast_report_to_database.__module__}.{ForecastDatabaseManager.add_forecast_report_to_database.__qualname__}"
        )
        return mock_function

    @staticmethod
    def quarterly_cup_is_not_active() -> bool:
        # Quarterly cup is not active from the 1st to the 10th day of the quarter while the initial questions are being set
        current_date = datetime.now().date()
        day_of_month = current_date.day
        month = current_date.month

        is_first_month_of_quarter = month in [1, 4, 7, 10]
        is_first_10_days = day_of_month <= 10

        return is_first_month_of_quarter and is_first_10_days