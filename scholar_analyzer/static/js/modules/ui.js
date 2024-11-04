// ui.js - UI handling and dynamic updates
class ScholarUI {
    constructor(analytics) {
        this.analytics = analytics
        this.state = {
            currentTab: 'trends',
            isLoading: false,
            theme: localStorage.getItem('theme') || 'light',
            layout: localStorage.getItem('layout') || 'grid',
            chartInstances: new Map()
        }
    }

    initialize() {
        this.initializeTheme()
        this.initializeLayout()
        this.setupEventListeners()
        this.initializeTooltips()
        this.initializeResizeObserver()
        this.setupKeyboardNavigation()
    }

    initializeTheme() {
        document.documentElement.setAttribute('data-theme', this.state.theme)
        this.updateThemeButton()
    }

    initializeLayout() {
        document.body.setAttribute('data-layout', this.state.layout)
        this.updateLayoutControls()
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('[role="tab"]').forEach((tab) => {
            tab.addEventListener('click', (e) => this.handleTabSwitch(e))
        })

        // Theme toggle
        document.getElementById('themeToggle')?.addEventListener('click', () => {
            this.toggleTheme()
        })

        // Layout controls
        document.getElementById('layoutToggle')?.addEventListener('click', () => {
            this.toggleLayout()
        })

        // Export buttons
        document.querySelectorAll('[data-export]').forEach((button) => {
            button.addEventListener('click', (e) => this.handleExport(e))
        })

        // Search functionality
        const searchInput = document.getElementById('searchInput')
        if (searchInput) {
            searchInput.addEventListener(
                'input',
                this.debounce((e) => {
                    this.handleSearch(e.target.value)
                }, 300)
            )
        }

        // Filters
        this.setupFilterListeners()

        // Card interactions
        this.setupCardInteractions()

        // Window resize handling
        window.addEventListener(
            'resize',
            this.debounce(() => {
                this.handleResize()
            }, 250)
        )
    }

    setupFilterListeners() {
        const filterForm = document.getElementById('filterForm')
        if (!filterForm) return

        // Year range inputs
        ;['yearStart', 'yearEnd'].forEach((id) => {
            const input = document.getElementById(id)
            input?.addEventListener('change', () => this.validateYearRange())
        })

        // Citation range inputs
        ;['citationMin', 'citationMax'].forEach((id) => {
            const input = document.getElementById(id)
            input?.addEventListener('change', () => this.validateCitationRange())
        })

        // Venue selection
        const venueSelect = document.getElementById('venueFilter')
        if (venueSelect) {
            $(venueSelect)
                .select2({
                    placeholder: 'Select venues...',
                    allowClear: true,
                    closeOnSelect: false
                })
                .on('change', () => this.handleFilterChange())
        }

        // Author filter with autocomplete
        const authorInput = document.getElementById('authorFilter')
        if (authorInput) {
            $(authorInput).autocomplete({
                source: this.getAuthorSuggestions.bind(this),
                minLength: 2,
                select: (event, ui) => {
                    this.handleAuthorSelection(ui.item)
                }
            })
        }
    }

    setupCardInteractions() {
        document.querySelectorAll('.card').forEach((card) => {
            // Expand/collapse functionality
            const header = card.querySelector('.card-header')
            if (header) {
                header.addEventListener('click', () => {
                    card.classList.toggle('expanded')
                    this.handleCardResize(card)
                })
            }

            // Drag to reorder (if enabled)
            if (card.classList.contains('draggable')) {
                this.makeCardDraggable(card)
            }
        })
    }

    makeCardDraggable(card) {
        let pos = { top: 0, left: 0, x: 0, y: 0 }

        const mouseDownHandler = (e) => {
            if (!e.target.classList.contains('card-header')) return

            card.style.cursor = 'grabbing'
            pos = {
                left: card.offsetLeft,
                top: card.offsetTop,
                x: e.clientX,
                y: e.clientY
            }

            document.addEventListener('mousemove', mouseMoveHandler)
            document.addEventListener('mouseup', mouseUpHandler)
        }

        const mouseMoveHandler = (e) => {
            const dx = e.clientX - pos.x
            const dy = e.clientY - pos.y

            card.style.position = 'absolute'
            card.style.left = `${pos.left + dx}px`
            card.style.top = `${pos.top + dy}px`
        }

        const mouseUpHandler = () => {
            card.style.cursor = 'grab'
            document.removeEventListener('mousemove', mouseMoveHandler)
            document.removeEventListener('mouseup', mouseUpHandler)
        }

        card.addEventListener('mousedown', mouseDownHandler)
    }

    handleTabSwitch(event) {
        const newTab = event.target.getAttribute('data-tab')
        if (newTab === this.state.currentTab) return

        // Update UI
        document.querySelectorAll('[role="tab"]').forEach((tab) => {
            const isSelected = tab.getAttribute('data-tab') === newTab
            tab.setAttribute('aria-selected', isSelected.toString())
            tab.classList.toggle('active', isSelected)
        })

        document.querySelectorAll('[role="tabpanel"]').forEach((panel) => {
            panel.classList.toggle('active', panel.id === newTab)
        })

        // Update state
        this.state.currentTab = newTab

        // Handle specific tab content
        this.handleTabContent(newTab)
    }

    handleTabContent(tabId) {
        switch (tabId) {
            case 'trends':
                this.refreshCharts()
                break
            case 'papers':
                this.refreshTable()
                break
            case 'insights':
                this.loadInsights()
                break
        }
    }

    refreshCharts() {
        this.state.chartInstances.forEach((chart, id) => {
            const container = document.getElementById(id)
            if (container && container.offsetParent !== null) {
                chart.resize()
            }
        })
    }

