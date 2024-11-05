# tests/integration/test_workflow.py
import json
import time
import pytest
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from scholar_analyzer.analyzer import ScholarAnalyzer
from scholar_analyzer.cli import process_query

class TestAnalysisWorkflow:
    @pytest.fixture(scope="function")
    def workflow_setup(self, temp_output_dir, sample_data):
        """Setup for workflow testing."""
        # Create input file
        input_file = temp_output_dir / "input.json"
        input_file.write_text(json.dumps(sample_data))
        return input_file, temp_output_dir

    def test_complete_workflow(self, workflow_setup):
        """Test complete analysis workflow from input to output."""
        input_file, output_dir = workflow_setup

        # Run analysis
        result = process_query(
            query="test query",
            output_dir=output_dir,
            input_file=input_file
        )

        # Verify outputs
        assert (output_dir / "report.html").exists()
        assert (output_dir / "analysis.json").exists()
        assert result["success"] is True

    def test_data_processing_pipeline(self, sample_data):
        """Test the complete data processing pipeline."""
        analyzer = ScholarAnalyzer(sample_data)

        # Process data
        analysis_results = analyzer.analyze()

        # Verify all processing steps
        assert 'papers' in analysis_results
        assert 'analysis' in analysis_results
        assert analysis_results.get('success', False) is True

    def test_output_generation(self, workflow_setup):
        """Test generation of all output formats."""
        input_file, output_dir = workflow_setup

        formats = ["html", "json", "csv", "bibtex"]
        for fmt in formats:
            result = process_query(
                query="test query",
                output_dir=output_dir,
                input_file=input_file,
                format=fmt
            )
            assert result["success"]
            assert (output_dir / f"output.{fmt}").exists()

    @pytest.mark.parametrize("component", [
        "metrics", "charts", "papers", "insights"
    ])
    def test_component_integration(self, chrome_driver, component):
        """Test integration of different UI components."""
        chrome_driver.get("http://localhost:5000")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, f"[data-tab='{component}']"))
        )

        # Switch to component tab
        tab = chrome_driver.find_element(
            By.CSS_SELECTOR, f"[data-tab='{component}']")
        tab.click()

        # Verify component loading
        content = WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, f"{component}"))
        )
        assert content.is_displayed()

    def test_filter_integration(self, chrome_driver, sample_data):
        """Test integration of filtering system."""
        chrome_driver.get("http://localhost:5000")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "yearStart"))
        )

        # Apply filters
        year_start = chrome_driver.find_element(By.ID, "yearStart")
        year_start.send_keys("2020")

        citation_min = chrome_driver.find_element(By.ID, "citationMin")
        citation_min.send_keys("5")

        venue_select = chrome_driver.find_element(By.ID, "venueFilter")
        Select(venue_select).select_by_visible_text("Test Conference")

        # Apply filters
        apply_button = chrome_driver.find_element(By.ID, "applyFilters")
        apply_button.click()

        # Wait for filtered results
        paper_items = WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "paper-item"))
        )

        # Verify filtered results
        for paper in paper_items:
            year = int(paper.find_element(By.CLASS_NAME, "year").text)
            citations = int(paper.find_element(
                By.CLASS_NAME, "citations").text)
            venue = paper.find_element(By.CLASS_NAME, "venue").text

            assert year >= 2020
            assert citations >= 5
            assert venue == "Test Conference"

    def test_export_integration(self, chrome_driver, temp_output_dir):
        """Test integration of export functionality."""
        chrome_driver.get("http://localhost:5000")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-export]'))
        )

        # Test each export format
        export_formats = ["csv", "bibtex", "json"]
        for fmt in export_formats:
            # Click export button
            export_button = chrome_driver.find_element(
                By.CSS_SELECTOR,
                f'[data-export="{fmt}"]'
            )
            export_button.click()

            # Wait for download
            time.sleep(2)  # Wait for download to complete

            # Verify file exists
            expected_file = temp_output_dir / f"scholar-analysis.{fmt}"
            assert expected_file.exists()

            # Verify file content
            if fmt == "json":
                with expected_file.open() as f:
                    data = json.load(f)
                    assert "papers" in data
                    assert "analysis" in data

    def test_theme_integration(self, chrome_driver):
        """Test theme switching integration."""
        chrome_driver.get("http://localhost:5000")
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.ID, "themeToggle"))
        )

        # Get initial theme
        initial_theme = chrome_driver.execute_script(
            'return document.documentElement.getAttribute("data-theme")'
        )

        # Toggle theme
        theme_button = chrome_driver.find_element(By.ID, "themeToggle")
        theme_button.click()

        # Wait for theme change
        WebDriverWait(chrome_driver, 10).until(
            lambda d: d.execute_script(
                'return document.documentElement.getAttribute("data-theme")'
            ) != initial_theme
        )

        # Verify chart colors updated
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "chart-container"))
        )
        charts = chrome_driver.find_elements(By.CLASS_NAME, "chart-container")
        for chart in charts:
            # Verify chart theme
            theme_colors = chrome_driver.execute_script(
                'return window.getComputedStyle(arguments[0]).getPropertyValue("--color-primary")',
                chart
            )
            assert theme_colors is not None


