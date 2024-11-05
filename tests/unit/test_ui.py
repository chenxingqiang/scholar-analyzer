# test_ui.py
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scholar_analyzer.static.js.modules.ui import ScholarUI


class TestUI:
    @pytest.fixture
    def ui(self, sample_data):
        """Initialize UI instance for testing."""
        return ScholarUI(sample_data)

    def test_theme_switching(self, ui, chrome_driver):
        """Test theme switching functionality."""
        chrome_driver.get("http://localhost:5000")

        # Get initial theme
        initial_theme = ui.getTheme()

        # Toggle theme
        ui.toggleTheme()

        # Verify theme changed
        assert ui.getTheme() != initial_theme

        # Verify CSS variables updated
        root_styles = chrome_driver.execute_script(
            "return getComputedStyle(document.documentElement)"
        )
        if ui.getTheme() == 'dark':
            assert root_styles.getPropertyValue(
                '--color-background').strip() == '#1a1a1a'
        else:
            assert root_styles.getPropertyValue(
                '--color-background').strip() == '#f8f9fa'

    def test_layout_management(self, ui, chrome_driver):
        """Test layout management functionality."""
        chrome_driver.get("http://localhost:5000")

        # Test grid layout
        ui.setLayout('grid')
        grid_classes = chrome_driver.find_element(
            By.CLASS_NAME, "content-wrapper"
        ).get_attribute("class")
        assert "layout-grid" in grid_classes

        # Test list layout
        ui.setLayout('list')
        list_classes = chrome_driver.find_element(
            By.CLASS_NAME, "content-wrapper"
        ).get_attribute("class")
        assert "layout-list" in list_classes

    def test_tab_switching(self, ui, chrome_driver):
        """Test tab switching functionality."""
        chrome_driver.get("http://localhost:5000")

        tabs = ['trends', 'papers', 'insights']
        for tab in tabs:
            ui.switchTab(tab)

            # Verify active tab
            active_tab = chrome_driver.find_element(
                By.CSS_SELECTOR,
                f'[data-tab="{tab}"]'
            )
            assert "active" in active_tab.get_attribute("class")

            # Verify content visibility
            content = chrome_driver.find_element(By.ID, tab)
            assert content.is_displayed()

    def test_card_interactions(self, ui, chrome_driver):
        """Test card interaction features."""
        chrome_driver.get("http://localhost:5000")

        cards = chrome_driver.find_elements(By.CLASS_NAME, "card")
        for card in cards:
            # Test expand/collapse
            header = card.find_element(By.CLASS_NAME, "card-header")
            header.click()

            # Verify expansion
            assert "expanded" in card.get_attribute("class")

            # Test content visibility
            content = card.find_element(By.CLASS_NAME, "card-content")
            assert content.is_displayed()

    def test_filter_panel(self, ui, chrome_driver):
        """Test filter panel functionality."""
        chrome_driver.get("http://localhost:5000")

        # Test panel toggle
        ui.toggleFilterPanel()

        filter_panel = chrome_driver.find_element(
            By.CLASS_NAME, "filters-panel")
        assert filter_panel.is_displayed()

        # Test filter application
        year_input = filter_panel.find_element(By.ID, "yearStart")
        year_input.send_keys("2020")

        apply_button = filter_panel.find_element(By.ID, "applyFilters")
        apply_button.click()

        # Verify filter tags
        filter_tags = chrome_driver.find_elements(By.CLASS_NAME, "filter-tag")
        assert len(filter_tags) > 0

    def test_search_functionality(self, ui, chrome_driver):
        """Test search functionality."""
        chrome_driver.get("http://localhost:5000")

        search_input = chrome_driver.find_element(By.ID, "searchInput")
        search_term = "test"
        search_input.send_keys(search_term)

        # Wait for search results
        results = WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "search-result"))
        )

        assert len(results) > 0
        for result in results:
            assert search_term.lower() in result.text.lower()

    def test_chart_controls(self, ui, chrome_driver):
        """Test chart control functionality."""
        chrome_driver.get("http://localhost:5000")

        # Test chart download
        download_buttons = chrome_driver.find_elements(
            By.CSS_SELECTOR,
            "[data-chart-action='download']"
        )
        for button in download_buttons:
            button.click()
            # Verify download initiated

        # Test fullscreen mode
        fullscreen_buttons = chrome_driver.find_elements(
            By.CSS_SELECTOR,
            "[data-chart-action='fullscreen']"
        )
        for button in fullscreen_buttons:
            button.click()

            # Verify fullscreen mode
            fullscreen_chart = WebDriverWait(chrome_driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "fullscreen"))
            )
            assert fullscreen_chart.is_displayed()

    def test_table_features(self, ui, chrome_driver):
        """Test data table features."""
        chrome_driver.get("http://localhost:5000")

        # Switch to papers tab
        ui.switchTab('papers')

        table = chrome_driver.find_element(By.ID, "papersTable")

        # Test sorting
        headers = table.find_elements(By.CSS_SELECTOR, "th.sortable")
        for header in headers:
            header.click()
            assert "sorted" in header.get_attribute("class")

        # Test pagination
        pagination = chrome_driver.find_element(By.CLASS_NAME, "pagination")
        next_page = pagination.find_element(By.CLASS_NAME, "next")
        next_page.click()

        # Verify page changed
        assert "active" in pagination.find_element(
            By.CSS_SELECTOR,
            "[data-page='2']"
        ).get_attribute("class")

    def test_responsive_behavior(self, ui, chrome_driver):
        """Test responsive design behavior."""
        viewport_sizes = [
            (1920, 1080),  # Desktop
            (1024, 768),   # Tablet Landscape
            (768, 1024),   # Tablet Portrait
            (375, 812)     # Mobile
        ]

        for width, height in viewport_sizes:
            chrome_driver.set_window_size(width, height)

            # Verify layout adjustments
            content_wrapper = chrome_driver.find_element(
                By.CLASS_NAME,
                "content-wrapper"
            )
            layout = content_wrapper.get_attribute("class")

            if width < 768:
                assert "mobile-layout" in layout
            else:
                assert "mobile-layout" not in layout

    def test_error_handling(self, ui, chrome_driver):
        """Test UI error handling."""
        chrome_driver.get("http://localhost:5000")

        # Simulate error
        chrome_driver.execute_script(
            "window.dispatchEvent(new CustomEvent('app-error', " +
            "{detail: {message: 'Test error', type: 'warning'}}))"
        )

        # Verify error message displayed
        error_message = WebDriverWait(chrome_driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
        )
        assert error_message.is_displayed()
        assert "Test error" in error_message.text

    def test_keyboard_navigation(self, ui, chrome_driver):
        """Test keyboard navigation support."""
        chrome_driver.get("http://localhost:5000")

        # Test tab navigation
        body = chrome_driver.find_element
