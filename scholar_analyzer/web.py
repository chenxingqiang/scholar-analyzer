# scholar_analyzer/web.py

import os
from typing import Dict, Any
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file, current_app
from werkzeug.utils import secure_filename
from .analyzer import ScholarAnalyzer


def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')

    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        """Render the main application page."""
        return render_template('index.html')

    @app.route('/api/analyze', methods=['POST'])
    def analyze():
        """Analyze scholar data."""
        data = request.get_json()

        # Initialize analyzer with data
        analyzer = ScholarAnalyzer(data)

        # Perform analysis
        try:
            results = analyzer.analyze()
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

    @app.route('/api/export/<format>', methods=['POST'])
    def export(format):
        """Export data in specified format."""
        if format not in ['csv', 'json', 'bibtex']:
            return jsonify({'error': 'Invalid export format'}), 400

        data = request.get_json()
        analyzer = ScholarAnalyzer(data)

        # Create temporary file for export
        output_path = os.path.join(app.instance_path, f'export.{format}')

        try:
            if format == 'csv':
                analyzer.export_to_csv(output_path)
            elif format == 'json':
                analyzer.export_to_json(output_path)
            elif format == 'bibtex':
                analyzer.export_to_bibtex(output_path)

            return send_file(
                output_path,
                as_attachment=True,
                download_name=f'scholar-analysis.{format}'
            )
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/filters', methods=['GET'])
    def get_filters():
        """Get available filter options."""
        # This would typically come from your data or a database
        return jsonify({
            'venues': [],  # List of available venues
            'years': [],   # List of available years
            'authors': []  # List of available authors
        })

    return app
