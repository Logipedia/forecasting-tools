import logging
import re

import dotenv
import streamlit as st

from forecasting_tools.forecasting.forecast_database_manager import (
    ForecastDatabaseManager,
    ForecastRunType,
)
from forecasting_tools.forecasting.forecast_reports.binary_report import (
    BinaryReport,
)
from forecasting_tools.forecasting.forecast_team.forecast_team import (
    ForecastTeam,
)
from forecasting_tools.forecasting.metaculus_api import MetaculusApi
from forecasting_tools.forecasting.metaculus_question import (
    BinaryQuestion,
    QuestionState,
)
from forecasting_tools.front_end.helpers.app_page import AppPage
from forecasting_tools.front_end.helpers.general import footer, header
from forecasting_tools.front_end.helpers.report_displayer import (
    ReportDisplayer,
)

logger = logging.getLogger(__name__)


class ForecasterPage(AppPage):
    FILE_PATH_IN_FRONT_END_FOLDER: str = "pages/forecaster_page.py"
    PAGE_DISPLAY_NAME: str = "🔍 Forecast a Question"
    URL_PATH: str = "/forecast"

    QUESTION_TEXT_BOX = "Question Text Box"
    BACKGROUND_INFO_BOX = "Background Info Box"
    RESOLUTION_CRITERIA_BOX = "Resolution Criteria Box"
    FINE_PRINT_BOX = "Fine Print Box"
    QUESTION_FORM = "metaculus_question_form"
    METACULUS_URL_INPUT = "metaculus_url_input"
    FETCH_BUTTON = "fetch_button"
    BASE_RATE_DEEP_RESEARCH = "base_rate_deep_research"

    @classmethod
    async def async_main(cls) -> None:
        header()
        cls.__display_title_info()
        cls.__display_metaculus_url_input()
        await cls.__display_forecaster_form()
        cls.__display_all_reports()
        footer()

    @classmethod
    def __display_title_info(cls) -> None:
        st.title("Forecast a Question with AI")
        st.write(
            "Enter the information for your question. Exa.ai is used to gather up to date information. Each citation attempts to link to a highlight of the a ~4 sentence quote found with Exa.ai. This project is in beta some inaccuracies are expected."
        )

    @classmethod
    def __display_metaculus_url_input(cls) -> None:
        with st.expander("Use an existing Metaculus Binary question"):
            st.write(
                "Enter a Metaculus question URL to autofill the form below."
            )

            metaculus_url = st.text_input(
                "Metaculus Question URL", key=cls.METACULUS_URL_INPUT
            )
            fetch_button = st.button("Fetch Question", key=cls.FETCH_BUTTON)

            if fetch_button and metaculus_url:
                with st.spinner("Fetching question details..."):
                    try:
                        question_id = cls.__extract_question_id(metaculus_url)
                        metaculus_question = MetaculusApi.get_question_by_id(
                            question_id
                        )
                        if isinstance(metaculus_question, BinaryQuestion):
                            cls.__autofill_form(metaculus_question)
                        else:
                            st.error(
                                "Only binary questions are supported at this time."
                            )
                    except Exception as e:
                        st.error(
                            f"An error occurred while fetching the question: {e.__class__.__name__}: {e}"
                        )

    @classmethod
    def __extract_question_id(cls, url: str) -> int:
        match = re.search(r"/questions/(\d+)/", url)
        if match:
            return int(match.group(1))
        raise ValueError(
            "Invalid Metaculus question URL. Please ensure it's in the format: https://metaculus.com/questions/[ID]/[question-title]/"
        )

    @classmethod
    def __autofill_form(cls, question: BinaryQuestion) -> None:
        st.session_state[cls.QUESTION_TEXT_BOX] = question.question_text
        st.session_state[cls.BACKGROUND_INFO_BOX] = (
            question.background_info or ""
        )
        st.session_state[cls.RESOLUTION_CRITERIA_BOX] = (
            question.resolution_criteria or ""
        )
        st.session_state[cls.FINE_PRINT_BOX] = question.fine_print or ""

    @classmethod
    async def __display_forecaster_form(cls) -> None:
        filled_in_metaculus_question: BinaryQuestion | None = None
        with st.form(cls.QUESTION_FORM):
            question_text = st.text_input(
                "Yes/No Binary Question", key=cls.QUESTION_TEXT_BOX
            )
            resolution_criteria = st.text_area(
                "Resolution Criteria (optional)",
                key=cls.RESOLUTION_CRITERIA_BOX,
            )
            fine_print = st.text_area(
                "Fine Print (optional)", key=cls.FINE_PRINT_BOX
            )
            background_info = st.text_area(
                "Background Info (optional)", key=cls.BACKGROUND_INFO_BOX
            )

            col1, col2 = st.columns(2)
            with col1:
                num_background_questions = st.number_input(
                    "Number of background questions to ask",
                    min_value=1,
                    max_value=5,
                    value=4,
                )
            with col2:
                num_base_rate_questions = st.number_input(
                    "Number of base rate questions to ask",
                    min_value=1,
                    max_value=5,
                    value=4,
                )
            submitted = st.form_submit_button("Submit")

            if submitted:
                try:
                    filled_in_metaculus_question = (
                        cls.__create_metaculus_question_from_form(
                            question_text,
                            background_info,
                            resolution_criteria,
                            fine_print,
                        )
                    )
                except Exception as e:
                    st.error(f"Error creating MetaculusQuestion: {e}")

        if filled_in_metaculus_question:
            with st.spinner("Forecasting... This may take a minute or two..."):
                report = await ForecastTeam(
                    filled_in_metaculus_question,
                    number_of_reports_to_aggregate=1,
                    number_of_background_questions_to_ask=int(
                        num_background_questions
                    ),
                    number_of_base_rate_questions_to_ask=int(
                        num_base_rate_questions
                    ),
                    number_of_base_rates_to_do_deep_research_on=0,
                ).run_forecast()
                assert isinstance(
                    report, BinaryReport
                ), "Report is not a BinaryReport"
                cls.__save_forecast_report_to_database_and_session(report)

    @classmethod
    def __save_forecast_report_to_database_and_session(
        cls,
        report: BinaryReport,
    ) -> None:
        if "saved_report_list" not in st.session_state:
            st.session_state.saved_report_list = []
        st.session_state.saved_report_list.append(report)

        try:
            ForecastDatabaseManager.add_forecast_report_to_database(
                report, run_type=ForecastRunType.WEB_APP_FORECAST
            )
        except Exception as e:
            logger.error(f"Error adding report to Coda: {e}")

    @classmethod
    def __display_all_reports(cls) -> None:
        if "saved_report_list" not in st.session_state:
            st.session_state.saved_report_list = []
        reports_to_display = st.session_state.saved_report_list
        ReportDisplayer.display_report_list(reports_to_display)

    @classmethod
    def __create_metaculus_question_from_form(
        cls,
        question_text: str,
        background_info: str | None,
        resolution_criteria: str | None,
        fine_print: str | None,
    ) -> BinaryQuestion:
        if question_text == "":
            raise ValueError("Question Text is required.")
        if background_info == "":
            background_info = None
        if resolution_criteria == "":
            resolution_criteria = None
        if fine_print == "":
            fine_print = None
        question_state = QuestionState.OTHER
        page_url = ""
        question_id = 0
        api_json = {}
        metaculus_question = BinaryQuestion(
            question_text=question_text,
            question_id=question_id,
            state=question_state,
            background_info=background_info,
            resolution_criteria=resolution_criteria,
            fine_print=fine_print,
            page_url=page_url,
            api_json=api_json,
        )
        return metaculus_question


if __name__ == "__main__":
    dotenv.load_dotenv()
    ForecasterPage.main()
