# Scholar Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/chenxingqiang/scholar-analyzer/actions/workflows/tests.yml/badge.svg)](https://github.com/chenxingqiang/scholar-analyzer/actions)
[![codecov](https://codecov.io/gh/chenxingqiang/scholar-analyzer/branch/main/graph/badge.svg)](https://codecov.io/gh/chenxingqiang/scholar-analyzer)

An advanced scholarly literature analysis and visualization tool that helps researchers analyze publication trends, citation patterns, and research networks.

## Features

- 📊 Interactive data visualization with customizable charts
- 📝 Comprehensive publication analysis
- 🔍 Advanced filtering and search capabilities
- 📈 Citation impact analysis
- 🌐 Collaboration network visualization
- 📱 Responsive design with dark/light mode support
- 📤 Multiple export formats (CSV, BibTeX, JSON)
- 📊 Statistical analysis and trend detection

## Installation

### Using pip

```bash
pip install scholar-analyzer
```

### From source

```bash
git clone https://github.com/chenxingqiang/scholar-analyzer.git
cd scholar-analyzer
pip install -e .
```

## Quick Start

```python
from scholar_analyzer import analyze_publications

# Analyze publications
analysis = analyze_publications("quantum computing", years=[2019, 2023])

# Generate interactive report
analysis.generate_report("report.html")

# Export results
analysis.export("results.json")
```

## Command Line Usage

```bash
# Basic analysis
scholar-analyzer analyze --query "machine learning" --years 2019-2023

# Generate report with specific format
scholar-analyzer analyze --query "deep learning" --format html --output report.html

# Advanced analysis with filters
scholar-analyzer analyze --query "AI" --min-citations 10 --venues "top" --format json
```

## Development Setup

1. Clone the repository:

```bash
git clone https://github.com/chenxingqiang/scholar-analyzer.git
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

4. Install pre-commit hooks:

```bash
pre-commit install
```

## Running Tests

The project uses pytest for testing. To run the tests:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=scholar_analyzer

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/frontend/

# Run with verbose output
pytest -v
```

### Test Structure

- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Integration tests for component interactions
- `tests/frontend/`: Frontend and UI tests
- `tests/conftest.py`: Shared test fixtures and configuration

## Project Structure

```
scholar_analyzer/
├── scholar_analyzer/
│   ├── static/
│   │   ├── css/
│   │   │   ├── base.css
│   │   │   ├── components.css
│   │   │   └── layouts.css
│   │   ├── js/
│   │   │   ├── config/
│   │   │   ├── modules/
│   │   │   └── main.js
│   │   └── themes/
│   ├── templates/
│   ├── analyzer.py
│   └── cli.py
├── tests/
├── docs/
└── examples/
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

Key areas for contribution:

- Additional analysis features
- UI/UX improvements
- Documentation
- Test coverage
- Bug fixes

## API Documentation

Detailed API documentation is available at [https://scholar-analyzer.readthedocs.io/](https://scholar-analyzer.readthedocs.io/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Xingqiang Chen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Author

**Xingqiang Chen**

- GitHub: [@chenxingqiang](https://github.com/chenxingqiang)
- Email: <chenxingqiang@gmail.com>
- Website: [https://chenxingqiang.github.io](https://chenxingqiang.github.io)

## Citation

If you use this software in your research, please cite:

```bibtex
@software{chen2024scholar,
  author = {Chen, Xingqiang},
  title = {Scholar Analyzer: A Tool for Scholarly Literature Analysis},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/chenxingqiang/scholar-analyzer}
}
```

## Acknowledgments

- ECharts for visualization
- Selenium for testing
- All contributors and users of the project
