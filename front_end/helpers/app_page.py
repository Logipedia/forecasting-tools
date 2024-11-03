from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod

import streamlit as st
from streamlit.navigation.page import StreamlitPage


class AppPage(ABC):
    PAGE_DISPLAY_NAME: str = NotImplemented
    URL_PATH: str = NotImplemented
    IS_DEFAULT_PAGE: bool = False

    def __init_subclass__(cls: type[AppPage], *args, **kwargs) -> None:
        super().__init_subclass__(*args, **kwargs)
        is_abstract = ABC in cls.__bases__
        if not is_abstract:
            if cls.PAGE_DISPLAY_NAME is NotImplemented:
                raise NotImplementedError(
                    "You forgot to define PAGE_DISPLAY_NAME"
                )
            if cls.URL_PATH is NotImplemented:
                raise NotImplementedError("You forgot to define URL_PATH")

    @classmethod
    def main(cls) -> None:
        asyncio.run(cls._async_main())

    @classmethod
    @abstractmethod
    async def _async_main(cls) -> None:
        pass

    @classmethod
    def convert_to_streamlit_page(cls) -> StreamlitPage:
        page = st.Page(
            cls.main,
            title=cls.PAGE_DISPLAY_NAME,
            icon=None,
            url_path=cls.URL_PATH,
            default=cls.IS_DEFAULT_PAGE,
        )
        return page