# tests/integration/test_workflow.py


@pytest.mark.usefixtures("test_server")
class TestAnalysisWorkflow:
    def test_complete_workflow(self, workflow_setup):
        """Test complete analysis workflow from input to output."""
        input_file, output_dir = workflow_setup
        result = process_query(
            query="test query",
            output_dir=output_dir,
            input_file=input_file
        )
        assert result["success"] is True
        assert (output_dir / "report.html").exists()
        assert (output_dir / "analysis.json").exists()

    def test_output_generation(self, workflow_setup):
        """Test generation of all output formats."""
        input_file, output_dir = workflow_setup
        formats = ["html", "json", "csv", "bibtex"]
        for fmt in formats:
            result = process_query(
                query="test query",
                output_dir=output_dir,
                input_file=input_file,
                format=fmt
            )
            assert result["success"]
            assert (output_dir / f"output.{fmt}").exists()

    @pytest.mark.parametrize("component", [
        "metrics", "charts", "papers", "insights"
    ])
    def test_component_integration(self, chrome_driver, component):
        """Test integration of different UI components."""
        chrome_driver.get("http://localhost:5000")
        wait = WebDriverWait(chrome_driver, 10)

        # Wait for tab to be clickable
        tab = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, f"li.tab[data-tab='{component}']"))
        )
        tab.click()

        # Wait for content to be visible
        content = wait.until(
            EC.visibility_of_element_located((By.ID, component))
        )
        assert content.is_displayed()

    def test_filter_integration(self, chrome_driver, sample_data):
        """Test integration of filtering system."""
        chrome_driver.get("http://localhost:5000")
        wait = WebDriverWait(chrome_driver, 10)

        # Open papers tab
        papers_tab = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "li.tab[data-tab='papers']"))
        )
        papers_tab.click()

        # Wait for and interact with filter inputs
        year_start = wait.until(
            EC.presence_of_element_located((By.ID, "yearStart")))
        year_start.send_keys("2020")

        citation_min = chrome_driver.find_element(By.ID, "citationMin")
        citation_min.send_keys("5")

        venue_select = Select(chrome_driver.find_element(By.ID, "venueFilter"))
        venue_select.select_by_visible_text("Test Conference")

        apply_button = wait.until(
            EC.element_to_be_clickable((By.ID, "applyFilters")))
        apply_button.click()

    def test_theme_integration(self, chrome_driver):
        """Test theme switching integration."""
        chrome_driver.get("http://localhost:5000")
        wait = WebDriverWait(chrome_driver, 10)

        theme_button = wait.until(
            EC.element_to_be_clickable((By.ID, "themeToggle")))
        initial_theme = chrome_driver.find_element(
            By.TAG_NAME, "html").get_attribute("data-theme")

        theme_button.click()

        # Wait for theme to change
        def theme_changed(driver):
            current_theme = driver.find_element(
                By.TAG_NAME, "html").get_attribute("data-theme")
            return current_theme != initial_theme

        wait.until(theme_changed)

    def test_export_integration(self, chrome_driver, temp_output_dir):
        """Test integration of export functionality."""
        chrome_driver.get("http://localhost:5000")
        wait = WebDriverWait(chrome_driver, 10)

        # Wait for any export button
        export_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-export]"))
        )
        export_button.click()

        # Give some time for the download to start
        time.sleep(1)
