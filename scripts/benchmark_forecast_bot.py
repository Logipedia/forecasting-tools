from __future__ import annotations

import asyncio
import logging
import os
import sys

import dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
top_level_dir = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.append(top_level_dir)
dotenv.load_dotenv()

from forecasting_tools.ai_models.resource_managers.monetary_cost_manager import (
    MonetaryCostManager,
)
from forecasting_tools.forecasting.team_manager import TeamManager
from forecasting_tools.util.custom_logger import CustomLogger

logger = logging.getLogger(__name__)


async def benchmark_forecast_bot() -> None:
    with MonetaryCostManager() as cost_manager:
        team_manager = TeamManager(time_to_wait_between_questions=65)
        score = await team_manager.benchmark_forecast_team("medium")
        logger.info(f"Total Cost: {cost_manager.current_usage}")
        logger.info(f"Final Score: {score}")


if __name__ == "__main__":
    CustomLogger.setup_logging()
    asyncio.run(benchmark_forecast_bot())
