import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestUIComponents:
    def test_metric_cards(self, chrome_driver):
        """Test metric cards display and interactions."""
        chrome_driver.get("http://localhost:5000")

        # Test all metric cards
        metric_cards = chrome_driver.find_elements(
            By.CLASS_NAME, "metric-card")
        for card in metric_cards:
            # Verify structure
            assert card.find_element(By.CLASS_NAME, "metric-value")
            assert card.find_element(By.CLASS_NAME, "metric-trend")

            # Test hover effect
            chrome_driver.execute_script(
                "arguments[0].dispatchEvent(new Event('mouseenter'))",
                card
            )

            # Verify hover state
            hover_style = chrome_driver.execute_script(
                "return window.getComputedStyle(arguments[0])",
                card
            )
            assert "transform" in hover_style.cssText

    def test_data_table(self, chrome_driver):
        """Test data table functionality."""
        chrome_driver.get("http://localhost:5000")

        # Switch to papers tab
        papers_tab = chrome_driver.find_element(
            By.CSS_SELECTOR, '[data-tab="papers"]')
        papers_tab.click()

        # Test sorting
        headers = chrome_driver.find_elements(By.CSS_SELECTOR, "th.sortable")
        for header in headers:
            header.click()
            # Verify sort indicator
            assert "sorted" in header.get_attribute("class")

        # Test pagination
        pagination = chrome_driver.find_element(By.CLASS_NAME, "pagination")
        assert pagination.find_elements(By.TAG_NAME, "button")

        # Test search
        search = chrome_driver.find_element(By.CLASS_NAME, "table-search")
        search.send_keys("test")

        # Verify filtered results
        WebDriverWait(chrome_driver, 10).until(
            lambda d: len(d.find_elements(By.CLASS_NAME, "table-row")) > 0
        )

    def test_chart_cards(self, chrome_driver):
        """Test chart cards and their controls."""
        chrome_driver.get("http://localhost:5000")

        chart_cards = chrome_driver.find_elements(By.CLASS_NAME, "chart-card")
        for card in chart_cards:
            # Test controls
            controls = card.find_elements(By.CLASS_NAME, "chart-control")
            for control in controls:
                control.click()
                # Verify control action
                if "download" in control.get_attribute("data-action"):
                    # Verify download started
                    pass
                elif "fullscreen" in control.get_attribute("data-action"):
                    # Verify fullscreen mode
                    WebDriverWait(chrome_driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, "fullscreen"))
                    )

    def test_filter_components(self, chrome_driver):
        """Test filter components functionality."""
        chrome_driver.get("http://localhost:5000")

        # Test range inputs
        range_inputs = chrome_driver.find_elements(
            By.CLASS_NAME, "range-input")
        for input_elem in range_inputs:
            input_elem.clear()
            input_elem.send_keys("10")

            # Verify validation
            assert "invalid" not in input_elem.get_attribute("class")

        # Test select components
        selects = chrome_driver.find_elements(By.TAG_NAME, "select")
        for select in selects:
            Select(select).select_by_index(1)

            # Verify selection
            assert Select(select).first_selected_option.is_selected()

        # Test filter tags
        filter_tags = chrome_driver.find_elements(By.CLASS_NAME, "filter-tag")
        for tag in filter_tags:
            # Test remove button
            remove_btn = tag.find_element(By.CLASS_NAME, "remove-filter")
            remove_btn.click()

            # Verify tag removed
            WebDriverWait(chrome_driver, 10).until(
                EC.staleness_of(tag)
            )

    def test_tooltips(self, chrome_driver):
        """Test tooltip functionality."""
        chrome_driver.get("http://localhost:5000")

        tooltip_elements = chrome_driver.find_elements(
            By.CSS_SELECTOR,
            "[data-tooltip]"
        )

        for element in tooltip_elements:
            # Hover over element
            chrome_driver.execute_script(
                "arguments[0].dispatchEvent(new Event('mouseenter'))",
                element
            )

            # Verify tooltip appears
            WebDriverWait(chrome_driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tooltip"))
            )

            tooltip = chrome_driver.find_element(By.CLASS_NAME, "tooltip")
            assert tooltip.is_displayed()

            # Verify tooltip content
            assert tooltip.text == element.get_attribute("data-tooltip")

    def test_modal_components(self, chrome_driver):
        """Test modal components."""
        chrome_driver.get("http://localhost:5000")

        # Find elements that trigger modals
        modal_triggers = chrome_driver.find_elements(
            By.CSS_SELECTOR,
            "[data-modal]"
        )

        for trigger in modal_triggers:
            trigger.click()

            # Verify modal appears
            modal = WebDriverWait(chrome_driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "modal"))
            )

            # Test modal structure
            assert modal.find_element(By.CLASS_NAME, "modal-header")
            assert modal.find_element(By.CLASS_NAME, "modal-content")
            assert modal.find_element(By.CLASS_NAME, "modal-footer")

            # Test close button
            close_btn = modal.find_element(By.CLASS_NAME, "modal-close")
            close_btn.click()

            # Verify modal closes
            WebDriverWait(chrome_driver, 10).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "modal"))
            )
