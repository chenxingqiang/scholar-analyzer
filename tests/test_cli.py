import pytest
import click.testing
from pathlib import Path
from scholar_analyzer.cli import cli


class TestCLI:
    @pytest.fixture
    def cli_runner(self):
        """Create a CLI runner for testing."""
        return click.testing.CliRunner()

    def test_basic_analysis(self, cli_runner, sample_data, temp_output_dir):
        """Test basic analysis command."""
        # Create input file
        input_file = temp_output_dir / "input.json"
        input_file.write_text(json.dumps(sample_data))

        result = cli_runner.invoke(cli, [
            'analyze',
            '--input', str(input_file),
            '--output', str(temp_output_dir),
            '--query', 'test query'
        ])

        assert result.exit_code == 0
        assert (temp_output_dir / "report.html").exists()
        assert (temp_output_dir / "analysis.json").exists()

    def test_export_formats(self, cli_runner, sample_data, temp_output_dir):
        """Test different export format options."""
        input_file = temp_output_dir / "input.json"
        input_file.write_text(json.dumps(sample_data))

        formats = ['html', 'json', 'csv', 'bibtex']
        for fmt in formats:
            result = cli_runner.invoke(cli, [
                'analyze',
                '--input', str(input_file),
                '--output', str(temp_output_dir),
                '--format', fmt
            ])

            assert result.exit_code == 0
            assert (temp_output_dir / f"output.{fmt}").exists()

    def test_error_handling(self, cli_runner, temp_output_dir):
        """Test CLI error handling."""
        # Test missing input file
        result = cli_runner.invoke(cli, [
            'analyze',
            '--input', 'nonexistent.json',
            '--output', str(temp_output_dir)
        ])
        assert result.exit_code != 0
        assert "Error: Input file not found" in result.output

        # Test invalid JSON
        invalid_json = temp_output_dir / "invalid.json"
        invalid_json.write_text("invalid json")

        result = cli_runner.invoke(cli, [
            'analyze',
            '--input', str(invalid_json),
            '--output', str(temp_output_dir)
        ])
        assert result.exit_code != 0
        assert "Error: Invalid JSON" in result.output

    def test_configuration_options(self, cli_runner, sample_data, temp_output_dir):
        """Test configuration options."""
        input_file = temp_output_dir / "input.json"
        input_file.write_text(json.dumps(sample_data))

        result = cli_runner.invoke(cli, [
            'analyze',
            '--input', str(input_file),
            '--output', str(temp_output_dir),
            '--theme', 'dark',
            '--lang', 'en',
            '--template', 'custom.html'
        ])

        assert result.exit_code == 0
        # Verify configuration was applied
        with open(temp_output_dir / "report.html") as f:
            content = f.read()
            assert 'data-theme="dark"' in content
            assert 'lang="en"' in content

    def test_batch_processing(self, cli_runner, temp_output_dir):
        """Test batch processing functionality."""
        # Create multiple input files
        for i in range(3):
            input_file = temp_output_dir / f"input_{i}.json"
            input_file.write_text(json.dumps({
                "papers": [{"title": f"Test Paper {i}"}]
            }))

        result = cli_runner.invoke(cli, [
            'batch',
            '--input-dir', str(temp_output_dir),
            '--output-dir', str(temp_output_dir / "output"),
            '--format', 'json'
        ])

        assert result.exit_code == 0
        # Verify batch outputs
        assert (temp_output_dir / "output").exists()
        assert len(list((temp_output_dir / "output").glob("*.json"))) == 3

    def test_interactive_mode(self, cli_runner):
        """Test interactive mode."""
        result = cli_runner.invoke(cli, ['interactive'], input='test query\n')

        assert result.exit_code == 0
        assert "Starting interactive analysis" in result.output

    def test_progress_reporting(self, cli_runner, sample_data, temp_output_dir):
        """Test progress reporting."""
        input_file = temp_output_dir / "input.json"
        input_file.write_text(json.dumps(sample_data))

        result = cli_runner.invoke(cli, [
            'analyze',
            '--input', str(input_file),
            '--output', str(temp_output_dir),
            '--verbose'
        ])

        assert "Processing data" in result.output
        assert "Generating visualizations" in result.output
        assert "Analysis complete" in result.output
