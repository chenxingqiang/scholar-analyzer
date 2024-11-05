import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestThemeSystem:
    def test_theme_switching(self, chrome_driver):
        """Test basic theme switching functionality."""
        chrome_driver.get("http://localhost:5000")

        # Get initial theme
        initial_theme = chrome_driver.execute_script(
            'return document.documentElement.getAttribute("data-theme")'
        )

        # Toggle theme
        theme_button = chrome_driver.find_element(By.ID, "themeToggle")
        theme_button.click()

        # Wait for theme change
        new_theme = WebDriverWait(chrome_driver, 10).until(
            lambda d: d.execute_script(
                'return document.documentElement.getAttribute("data-theme")'
            ) != initial_theme
        )

        assert new_theme != initial_theme

    def test_theme_persistence(self, chrome_driver):
        """Test theme persistence across page reloads."""
        chrome_driver.get("http://localhost:5000")

        # Change theme
        theme_button = chrome_driver.find_element(By.ID, "themeToggle")
        theme_button.click()

        # Get selected theme
        selected_theme = chrome_driver.execute_script(
            'return document.documentElement.getAttribute("data-theme")'
        )

        # Reload page
        chrome_driver.refresh()

        # Verify theme persists
        persisted_theme = chrome_driver.execute_script(
            'return document.documentElement.getAttribute("data-theme")'
        )

        assert selected_theme == persisted_theme

    @pytest.mark.parametrize("theme,expected_colors", [
        ("light", {
            "--color-primary": "#4285f4",
            "--color-background": "#f8f9fa",
            "--color-text": "#202124"
        }),
        ("dark", {
            "--color-primary": "#7aa7f8",
            "--color-background": "#1a1a1a",
            "--color-text": "#e0e0e0"
        })
    ])
    def test_theme_colors(self, chrome_driver, theme, expected_colors):
        """Test color schemes for different themes."""
        chrome_driver.get("http://localhost:5000")

        # Set theme
        chrome_driver.execute_script(
            f'document.documentElement.setAttribute("data-theme", "{theme}")'
        )

        # Verify colors
        for var, expected in expected_colors.items():
            color = chrome_driver.execute_script(
                f'return getComputedStyle(document.documentElement).getPropertyValue("{var}")'
            ).strip()
            assert color == expected

    def test_theme_component_styles(self, chrome_driver):
        """Test component styling across themes."""
        chrome_driver.get("http://localhost:5000")

        components = {
            "card": ".card",
            "button": ".btn-primary",
            "input": "input[type='text']",
            "table": ".data-table"
        }

        # Test both themes
        for theme in ["light", "dark"]:
            chrome_driver.execute_script(
                f'document.documentElement.setAttribute("data-theme", "{theme}")'
            )

            for component, selector in components.items():
                element = chrome_driver.find_element(By.CSS_SELECTOR, selector)
                styles = chrome_driver.execute_script(
                    'return window.getComputedStyle(arguments[0])',
                    element
                )

                # Verify theme-specific styles
                if theme == "dark":
                    assert "rgba(255" in styles.backgroundColor or "#" in styles.backgroundColor
                else:
                    assert "rgba(0" in styles.backgroundColor or "#" in styles.backgroundColor

    def test_theme_transition(self, chrome_driver):
        """Test theme transition animations."""
        chrome_driver.get("http://localhost:5000")

        # Get transition properties
        transition = chrome_driver.execute_script(
            'return getComputedStyle(document.documentElement).getPropertyValue("--transition-normal")'
        )

        assert "ms" in transition

        # Toggle theme
        theme_button = chrome_driver.find_element(By.ID, "themeToggle")
        theme_button.click()

        # Verify transition class is applied
        body_classes = chrome_driver.find_element(
            By.TAG_NAME, "body").get_attribute("class")
        assert "theme-transitioning" in body_classes

        # Wait for transition to complete
        time.sleep(float(transition.replace("ms", "")) / 1000)

        # Verify transition class is removed
        body_classes = chrome_driver.find_element(
            By.TAG_NAME, "body").get_attribute("class")
        assert "theme-transitioning" not in body_classes

    def test_system_theme_preference(self, chrome_driver):
        """Test system theme preference detection."""
        chrome_driver.get("http://localhost:5000")

        # Simulate system dark mode
        chrome_driver.execute_script("""
            window.matchMedia = function(query) {
                return {
                    matches: query.includes('dark'),
                    addListener: function() {}
                }
            }
        """)

        # Reload page
        chrome_driver.refresh()

        # Verify theme matches system preference
        theme = chrome_driver.execute_script(
            'return document.documentElement.getAttribute("data-theme")'
        )

        assert theme == "dark"
