from __future__ import annotations

import os
import sys

import dotenv

# # Dynamically determine the absolute path to the top-level directory
# current_dir = os.path.dirname(os.path.abspath(__file__))
# top_level_dir = os.path.abspath(os.path.join(current_dir, "../"))
# sys.path.append(top_level_dir)
# dotenv.load_dotenv()

import asyncio
import logging

from src.ai_models.resource_managers.monetary_cost_manager import MonetaryCostManager
from src.forecasting.team_manager import TeamManager
from src.util.custom_logger import CustomLogger


async def benchmark_forecast_bot() -> None:
    CustomLogger.setup_logging()
    logger = logging.getLogger(__name__)

    with MonetaryCostManager() as cost_manager:
        team_manager = TeamManager(time_to_wait_between_questions=65)
        score = await team_manager.benchmark_forecast_team("medium")
        logger.critical(f"Total Cost: {cost_manager.current_usage}")
        logger.critical(f"Final Score: {score}")


if __name__ == "__main__":
    dotenv.load_dotenv()
    asyncio.run(benchmark_forecast_bot())
