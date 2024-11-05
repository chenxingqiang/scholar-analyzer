# test_analytics.py
import pytest
from scholar_analyzer.static.js.modules.analytics import ScholarAnalytics


class TestAnalytics:
    @pytest.fixture
    def analytics(self, sample_data):
        """Initialize analytics instance for testing."""
        return ScholarAnalytics(sample_data)

    def test_citation_statistics(self, analytics):
        """Test citation statistics calculations."""
        citations = analytics.processCitations()
        assert all(key in citations for key in [
            'distribution', 'total', 'average', 'median', 'max', 'min'
        ])

        # Test statistical calculations
        assert citations['total'] > 0
        assert citations['average'] >= 0
        assert citations['min'] <= citations['max']
        assert isinstance(citations['distribution']['bins'], list)

    def test_venue_analysis(self, analytics):
        """Test venue analysis functionality."""
        venues = analytics.processVenues()
        assert isinstance(venues, dict)

        # Test venue metrics
        top_venues = analytics.getTopVenues(limit=5)
        assert len(top_venues) <= 5
        assert all('name' in venue and 'count' in venue for venue in top_venues)

    def test_author_analysis(self, analytics):
        """Test author analysis functionality."""
        authors = analytics.processAuthors()

        assert 'collaborations' in authors
        assert 'productivity' in authors
        assert 'impact' in authors

        # Test author metrics
        top_authors = analytics.getTopAuthors(metric='citations', limit=5)
        assert len(top_authors) <= 5
        assert all(author['citations'] >= 0 for author in top_authors)

    def test_temporal_analysis(self, analytics):
        """Test temporal analysis capabilities."""
        temporal = analytics.analyzeTemporalTrends()

        assert 'yearly_counts' in temporal
        assert 'growth_rate' in temporal
        assert 'peak_years' in temporal

        # Verify trend calculations
        assert all(count >= 0 for count in temporal['yearly_counts'].values())
        assert isinstance(temporal['growth_rate'], float)

    def test_topic_modeling(self, analytics):
        """Test topic modeling and analysis."""
        topics = analytics.analyzeTopics()

        assert 'keywords' in topics
        assert 'clusters' in topics
        assert 'trends' in topics

        # Test topic extraction
        assert len(topics['keywords']) > 0
        assert all('weight' in keyword for keyword in topics['keywords'])

    def test_impact_metrics(self, analytics):
        """Test impact metrics calculations."""
        impact = analytics.calculateImpactMetrics()

        assert 'h_index' in impact
        assert 'g_index' in impact
        assert 'i10_index' in impact

        # Validate index calculations
        assert impact['h_index'] >= 0
        assert impact['g_index'] >= impact['h_index']

    def test_network_analysis(self, analytics):
        """Test collaboration network analysis."""
        network = analytics.analyzeCollaborationNetwork()

        assert 'nodes' in network
        assert 'edges' in network
        assert 'metrics' in network

        # Test network metrics
        metrics = network['metrics']
        assert 'density' in metrics
        assert 'centrality' in metrics
        assert 0 <= metrics['density'] <= 1

    def test_trend_detection(self, analytics):
        """Test research trend detection."""
        trends = analytics.detectTrends()

        assert 'emerging_topics' in trends
        assert 'declining_topics' in trends
        assert 'stable_topics' in trends

        # Validate trend scores
        for topic in trends['emerging_topics']:
            assert topic['growth_rate'] > 0

    def test_comparative_analysis(self, analytics):
        """Test comparative analysis features."""
        groups = {
            'group1': {'year_range': [2015, 2018]},
            'group2': {'year_range': [2019, 2022]}
        }
        comparison = analytics.compareGroups(groups)

        assert len(comparison) == len(groups)
        for group_result in comparison.values():
            assert 'metrics' in group_result
            assert 'significant_differences' in group_result

    def test_data_validation(self, analytics):
        """Test data validation and cleaning."""
        with pytest.raises(ValueError):
            analytics.validate_paper({})  # Empty paper

        with pytest.raises(ValueError):
            analytics.validate_paper({'title': '', 'year': 'invalid'})

        # Test valid paper
        valid_paper = {
            'title': 'Test Paper',
            'authors': ['Author One'],
            'year': 2020,
            'citations': 10,
            'venue': 'Test Venue'
        }
        assert analytics.validate_paper(valid_paper) == valid_paper

    @pytest.mark.parametrize("metric,expected_type", [
        ('citations', int),
        ('h_index', int),
        ('author_count', int),
        ('venue_diversity', float),
        ('collaboration_index', float)
    ])
    def test_metric_types(self, analytics, metric, expected_type):
        """Test metric value types."""
        metrics = analytics.calculateMetrics()
        assert isinstance(metrics[metric], expected_type)

    def test_error_handling(self, analytics):
        """Test error handling in analytics."""
        # Test missing data
        with pytest.raises(ValueError):
            analytics.rawData = None
            analytics.initialize()

        # Test invalid year range
        with pytest.raises(ValueError):
            analytics.filterByYearRange(start_year=2025, end_year=2020)

        # Test invalid citation range
        with pytest.raises(ValueError):
            analytics.filterByCitations(min_citations=-1)

    def test_caching(self, analytics):
        """Test caching mechanism."""
        # First call should compute
        result1 = analytics.getTopVenues()

        # Second call should use cache
        analytics._cache_timestamp = analytics._cache_timestamp  # Access private for testing
        result2 = analytics.getTopVenues()

        assert result1 == result2

        # Force recomputation
        analytics.clearCache()
        analytics._cache_timestamp = 0
        result3 = analytics.getTopVenues()

        assert result3 == result1  # Results should still be equal
