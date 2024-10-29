import logging
from enum import Enum

from pydantic import BaseModel

from src.forecasting.forecast_team.research_manager import ResearchManager
from src.forecasting.llms.configured_llms import (
    BaseRateProjectLlm,
    clean_indents,
)
from src.forecasting.llms.smart_searcher import SmartSearcher
from src.forecasting.metaculus_api import MetaculusQuestion
from src.forecasting.sub_question_responders.deduplicator import Deduplicator
from src.util import async_batching

logger = logging.getLogger(__name__)


class KeyFactorType(str, Enum):
    BASE_RATE = "base_rate"
    PRO = "pro"
    CON = "con"


class KeyFigure(BaseModel):
    text: str
    factor_type: KeyFactorType
    citation: str
    score: int | None = None


class KeyFactorsSearcher:

    @classmethod
    async def find_key_factors(
        cls,
        metaculus_question: MetaculusQuestion,
        num_key_factors_to_return: int = 10,
        num_questions_to_research_with: int = 8,
    ) -> list[KeyFigure]:
        num_background_questions = num_questions_to_research_with // 2
        num_base_rate_questions = (
            num_questions_to_research_with - num_background_questions
        )
        research_manager = ResearchManager(metaculus_question)
        background_questions = (
            await research_manager.brainstorm_background_questions(
                num_background_questions
            )
        )
        base_rate_questions = (
            await research_manager.brainstorm_base_rate_questions(
                num_base_rate_questions,
            )
        )
        combined_questions = background_questions + base_rate_questions
        key_factor_tasks = [
            cls.__find_key_factors_for_question(question)
            for question in combined_questions
        ]
        key_factors, _ = (
            async_batching.run_coroutines_while_removing_and_logging_exceptions(
                key_factor_tasks
            )
        )
        logger.info(f"Found {len(key_factors)} key factors. Now scoring them.")
        flattened_key_factors = [
            factor for sublist in key_factors for factor in sublist
        ]
        scored_key_factors = await cls.__score_key_factor_list(
            metaculus_question, flattened_key_factors
        )
        sorted_key_factors = sorted(
            scored_key_factors, key=lambda x: x.score or 0, reverse=True
        )
        top_key_factors = sorted_key_factors[:num_key_factors_to_return]
        deduplicated_key_factors = await cls.__deduplicate_key_factors(
            top_key_factors
        )
        logger.info(
            f"Found {len(deduplicated_key_factors)} final key factors (deduplicated and filtering for top scores)"
        )
        return deduplicated_key_factors

    @classmethod
    async def __find_key_factors_for_question(
        cls, question_description: str
    ) -> list[KeyFigure]:
        prompt = clean_indents(
            f"""
            Analyze the following question and provide key factors that could influence the outcome of the larger question.
            Include base rates, pros (factors supporting a positive outcome), and cons (factors supporting a negative outcome).
            Each factor should be a single sentence and include a citation.

            Question: {question_description}

            Provide your answer as a list of JSON objects, each representing a KeyFigure with the following format:
            {{
                "text": "The key factor statement",
                "factor_type": "base_rate" or "pro" or "con",
                "citation": "citation (e.g. [1])"
            }}

            Return only the list of JSON objects and nothing else.
            """
        )

        smart_searcher = SmartSearcher(use_brackets_around_citations=False)
        key_figures = await smart_searcher.invoke_and_return_verified_type(
            prompt, list[KeyFigure]
        )

        return key_figures

    @classmethod
    async def __deduplicate_key_factors(
        cls, key_factors: list[KeyFigure]
    ) -> list[KeyFigure]:
        strings_to_check = [factor.text for factor in key_factors]
        deduplicated_strings = (
            await Deduplicator.deduplicate_list_one_item_at_a_time(
                strings_to_check, use_internet_search=False
            )
        )
        deduplicated_factors: list[KeyFigure] = []
        for factor in key_factors:
            if factor.text in deduplicated_strings:
                deduplicated_factors.append(factor)
        return deduplicated_factors

    @classmethod
    async def __score_key_factor_list(
        cls,
        metaculus_question: MetaculusQuestion,
        key_factors: list[KeyFigure],
    ) -> list[KeyFigure]:
        scoring_coroutines = [
            cls.__score_key_factor(metaculus_question.question_text, factor)
            for factor in key_factors
        ]
        scored_factors, _ = (
            async_batching.run_coroutines_while_removing_and_logging_exceptions(
                scoring_coroutines
            )
        )
        return scored_factors

    @classmethod
    async def __score_key_factor(
        cls, question: str, key_factor: KeyFigure
    ) -> KeyFigure:
        prompt = clean_indents(
            f"""
            # Instructions
            You are a superforecaster and an expert at evaluating the importance and relevance of key factors in forecasting questions.
            Please evaluate the following key factor and assign it a score from 1 to 10, where:
            1 = Not relevant or important at all
            10 = Extremely relevant and important

            Consider the following criteria:
            1. Relevance to the question
            2. Potential impact on the outcome
            3. Reliability of the information

            Provide your score as a single integer between 1 and 10.
            Give your answer as a json like the below.
            {{
                "reasoning": "Step 1) ... Step 2) ... Step 3)",
                "score": 5
            }}
            Give the json and nothing else

            # Example
            If you were given the following question and key factor:
            Question: Will Ron DeSantis win the 2024 presidential election?
            Key Factor: FiveThirtyEight gives him a 70% chance of winning the swing state of Florida.
            Citation: [1](https://projects.fivethirtyeight.com/2024-election-forecast/)

            You would return:
            {{
                "reasoning": "Step 1) The key factor is relevant because it's about the current state of the race. Step 2) The key factor is important because its about the swing state, but also doesn't give an overall picture of the race. Step 3) FiveThirtyEight is a reliable source and well known for its skill in election forecasting. Conclusion) This key factor is relevant and reliable, but I'll give it a 6 because it useful but is also very specific.",
                "score": 6
            }}

            # Your Turn
            Please score the following key factor:
            Question: {question}
            Key Factor: {key_factor.text}
            Citation: {key_factor.citation}
            """
        )

        model = BaseRateProjectLlm(temperature=0)
        score_data = await model.invoke_and_return_verified_type(prompt, dict)
        base_score = int(score_data["score"])
        base_score = max(1, min(10, base_score))

        contains_number = any(char.isdigit() for char in key_factor.text)
        final_score = base_score + (
            1 if contains_number else 0
        )  # Key factors with numbers are usually higher quality

        key_factor.score = final_score
        return key_factor
