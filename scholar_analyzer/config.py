# scholar_analyzer/config.py

import tempfile
from pathlib import Path

# Flask settings
DEBUG = True
SECRET_KEY = 'dev'

# Application settings
TEMP_FOLDER = tempfile.gettempdir()
UPLOAD_FOLDER = Path(TEMP_FOLDER) / 'uploads'
ALLOWED_EXTENSIONS = {'json', 'csv'}

# Create required directories
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
