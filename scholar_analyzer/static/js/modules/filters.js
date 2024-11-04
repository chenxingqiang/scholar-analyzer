// filters.js - Advanced search and filtering capabilities
class ScholarFilters {
    constructor(analytics) {
        this.analytics = analytics;
        this.activeFilters = new Map();
    }

    initializeFilters() {
        this.createFilterUI();
        this.setupEventListeners();
    }

    createFilterUI() {
        const filterContainer = document.createElement('div');
        filterContainer.className = 'advanced-filters card';
        filterContainer.innerHTML = `
            <div class="filter-header">
                <h3>Advanced Filters</h3>
                <button class="btn-secondary" id="clearFilters">Clear All</button>
            </div>
            <div class="filter-body">
                <div class="filter-group">
                    <label>Year Range</label>
                    <div class="range-inputs">
                        <input type="number" id="yearStart" placeholder="From">
                        <input type="number" id="yearEnd" placeholder="To">
                    </div>
                </div>
                <div class="filter-group">
                    <label>Citation Count</label>
                    <div class="range-inputs">
                        <input type="number" id="citationMin" placeholder="Min">
                        <input type="number" id="citationMax" placeholder="Max">
                    </div>
                </div>
                <div class="filter-group">
                    <label>Authors</label>
                    <input type="text" id="authorFilter" placeholder="Filter by author">
                </div>
                <div class="filter-group">
                    <label>Venues</label>
                    <select id="venueFilter" multiple>
                        <option value="">Select venues...</option>
                    </select>
                </div>
            </div>
            <div class="filter-footer">
                <button class="btn-primary" id="applyFilters">Apply Filters</button>
            </div>
        `;

        document.querySelector('.tab-content').prepend(filterContainer);
        this.populateVenueOptions();
    }

