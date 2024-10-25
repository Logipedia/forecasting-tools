import os
import json
import datetime as dat
import pandas as pd
import functools
from typing import Callable, Any

NAME_OF_PACKAGE: str = "pro_con_searcher"


def get_absolute_path(path_in_package: str = "") -> str:
    """
    This function returns the absolute path of a file in the package
    If there is no parameter given, it will just give the absolute path of the package
    @param path_in_package: The path of the file in the package starting just after the package name (e.g. "data/claims.csv")
    """

    # Get the path of the current file
    current_file_path = os.path.abspath(__file__)

    # Get the absolute path of the package that the function is in
    package_path = os.path.dirname(current_file_path)
    while os.path.basename(package_path) != NAME_OF_PACKAGE:
        package_path = os.path.dirname(package_path)

    # Get the absolute path of the file in the package
    file_path = str(os.path.join(package_path, path_in_package))

    return file_path


def skip_if_file_writing_not_allowed(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs): # NOSONAR
        not_allowed_to_write_to_files_string: str = os.environ.get("FILE_WRITING_ALLOWED", "TRUE")
        is_allowed = not_allowed_to_write_to_files_string.upper() == "TRUE"
        if is_allowed:
            return func(*args, **kwargs)
        else:
            print("WARNING: Skipping function execution as file writing is not allowed.")
            return None
    return wrapper





def load_json_file(project_file_path: str) -> list[dict]:
    """
    This function loads a json file. Output can be dictionary or list of dictionaries (or other json objects)
    @param project_file_path: The path of the json file starting from top of package
    """
    full_file_path = get_absolute_path(project_file_path)
    with open(full_file_path, "r") as file:
        return json.load(file)


def csv_to_dataframe(file_path_in_package: str, delimiter: str = ",") -> pd.DataFrame:
    """
    This function converts a csv file into a pandas dataframe
    """
    full_file_path = get_absolute_path(file_path_in_package)
    return pd.read_csv(full_file_path, sep=delimiter)


def load_text_file(file_path_in_package: str) -> str:
    full_file_path = get_absolute_path(file_path_in_package)
    with open(full_file_path, "r") as file:
        return file.read()



def write_json_file(file_path_in_package: str, input: list[dict]) -> None:
    json_string = json.dumps(input, indent=4)
    create_or_overwrite_file(file_path_in_package, json_string)


@skip_if_file_writing_not_allowed
def create_or_overwrite_file(file_path_in_package: str, text: str) -> None:
    """
    This function writes text to a file, and creates the file if it does not exist
    """
    full_file_path = get_absolute_path(file_path_in_package)
    os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
    with open(full_file_path, 'w') as file:
        file.write(text)


@skip_if_file_writing_not_allowed
def create_or_append_to_file(file_path_in_package: str, text: str) -> None:
    """
    This function appends text to a file, and creates the file if it does not exist
    """
    full_file_path = get_absolute_path(file_path_in_package)
    os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
    with open(full_file_path, 'a') as file:
        file.write(text)


@skip_if_file_writing_not_allowed
def write_dataframe_to_csv_file(dataframe: pd.DataFrame, file_path_in_package: str, delimiter: str = ",") -> None:
    """
    This function converts a pandas dataframe into a csv file
    """
    full_file_path = get_absolute_path(file_path_in_package)
    os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
    dataframe.to_csv(full_file_path, sep=delimiter, index=False)


@skip_if_file_writing_not_allowed
def log_to_file(file_path_in_package: str, text: str, type: str = "DEBUG") -> None:
    """
    This function writes text to a file but adds a time stamp and a type statement
    """
    new_text = f"{type} - {dat.datetime.now()} - {text}"
    full_file_path = get_absolute_path(file_path_in_package)
    os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
    with open(full_file_path, 'a+') as file:
        file.write(new_text + "\n")


def current_date_time_string() -> str:
    return dat.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


if __name__ == "__main__":
    """
    This is the "main" code area, and can be used for quickly sandboxing and testing functions
    """
    pass