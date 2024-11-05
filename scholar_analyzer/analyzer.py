# scholar_analyzer/analyzer.py
from typing import Dict, Any, Optional, List
from pathlib import Path
from .visualization.chart_generator import ChartGenerator
from pyecharts.globals import ThemeType


class ScholarAnalyzer:
    """Analyzer for scholarly publication data."""

    def __init__(self, data: Dict[str, Any], theme: str = "light"):
        """Initialize analyzer with data and theme."""
        self.data = data
        self.theme = theme
        self.chart_generator = ChartGenerator(theme=theme)
        self.analysis_results = None
        self.charts = None

    def _generate_charts(self) -> Dict[str, str]:
        """Generate visualization charts."""
        if not self.analysis_results:
            self.analysis_results = self._perform_analysis()

        return {
            "yearly_trend": self.chart_generator.generate_yearly_trend_chart(
                self.analysis_results["yearly_data"]
            ),
            "citation_dist": self.chart_generator.generate_citation_chart(
                self.analysis_results["citation_data"]
            ),
            "venues": self.chart_generator.generate_venue_chart(
                self.analysis_results["venue_data"]
            )
        }

    def analyze(self) -> Dict[str, Any]:
        """Analyze data and generate visualizations."""
        self.analysis_results = self._perform_analysis()
        self.charts = self._generate_charts()

        return {
            "success": True,
            "papers": self.data.get("papers", []),
            "analysis": self.analysis_results,
            "charts": self.charts
        }

    def _perform_analysis(self) -> Dict[str, Any]:
        """Perform detailed analysis of scholarly data."""
        return {
            "yearly_data": self._analyze_yearly_trends(),
            "citation_data": self._analyze_citations(),
            "venue_data": self._analyze_venues(),
            "metrics": {
                "total_papers": len(self.data.get("papers", [])),
                "total_citations": sum(p.get("citations", 0) for p in self.data.get("papers", [])),
                "unique_venues": len(set(p.get("venue", "") for p in self.data.get("papers", [])))
            }
        }

    def generate_report(self, output_path: str) -> None:
        """Generate analysis report."""
        if not self.analysis_results:
            self.analyze()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Use the template to generate the report
        template_data = {
            "analysis": self.analysis_results,
            "papers": self.data.get("papers", []),
            "charts": self.charts,
            "query": self.data.get("metadata", {}).get("query", "")
        }

        self._render_template(output_path, template_data)

    def export_to_json(self, output_path: str) -> None:
        """Export data to JSON format."""
        import json
        if not self.analysis_results:
            self.analyze()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "papers": self.data.get("papers", []),
                "analysis": self.analysis_results
            }, f, indent=2)

    def export_to_csv(self, output_path: str) -> None:
        """Export data to CSV format."""
        import csv
        if not self.analysis_results:
            self.analyze()

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['title', 'authors', 'year', 'venue', 'citations']
            )
            writer.writeheader()
            for paper in self.data.get("papers", []):
                writer.writerow({
                    'title': paper.get('title', ''),
                    'authors': ', '.join(paper.get('authors', [])),
                    'year': paper.get('year', ''),
                    'venue': paper.get('venue', ''),
                    'citations': paper.get('citations', 0)
                })

    def export_to_bibtex(self, output_path: str) -> None:
        """Export data to BibTeX format."""
        if not self.analysis_results:
            self.analyze()

        with open(output_path, 'w', encoding='utf-8') as f:
            for paper in self.data.get("papers", []):
                f.write(self._paper_to_bibtex(paper))
                f.write('\n\n')

    def _paper_to_bibtex(self, paper: Dict[str, Any]) -> str:
        """Convert paper data to BibTeX entry."""
        return f"""@article{{{paper.get('title', '').replace(' ', '_').lower()},
                title = {{{paper.get('title', '')}}},
                author = {{{' and '.join(paper.get('authors', []))}}},
                year = {{{paper.get('year', '')}}},
                journal = {{{paper.get('venue', '')}}},
                citations = {{{paper.get('citations', 0)}}}
            }}"""

    def _render_template(self, output_path: Path, data: Dict[str, Any]) -> None:
        """Render HTML template with provided data."""
        from jinja2 import Template

        template = Template(self._get_default_template())
        html_content = template.render(**data)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _get_default_template(self) -> str:
        """Get default HTML template."""
        return """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Scholar Analysis Report</title>
                </head>
                <body>
                    <h1>Scholar Analysis Report</h1>
                    <h2>Analysis Results</h2>
                    <pre>{{ analysis | tojson(indent=2) }}</pre>

                    <h2>Papers</h2>
                    <ul>
                    {% for paper in papers %}
                        <li>{{ paper.title }} ({{ paper.year }}) - Citations: {{ paper.citations }}</li>
                    {% endfor %}
                    </ul>
                </body>
                </html>
                """


    def _analyze_yearly_trends(self) -> Dict[str, int]:
        """
        Analyze publication trends by year.

        Returns:
            Dictionary mapping years to publication counts
        """
        yearly_counts = {}
        for paper in self.data.get('papers', []):
            year = paper.get('year')
            if year:
                yearly_counts[year] = yearly_counts.get(year, 0) + 1
        return dict(sorted(yearly_counts.items()))

    def _analyze_citations(self) -> Dict[str, int]:
        """
        Analyze citation distribution.

        Returns:
            Dictionary mapping citation ranges to paper counts
        """
        citation_ranges = {
            '0': 0, '1-10': 0, '11-50': 0,
            '51-100': 0, '101-500': 0, '500+': 0
        }

        for paper in self.data.get('papers', []):
            citations = paper.get('citations', 0)
            if citations == 0:
                citation_ranges['0'] += 1
            elif citations <= 10:
                citation_ranges['1-10'] += 1
            elif citations <= 50:
                citation_ranges['11-50'] += 1
            elif citations <= 100:
                citation_ranges['51-100'] += 1
            elif citations <= 500:
                citation_ranges['101-500'] += 1
            else:
                citation_ranges['500+'] += 1

        return citation_ranges

    def _analyze_venues(self) -> Dict[str, int]:
        """
        Analyze publication venues.

        Returns:
            Dictionary mapping venue names to publication counts
        """
        venue_counts = {}
        for paper in self.data.get('papers', []):
            venue = paper.get('venue')
            if venue:
                venue_counts[venue] = venue_counts.get(venue, 0) + 1
        return dict(sorted(venue_counts.items(), key=lambda x: x[1], reverse=True))

    def _extract_network_nodes(self) -> List[Dict[str, Any]]:
        """
        Extract collaboration network nodes.

        Returns:
            List of dictionaries containing node information
        """
        authors = set()
        for paper in self.data.get('papers', []):
            authors.update(paper.get('authors', []))

        return [{'name': author, 'symbolSize': 10} for author in authors]

    def _extract_network_links(self) -> List[Dict[str, Any]]:
        """
        Extract collaboration network links.

        Returns:
            List of dictionaries containing link information
        """
        collaborations = {}
        for paper in self.data.get('papers', []):
            authors = paper.get('authors', [])
            for i, author1 in enumerate(authors):
                for author2 in authors[i+1:]:
                    key = tuple(sorted([author1, author2]))
                    collaborations[key] = collaborations.get(key, 0) + 1

        return [
            {
                'source': source,
                'target': target,
                'value': weight
            }
            for (source, target), weight in collaborations.items()
        ]

    def _render_report_template(self, output_path: str,
                                analysis_results: Dict[str, Any],
                                chart_paths: Dict[str, str]) -> None:
        """
        Render HTML report using template.

        Args:
            output_path: Path where the report will be saved
            analysis_results: Results of the data analysis
            chart_paths: Paths to the generated chart files
        """
        from jinja2 import Environment, FileSystemLoader
        import pkg_resources

        # Get template path
        template_path = pkg_resources.resource_filename(
            'scholar_analyzer',
            'templates'
        )

        env = Environment(loader=FileSystemLoader(template_path))
        template = env.get_template('report.html')

        # Render report
        html_content = template.render(
            analysis=analysis_results,
            charts=chart_paths,
            theme=self.theme.value
        )

        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
