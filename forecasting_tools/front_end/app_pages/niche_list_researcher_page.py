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

from forecasting_tools.ai_models.resource_managers.monetary_cost_manager import (
    MonetaryCostManager,
)
from forecasting_tools.forecasting.forecast_database_manager import (
    ForecastDatabaseManager,
    ForecastRunType,
)
from forecasting_tools.forecasting.sub_question_responders.niche_list_researcher import (
    FactCheckedItem,
    NicheListResearcher,
)
from forecasting_tools.front_end.helpers.app_page import AppPage
from forecasting_tools.front_end.helpers.general import footer, header

logger = logging.getLogger(__name__)


class NicheListResearchPage(AppPage):
    FILE_PATH_IN_FRONT_END_FOLDER: str = "pages/niche_list_research_page.py"
    PAGE_DISPLAY_NAME: str = "📋 Niche List Researcher"
    URL_PATH: str = "/niche-list-researcher"

    QUESTION_TEXT_BOX = "Question Text Box"
    QUESTION_FORM = "niche_list_research_form"

    @classmethod
    async def async_main(cls) -> None:
        header()
        cls.__display_title_info()
        await cls.__display_niche_list_form()
        footer()

    @classmethod
    def __display_title_info(cls) -> None:
        st.title("Niche List Researcher")

        markdown = textwrap.dedent(
            """
            Enter a description of the niche topic you want to research and create a comprehensive list for. The tool will have problems with lists that include more than 15-30 items.
            The AI will attempt to find all relevant instances and fact-check them. Examples:
            - Times there has been a declaration of a public health emergency of international concern by the World Health Organization
            - Times that Apple was successfully sued for patent violations
            """
        )
        st.markdown(markdown)

    @classmethod
    async def __display_niche_list_form(cls) -> None:
        with st.form(cls.QUESTION_FORM):
            question_text = st.text_input(
                "Enter your niche list research query here",
                key=cls.QUESTION_TEXT_BOX,
            )

            submitted = st.form_submit_button("Research and Generate List")

            if submitted:
                if question_text:
                    with st.spinner(
                        "Researching and fact-checking... This may take several minutes..."
                    ):
                        await cls.__run_niche_list_research(question_text)
                else:
                    st.error("Please enter a research query.")

    @classmethod
    async def __run_niche_list_research(
        cls,
        question_text: str,
    ) -> None:
        try:
            with MonetaryCostManager() as cost_manager:
                generator = NicheListResearcher(question_text)
                fact_checked_items = (
                    await generator.research_list_of_niche_reference_class(
                        include_incorrect_items=True
                    )
                )

                st.subheader("Niche List Research Results")
                markdown = (
                    FactCheckedItem.make_markdown_with_valid_and_invalid_lists(
                        fact_checked_items
                    )
                )
                cost = cost_manager.current_usage
                st.markdown(f"**Cost:** ${cost:.2f}\n\n{markdown}")

                ForecastDatabaseManager.add_general_report_to_database(
                    question_text=question_text,
                    background_info=None,
                    resolution_criteria=None,
                    fine_print=None,
                    prediction=len(fact_checked_items),
                    explanation=markdown,
                    page_url=None,
                    price_estimate=cost,
                    run_type=ForecastRunType.WEB_APP_NICHE_LIST,
                )
        except Exception as e:
            logger.exception(f"Unexpected error in niche list research: {e}")
            st.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    NicheListResearchPage.main()
