import os
import re
from unittest.mock import Mock, mock_open, patch

from forecasting_tools.util import file_manipulation


class TestFileManipulationData:
    ALLOW_WRITING_DICT = {"FILE_WRITING_ALLOWED": "TRUE"}
    DISALLOW_WRITING_DICT = {"FILE_WRITING_ALLOWED": "FALSE"}
    FILE_PATH = "temp/file_manipulation_test.txt"


def test_read_file_of_inner_package() -> None:
    file_path_to_code_file = "forecasting_tools/util/file_manipulation.py"
    file_contents = file_manipulation.load_text_file(file_path_to_code_file)
    assert file_contents is not None
    assert "import" in file_contents


def test_read_file_of_outer_package() -> None:
    file_path_to_gitignore_file = ".gitignore"
    file_contents = file_manipulation.load_text_file(
        file_path_to_gitignore_file
    )
    assert file_contents is not None
    assert ".env" in file_contents


@patch("builtins.open", new_callable=mock_open)
@patch("os.makedirs")
def test_create_or_overwrite_file(mock_makedirs, mock_open_file):
    test_file = TestFileManipulationData.FILE_PATH
    with patch.dict(
        os.environ, TestFileManipulationData.DISALLOW_WRITING_DICT
    ):
        file_manipulation.create_or_overwrite_file(test_file, "test content")
        mock_open_file.assert_not_called()

    with patch.dict(os.environ, TestFileManipulationData.ALLOW_WRITING_DICT):
        file_manipulation.create_or_overwrite_file(test_file, "test content")
        mock_makedirs.assert_called_once()
        mock_open_file.assert_called_once_with(
            file_manipulation.get_absolute_path(test_file), "w"
        )


@patch("builtins.open", new_callable=mock_open)
@patch("os.makedirs")
def test_create_or_append_to_file(
    mock_makedirs: Mock, mock_open_file: Mock
) -> None:
    test_file = TestFileManipulationData.FILE_PATH
    with patch.dict(
        os.environ, TestFileManipulationData.DISALLOW_WRITING_DICT
    ):
        file_manipulation.create_or_append_to_file(test_file, "test content")
        mock_open_file.assert_not_called()

    with patch.dict(os.environ, TestFileManipulationData.ALLOW_WRITING_DICT):
        file_manipulation.create_or_append_to_file(test_file, "test content")
        mock_makedirs.assert_called_once()
        mock_open_file.assert_called_once_with(
            file_manipulation.get_absolute_path(test_file), "a"
        )


@patch("builtins.open", new_callable=mock_open)
@patch("os.makedirs")
def test_log_to_file(mock_makedirs: Mock, mock_open_file: Mock) -> None:
    test_file = TestFileManipulationData.FILE_PATH
    with patch.dict(
        os.environ, TestFileManipulationData.DISALLOW_WRITING_DICT
    ):
        file_manipulation.log_to_file(test_file, "test log")
        mock_open_file.assert_not_called()

    with patch.dict(os.environ, TestFileManipulationData.ALLOW_WRITING_DICT):
        file_manipulation.log_to_file(test_file, "test log")
        mock_makedirs.assert_called_once()
        mock_open_file.assert_called_once_with(
            file_manipulation.get_absolute_path(test_file), "a+"
        )


def find__with_open__usage(
    directory: str, excluded_files: list[str]
) -> list[str]:
    pattern = re.compile(r"\bwith\s+open\(")
    violations = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file not in excluded_files:
                file_path = os.path.join(root, file)
                file_contents = file_manipulation.load_text_file(file_path)
                if pattern.search(file_contents):
                    violations.append(file_path)
    return violations


def test_no_with_open_usage() -> None:
    file_manipulation_name = file_manipulation.__name__.split(".")[-1] + ".py"
    excluded_files: list[str] = [file_manipulation_name]

    directory_to_check = file_manipulation.get_absolute_path("src")
    violations = find__with_open__usage(directory_to_check, excluded_files)
    assert (
        not violations
    ), f"Found 'with open()' usage in the following files: {violations}. Only use 'with open()' in {file_manipulation_name}"
