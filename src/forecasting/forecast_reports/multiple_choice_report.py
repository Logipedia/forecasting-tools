from src.forecasting.forecast_reports.forecast_report import ForecastReport
from src.forecasting.metaculus_question import MultipleChoiceQuestion


class MultipleChoiceReport(ForecastReport):
    question: MultipleChoiceQuestion
    prediction: list[tuple[str, float]]
