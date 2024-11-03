import dotenv
import streamlit as st

from forecasting_tools.forecasting.forecast_reports.binary_report import (
    BinaryReport,
)
from forecasting_tools.front_end.helpers.app_page import AppPage
from forecasting_tools.front_end.helpers.general import footer, header
from forecasting_tools.front_end.helpers.report_displayer import (
    ReportDisplayer,
)


class ExampleForecastsPage(AppPage):
    PAGE_DISPLAY_NAME: str = "🧪  Premade Example Forecasts"
    URL_PATH: str = "/forecast-examples"

    @classmethod
    async def _async_main(cls) -> None:
        header()
        st.title("Forecast Examples")
        st.write("")
        st.markdown(
            """
            ## Overview
            Below are some example forecasts run on Sep 3, 2024 related to important questions on Metaculus.
            Reports include:
            - Will Israel invade Lebanon before October 1, 2024? Bot predicted 10%, [community vote was 10%](https://www.metaculus.com/questions/25846/israel-to-invade-lebanon/)
            - Will Donald Trump win the US 2024 Election? Bot predicted 66%, [community vote was 45%](https://www.metaculus.com/questions/11245/2024-us-presidential-election-winner/)
            - Will Kamala Harris win the US 2024 Election? Bot predicted 32%, [community vote was 55%](https://www.metaculus.com/questions/11245/2024-us-presidential-election-winner/)

            My Take: The bot's biggest strength is as a research aid. None of the bots in the Metaculus AI Benchmark Competition are to be as good as a good human forecaster yet, but many (including mine) are better than random chance, and they can research a heck of a lot faster than a human.

            # Example Reports
            """
        )
        reports = cls.get_example_reports()
        ReportDisplayer.display_report_list(reports)
        footer()

    @classmethod
    def get_example_reports(cls) -> list[BinaryReport]:
        report_file_path = "forecasting_tools/front_end/app_pages/example_forecast_reports.json"
        return BinaryReport.convert_project_file_path_to_object_list(
            report_file_path
        )


if __name__ == "__main__":
    dotenv.load_dotenv()
    ExampleForecastsPage.main()
