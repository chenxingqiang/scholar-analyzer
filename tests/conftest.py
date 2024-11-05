# tests/conftest.py

import pytest
import tempfile
import json
import time
from pathlib import Path
from threading import Thread
from werkzeug.serving import make_server
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def run_flask_server(app, host='127.0.0.1', port=5000):
    """Run flask server in a separate thread."""
    server = make_server(host, port, app)
    ctx = app.app_context()
    ctx.push()  # Push an application context
    server.serve_forever()


@pytest.fixture(scope="session")
def app():
    """Create Flask app for testing."""
    from scholar_analyzer.web import create_app
    app = create_app({
        'TESTING': True,
        'DEBUG': True,
        'SERVER_NAME': 'localhost:5000'
    })
    return app


@pytest.fixture(scope="session")
def test_server(app):
    """Start test server in a separate thread."""
    server_thread = Thread(target=run_flask_server, args=(app,), daemon=True)
    server_thread.start()
    time.sleep(1)  # Give the server a moment to start
    yield server_thread


@pytest.fixture(scope="session")
def chrome_driver():
    """Set up Chrome WebDriver with automatic ChromeDriver installation."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    # Use webdriver_manager to automatically handle ChromeDriver installation
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    yield driver
    driver.quit()


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return {
        "metadata": {
            "query": "test query",
            "date": "2024-01-01",
            "filters": {},
        },
        "papers": [
            {
                "title": "Test Paper 1",
                "authors": ["Author One", "Author Two"],
                "year": 2023,
                "venue": "Test Conference",
                "citations": 10,
                "url": "https://example.com/paper1"
            },
            {
                "title": "Test Paper 2",
                "authors": ["Author Three"],
                "year": 2022,
                "venue": "Test Journal",
                "citations": 5,
                "url": "https://example.com/paper2"
            }
        ],
        "timestamp": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def workflow_setup(temp_output_dir, sample_data):
    """Setup for workflow testing."""
    input_file = temp_output_dir / "input.json"
    input_file.write_text(json.dumps(sample_data))
    return input_file, temp_output_dir
