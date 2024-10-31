from __future__ import annotations

import json
import logging
from abc import ABC
from typing import Any, TypeVar

from pydantic import BaseModel

from src.util import file_manipulation

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="Jsonable")


class Jsonable(ABC):
    """
    An interface that allows a class to be converted to and from json
    """

    def to_json(self) -> dict:
        if isinstance(self, BaseModel):
            return self._pydantic_model_to_dict(self)
        else:
            raise NotImplementedError(
                f"Class {self.__class__.__name__} does not have a to_json method."
            )

    @classmethod
    def from_json(cls: type[T], json: dict) -> T:
        if issubclass(cls, BaseModel):
            return cls._pydantic_model_from_dict(cls, json)
        else:
            raise NotImplementedError(
                f"Class {cls.__name__} does not have a from_json method. This should be implemented in the subclass."
            )

    @classmethod
    def convert_project_file_path_to_object_list(
        cls: type[T], project_file_path: str
    ) -> list[T]:
        return (
            cls._use__from_json__to_convert_project_file_path_to_object_list(
                project_file_path
            )
        )

    @classmethod
    def _use__from_json__to_convert_project_file_path_to_object_list(
        cls: type[T], project_file_path: str
    ) -> list[T]:
        jsons = file_manipulation.load_json_file(project_file_path)
        assert isinstance(
            jsons, list
        ), f"The json file at {project_file_path} did not contain a list."
        objects = [cls.from_json(json) for json in jsons]
        return objects

    @staticmethod
    def save_object_list_to_file_path(
        objects: list[T], file_path_from_top_of_project: str
    ) -> None:
        file_manipulation.write_json_file(
            file_path_from_top_of_project,
            [object.to_json() for object in objects],
        )

    @staticmethod
    def _pydantic_model_to_dict(pydantic_model: BaseModel) -> dict:
        json_string: str = pydantic_model.model_dump_json()
        json_dict: dict = json.loads(json_string)
        return json_dict

    @staticmethod
    def _pydantic_model_from_dict(
        cls_type: type[BaseModel], json_dict: dict
    ) -> Any:
        json_string: str = json.dumps(json_dict)
        return cls_type.model_validate_json(json_string)