import logging

from streamlit.testing.v1 import AppTest

from front_end.mokoresearch_site.helpers.report_displayer import ReportDisplayer
from front_end.mokoresearch_site.Home import AppPage
from src.forecasting.forecast_reports.binary_report import BinaryReport

logger = logging.getLogger(__name__)


class FrontEndTestUtils:

    @staticmethod
    def convert_page_to_app_tester(app_page: type[AppPage]) -> AppTest:
        module_name = app_page.__module__
        project_path = module_name.replace(".", "/") + ".py"
        app_test = AppTest.from_file(project_path, default_timeout=600)
        return app_test

    @classmethod
    def assert_x_valid_forecast_reports_are_on_the_page(
        cls,
        app_test: AppTest,
        reports: list[BinaryReport],
    ) -> None:
        if len(reports) == 0:
            logger.warning("No reports to display")
            return
        reports = ReportDisplayer._make_new_list_of_sorted_reports(reports)
        num_reports_expected = len(reports)
        report_selectbox = app_test.selectbox(ReportDisplayer.REPORT_SELECTBOX_KEY)
        assert len(report_selectbox.options) == num_reports_expected
        assert not app_test.exception, f"Exception occurred: {app_test.exception}"
        assert num_reports_expected > 0
        for i, _ in enumerate(report_selectbox.options):
            report_selectbox = app_test.selectbox(ReportDisplayer.REPORT_SELECTBOX_KEY)
            report_selectbox.select(i)
            app_test.run()
            assert not app_test.exception, f"Exception occurred: {app_test.exception}"
            expected_markdown = reports[i].explanation
            cls.__assert_correct_number_of_sections(app_test, expected_markdown)
            cls.__assert_report_text_matches_expected(app_test, expected_markdown)

    @classmethod
    def __assert_correct_number_of_sections(
        cls, app_test: AppTest, expected_report_markdown: str
    ) -> None:
        expanders_within_tabs = [
            expander for tab in app_test.tabs for expander in tab.expander
        ]
        num_h1_headers = cls.__count_num_headers(1, expected_report_markdown)
        assert (
            len(app_test.tabs) >= num_h1_headers
            or len(app_test.tabs) <= num_h1_headers + 2
        ), f"Expected {num_h1_headers} to {num_h1_headers + 2} tabs (There can be a starting section without a header, and an extra question section), but got {len(app_test.tabs)}"
        num_h2_headers = cls.__count_num_headers(2, expected_report_markdown)
        assert (
            len(expanders_within_tabs) == num_h2_headers
        ), f"Expected {num_h2_headers} expanders, but got {len(expanders_within_tabs)}"

    @classmethod
    def __assert_report_text_matches_expected(
        cls, app_test: AppTest, expected_report_markdown: str
    ) -> None:
        actual_combined_explanation = ""
        for tab in app_test.tabs:
            for markdown in tab.markdown:
                actual_combined_explanation += markdown.value

        expected_explanation_compressed = ReportDisplayer.clean_markdown(
            expected_report_markdown
        ).replace("\n", "")
        actual_combined_explanation_compressed = ReportDisplayer.clean_markdown(
            actual_combined_explanation
        ).replace("\n", "")
        assert (
            expected_explanation_compressed in actual_combined_explanation_compressed
        ), f"Explanation does not match, expected '{expected_explanation_compressed}', got '{actual_combined_explanation_compressed}'"

    @staticmethod
    def __count_num_headers(heading_level: int, explanation: str) -> int:
        header_as_hashtags = "#" * heading_level + " "
        return sum(
            1
            for line in explanation.splitlines()
            if line.strip().startswith(header_as_hashtags)
        )
