import re
from datetime import datetime

from forecasting_tools.ai_models.ai_utils.ai_misc import clean_indents
from forecasting_tools.forecasting.forecast_team.forecast_bot import (
    ForecastBot,
)
from forecasting_tools.forecasting.helpers.configured_llms import AdvancedLlm
from forecasting_tools.forecasting.questions_and_reports.forecast_report import (
    ReasonedPrediction,
)
from forecasting_tools.forecasting.questions_and_reports.metaculus_questions import (
    BinaryQuestion,
    MetaculusQuestion,
    MultipleChoiceQuestion,
    NumericQuestion,
)
from forecasting_tools.forecasting.questions_and_reports.multiple_choice_report import (
    PredictedOptionSet,
)
from forecasting_tools.forecasting.questions_and_reports.numeric_report import (
    NumericDistribution,
    Percentile,
)


class DefaultForecastBot(ForecastBot):

    def __init__(
        self,
        *args,
        number_of_background_questions_to_ask: int = 3,
        number_of_base_rate_questions_to_ask: int = 3,
        number_of_base_rates_to_do_deep_research_on: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            **kwargs,
        )
        self.number_of_background_questions_to_ask = (
            number_of_background_questions_to_ask
        )
        self.number_of_base_rate_questions_to_ask = (
            number_of_base_rate_questions_to_ask
        )
        self.number_of_base_rates_to_do_deep_research_on = (
            number_of_base_rates_to_do_deep_research_on
        )

    async def run_research(self, question: MetaculusQuestion) -> str:
        raise NotImplementedError(
            "DefaultForecastBot does not implement run_research"
        )

    async def run_forecast_on_binary(
        self, question: BinaryQuestion, research: str
    ) -> ReasonedPrediction[float]:
        assert isinstance(
            question, BinaryQuestion
        ), "Question must be a BinaryQuestion"
        prompt = clean_indents(
            f"""
            You are a professional forecaster interviewing for a job.
            Your interview question is:
            {question.question_text}

            Background information:
            {question.background_info if question.background_info else "No background information provided."}

            Resolution criteria:
            {question.resolution_criteria if question.resolution_criteria else "No resolution criteria provided."}

            Fine print:
            {question.fine_print if question.fine_print else "No fine print provided."}


            Your research assistant says:
            ```
            {research}
            ```

            Today is {datetime.now().strftime("%Y-%m-%d")}.


            Before answering you write:
            (a) The time left until the outcome to the question is known.
            (b) What the outcome would be if nothing changed.
            (c) The most important factors that will influence a successful/unsuccessful resolution.
            (d) What do you not know that should give you pause and lower confidence? Remember people are statistically overconfident.
            (e) What you would forecast if you were to only use historical precedent (i.e. how often this happens in the past) without any current information.
            (f) What you would forecast if there was only a quarter of the time left.
            (g) What you would forecast if there was 4x the time left.

            You write your rationale and then the last thing you write is your final answer as: "Probability: ZZ%", 0-100
            """
        )
        final_prediction_model = AdvancedLlm()
        gpt_forecast = await final_prediction_model.invoke(prompt)
        prediction = self._extract_forecast_from_binary_rationale(gpt_forecast)
        reasoning = (
            gpt_forecast
            + "\nThe original forecast may have been clamped between 5% and 95%."
        )
        return ReasonedPrediction(
            prediction_value=prediction, reasoning=reasoning
        )

    async def run_forecast_on_multiple_choice(
        self, question: MultipleChoiceQuestion, research: str
    ) -> ReasonedPrediction[PredictedOptionSet]:
        raise NotImplementedError(
            "DefaultForecastBot does not implement run_forecast_on_multiple_choice"
        )

    async def run_forecast_on_numeric(
        self, question: NumericQuestion, research: str
    ) -> ReasonedPrediction[NumericDistribution]:
        prompt = clean_indents(
            f"""
            You are a professional forecaster interviewing for a job.
            Your interview question is:
            {question.question_text}

            Background:
            {question.background_info}

            {question.resolution_criteria}

            {question.fine_print}

            Your research assistant says:
            ```
            {research}
            ```

            The question implies that the majority of the probability distribution is probably in the range:
            {question.lower_bound} to {question.upper_bound}

            Today is {datetime.now().strftime("%Y-%m-%d")}.

            Before answering you write:
            (a) The time left until the outcome to the question is known.
            (b) What the outcome would be if nothing changed.
            (c) What you would forecast if there was only a quarter of the time left.
            (d) What you would forecast if there was 4x the time left.

            You write your rationale and then the last thing you write is your final answer as a series of probability distributions.
            Each line should be in the format: "Probability of a value below Y is X%". Make sure to use this EXACT format, and change out only Y and X.
            Provide at values for your 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90% estimates.
            The lowest value should have a probability approaching 10%, and the highest value should approach 90%.
            Remember that its very easy to be overconfident. 10% should feel like "this couldn't possibly get below this number!", and probability of 90% should feel like "There is not chance this will get anywhere above this number!"
            """
        )
        final_prediction_model = AdvancedLlm(temperature=0.7)
        reasoning = await final_prediction_model.invoke(prompt)
        prediction = self._extract_forecast_from_numeric_rationale(
            reasoning, question
        )
        return ReasonedPrediction(
            prediction_value=prediction, reasoning=reasoning
        )

    def _extract_forecast_from_binary_rationale(self, rationale: str) -> float:
        max_prediction = 95
        min_prediction = 5
        matches = re.findall(r"(\d+)%", rationale)
        if matches:
            # Return the last number found before a '%'
            original_number = int(matches[-1])
            clamped_number = min(
                max_prediction, max(min_prediction, original_number)
            )
            assert min_prediction <= clamped_number <= max_prediction
            return clamped_number / 100
        else:
            raise ValueError(
                f"Could not extract prediction from response: {rationale}"
            )

    def _extract_forecast_from_multiple_choice_rationale(
        self, reasoning: str
    ) -> PredictedOptionSet:
        raise NotImplementedError(
            "DefaultForecastBot does not implement _extract_forecast_from_multiple_choice_rationale"
        )

    def _extract_forecast_from_numeric_rationale(
        self, reasoning: str, question: NumericQuestion
    ) -> NumericDistribution:
        matches = re.findall(
            r"Probability of a value below (\d+(?:\.\d+)?) is (\d+(?:\.\d+)?)%",
            reasoning,
        )
        if matches:
            percentiles = []
            for value, percentile in matches:
                percentiles.append(
                    Percentile(
                        value=float(value.replace(",", "")),
                        percentile=float(percentile) / 100,
                    )
                )
            return NumericDistribution(
                declared_percentiles=percentiles,
                open_upper_bound=False,
                open_lower_bound=False,
                upper_bound=question.upper_bound,
                lower_bound=question.lower_bound,
                zero_point=question.zero_point,
            )
        else:
            raise ValueError(
                f"Could not extract prediction from response: {reasoning}"
            )