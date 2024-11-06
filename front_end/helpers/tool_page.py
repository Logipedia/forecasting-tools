from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import streamlit as st
from pydantic import BaseModel

from forecasting_tools.util.file_manipulation import load_json_file
from forecasting_tools.util.jsonable import Jsonable
from front_end.helpers.app_page import AppPage

logger = logging.getLogger(__name__)


class Example(Jsonable, BaseModel):
    input: dict
    output: dict


class ToolPage(AppPage, ABC):
    OUTPUT_TYPE: type[Jsonable] = Jsonable
    INPUT_TYPE: type[Jsonable] = Jsonable
    EXAMPLES_FILE_PATH: str | None = NotImplemented

    def __init_subclass__(cls: type[ToolPage], *args, **kwargs) -> None:
        super().__init_subclass__(*args, **kwargs)
        is_abstract = ABC in cls.__bases__
        if not is_abstract:
            if cls.OUTPUT_TYPE is Jsonable or not issubclass(
                cls.OUTPUT_TYPE, Jsonable
            ):
                raise NotImplementedError(
                    "You forgot to define OUTPUT_TYPE as a subclass of Jsonable"
                )
            if cls.INPUT_TYPE is Jsonable or not issubclass(
                cls.INPUT_TYPE, Jsonable
            ):
                raise NotImplementedError(
                    "You forgot to define INPUT_TYPE as a subclass of Jsonable"
                )
            if cls.EXAMPLES_FILE_PATH is NotImplemented:
                raise NotImplementedError(
                    "You forgot to define EXAMPLES_FILE_PATH"
                )

    @classmethod
    async def _async_main(cls) -> None:
        st.title(cls.PAGE_DISPLAY_NAME)
        await cls._display_intro_text()
        await cls._show_example_buttons()
        input_to_tool = await cls._get_input()
        if input_to_tool:
            assert isinstance(input_to_tool, cls.INPUT_TYPE)
            output = await cls._run_tool(input_to_tool)
            assert isinstance(output, cls.OUTPUT_TYPE)
            await cls._save_run(input_to_tool, output)
        outputs = await cls._get_saved_outputs()
        if outputs:
            await cls._display_outputs(outputs)

    @classmethod
    @abstractmethod
    async def _display_intro_text(cls) -> None:
        pass

    @classmethod
    async def _show_example_buttons(cls) -> None:
        examples = await cls._get_example_input_output_pairs()
        if examples:
            with st.expander("📋 Premade Examples", expanded=False):
                cols = st.columns(len(examples))
                for index, example in enumerate(examples):
                    with cols[index]:
                        button_label = f"Show Example {index + 1}"
                        if st.button(button_label, use_container_width=True):
                            input_to_tool = cls.INPUT_TYPE.from_json(
                                example.input
                            )
                            output = cls.OUTPUT_TYPE.from_json(example.output)
                            await cls._save_run(
                                input_to_tool, output, is_premade=True
                            )

    @classmethod
    async def _get_example_input_output_pairs(cls) -> list[Example]:
        if cls.EXAMPLES_FILE_PATH is None:
            return []
        examples_raw = load_json_file(cls.EXAMPLES_FILE_PATH)
        examples = [Example.from_json(ex) for ex in examples_raw]
        return examples

    @classmethod
    @abstractmethod
    async def _get_input(cls) -> Any:
        pass

    @classmethod
    @abstractmethod
    async def _run_tool(cls, input: Any) -> Jsonable:
        pass

    @classmethod
    async def _save_run(
        cls, input_to_tool: Jsonable, output: Jsonable, is_premade=False
    ) -> None:
        assert isinstance(output, cls.OUTPUT_TYPE)
        await cls._save_output_to_browser_storage(output)
        try:
            await cls._save_run_to_coda(input_to_tool, output, is_premade)
        except Exception as e:
            logger.error(f"Error saving output to Coda: {e}")
        if not is_premade:
            try:
                await cls._save_output_to_file(input_to_tool, output)
            except Exception as e:
                logger.error(f"Error saving output to file: {e}")

    @classmethod
    @abstractmethod
    async def _save_run_to_coda(
        cls, input_to_tool: Jsonable, output: Jsonable, is_premade: bool
    ) -> None:
        pass

    @classmethod
    async def _save_output_to_browser_storage(cls, output: Jsonable) -> None:
        assert isinstance(output, cls.OUTPUT_TYPE)
        session_state_key = cls.__get_saved_outputs_key()
        if session_state_key not in st.session_state:
            st.session_state[session_state_key] = []
        st.session_state[session_state_key].insert(0, output)

    @classmethod
    async def _save_output_to_file(
        cls, input_to_tool: Jsonable, output: Jsonable
    ) -> None:
        assert isinstance(output, cls.OUTPUT_TYPE)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"logs/forecasts/streamlit/{timestamp}_{cls.__name__}.json"
        Example.save_object_list_to_file_path(
            [Example(input=input_to_tool.to_json(), output=output.to_json())],
            file_path,
        )

    @classmethod
    async def _get_saved_outputs(cls) -> list[Jsonable]:
        session_state_key = cls.__get_saved_outputs_key()
        if session_state_key not in st.session_state:
            st.session_state[session_state_key] = []
        outputs = st.session_state[session_state_key]
        validated_outputs = [
            cls.OUTPUT_TYPE.from_json(output.to_json()) for output in outputs
        ]
        return validated_outputs

    @classmethod
    def __get_saved_outputs_key(cls) -> str:
        return f"{cls.__name__}_saved_outputs"

    @classmethod
    @abstractmethod
    async def _display_outputs(cls, outputs: list[Jsonable]) -> None:
        pass
