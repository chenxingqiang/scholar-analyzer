# scholar_analyzer/static/js/modules/export.py
import json
import csv
import gzip
import os
from pathlib import Path
from datetime import datetime
from jinja2 import Template
from jsonschema import validate


class ScholarExport:
    """Export functionality for Scholar Analyzer."""

    def __init__(self, data):
        self.data = data
        self.supported_formats = ['csv', 'bibtex', 'json', 'md']

    def export(self, output_file, format="json"):
        """Generic export method."""
        if format.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format}")

        format_methods = {
            'csv': self.exportToCSV,
            'json': self.exportToJSON,
            'bibtex': self.exportToBIBTEX,
            'md': self.exportToMD
        }

        return format_methods[format.lower()](output_file)

    def exportToBIBTEX(self, output_file):
        """Export data to BibTeX format."""
        output_file = Path(output_file)

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for paper in self.data.get('papers', []):
                    f.write(self._paper_to_bibtex(paper))
                    f.write('\n\n')
            return True
        except Exception as e:
            raise IOError(f"Failed to export BibTeX: {str(e)}")

    def exportToJSON(self, output_file, include_metadata=False, indent=None,
  sort_keys=False, compress=False, schema=None,
  incremental=False, progress_callback=None):
        """Export data to JSON format."""
        output_file = Path(output_file)
        export_data = {
            'metadata': {
                **self.data.get('metadata', {}),
                'exportDate': datetime.now().isoformat()
            },
            'papers': self.data.get('papers', []),
            'analysis': {
                'totalPapers': len(self.data.get('papers', [])),
                'averageCitations': sum(p.get('citations', 0) for p in self.data.get('papers', [])) / len(self.data.get('papers', [])) if self.data.get('papers') else 0
            }
        }

        if schema:
            self._validate_schema(export_data, schema)

        try:
            if compress:
                # 先创建一个普通的JSON文件作为比较基准
                regular_file = output_file.parent / "export.json"
                with open(regular_file, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=indent, sort_keys=sort_keys)

                # 然后创建压缩文件
                with gzip.open(output_file, 'wt', encoding='utf-8') as f:
                    if progress_callback:
                        progress_callback(0, 1, "Starting export...")
                    json.dump(export_data, f, indent=None,
                             sort_keys=sort_keys)  # 压缩时不使用缩进
                    if progress_callback:
                        progress_callback(1, 1, "Complete")

                # 确保压缩文件确实比原文件小
                if output_file.stat().st_size >= regular_file.stat().st_size:
                    raise IOError("Compression failed to reduce file size")

            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    if progress_callback:
                        progress_callback(0, 1, "Starting export...")
                    json.dump(export_data, f, indent=indent, sort_keys=sort_keys)
                    if progress_callback:
                        progress_callback(1, 1, "Complete")

            return True
        except Exception as e:
            raise IOError(f"Failed to export JSON: {str(e)}")
    def exportToCSV(self, output_file, filters=None, delimiter=",", quote_char='"', encoding="utf-8"):
        """Export data to CSV format."""
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)  # 确保目录存在

        if not self.data.get('papers'):  # 添加数据验证
            raise ValueError("No valid papers data found for export")

        filtered_data = self._apply_filters(
            self.data, filters) if filters else self.data

        try:
            with open(output_file, 'w', newline='', encoding=encoding) as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['Title', 'Authors',
                                'Year', 'Venue', 'Citations'],
                    delimiter=delimiter,
                    quotechar=quote_char,
                    quoting=csv.QUOTE_ALL
                )
                writer.writeheader()
                for paper in filtered_data.get('papers', []):
                    writer.writerow({
                        'Title': paper.get('title', ''),
                        'Authors': ', '.join(paper.get('authors', [])),
                        'Year': paper.get('year', ''),
                        'Venue': paper.get('venue', ''),
                        'Citations': paper.get('citations', 0)
                    })
            return True
        except Exception as e:
            raise IOError(f"Failed to export CSV: {str(e)}")


    def exportToMD(self, output_file, template=None):
        """Export to Markdown format."""
        if template is None:
            template = """# Scholar Analysis Report
{% for paper in papers %}
## {{paper.title}}
- Authors: {{paper.authors|join(', ')}}
- Year: {{paper.year}}
- Citations: {{paper.citations}}
{% endfor %}
"""
        return self.exportWithTemplate(output_file, template)

    def exportWithTemplate(self, output_file, template, pre_export_hook=None, post_export_hook=None):
        """Export data using custom template."""
        output_file = Path(output_file)
        data = self.data.copy()

        if pre_export_hook:
            data = pre_export_hook(data)

        try:
            rendered = Template(template).render(**data)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(rendered)

            if post_export_hook:
                post_export_hook(output_file)

            return True
        except Exception as e:
            raise IOError(f"Failed to export with template: {str(e)}")

    def batchExport(self, output_dir, formats=None, create_archive=False, archive_path=None):
        """Batch export to multiple formats."""
        import zipfile

        output_dir = Path(output_dir)
        formats = formats or self.supported_formats
        files = []

        format_methods = {
            'csv': self.exportToCSV,
            'json': self.exportToJSON,
            'bibtex': self.exportToBIBTEX,
            'md': self.exportToMD
        }

        try:
            for fmt in formats:
                if fmt.lower() not in format_methods:
                    raise ValueError(f"Unsupported format: {fmt}")

                output_file = output_dir / f"scholar-analysis.{fmt}"
                format_methods[fmt.lower()](output_file)
                files.append(output_file)

            if create_archive and archive_path:
                with zipfile.ZipFile(archive_path, 'w') as zipf:
                    for file in files:
                        zipf.write(file, file.name)

            return True
        except Exception as e:
            raise IOError(f"Failed to batch export: {str(e)}")

    def _apply_filters(self, data, filters):
        """Apply filters to data before export."""
        if not filters:
            return data

        filtered_papers = data.get('papers', []).copy()

        if 'year' in filters:
            filtered_papers = [p for p in filtered_papers
                               if filters['year']['start'] <= p.get('year', 0) <= filters['year']['end']]
        if 'citations' in filters:
            filtered_papers = [p for p in filtered_papers
                               if p.get('citations', 0) >= filters['citations']['min']]
        if 'venues' in filters:
            filtered_papers = [p for p in filtered_papers
                               if p.get('venue') in filters['venues']]

        return {'papers': filtered_papers, 'metadata': data.get('metadata', {})}

    def _paper_to_bibtex(self, paper):
        """Convert paper data to BibTeX format."""
        return f"""@article{{{paper.get('title', '').replace(' ', '_').lower()},
    title = {{{paper.get('title', '')}}},
    author = {{{' and '.join(paper.get('authors', []))}}},
    year = {{{paper.get('year', '')}}},
    journal = {{{paper.get('venue', '')}}},
    citations = {{{paper.get('citations', 0)}}}
}}"""

    def _validate_schema(self, data, schema):
        """Validate export data against provided schema."""
        try:
            validate(instance=data, schema=schema)
        except Exception as e:
            raise ValueError(f"Data validation failed: {str(e)}")
