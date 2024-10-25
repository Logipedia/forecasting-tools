from src.forecasting.forecast_reports.forecast_report import ForecastReport
from src.forecasting.metaculus_question import DateQuestion
from datetime import datetime

class DateReport(ForecastReport):
    question: DateQuestion
    prediction: list[tuple[datetime, float]]


