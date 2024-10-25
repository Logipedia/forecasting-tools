from __future__ import annotations

import asyncio

import dotenv

from src.forecasting.forecast_database_manager import (
    ForecastDatabaseManager,
    ForecastRunType,
)
from src.forecasting.sub_question_responders.base_rate_responder import (
    BaseRateReport,
    BaseRateResponder,
)
from src.util.custom_logger import CustomLogger


def run_base_rate() -> None:
    question = input("Enter you question: ")
    base_rate_responder = BaseRateResponder(question)
    report = asyncio.run(base_rate_responder.make_base_rate_report())
    escaped_question = "".join(char if char.isalnum() else "_" for char in question)
    log_path = f"logs/forecasts/base_rates/{escaped_question}.json"
    BaseRateReport.save_object_list_to_file_path([report], log_path)
    ForecastDatabaseManager.add_base_rate_report_to_database(
        report, ForecastRunType.REGULAR_BASE_RATE
    )


if __name__ == "__main__":
    dotenv.load_dotenv()
    CustomLogger.setup_logging()
    run_base_rate()
