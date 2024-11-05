import pytest
import json
import csv
from pathlib import Path
from scholar_analyzer.static.js.modules.export import ScholarExport


class TestExportModule:
    @pytest.fixture
    def exporter(self, sample_data):
        """Create export instance with sample data."""
        return ScholarExport(sample_data)

    def test_csv_export(self, exporter, temp_output_dir):
        """Test CSV export functionality."""
        output_file = temp_output_dir / "export.csv"
        exporter.exportToCSV(output_file)

        assert output_file.exists()

        # Verify CSV content
        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Verify headers
            assert all(field in reader.fieldnames for field in [
                'Title', 'Authors', 'Year', 'Venue', 'Citations'
            ])

            # Verify data
            for row in rows:
                assert row['Title']
                assert row['Year'].isdigit()
                assert row['Citations'].isdigit()

    def test_bibtex_export(self, exporter, temp_output_dir):
        """Test BibTeX export functionality."""
        output_file = temp_output_dir / "export.bib"
        exporter.exportToBIBTEX(output_file)

        assert output_file.exists()

        with open(output_file) as f:
            content = f.read()

            # Verify BibTeX format
            assert content.startswith('@article{')
            assert 'title = {' in content
            assert 'author = {' in content
            assert 'year = {' in content

    def test_json_export(self, exporter, temp_output_dir):
        """Test JSON export functionality."""
        output_file = temp_output_dir / "export.json"
        exporter.exportToJSON(output_file)

        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

            # Verify JSON structure
            assert "metadata" in data
            assert "papers" in data
            assert "analysis" in data

    def test_export_with_filters(self, exporter, temp_output_dir):
        """Test export with applied filters."""
        filters = {
            "year": {"start": 2020, "end": 2022},
            "citations": {"min": 5},
            "venues": ["Test Conference"]
        }

        output_file = temp_output_dir / "filtered_export.csv"
        exporter.exportToCSV(output_file, filters=filters)

        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            # Verify filtered data
            for row in rows:
                assert 2020 <= int(row['Year']) <= 2022
                assert int(row['Citations']) >= 5
                assert row['Venue'] == "Test Conference"

    def test_batch_export(self, exporter, temp_output_dir):
        """Test batch export functionality."""
        formats = ['csv', 'bibtex', 'json']

        exporter.batchExport(temp_output_dir, formats=formats)

        # Verify all formats exported
        for fmt in formats:
            assert (temp_output_dir / f"scholar-analysis.{fmt}").exists()

    def test_error_handling(self, exporter, temp_output_dir):
        """Test export error handling."""
        # Test invalid format
        with pytest.raises(ValueError):
            exporter.export(temp_output_dir / "test.xyz", format="xyz")

        # Test invalid path
        with pytest.raises(IOError):
            exporter.exportToCSV("/nonexistent/path/file.csv")

        # Test invalid data
        invalid_exporter = ScholarExport({"invalid": "data"})
        with pytest.raises(ValueError):
            invalid_exporter.exportToCSV(temp_output_dir / "invalid.csv")

    def test_custom_export_templates(self, exporter, temp_output_dir):
        """Test custom export templates."""
        template = """
        # Scholar Analysis Report
        {% for paper in papers %}
        ## {{paper.title}}
        - Authors: {{paper.authors|join(', ')}}
        - Year: {{paper.year}}
        - Citations: {{paper.citations}}
        {% endfor %}
        """

        output_file = temp_output_dir / "custom_export.md"
        exporter.exportWithTemplate(output_file, template)

        assert output_file.exists()
        with open(output_file) as f:
            content = f.read()
            assert "# Scholar Analysis Report" in content
            assert "## " in content  # Verify paper titles
            assert "Authors: " in content

    def test_export_metadata(self, exporter, temp_output_dir):
        """Test metadata inclusion in exports."""
        output_file = temp_output_dir / "export.json"
        exporter.exportToJSON(output_file, include_metadata=True)

        with open(output_file) as f:
            data = json.load(f)

            assert "metadata" in data
            metadata = data["metadata"]
            assert "exportDate" in metadata
            assert "query" in metadata
            assert "filters" in metadata

    def test_incremental_export(self, exporter, temp_output_dir):
        """Test incremental export functionality."""
        # First export
        output_file = temp_output_dir / "incremental.json"
        exporter.exportToJSON(output_file)

        # Modify data and export incrementally
        exporter.data["papers"].append({
            "title": "New Paper",
            "authors": ["New Author"],
            "year": 2024,
            "citations": 0
        })

        exporter.exportToJSON(output_file, incremental=True)

        with open(output_file) as f:
            data = json.load(f)
            papers = data["papers"]
            assert any(p["title"] == "New Paper" for p in papers)

    def test_export_formatting(self, exporter, temp_output_dir):
        """Test export formatting options."""
        # Test CSV formatting
        csv_file = temp_output_dir / "formatted.csv"
        exporter.exportToCSV(
            csv_file,
            delimiter=";",
            quote_char="'",
            encoding="utf-8-sig"
        )

        with open(csv_file, encoding="utf-8-sig") as f:
            content = f.read()
            assert ";" in content  # Custom delimiter
            assert "'" in content  # Custom quote character

        # Test JSON formatting
        json_file = temp_output_dir / "formatted.json"
        exporter.exportToJSON(
            json_file,
            indent=2,
            sort_keys=True
        )

        with open(json_file) as f:
            content = f.read()
            assert "  " in content  # Verify indentation
            # Verify key sorting
            keys = json.loads(content)["papers"][0].keys()
            assert list(keys) == sorted(list(keys))

    def test_export_compression(self, exporter, temp_output_dir):
        """Test export compression options."""
        # Test gzip compression
        gzip_file = temp_output_dir / "export.json.gz"
        exporter.exportToJSON(gzip_file, compress=True)

        assert gzip_file.exists()
        assert gzip_file.stat().st_size < (temp_output_dir / "export.json").stat().st_size

        # Test zip archive with multiple formats
        zip_file = temp_output_dir / "export.zip"
        exporter.batchExport(
            temp_output_dir,
            formats=['csv', 'json', 'bibtex'],
            create_archive=True,
            archive_path=zip_file
        )

        assert zip_file.exists()

    def test_export_validation(self, exporter, temp_output_dir):
        """Test export data validation."""
        # Test schema validation
        schema = {
            "type": "object",
            "required": ["papers", "metadata"],
            "properties": {
                "papers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["title", "authors", "year", "citations"],
                        "properties": {
                            "title": {"type": "string"},
                            "authors": {"type": "array"},
                            "year": {"type": "integer"},
                            "citations": {"type": "integer"}
                        }
                    }
                }
            }
        }

        # Valid export
        output_file = temp_output_dir / "valid_export.json"
        assert exporter.exportToJSON(output_file, schema=schema) == True

        # Invalid data
        invalid_exporter = ScholarExport({"papers": [{"invalid": "data"}]})
        with pytest.raises(ValueError):
            invalid_exporter.exportToJSON(output_file, schema=schema)

    def test_export_hooks(self, exporter, temp_output_dir):
        """Test export processing hooks."""
        def pre_export_hook(data):
            """Modify data before export."""
            for paper in data["papers"]:
                paper["score"] = paper["citations"] / (2024 - paper["year"])
            return data

        def post_export_hook(filepath):
            """Process exported file."""
            with open(filepath, "a") as f:
                f.write("\n# Generated by test hooks")

        output_file = temp_output_dir / "hooked_export.md"
        exporter.exportWithTemplate(
            output_file,
            template="{% for paper in papers %}{{paper.score}}{% endfor %}",
            pre_export_hook=pre_export_hook,
            post_export_hook=post_export_hook
        )

        with open(output_file) as f:
            content = f.read()
            assert "Generated by test hooks" in content
            assert any(c.isdigit()
                       for c in content)  # Verify scores were added

    def test_concurrent_export(self, exporter, temp_output_dir):
        """Test concurrent export operations."""
        import concurrent.futures

        formats = ['csv', 'json', 'bibtex', 'md']
        files = [temp_output_dir /
                 f"concurrent_export.{fmt}" for fmt in formats]

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(formats)) as executor:
            futures = []
            for fmt, file in zip(formats, files):
                if fmt == 'md':
                    futures.append(executor.submit(
                        exporter.exportWithTemplate,
                        file,
                        "# {{papers|length}} papers"
                    ))
                else:
                    export_method = getattr(exporter, f'exportTo{fmt.upper()}')
                    futures.append(executor.submit(export_method, file))

            # Wait for all exports to complete
            concurrent.futures.wait(futures)

            # Verify all files were created
            for file in files:
                assert file.exists()

    def test_export_progress(self, exporter, temp_output_dir):
        """Test export progress reporting."""
        progress_updates = []

        def progress_callback(current, total, status):
            progress_updates.append((current, total, status))

        output_file = temp_output_dir / "progress_export.json"
        exporter.exportToJSON(
            output_file,
            progress_callback=progress_callback
        )

        assert len(progress_updates) > 0
        assert progress_updates[-1][0] == progress_updates[-1][1]  # Completed
        assert "Complete" in progress_updates[-1][2]
