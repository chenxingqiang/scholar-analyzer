// main.js - Application entry point
import ScholarAnalytics from './modules/analytics.js';
import chartConfig from './config/charts.js';
import { initializeUI, updateUI } from './modules/ui.js';

class ScholarApp {
    constructor() {
        this.analytics = null
        this.charts = []
        this.state = {
            isLoading: true,
            activeTab: 'trends',
            theme: 'light'
        }
    }

    async initialize() {
        try {
            // Show loading state
            this.toggleLoading(true)

            // Load data
            const response = await fetch('/data/analysis.json')
            const data = await response.json()

            // Initialize analytics
            this.analytics = new ScholarAnalytics(data)
            await this.analytics.initialize()

            // Initialize UI
            initializeUI()
            this.setupEventListeners()

            // Initialize charts
            this.initializeCharts()

            // Update UI with data
            this.updateDisplay()

            // Hide loading state
            this.toggleLoading(false)
        } catch (error) {
            console.error('Failed to initialize application:', error)
            this.handleError(error)
        }
    }

    initializeCharts() {
        // Initialize each chart
        const yearlyTrendChart = chartConfig.yearTrendChart.createChart(
            document.getElementById('yearlyTrendChart'),
            this.analytics.processedData.years
        )

        const citationChart = chartConfig.citationChart.createChart(
            document.getElementById('citationDistChart'),
            this.analytics.processedData.citations.distribution
        )

        const venueChart = chartConfig.venueChart.createChart(
            document.getElementById('venueDistChart'),
            this.analytics.processedData.venues
        )

        this.charts = [yearlyTrendChart, citationChart, venueChart]

        // Setup resize handlers
        chartConfig.utils.handleResize(this.charts)
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.tab-button').forEach((button) => {
            button.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab)
            })
        })

        // Theme toggling
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme()
        })

        // Export functionality
        document.getElementById('exportData').addEventListener('click', () => {
            this.exportData()
        })

        // Table interactions
        const papersTable = document.getElementById('papersTable')
        if (papersTable) {
            this.initializeDataTable(papersTable)
        }

        // Window resize handler
        window.addEventListener('resize', this.handleResize.bind(this))
    }

    updateDisplay() {
        // Update metrics
        const metrics = this.analytics.metrics
        document.getElementById('totalPapers').textContent = metrics.totalPapers.toLocaleString()
        document.getElementById('avgCitations').textContent = metrics.averageCitations.toFixed(1)
        document.getElementById('totalVenues').textContent = Object.keys(metrics.uniqueVenues).length
        document.getElementById('yearRange').textContent = `${metrics.yearRange.start} - ${metrics.yearRange.end}`

        // Update query information
        const queryParams = new URLSearchParams(window.location.search)
        document.getElementById('queryTerms').textContent = queryParams.get('query') || 'Not specified'
        document.getElementById('queryTimestamp').textContent = new Date().toLocaleString()

        // Update insights
        this.updateInsights()
    }

    initializeDataTable(table) {
        return $(table).DataTable({
            data: this.analytics.processedData.papers,
            columns: [
                {
                    data: 'title',
                    render: (data, type, row) => {
                        return row.url ? `<a href="${row.url}" target="_blank" rel="noopener">${data}</a>` : data
                    }
                },
                {
                    data: 'authors',
                    render: (data) => (Array.isArray(data) ? data.join(', ') : data)
                },
                { data: 'year' },
                { data: 'venue' },
                {
                    data: 'citations',
                    render: (data) => data.toLocaleString()
                }
            ],
            order: [[4, 'desc']],
            pageLength: 25,
            responsive: true,
            language: {
                search: 'Filter papers:',
                lengthMenu: 'Show _MENU_ papers per page',
                info: 'Showing _START_ to _END_ of _TOTAL_ papers'
            },
            initComplete: function () {
                // Add custom filters
                this.api()
                    .columns()
                    .every(function () {
                        const column = this
                        if (column.header().textContent === 'Year' || column.header().textContent === 'Venue') {
                            const select = $('<select><option value="">All</option></select>')
                                .appendTo($(column.header()))
                                .on('change', function () {
                                    const val = $.fn.dataTable.util.escapeRegex($(this).val())
                                    column.search(val ? `^${val}$` : '', true, false).draw()
                                })

                            column
                                .data()
                                .unique()
                                .sort()
                                .each(function (d) {
                                    select.append(`<option value="${d}">${d}</option>`)
                                })
                        }
                    })
            }
        })
    }

    updateInsights() {
        // Update author insights
        const authorInsights = document.getElementById('authorInsights')
        const topAuthors = this.analytics.metrics.topAuthors
        authorInsights.innerHTML = this.generateInsightsHTML('authors', topAuthors)

        // Update topic insights
        const topicInsights = document.getElementById('topicInsights')
        const researchTopics = this.analytics.processedData.topics
        topicInsights.innerHTML = this.generateInsightsHTML('topics', researchTopics)

        // Update citation insights
        const citationInsights = document.getElementById('citationInsights')
        const citationPatterns = this.analytics.processedData.citations
        citationInsights.innerHTML = this.generateCitationInsightsHTML(citationPatterns)
    }

    generateInsightsHTML(type, data) {
        const insightsList = Object.entries(data)
            .sort(([, a], [, b]) => b - a)
            .slice(0, 10)
            .map(
                ([key, value]) => `
                <div class="insight-item">
                    <span class="insight-label">${key}</span>
                    <span class="insight-value">${value}</span>
                </div>
            `
            )
            .join('')

        return `
            <div class="insights-list">
                ${insightsList}
            </div>
        `
    }

    generateCitationInsightsHTML(citationData) {
        return `
            <div class="citation-insights">
                <div class="insight-item">
                    <span class="insight-label">Median Citations</span>
                    <span class="insight-value">${citationData.median.toFixed(1)}</span>
                </div>
                <div class="insight-item">
                    <span class="insight-label">Most Cited Paper</span>
                    <span class="insight-value">${citationData.max} citations</span>
                </div>
                <div class="insight-item">
                    <span class="insight-label">h-index</span>
                    <span class="insight-value">${citationData.hIndex}</span>
                </div>
            </div>
        `
    }

    switchTab(tabId) {
        // Update active tab
        document.querySelectorAll('.tab-button').forEach((button) => {
            button.classList.toggle('active', button.dataset.tab === tabId)
        })

        document.querySelectorAll('.tab-panel').forEach((panel) => {
            panel.classList.toggle('active', panel.id === tabId)
        })

        // Trigger resize for charts if switching to trends tab
        if (tabId === 'trends') {
            this.charts.forEach((chart) => chart.resize())
        }

        this.state.activeTab = tabId
    }

    toggleTheme() {
        const newTheme = this.state.theme === 'light' ? 'dark' : 'light'
        document.body.classList.toggle('theme-dark')
        this.state.theme = newTheme

        // Update charts theme
        chartConfig.utils.updateTheme(this.charts, newTheme)

        // Save preference
        localStorage.setItem('theme', newTheme)
    }

    exportData() {
        const format = window.prompt('Choose export format (csv/bibtex):', 'csv')
        if (!format) return

        switch (format.toLowerCase()) {
            case 'csv':
                this.analytics.exportToCSV()
                break
            case 'bibtex':
                this.analytics.exportToBibTeX()
                break
            default:
                alert('Unsupported format. Please choose CSV or BibTeX.')
        }
    }

    toggleLoading(show) {
        document.body.classList.toggle('loading', show)
        this.state.isLoading = show
    }

    handleError(error) {
        // Remove loading state
        this.toggleLoading(false)

        // Show error message
        const errorContainer = document.createElement('div')
        errorContainer.classList.add('error-message')
        errorContainer.innerHTML = `
            <h2>Error Loading Data</h2>
            <p>There was a problem loading the analysis data. Please try refreshing the page.</p>
            <p class="error-details">${error.message}</p>
        `

        document.querySelector('.container').prepend(errorContainer)
    }

    handleResize() {
        if (this.state.activeTab === 'trends') {
            this.charts.forEach((chart) => chart.resize())
        }
    }
}

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    const app = new ScholarApp()
    app.initialize()
})