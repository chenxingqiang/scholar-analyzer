# test_filters.py
import pytest
from scholar_analyzer.static.js.modules.filters import ScholarFilters


class TestFilters:
    @pytest.fixture
    def filters(self, sample_data):
        """Initialize filters instance for testing."""
        return ScholarFilters(sample_data)

    def test_year_range_filter(self, filters):
        """Test year range filtering."""
        filtered = filters.filterByYearRange(2019, 2021)

        assert all(2019 <= paper['year'] <= 2021 for paper in filtered)

        # Test invalid ranges
        with pytest.raises(ValueError):
            filters.filterByYearRange(2021, 2019)  # End before start

        with pytest.raises(ValueError):
            filters.filterByYearRange(1800, 2025)  # Out of reasonable range

    def test_citation_filter(self, filters):
        """Test citation count filtering."""
        min_citations = 5
        filtered = filters.filterByCitations(min_citations=min_citations)

        assert all(paper['citations'] >= min_citations for paper in filtered)

        # Test maximum citations
        max_citations = 100
        filtered = filters.filterByCitations(max_citations=max_citations)
        assert all(paper['citations'] <= max_citations for paper in filtered)

    def test_author_filter(self, filters):
        """Test author filtering."""
        author_name = "Test Author"
        filtered = filters.filterByAuthor(author_name)

        assert all(
            any(author_name.lower() in author.lower()
                for author in paper['authors'])
            for paper in filtered
        )

        # Test multiple authors
        authors = ["Author One", "Author Two"]
        filtered = filters.filterByAuthors(authors, match_all=True)
        assert all(
            all(author in paper['authors'] for author in authors)
            for paper in filtered
        )

    def test_venue_filter(self, filters):
        """Test venue filtering."""
        venue = "Test Conference"
        filtered = filters.filterByVenue(venue)

        assert all(paper['venue'] == venue for paper in filtered)

        # Test venue patterns
        pattern = "Conference"
        filtered = filters.filterByVenuePattern(pattern)
        assert all(pattern in paper['venue'] for paper in filtered)

    def test_keyword_filter(self, filters):
        """Test keyword filtering."""
        keyword = "machine learning"
        filtered = filters.filterByKeyword(keyword)

        assert all(
            keyword.lower() in paper['title'].lower() or
            keyword.lower() in paper.get('abstract', '').lower()
            for paper in filtered
        )

    def test_complex_filters(self, filters):
        """Test complex filter combinations."""
        filter_config = {
            'year_range': {'start': 2019, 'end': 2021},
            'citations': {'min': 5},
            'venues': ['Test Conference'],
            'keywords': ['machine learning']
        }

        filtered = filters.applyFilters(filter_config)

        # Verify all conditions
        for paper in filtered:
            assert 2019 <= paper['year'] <= 2021
            assert paper['citations'] >= 5
            assert paper['venue'] in filter_config['venues']
            assert any(kw.lower() in paper['title'].lower()
                       for kw in filter_config['keywords'])

    def test_filter_validation(self, filters):
        """Test filter validation."""
        # Test invalid citation range
        with pytest.raises(ValueError):
            filters.filterByCitations(min_citations=-1)

        # Test invalid year range
        with pytest.raises(ValueError):
            filters.filterByYearRange(start_year=2025, end_year=2020)

        # Test empty filter
        with pytest.raises(ValueError):
            filters.filterByAuthor("")

    def test_filter_chaining(self, filters):
        """Test filter chaining capabilities."""
        result = (filters
                  .filterByYearRange(2019, 2021)
                  .filterByCitations(min_citations=5)
                  .filterByVenue("Test Conference")
                  .getResults())

        assert isinstance(result, list)
        assert all(
            2019 <= paper['year'] <= 2021 and
            paper['citations'] >= 5 and
            paper['venue'] == "Test Conference"
            for paper in result
        )

    def test_filter_persistence(self, filters):
        """Test filter state persistence."""
        filters.addFilter('year_range', {'start': 2019, 'end': 2021})
        filters.addFilter('citations', {'min': 5})

        assert len(filters.activeFilters) == 2
        assert filters.hasActiveFilters()

        filters.clearFilters()
        assert len(filters.activeFilters) == 0
        assert not filters.hasActiveFilters()

    def test_custom_filters(self, filters):
        """Test custom filter creation."""
        def custom_filter(paper):
            return len(paper['authors']) > 2

        filtered = filters.applyCustomFilter(custom_filter)
        assert all(len(paper['authors']) > 2 for paper in filtered)

    @pytest.mark.parametrize("filter_type,invalid_value", [
        ('year_range', {'start': 'invalid'}),
        ('citations', {'min': 'invalid'}),
        ('venues', 123),  # Should be list or string
        ('authors', {}),  # Should be list or string
    ])
    def test_filter_type_validation(self, filters, filter_type, invalid_value):
        """Test filter type validation."""
        with pytest.raises((ValueError, TypeError)):
            filters.addFilter(filter_type, invalid_value)

    def test_filter_suggestions(self, filters):
        """Test filter suggestion functionality."""
        # Author suggestions
        suggestions = filters.getAuthorSuggestions("Test")
        assert isinstance(suggestions, list)
        assert all('name' in s and 'count' in s for s in suggestions)

        # Venue suggestions
        suggestions = filters.getVenueSuggestions("Conf")
        assert isinstance(suggestions, list)
        assert all('name' in s and 'count' in s for s in suggestions)
