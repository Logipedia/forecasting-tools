import asyncio
import textwrap

import streamlit as st

from forecasting_tools.ai_models.resource_managers.monetary_cost_manager import (
    MonetaryCostManager,
)
from forecasting_tools.forecasting.forecast_database_manager import (
    ForecastDatabaseManager,
    ForecastRunType,
)
from forecasting_tools.forecasting.sub_question_responders.estimator import (
    Estimator,
)
from forecasting_tools.front_end.helpers.app_page import AppPage
from forecasting_tools.front_end.helpers.general import footer, header


class EstimatorPage(AppPage):
    FILE_PATH_IN_FRONT_END_FOLDER: str = "pages/estimator_page.py"
    PAGE_DISPLAY_NAME: str = "🧮 Fermi Estimator"
    URL_PATH: str = "/estimator"

    ESTIMATE_TYPE_INPUT = "estimate_type_input"
    PREVIOUS_RESEARCH_INPUT = "previous_research_input"

    @classmethod
    async def async_main(cls) -> None:
        header()
        st.title("Fermi Estimator")
        st.write(
            "Use this tool to make Fermi estimates for various questions. For example:"
        )

        question_examples = textwrap.dedent(
            """
            - Number of electricians in Oregon
            - Number of of meteorites that will hit the Earth in the next year
            """
        )
        st.markdown(question_examples)
        estimate_type = st.text_input(
            "What do you want to estimate?",
            key=cls.ESTIMATE_TYPE_INPUT,
        )

        if st.button("Generate Estimate"):
            if estimate_type:
                with st.spinner("Generating estimate..."):
                    await cls.generate_estimate(estimate_type)
            else:
                st.warning("Please enter what you want to estimate.")

        footer()

    @classmethod
    async def generate_estimate(
        cls, estimate_type: str, previous_research: str | None = None
    ) -> None:
        with MonetaryCostManager() as cost_manager:
            estimator = Estimator(estimate_type, previous_research)
            try:
                number, markdown = await estimator.estimate_size()
                cost = cost_manager.current_usage
                st.success(
                    f"Estimate generated successfully! Cost: ${cost:.2f}"
                )
                st.markdown(markdown)
                ForecastDatabaseManager.add_general_report_to_database(
                    question_text=estimate_type,
                    background_info=previous_research,
                    resolution_criteria=None,
                    fine_print=None,
                    prediction=number,
                    explanation=markdown,
                    page_url=None,
                    price_estimate=cost,
                    run_type=ForecastRunType.WEB_APP_ESTIMATOR,
                )
            except Exception as e:
                st.error(
                    f"An error occurred while generating the estimate: {str(e)}"
                )


if __name__ == "__main__":
    asyncio.run(EstimatorPage.async_main())
