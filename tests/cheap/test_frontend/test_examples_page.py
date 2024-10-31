from front_end.mokoresearch_site.app_pages.example_forecasts import (
    ExampleForecastsPage,
)
from front_end.mokoresearch_site.helpers.report_displayer import (
    ReportDisplayer,
)
from tests.cheap.test_frontend.front_end_test_utils import FrontEndTestUtils


def test_examples_are_on_page() -> None:
    app_test = FrontEndTestUtils.convert_page_to_app_tester(
        ExampleForecastsPage
    )
    app_test.run()
    expected_reports = ExampleForecastsPage.get_example_reports()
    FrontEndTestUtils.assert_x_valid_forecast_reports_are_on_the_page(
        app_test, expected_reports
    )


def test_all_markdown_is_clean_after_reports_displayed() -> None:
    app_test = FrontEndTestUtils.convert_page_to_app_tester(
        ExampleForecastsPage
    )
    app_test.run()
    all_markdown = app_test.markdown
    for markdown_element in all_markdown:
        assert ReportDisplayer.markdown_is_clean(markdown_element.value)
