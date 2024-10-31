from datetime import datetime

from src.forecasting.forecast_reports.forecast_report import ForecastReport
from src.forecasting.metaculus_question import DateQuestion


class DateReport(ForecastReport):
    question: DateQuestion
    prediction: list[tuple[datetime, float]]
