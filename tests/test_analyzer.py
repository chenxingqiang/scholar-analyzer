import pytest
from scholar_analyzer.static.js.modules.analytics import ScholarAnalytics


def test_initialize_analytics(sample_data):
    """Test analytics initialization."""
    analytics = ScholarAnalytics(sample_data)
    assert analytics.rawData == sample_data
    assert analytics.processedData is None
    assert analytics.metrics is None


def test_process_raw_data(sample_data):
    """Test raw data processing."""
    analytics = ScholarAnalytics(sample_data)
    processed = analytics.processRawData()

    assert "papers" in processed
    assert "citations" in processed
    assert "venues" in processed
    assert "years" in processed


def test_calculate_metrics(sample_data):
    """Test metrics calculation."""
    analytics = ScholarAnalytics(sample_data)
    analytics.initialize()
    metrics = analytics.metrics

    assert metrics["totalPapers"] == len(sample_data["papers"])
    assert isinstance(metrics["averageCitations"], float)
    assert isinstance(metrics["uniqueVenues"], dict)
    assert "yearRange" in metrics


def test_citation_analysis(sample_data):
    """Test citation analysis functionality."""
    analytics = ScholarAnalytics(sample_data)
    citations = analytics.processCitations()

    assert "distribution" in citations
    assert "total" in citations
    assert "average" in citations
    assert "median" in citations
    assert citations["total"] == sum(p["citations"]
                                     for p in sample_data["papers"])


@pytest.mark.parametrize("year,expected_count", [
    (2020, 1),
    (2021, 1),
    (2022, 0)
])
def test_yearly_distribution(sample_data, year, expected_count):
    """Test yearly publication distribution."""
    analytics = ScholarAnalytics(sample_data)
    yearly_data = analytics.processYearlyTrends()
    assert yearly_data.get(str(year), 0) == expected_count


def test_venue_analysis(sample_data):
    """Test venue analysis functionality."""
    analytics = ScholarAnalytics(sample_data)
    venues = analytics.processVenues()

    assert "Test Conference" in venues
    assert "Test Journal" in venues
    assert venues["Test Conference"] == 1
    assert venues["Test Journal"] == 1


@pytest.mark.parametrize("field", ["title", "authors", "year", "venue", "citations"])
def test_paper_processing(sample_data, field):
    """Test paper data processing for required fields."""
    analytics = ScholarAnalytics(sample_data)
    processed_papers = analytics.processPapers()

    for paper in processed_papers:
        assert field in paper
        assert paper[field] is not None


def test_error_handling():
    """Test error handling for invalid data."""
    with pytest.raises(ValueError):
        analytics = ScholarAnalytics(None)
        analytics.initialize()

    with pytest.raises(ValueError):
        analytics = ScholarAnalytics({})
        analytics.initialize()
