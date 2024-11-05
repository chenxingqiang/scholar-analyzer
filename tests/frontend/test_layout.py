import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestLayout:
    def test_responsive_grid(self, chrome_driver):
        """Test responsive grid layout at different viewport sizes."""
        viewport_sizes = [
            (1920, 1080),  # Desktop
            (1024, 768),   # Tablet Landscape
            (768, 1024),   # Tablet Portrait
            (375, 812)     # Mobile
        ]

        for width, height in viewport_sizes:
            chrome_driver.set_window_size(width, height)
            chrome_driver.get("http://localhost:5000")

            content_wrapper = chrome_driver.find_element(
                By.CLASS_NAME, "content-wrapper")
            display = chrome_driver.execute_script(
                "return window.getComputedStyle(arguments[0]).display",
                content_wrapper
            )

            if width >= 992:
                assert display == "grid"
            else:
                assert display == "block"

    def test_filter_panel_visibility(self, chrome_driver):
        """Test filter panel visibility and toggle functionality."""
        chrome_driver.get("http://localhost:5000")

        # Test initial state
        filter_panel = chrome_driver.find_element(
            By.CLASS_NAME, "filters-panel")
        is_visible = filter_panel.is_displayed()

        # Test toggle functionality
        toggle_button = chrome_driver.find_element(By.ID, "filterToggle")
        toggle_button.click()

        WebDriverWait(chrome_driver, 10).until(
            lambda d: filter_panel.get_attribute("class").find("active") != -1
        )

        # Test panel position
        panel_style = chrome_driver.execute_script(
            "return window.getComputedStyle(arguments[0])",
            filter_panel
        )
        assert "position: sticky" in panel_style.cssText

    def test_chart_grid_layout(self, chrome_driver):
        """Test chart grid layout and responsiveness."""
        chrome_driver.get("http://localhost:5000")

        chart_grid = chrome_driver.find_element(By.CLASS_NAME, "chart-grid")
        charts = chart_grid.find_elements(By.CLASS_NAME, "chart-card")

        # Test number of charts
        assert len(charts) > 0

        # Test chart dimensions
        for chart in charts:
            size = chart.size
            assert size['width'] > 0
            assert size['height'] > 0

    def test_fullscreen_mode(self, chrome_driver):
        """Test chart fullscreen functionality."""
        chrome_driver.get("http://localhost:5000")

        # Find first chart and its fullscreen button
        chart_card = chrome_driver.find_element(By.CLASS_NAME, "chart-card")
        fullscreen_btn = chart_card.find_element(
            By.CSS_SELECTOR,
            "[data-chart-action='fullscreen']"
        )

        # Click fullscreen button
        fullscreen_btn.click()

        # Verify fullscreen state
        WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "fullscreen"))
        )

        fullscreen_element = chrome_driver.find_element(
            By.CLASS_NAME, "fullscreen")
        assert fullscreen_element.is_displayed()

    @pytest.mark.parametrize("device", ["desktop", "tablet", "mobile"])
    def test_header_layout(self, chrome_driver, device):
        """Test header layout across different devices."""
        viewport_sizes = {
            "desktop": (1920, 1080),
            "tablet": (768, 1024),
            "mobile": (375, 812)
        }

        width, height = viewport_sizes[device]
        chrome_driver.set_window_size(width, height)
        chrome_driver.get("http://localhost:5000")

        header = chrome_driver.find_element(By.CLASS_NAME, "app-header")
        header_content = header.find_element(By.CLASS_NAME, "header-content")

        if device == "mobile":
            assert "flex-direction: column" in header_content.get_attribute(
                "style")
        else:
            assert "flex-direction: row" in header_content.get_attribute(
                "style")

    def test_print_layout(self, chrome_driver):
        """Test print layout optimization."""
        chrome_driver.get("http://localhost:5000")

        # Inject print media query
        chrome_driver.execute_script("""
            const style = document.createElement('style');
            style.media = 'print';
            style.textContent = `
                @media print {
                    .app-header, .filters-panel { display: none !important; }
                    .content-wrapper { display: block !important; }
                }
            `;
            document.head.appendChild(style);
        """)

        # Verify print styles are applied
        print_style = chrome_driver.execute_script("""
            return window.matchMedia('print').matches;
        """)

        assert print_style