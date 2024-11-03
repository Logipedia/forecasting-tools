from __future__ import annotations

import json
import logging
import os
import random
import re
from datetime import datetime, timedelta
from typing import Any, Sequence, TypeVar

import requests
import typeguard

from forecasting_tools.forecasting.metaculus_question import (
    BinaryQuestion,
    DateQuestion,
    MetaculusQuestion,
    MultipleChoiceQuestion,
    NumericQuestion,
)
from forecasting_tools.util.misc import raise_for_status_with_additional_info

logger = logging.getLogger(__name__)

Q = TypeVar("Q", bound=MetaculusQuestion)


class MetaculusApi:
    """
    Documentation for the API can be found at https://www.metaculus.com/api/
    """

    AI_WARMUP_TOURNAMENT_ID = 3294
    AI_COMPETITION_ID_Q3 = 3349
    AI_COMPETITION_ID_Q4 = 32506
    Q3_2024_QUARTERLY_CUP = 3366
    Q4_2024_QUARTERLY_CUP = 3672
    CURRENT_QUARTERLY_CUP_ID = Q4_2024_QUARTERLY_CUP

    METACULUS_TOKEN = os.getenv("METACULUS_TOKEN")
    AUTH_HEADERS = {"headers": {"Authorization": f"Token {METACULUS_TOKEN}"}}
    API_BASE_URL = "https://www.metaculus.com/api2"
    MAX_QUESTIONS_FROM_QUESTION_API = 100

    @classmethod
    def post_question_comment(
        cls, question_id: int, comment_text: str
    ) -> None:
        response = requests.post(
            f"{cls.API_BASE_URL}/comments/",
            json={
                "comment_text": comment_text,
                "submit_type": "N",
                "include_latest_prediction": True,
                "question": question_id,
            },
            **cls.AUTH_HEADERS,  # type: ignore
        )
        logger.info(f"Posted comment on question {question_id}")
        raise_for_status_with_additional_info(response)

    @classmethod
    def post_binary_question_prediction(
        cls, question_id: int, prediction_in_decimal: float
    ) -> None:
        logger.info(f"Posting prediction on question {question_id}")
        if prediction_in_decimal < 0.01 or prediction_in_decimal > 0.99:
            raise ValueError("Prediction value must be between 0.001 and 0.99")
        url = f"{cls.API_BASE_URL}/questions/{question_id}/predict/"
        response = requests.post(
            url,
            json={"prediction": float(prediction_in_decimal)},
            **cls.AUTH_HEADERS,  # type: ignore
        )
        logger.info(f"Posted prediction on question {question_id}")
        raise_for_status_with_additional_info(response)

    @classmethod
    def get_question_by_url(cls, question_url: str) -> MetaculusQuestion:
        # URL looks like https://www.metaculus.com/questions/28841/will-eric-adams-be-the-nyc-mayor-on-january-1-2025/
        match = re.search(r"/questions/(\d+)", question_url)
        if not match:
            raise ValueError(
                f"Could not find question ID in URL: {question_url}"
            )
        question_id = int(match.group(1))
        return cls.get_question_by_id(question_id)

    @classmethod
    def get_question_by_id(cls, question_id: int) -> MetaculusQuestion:
        logger.info(f"Retrieving question details for question {question_id}")
        url = f"{cls.API_BASE_URL}/questions/{question_id}/"
        response = requests.get(
            url,
            **cls.AUTH_HEADERS,  # type: ignore
        )
        raise_for_status_with_additional_info(response)
        json_question = json.loads(response.content)
        metaculus_question = MetaculusApi.__metaculus_api_json_to_question(
            json_question
        )
        logger.info(f"Retrieved question details for question {question_id}")
        return metaculus_question

    @classmethod
    def get_all_questions_from_tournament(
        cls,
        tournament_id: int,
        filter_by_open: bool = False,
    ) -> list[MetaculusQuestion]:
        logger.info(f"Retrieving questions from tournament {tournament_id}")
        url_qparams = {
            "limit": cls.MAX_QUESTIONS_FROM_QUESTION_API,
            "offset": 0,
            "has_group": "false",
            "order_by": "-activity",
            "project": tournament_id,
            "type": "forecast",
        }
        if filter_by_open:
            url_qparams["status"] = "open"

        metaculus_questions = cls.__get_questions_from_api(url_qparams)
        logger.info(
            f"Retrieved {len(metaculus_questions)} questions from tournament {tournament_id}"
        )
        return metaculus_questions

    @classmethod
    def get_benchmark_questions(
        cls, num_of_questions_to_return: int
    ) -> list[BinaryQuestion]:
        assert (
            num_of_questions_to_return <= 30
        ), "There are limited questions, with current implementation. You are already losing some randomness at 30"
        est_num_matching_filter = (
            150  # As of Aug 29, there were only 160 questions matching filter
        )
        questions: list[BinaryQuestion] = []
        iterations_to_get_past_estimate = 3
        assert (
            num_of_questions_to_return <= est_num_matching_filter
        ), "There are not enough questions matching the filter"

        for i in range(iterations_to_get_past_estimate):
            limit = cls.MAX_QUESTIONS_FROM_QUESTION_API
            offset = i * limit
            new_questions = (
                cls.__get_general_open_binary_questions_resolving_in_3_months(
                    limit, offset
                )
            )
            questions.extend(new_questions)
        logger.info(
            f"There are {len(questions)} questions matching filter after iterating through {iterations_to_get_past_estimate} pages of {cls.MAX_QUESTIONS_FROM_QUESTION_API} questions that matched the filter"
        )
        qs_with_enough_forecasters = cls.__filter_questions_by_forecasters(
            questions, min_forecasters=40
        )
        qs_with_community_vote_and_enough_forecasters = [
            question
            for question in qs_with_enough_forecasters
            if question.community_prediction_at_access_time is not None
        ]
        logger.info(
            f"Reduced to {len(qs_with_community_vote_and_enough_forecasters)} questions with enough forecasters"
        )
        random_sample = random.sample(
            qs_with_community_vote_and_enough_forecasters,
            num_of_questions_to_return,
        )
        return random_sample

    @classmethod
    def __get_general_open_binary_questions_resolving_in_3_months(
        cls, number_of_questions: int, offset: int = 0
    ) -> Sequence[BinaryQuestion]:
        three_months_from_now = datetime.now() + timedelta(days=90)
        params = {
            "type": "forecast",
            "forecast_type": "binary",
            "status": "open",
            "number_of_forecasters__gte": 40,
            "scheduled_resolve_time__lt": three_months_from_now,
            "order_by": "publish_time",
            "offset": offset,
            "limit": number_of_questions,
        }
        questions = cls.__get_questions_from_api(params)
        checked_questions = typeguard.check_type(
            questions, list[BinaryQuestion]
        )
        return checked_questions

    @classmethod
    def _get_open_binary_questions_from_current_quarterly_cup(
        cls,
    ) -> list[BinaryQuestion]:
        questions = cls.get_all_questions_from_tournament(
            cls.CURRENT_QUARTERLY_CUP_ID,
            filter_by_open=True,
        )
        binary_questions = [
            question
            for question in questions
            if isinstance(question, BinaryQuestion)
        ]
        assert all(
            isinstance(question, BinaryQuestion)
            for question in binary_questions
        )
        return binary_questions  # type: ignore

    @classmethod
    def __get_questions_from_api(
        cls, params: dict[str, Any]
    ) -> list[MetaculusQuestion]:
        num_requested = params.get("limit")
        assert (
            num_requested is None
            or num_requested <= cls.MAX_QUESTIONS_FROM_QUESTION_API
        ), "You cannot get more than 100 questions at a time"
        url = f"{cls.API_BASE_URL}/questions/"
        response = requests.get(url, params=params, **cls.AUTH_HEADERS)  # type: ignore
        raise_for_status_with_additional_info(response)
        data = json.loads(response.content)
        questions = [
            cls.__metaculus_api_json_to_question(q) for q in data["results"]
        ]
        return questions

    @classmethod
    def __metaculus_api_json_to_question(
        cls, api_json: dict
    ) -> MetaculusQuestion:
        question_type = api_json["question"]["type"]  # type: ignore
        if question_type == "binary":
            return BinaryQuestion.from_metaculus_api_json(api_json)
        elif question_type == "numeric":
            return NumericQuestion.from_metaculus_api_json(api_json)
        elif question_type == "multiple_choice":
            return MultipleChoiceQuestion.from_metaculus_api_json(api_json)
        elif question_type == "date":
            return DateQuestion.from_metaculus_api_json(api_json)
        else:
            raise ValueError(f"Unknown question type: {question_type}")

    @classmethod
    def __filter_questions_by_forecasters(
        cls, questions: list[Q], min_forecasters: int
    ) -> list[Q]:
        questions_with_enough_forecasters: list[Q] = []
        for question in questions:
            assert question.num_forecasters is not None
            if question.num_forecasters >= min_forecasters:
                questions_with_enough_forecasters.append(question)
        return questions_with_enough_forecasters
