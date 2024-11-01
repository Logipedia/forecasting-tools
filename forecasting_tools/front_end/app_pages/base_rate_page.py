import logging
import os
import sys
import textwrap

import dotenv
import streamlit as st

dotenv.load_dotenv()
current_dir = os.path.dirname(os.path.abspath(__file__))
top_level_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.append(top_level_dir)


from forecasting_tools.forecasting.forecast_database_manager import (
    ForecastDatabaseManager,
    ForecastRunType,
)
from forecasting_tools.forecasting.sub_question_responders.base_rate_responder import (
    BaseRateReport,
    BaseRateResponder,
)
from forecasting_tools.front_end.helpers.app_page import AppPage
from forecasting_tools.front_end.helpers.general import footer, header
from forecasting_tools.front_end.helpers.report_displayer import (
    ReportDisplayer,
)

logger = logging.getLogger(__name__)


class BaseRatePage(AppPage):
    FILE_PATH_IN_FRONT_END_FOLDER: str = "pages/base_rate_page.py"
    PAGE_DISPLAY_NAME: str = "🦕 Find a Historical Base Rate"
    URL_PATH: str = "/base-rate-generator"

    QUESTION_TEXT_BOX = "Question Text Box"
    QUESTION_FORM = "base_rate_question_form"

    @classmethod
    async def async_main(cls) -> None:
        header()
        cls.__display_title_info()
        await cls.__display_base_rate_form()
        cls.__display_all_reports()
        footer()

    @classmethod
    def __display_title_info(cls) -> None:
        st.title("Find a Historical Base Rate with AI")
        example_questions = [
            "How often has someone successfully sued Apple regarding violated patents?",
            "How often has there been a declaration of a public health emergency of international concern by the World Health Organization",
            "In what percentage of US presidential elections have their been faithless electors?",
        ]
        examples_as_markdown = "\n" + "\n".join(
            [f" - {question}" for question in example_questions]
        )
        markdown = textwrap.dedent(
            f"""
            Enter your question about historical base rates.

            {examples_as_markdown}
            """
        )
        st.markdown(markdown)

    @classmethod
    async def __display_base_rate_form(cls) -> None:
        with st.form(cls.QUESTION_FORM):
            question_text = st.text_area(
                "Enter your question here",
                key=cls.QUESTION_TEXT_BOX,
            )

            submitted = st.form_submit_button("Submit")

            if submitted:
                if question_text:
                    with st.spinner(
                        "Analyzing... This may take a minute or two..."
                    ):
                        await cls.__run_base_rate_analysis(question_text)
                else:
                    st.error("Please enter a question.")

    @classmethod
    async def __run_base_rate_analysis(cls, question_text: str) -> None:
        try:
            report = await BaseRateResponder(
                question_text
            ).make_base_rate_report()
            cls.__save_base_rate_report(report)
        except Exception as e:
            st.error(f"Error: {e}")

    @classmethod
    def __save_base_rate_report(
        cls,
        report: BaseRateReport,
    ) -> None:
        if "saved_base_rate_list" not in st.session_state:
            st.session_state.saved_base_rate_list = []
        st.session_state.saved_base_rate_list.append(report)
        ForecastDatabaseManager.add_base_rate_report_to_database(
            report, ForecastRunType.WEB_APP_BASE_RATE
        )

    @classmethod
    def __display_all_reports(cls) -> None:
        if "saved_base_rate_list" not in st.session_state:
            st.session_state.saved_base_rate_list = []
        reports_to_display: list[BaseRateReport] = (
            st.session_state.saved_base_rate_list
        )
        for report in reports_to_display:
            assert isinstance(
                report, BaseRateReport
            ), f"Report is not a BaseRateReport. Type: {type(report)}. Report: {report}"
            with st.expander(report.question):
                st.markdown(
                    ReportDisplayer.clean_markdown(report.markdown_report)
                )


if __name__ == "__main__":
    BaseRatePage.main()
