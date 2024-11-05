# scholar_analyzer/cli.py

import click
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .analyzer import ScholarAnalyzer


# scholar_analyzer/cli.py

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .analyzer import ScholarAnalyzer


def process_query(
    query: str,
    output_dir: Path,
    input_file: Optional[Path] = None,
    format: str = "html"
) -> Dict[str, Any]:
    """Process a scholarly query and generate analysis outputs."""
    try:
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Load input data
        if input_file and input_file.exists():
            with open(input_file) as f:
                data = json.load(f)
        else:
            raise ValueError("Input file not found or invalid")

        # Initialize analyzer
        analyzer = ScholarAnalyzer(data)

        # Generate analysis
        results = analyzer.analyze()

        # Save analysis results
        analysis_file = output_dir / "analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump(results, f, indent=2)

        # Generate outputs based on format
        if format == "html":
            analyzer.generate_report(output_dir / "report.html")
            output_file = output_dir / "output.html"
            analyzer.generate_report(output_file)
        elif format == "json":
            output_file = output_dir / "output.json"
            analyzer.export_to_json(output_file)
        elif format == "csv":
            output_file = output_dir / "output.csv"
            analyzer.export_to_csv(output_file)
        elif format == "bibtex":
            output_file = output_dir / "output.bibtex"
            analyzer.export_to_bibtex(output_file)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return {
            "success": True,
            "message": "Analysis completed successfully",
            "output_file": str(output_file)
        }

    except Exception as e:
        logging.error(f"Error processing query: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


@click.group()
def cli():
    """Scholar analysis tools."""
    pass


@cli.command()
@click.argument('query')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
@click.option('--input', '-i', type=click.Path(exists=True), help='Input file')
@click.option('--format', '-f', type=click.Choice(['html', 'json', 'csv', 'bibtex']),
              default='html', help='Output format')
def analyze(query: str, output: Optional[str], input: Optional[str], format: str):
    """Analyze scholarly papers based on search query."""
    result = process_query(
        query=query,
        output_dir=Path(output) if output else None,
        input_file=Path(input) if input else None,
        format=format
    )

    if result["success"]:
        click.echo(
            f"Analysis complete. Results saved to: {result['output_dir']}")
    else:
        click.echo(f"Error: {result['error']}", err=True)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['html', 'json', 'csv', 'bibtex']),
              default='html', help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output path')
def export(input_file: str, format: str, output: Optional[str]):
    """Export analysis results to different formats."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        analyzer = ScholarAnalyzer(data)

        if not output:
            output = f"scholar_export.{format}"

        if format == "html":
            analyzer.generate_report(output)
        else:
            export_method = getattr(analyzer, f"export_to_{format}")
            export_method(output)

        click.echo(f"Export complete. File saved as: {output}")

    except Exception as e:
        click.echo(f"Error during export: {str(e)}", err=True)


if __name__ == '__main__':
    cli()
