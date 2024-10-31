# This file is run before any tests are run in order to configure tests

import dotenv
import pytest

from src.util.custom_logger import CustomLogger


@pytest.fixture(scope="session", autouse=True)
def setup_logging() -> None:
    dotenv.load_dotenv()
    CustomLogger.setup_logging()