    refreshTable() {
        const table = $('#papersTable').DataTable()
        table.columns.adjust().draw()
    }

    async loadInsights() {
        try {
            this.setLoading(true)
            const insights = await this.analytics.generateInsights()
            this.updateInsightsView(insights)
        } catch (error) {
            this.showError('Failed to load insights', error)
        } finally {
            this.setLoading(false)
        }
    }

    updateInsightsView(insights) {
        const container = document.getElementById('insightsContent')
        if (!container) return

        container.innerHTML = `
            <div class="insights-grid">
                ${this.renderAuthorsInsight(insights.authors)}
                ${this.renderVenuesInsight(insights.venues)}
                ${this.renderTrendsInsight(insights.trends)}
                ${this.renderTopicsInsight(insights.topics)}
            </div>
        `
    }

    renderAuthorsInsight(authors) {
        return `
            <div class="insight-card">
                <h3>Top Authors</h3>
                <div class="insight-content">
                    ${authors.top
                        .map(
                            (author) => `
                        <div class="insight-item">
                            <span class="author-name">${author.name}</span>
                            <span class="author-stats">
                                ${author.papers} papers, ${author.citations} citations
                            </span>
                        </div>
                    `
                        )
                        .join('')}
                </div>
            </div>
        `
    }

    renderVenuesInsight(venues) {
        return `
            <div class="insight-card">
                <h3>Top Venues</h3>
                <div class="insight-content">
                    ${venues.top
                        .map(
                            (venue) => `
                        <div class="insight-item">
                            <span class="venue-name">${venue.name}</span>
                            <span class="venue-stats">
                                ${venue.papers} papers, Impact: ${venue.impact.toFixed(2)}
                            </span>
                        </div>
                    `
                        )
                        .join('')}
                </div>
            </div>
        `
    }

    renderTrendsInsight(trends) {
        return `
            <div class="insight-card">
                <h3>Research Trends</h3>
                <div class="insight-content">
                    <div class="trend-chart" id="trendMiniChart"></div>
                    <div class="trend-highlights">
                        ${trends.highlights
                            .map(
                                (highlight) => `
                            <div class="highlight-item">
                                <span class="highlight-label">${highlight.label}</span>
                                <span class="highlight-value">${highlight.value}</span>
                            </div>
                        `
                            )
                            .join('')}
                    </div>
                </div>
            </div>
        `
    }

    renderTopicsInsight(topics) {
        return `
            <div class="insight-card">
                <h3>Research Topics</h3>
                <div class="insight-content">
                    <div class="topics-cloud" id="topicsCloud"></div>
                    <div class="emerging-topics">
                        <h4>Emerging Topics</h4>
                        ${topics.emerging
                            .map(
                                (topic) => `
                            <div class="topic-item">
                                <span class="topic-name">${topic.name}</span>
                                <span class="topic-growth">+${topic.growth}%</span>
                            </div>
                        `
                            )
                            .join('')}
                    </div>
                </div>
            </div>
        `
    }

    toggleTheme() {
        const newTheme = this.state.theme === 'light' ? 'dark' : 'light'
        this.state.theme = newTheme
        document.documentElement.setAttribute('data-theme', newTheme)
        localStorage.setItem('theme', newTheme)
        this.updateThemeButton()
        this.refreshCharts()
    }

    toggleLayout() {
        const newLayout = this.state.layout === 'grid' ? 'list' : 'grid'
        this.state.layout = newLayout
        document.body.setAttribute('data-layout', newLayout)
        localStorage.setItem('layout', newLayout)
        this.updateLayoutControls()
        this.refreshCharts()
    }

    updateThemeButton() {
        const button = document.getElementById('themeToggle')
        if (button) {
            button.innerHTML = `
                <span class="icon">
                    ${this.state.theme === 'light' ? '🌙' : '☀️'}
                </span>
                <span class="sr-only">
                    Switch to ${this.state.theme === 'light' ? 'dark' : 'light'} theme
                </span>
            `
        }
    }

    updateLayoutControls() {
        const button = document.getElementById('layoutToggle')
        if (button) {
            button.innerHTML = `
                <span class="icon">
                    ${this.state.layout === 'grid' ? '☰' : '⊞'}
                </span>
                <span class="sr-only">
                    Switch to ${this.state.layout === 'grid' ? 'list' : 'grid'} layout
                </span>
            `
        }
    }

    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            // Tab navigation
            if (e.ctrlKey && e.key >= '1' && e.key <= '3') {
                e.preventDefault()
                const tabs = ['trends', 'papers', 'insights']
                const index = parseInt(e.key) - 1
                if (tabs[index]) {
                    this.handleTabSwitch({ target: { getAttribute: () => tabs[index] } })
                }
            }

            // Search focus
            if (e.ctrlKey && e.key === 'f') {
                e.preventDefault()
                document.getElementById('searchInput')?.focus()
            }

            // Theme toggle
            if (e.ctrlKey && e.key === 't') {
                e.preventDefault()
                this.toggleTheme()
            }
        })
    }

    setLoading(loading) {
        this.state.isLoading = loading
        document.body.classList.toggle('loading', loading)
    }

    showError(message, error) {
        console.error(error)
        const container = document.createElement('div')
        container.className = 'error-message'
        container.innerHTML = `
            <div class="error-content">
                <h3>Error</h3>
                <p>${message}</p>
                <button class="btn-secondary">Dismiss</button>
            </div>
        `

        container.querySelector('button').addEventListener('click', () => {
            container.remove()
        })

        document.body.appendChild(container)
    }

    debounce(func, wait) {
        let timeout
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout)
                func(...args)
            }
            clearTimeout(timeout)
            timeout = setTimeout(later, wait)
        }
    }
}

export default ScholarUI