    setupEventListeners() {
        // Year range filter
        const yearInputs = ['yearStart', 'yearEnd'].map(id => 
            document.getElementById(id));
        yearInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.validateYearRange(yearInputs[0], yearInputs[1]);
            });
        });

        // Citation range filter
        const citationInputs = ['citationMin', 'citationMax'].map(id => 
            document.getElementById(id));
        citationInputs.forEach(input => {
            input.addEventListener('change', () => {
                this.validateCitationRange(citationInputs[0], citationInputs[1]);
            });
        });

        // Author filter with debounce
        const authorInput = document.getElementById('authorFilter');
        authorInput.addEventListener('input', this.debounce(() => {
            this.updateAuthorSuggestions(authorInput.value);
        }, 300));

        // Apply filters
        document.getElementById('applyFilters').addEventListener('click', () => {
            this.applyFilters();
        });

        // Clear filters
        document.getElementById('clearFilters').addEventListener('click', () => {
            this.clearFilters();
        });
    }

    populateVenueOptions() {
        const venueSelect = document.getElementById('venueFilter');
        const venues = Object.keys(this.analytics.processedData.venues)
            .sort((a, b) => a.localeCompare(b));

        venues.forEach(venue => {
            const option = document.createElement('option');
            option.value = venue;
            option.textContent = venue;
            venueSelect.appendChild(option);
        });

        // Initialize Select2 for better UX
        $(venueSelect).select2({
            placeholder: 'Select venues...',
            allowClear: true,
            closeOnSelect: false
        });
    }

    validateYearRange(startInput, endInput) {
        const start = parseInt(startInput.value);
        const end = parseInt(endInput.value);
        
        if (start && end && start > end) {
            endInput.value = start;
        }

        const minYear = Math.min(...Object.keys(this.analytics.processedData.years));
        const maxYear = Math.max(...Object.keys(this.analytics.processedData.years));

        if (start < minYear) startInput.value = minYear;
        if (end > maxYear) endInput.value = maxYear;
    }

    validateCitationRange(minInput, maxInput) {
        const min = parseInt(minInput.value);
        const max = parseInt(maxInput.value);
        
        if (min && max && min > max) {
            maxInput.value = min;
        }

        if (min < 0) minInput.value = 0;
    }

    updateAuthorSuggestions(query) {
        if (!query) return;

        const authors = new Set();
        this.analytics.processedData.papers.forEach(paper => {
            paper.authors.forEach(author => {
                if (author.toLowerCase().includes(query.toLowerCase())) {
                    authors.add(author);
                }
            });
        });

        // Update UI with suggestions
        this.showAuthorSuggestions(Array.from(authors));
    }

    showAuthorSuggestions(authors) {
        let suggestionsContainer = document.getElementById('authorSuggestions');
        if (!suggestionsContainer) {
            suggestionsContainer = document.createElement('div');
            suggestionsContainer.id = 'authorSuggestions';
            suggestionsContainer.className = 'suggestions-container';
            document.getElementById('authorFilter').parentNode.appendChild(suggestionsContainer);
        }

        suggestionsContainer.innerHTML = authors
            .slice(0, 5)
            .map(author => `<div class="suggestion-item">${author}</div>`)
            .join('');

        // Add click handlers
        suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                document.getElementById('authorFilter').value = item.textContent;
                suggestionsContainer.innerHTML = '';
            });
        });
    }

    applyFilters() {
        const filters = {
            yearRange: {
                start: document.getElementById('yearStart').value,
                end: document.getElementById('yearEnd').value
            },
            citationRange: {
                min: document.getElementById('citationMin').value,
                max: document.getElementById('citationMax').value
            },
            author: document.getElementById('authorFilter').value,
            venues: Array.from(document.getElementById('venueFilter').selectedOptions)
                .map(option => option.value)
        };

        const filteredPapers = this.analytics.processedData.papers.filter(paper => {
            // Year filter
            if (filters.yearRange.start && paper.year < filters.yearRange.start) return false;
            if (filters.yearRange.end && paper.year > filters.yearRange.end) return false;

            // Citation filter
            if (filters.citationRange.min && paper.citations < filters.citationRange.min) return false;
            if (filters.citationRange.max && paper.citations > filters.citationRange.max) return false;

            // Author filter
            if (filters.author && !paper.authors.some(author => 
                author.toLowerCase().includes(filters.author.toLowerCase()))) return false;

            // Venue filter
            if (filters.venues.length && !filters.venues.includes(paper.venue)) return false;

            return true;
        });

        // Update UI with filtered results
        this.updateResults(filteredPapers);
        this.updateActiveFiltersUI(filters);
    }

    clearFilters() {
        // Reset all inputs
        document.getElementById('yearStart').value = '';
        document.getElementById('yearEnd').value = '';
        document.getElementById('citationMin').value = '';
        document.getElementById('citationMax').value = '';
        document.getElementById('authorFilter').value = '';
        $('#venueFilter').val(null).trigger('change');

        // Clear active filters
        this.activeFilters.clear();
        this.updateActiveFiltersUI({});

        // Reset to original data
        this.updateResults(this.analytics.processedData.papers);
    }

    updateResults(filteredPapers) {
        // Update papers table
        const dataTable = $('#papersTable').DataTable();
        dataTable.clear();
        dataTable.rows.add(filteredPapers);
        dataTable.draw();

        // Update metrics
        this.updateFilteredMetrics(filteredPapers);

        // Update charts if on trends tab
        if (document.getElementById('trends').classList.contains('active')) {
            this.updateFilteredCharts(filteredPapers);
        }
    }

    updateFilteredMetrics(filteredPapers) {
        const metrics = {
            totalPapers: filteredPapers.length,
            avgCitations: filteredPapers.reduce((sum, p) => sum + p.citations, 0) / filteredPapers.length,
            uniqueVenues: new Set(filteredPapers.map(p => p.venue)).size,
            yearRange: {
                start: Math.min(...filteredPapers.map(p => p.year)),
                end: Math.max(...filteredPapers.map(p => p.year))
            }
        };

        // Update UI
        document.getElementById('totalPapers').textContent = metrics.totalPapers.toLocaleString();
        document.getElementById('avgCitations').textContent = metrics.avgCitations.toFixed(1);
        document.getElementById('totalVenues').textContent = metrics.uniqueVenues;
        document.getElementById('yearRange').textContent = 
            `${metrics.yearRange.start} - ${metrics.yearRange.end}`;
    }

    updateFilteredCharts(filteredPapers) {
        // Recalculate data for charts
        const yearlyData = {};
        const venueData = {};
        const citationData = [];

        filteredPapers.forEach(paper => {
            // Yearly trends
            yearlyData[paper.year] = (yearlyData[paper.year] || 0) + 1;
            
            // Venue distribution
            venueData[paper.venue] = (venueData[paper.venue] || 0) + 1;
            
            // Citation data
            citationData.push(paper.citations);
        });

        // Update charts
        this.analytics.charts.forEach(chart => {
            if (chart.id === 'yearlyTrendChart') {
                chart.setOption({
                    xAxis: { data: Object.keys(yearlyData) },
                    series: [{ data: Object.values(yearlyData) }]
                });
            } else if (chart.id === 'venueDistChart') {
                const sortedVenues = Object.entries(venueData)
                    .sort(([,a], [,b]) => b - a)
                    .slice(0, 10);
                
                chart.setOption({
                    yAxis: { data: sortedVenues.map(([venue]) => venue) },
                    series: [{ data: sortedVenues.map(([,count]) => count) }]
                });
            } else if (chart.id === 'citationDistChart') {
                const distribution = this.calculateDistribution(citationData);
                chart.setOption({
                    xAxis: { data: distribution.bins },
                    series: [{ data: distribution.counts }]