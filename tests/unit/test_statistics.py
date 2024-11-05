# test_statistics.py
import pytest
from scholar_analyzer.static.js.modules.statistics import ScholarStatistics


class TestStatistics:
    @pytest.fixture
    def statistics(self, sample_data):
        """Initialize statistics instance for testing."""
        return ScholarStatistics(sample_data)

    def test_basic_statistics(self, statistics):
        """Test basic statistical calculations."""
        stats = statistics.calculateBasicStats()

        assert all(key in stats for key in [
            'mean', 'median', 'mode', 'std_dev', 'variance'
        ])

        assert stats['mean'] >= 0
        assert stats['median'] >= 0
        assert stats['std_dev'] >= 0

    def test_distribution_analysis(self, statistics):
        """Test distribution analysis."""
        distribution = statistics.analyzeDistribution(bins=10)

        assert 'histogram' in distribution
        assert 'percentiles' in distribution
        assert 'skewness' in distribution
        assert 'kurtosis' in distribution

        assert len(distribution['histogram']['bins']) == 11  # n+1 bin edges
        assert len(distribution['histogram']['counts']) == 10

    def test_time_series_analysis(self, statistics):
        """Test time series analysis."""
        time_series = statistics.analyzeTimeSeries()

        assert 'trend' in time_series
        assert 'seasonality' in time_series
        assert 'forecast' in time_series

        # Test trend detection
        assert isinstance(time_series['trend']['slope'], float)
        assert 'r_squared' in time_series['trend']

    def test_correlation_analysis(self, statistics):
        """Test correlation analysis."""
        correlations = statistics.calculateCorrelations([
            'citations', 'author_count', 'year'
        ])

        assert isinstance(correlations, dict)
        for var1 in correlations:
            for var2 in correlations[var1]:
                assert -1 <= correlations[var1][var2] <= 1

    def test_hypothesis_testing(self, statistics):
        """Test statistical hypothesis testing."""
        # Test t-test
        t_test = statistics.performTTest(
            group1_data=[1, 2, 3],
            group2_data=[2, 3, 4]
        )
        assert 'statistic' in t_test
        assert 'p_value' in t_test

        # Test chi-square test
        chi_square = statistics.performChiSquareTest(
            observed=[10, 20, 30],
            expected=[13, 17, 30]
        )
        assert 'statistic' in chi_square
        assert 'p_value' in chi_square

    def test_regression_analysis(self, statistics):
        """Test regression analysis capabilities."""
        regression = statistics.performRegression(
            x_var='year',
            y_var='citations',
            regression_type='linear'
        )

        assert 'coefficients' in regression
        assert 'r_squared' in regression
        assert 'p_values' in regression
        assert 'predictions' in regression

        # Test polynomial regression
        poly_regression = statistics.performRegression(
            x_var='year',
            y_var='citations',
            regression_type='polynomial',
            degree=2
        )
        assert len(poly_regression['coefficients']) == 3  # degree + 1

    def test_clustering_analysis(self, statistics):
        """Test clustering analysis."""
        clusters = statistics.performClustering(
            features=['citations', 'year'],
            n_clusters=3
        )

        assert 'labels' in clusters
        assert 'centroids' in clusters
        assert 'inertia' in clusters
        assert 'silhouette_score' in clusters

        # Verify cluster assignments
        assert all(label >= 0 for label in clusters['labels'])
        assert max(clusters['labels']) == 2  # 3 clusters (0-2)

    def test_outlier_detection(self, statistics):
        """Test outlier detection methods."""
        outliers = statistics.detectOutliers(
            variable='citations',
            method='zscore',
            threshold=3
        )

        assert 'indices' in outliers
        assert 'scores' in outliers
        assert 'threshold_used' in outliers

        # Test IQR method
        iqr_outliers = statistics.detectOutliers(
            variable='citations',
            method='iqr',
            threshold=1.5
        )
        assert isinstance(iqr_outliers['indices'], list)

    def test_statistical_summaries(self, statistics):
        """Test generation of statistical summaries."""
        summary = statistics.generateSummary(['citations', 'year'])

        for variable in ['citations', 'year']:
            var_stats = summary[variable]
            assert 'count' in var_stats
            assert 'missing' in var_stats
            assert 'unique' in var_stats
            assert 'mean' in var_stats
            assert 'std' in var_stats
            assert 'min' in var_stats
            assert 'max' in var_stats
            assert 'quartiles' in var_stats

    def test_significance_tests(self, statistics):
        """Test various significance tests."""
        # ANOVA test
        anova_result = statistics.performANOVA(
            groups={
                'group1': [1, 2, 3],
                'group2': [2, 3, 4],
                'group3': [3, 4, 5]
            }
        )
        assert 'f_statistic' in anova_result
        assert 'p_value' in anova_result

        # Kolmogorov-Smirnov test
        ks_result = statistics.performKSTest(
            data=[1, 2, 3, 4, 5],
            distribution='normal'
        )
        assert 'statistic' in ks_result
        assert 'p_value' in ks_result

    def test_time_window_analysis(self, statistics):
        """Test analysis over time windows."""
        windows = statistics.analyzeTimeWindows(
            window_size=2,  # years
            metrics=['citations', 'paper_count']
        )

        assert isinstance(windows, dict)
        for window in windows:
            assert 'start_year' in window
            assert 'end_year' in window
            assert 'metrics' in window
            assert all(metric in window['metrics']
                       for metric in ['citations', 'paper_count'])

    def test_comparative_statistics(self, statistics):
        """Test comparative statistical analysis."""
        comparison = statistics.compareGroups(
            group1_data={'name': 'A', 'values': [1, 2, 3]},
            group2_data={'name': 'B', 'values': [2, 3, 4]},
            tests=['t_test', 'mann_whitney']
        )

        assert 't_test' in comparison
        assert 'mann_whitney' in comparison
        for test_result in comparison.values():
            assert 'statistic' in test_result
            assert 'p_value' in test_result

    def test_trend_analysis(self, statistics):
        """Test trend analysis methods."""
        trends = statistics.analyzeTrends(
            variable='citations',
            min_periods=3
        )

        assert 'overall_trend' in trends
        assert 'change_points' in trends
        assert 'seasonality' in trends
        assert 'growth_rate' in trends

        # Verify trend direction
        assert trends['overall_trend'] in [
            'increasing', 'decreasing', 'stable']

    @pytest.mark.parametrize("metric,expected_range", [
        ('mean', (0, float('inf'))),
        ('correlation', (-1, 1)),
        ('p_value', (0, 1)),
        ('r_squared', (0, 1))
    ])
    def test_metric_ranges(self, statistics, metric, expected_range):
        """Test that statistical metrics fall within expected ranges."""
        result = statistics.calculateMetric(metric, [1, 2, 3, 4, 5])
        min_val, max_val = expected_range
        assert min_val <= result <= max_val

    def test_error_handling(self, statistics):
        """Test error handling in statistical calculations."""
        # Test empty data
        with pytest.raises(ValueError):
            statistics.calculateBasicStats([])

        # Test invalid input types
        with pytest.raises(TypeError):
            statistics.performRegression(
                x_var='year',
                y_var='citations',
                regression_type='invalid'
            )

        # Test insufficient data
        with pytest.raises(ValueError):
            statistics.performTTest(
                group1_data=[1],  # Need at least 2 values
                group2_data=[2]
            )

    def test_cross_validation(self, statistics):
        """Test cross-validation procedures."""
        cv_results = statistics.performCrossValidation(
            model_type='regression',
            x_var='year',
            y_var='citations',
            folds=5
        )

        assert 'scores' in cv_results
        assert 'mean_score' in cv_results
        assert 'std_score' in cv_results
        assert len(cv_results['scores']) == 5  # Number of folds

    def test_bootstrap_analysis(self, statistics):
        """Test bootstrap analysis methods."""
        bootstrap = statistics.performBootstrap(
            data=[1, 2, 3, 4, 5],
            statistic='mean',
            n_iterations=1000,
            confidence_level=0.95
        )

        assert 'estimate' in bootstrap
        assert 'confidence_interval' in bootstrap
        assert 'standard_error' in bootstrap
        assert len(bootstrap['confidence_interval']) == 2
