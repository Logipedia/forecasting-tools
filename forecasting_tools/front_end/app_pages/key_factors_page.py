import logging
import os
import re
import sys

import dotenv
import streamlit as st

dotenv.load_dotenv()
current_dir = os.path.dirname(os.path.abspath(__file__))
top_level_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.append(top_level_dir)

from forecasting_tools.ai_models.resource_managers.monetary_cost_manager import (
    MonetaryCostManager,
)
from forecasting_tools.forecasting.forecast_database_manager import (
    ForecastDatabaseManager,
    ForecastRunType,
)
from forecasting_tools.forecasting.metaculus_api import (
    MetaculusApi,
    MetaculusQuestion,
)
from forecasting_tools.forecasting.sub_question_responders.key_factors_searcher import (
    KeyFactorsSearcher,
    ScoredKeyFactor,
)
from forecasting_tools.front_end.helpers.app_page import AppPage
from forecasting_tools.front_end.helpers.general import footer, header

logger = logging.getLogger(__name__)


class KeyFactorsPage(AppPage):
    FILE_PATH_IN_FRONT_END_FOLDER: str = "pages/key_factors_page.py"
    PAGE_DISPLAY_NAME: str = "🔑 Key Factors Researcher"
    URL_PATH: str = "/key-factors"

    METACULUS_URL_INPUT = "metaculus_url_input"

    @classmethod
    async def async_main(cls) -> None:
        header()
        st.title("Metaculus Question Key Factors")

        metaculus_url = cls.__display_metaculus_url_input()

        if st.button("Find Key Factors"):
            if metaculus_url:
                await cls.fetch_and_analyze_question(metaculus_url)
            else:
                st.warning("Please enter a valid Metaculus Question URL.")
        footer()

    @classmethod
    def __display_metaculus_url_input(cls) -> str:
        st.write("Enter a Metaculus question URL to analyze its key factors.")
        return st.text_input(
            "Metaculus Question URL", key=cls.METACULUS_URL_INPUT
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
    async def fetch_and_analyze_question(cls, metaculus_url: str) -> None:
        try:
            question_id = cls.__extract_question_id(metaculus_url)
            metaculus_question = MetaculusApi.get_question_by_id(question_id)
            await cls.analyze_question(metaculus_question)
        except Exception as e:
            st.error(
                f"An error occurred while fetching the question: {e.__class__.__name__}: {e}"
            )

    @classmethod
    async def analyze_question(
        cls, metaculus_question: MetaculusQuestion
    ) -> None:
        st.markdown(f"## Question: {metaculus_question.question_text}")
        with st.spinner("Analyzing key factors..."):
            try:
                with MonetaryCostManager() as cost_manager:
                    num_questions_to_research = 8
                    num_key_factors_to_return = 10
                    key_factors = await KeyFactorsSearcher.find_key_factors(
                        metaculus_question,
                        num_questions_to_research_with=num_questions_to_research,
                        num_key_factors_to_return=num_key_factors_to_return,
                    )

                    cost = cost_manager.current_usage
                    st.success(
                        f"Key factors analysis completed successfully! Cost: ${cost:.2f}"
                    )
                    markdown = cls.make_key_factor_markdown(key_factors)
                    st.markdown(markdown)

                    ForecastDatabaseManager.add_general_report_to_database(
                        question_text=metaculus_question.question_text,
                        background_info=None,
                        resolution_criteria=None,
                        fine_print=None,
                        prediction=None,
                        explanation=markdown,
                        page_url=None,
                        price_estimate=cost,
                        run_type=ForecastRunType.WEB_APP_KEY_FACTORS,
                    )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

    @classmethod
    def make_key_factor_markdown(
        cls, key_factors: list[ScoredKeyFactor]
    ) -> str:
        sorted_factors = sorted(
            key_factors, key=lambda x: x.score, reverse=True
        )
        st.subheader("Key Factors")
        markdown = ScoredKeyFactor.turn_key_factors_into_markdown_list(
            sorted_factors
        )
        return markdown


if __name__ == "__main__":
    KeyFactorsPage.main()
