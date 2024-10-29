from __future__ import annotations

import asyncio
import time

import dotenv

from src.forecasting.forecast_database_manager import (
    ForecastDatabaseManager,
    ForecastRunType,
)
from src.forecasting.metaculus_api import MetaculusApi
from src.forecasting.team_manager import TeamManager
from src.util.custom_logger import CustomLogger


def run_morning_forecasts() -> None:
    CustomLogger.setup_logging()
    forecaster = TeamManager(time_to_wait_between_questions=65)
    TOURNAMENT_ID = MetaculusApi.AI_COMPETITION_ID_Q4
    try:
        reports = asyncio.run(
            forecaster.run_and_publish_forecasts_on_all_open_questions(
                TOURNAMENT_ID
            )
        )
    except Exception:
        reports = asyncio.run(
            forecaster.run_and_publish_forecasts_on_all_open_questions(
                TOURNAMENT_ID
            )
        )
    for report in reports:
        ForecastDatabaseManager.add_forecast_report_to_database(
            report, ForecastRunType.REGULAR_FORECAST
        )
        time.sleep(10)


if __name__ == "__main__":
    dotenv.load_dotenv()
    run_morning_forecasts()
