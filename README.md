# Scholar Analyzer

A comprehensive tool for analyzing Google Scholar research papers.

## Features

- Batch download of research papers information
- Advanced analysis and visualization
- Interactive HTML report generation
- Command-line interface
- Export to various formats (CSV, JSON)

## Installation

### Using pip

```bash
pip install scholar-analyzer
```

### Using Homebrew (macOS)

```bash
brew tap yourusername/scholar-analyzer
brew install scholar-analyzer
```

### Using yum (RHEL/CentOS)

```bash
sudo yum install epel-release
sudo yum install scholar-analyzer
```

## Quick Start

```bash
# Basic usage
scholar-analyzer "your search query" --limit 1000

# With specific output directory
scholar-analyzer "your search query" -o /path/to/output

# Help
scholar-analyzer --help
```

## Development Setup

1. Clone the repository

```bash
git clone https://github.com/yourusername/scholar-analyzer.git
cd scholar-analyzer
```

2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

3. Install development dependencies

```bash
pip install -e ".[dev]"
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
