// scholar_analyzer/static/js/main.js

// Tab Management
function initTabs() {
    const tabs = document.querySelectorAll('[data-tab]')
    const contents = document.querySelectorAll('.tab-content')

    tabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            const targetId = tab.getAttribute('data-tab')

            // Update active states
            tabs.forEach((t) => t.classList.remove('active'))
            contents.forEach((c) => c.classList.remove('active'))

            tab.classList.add('active')
            document.getElementById(targetId).classList.add('active')
        })
    })

    // Activate first tab by default
    if (tabs.length > 0) {
        tabs[0].click()
    }
}

// Theme Management
function initTheme() {
    const themeToggle = document.getElementById('themeToggle')
    if (!themeToggle) return

    themeToggle.addEventListener('click', () => {
        const html = document.documentElement
        const currentTheme = html.getAttribute('data-theme') || 'light'
        const newTheme = currentTheme === 'light' ? 'dark' : 'light'

        html.setAttribute('data-theme', newTheme)
        localStorage.setItem('theme', newTheme)

        // Update theme stylesheet
        const themeStylesheet = document.getElementById('theme-stylesheet')
        if (themeStylesheet) {
            themeStylesheet.href = `/static/themes/${newTheme}.css`
        }
    })
}

// Export Functionality
function initExport() {
    document.querySelectorAll('[data-export]').forEach((button) => {
        button.addEventListener('click', async () => {
            const format = button.getAttribute('data-export')
            try {
                const response = await fetch(`/api/export/${format}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        /* Add any necessary data */
                    })
                })

                if (response.ok) {
                    const blob = await response.blob()
                    const url = window.URL.createObjectURL(blob)
                    const a = document.createElement('a')
                    a.href = url
                    a.download = `scholar-analysis.${format}`
                    document.body.appendChild(a)
                    a.click()
                    window.URL.revokeObjectURL(url)
                    a.remove()
                } else {
                    console.error('Export failed:', await response.text())
                }
            } catch (error) {
                console.error('Export error:', error)
            }
        })
    })
}

// Filter Management
function initFilters() {
    const applyFilters = document.getElementById('applyFilters')
    if (!applyFilters) return

    applyFilters.addEventListener('click', async () => {
        const yearStart = document.getElementById('yearStart').value
        const citationMin = document.getElementById('citationMin').value
        const venue = document.getElementById('venueFilter').value

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filters: {
                        yearStart,
                        citationMin,
                        venue
                    }
                })
            })

            if (response.ok) {
                const data = await response.json()
                updateResults(data)
            } else {
                console.error('Filter application failed:', await response.text())
            }
        } catch (error) {
            console.error('Filter error:', error)
        }
    })
}

// Results Update
function updateResults(data) {
    // Update papers list
    const papersList = document.querySelector('.papers-list')
    if (papersList && data.papers) {
        papersList.innerHTML = data.papers
            .map(
                (paper) => `
            <div class="paper-item">
                <h3 class="paper-title">${paper.title}</h3>
                <p class="paper-authors">${paper.authors.join(', ')}</p>
                <p class="paper-year">${paper.year}</p>
                <p class="paper-venue">${paper.venue}</p>
                <p class="paper-citations">Citations: ${paper.citations}</p>
            </div>
        `
            )
            .join('')
    }

    // Update metrics
    const metricsGrid = document.querySelector('.metrics-grid')
    if (metricsGrid && data.metrics) {
        metricsGrid.innerHTML = `
            <div class="metric">
                <h4>Total Papers</h4>
                <p>${data.metrics.total_papers}</p>
            </div>
            <div class="metric">
                <h4>Total Citations</h4>
                <p>${data.metrics.total_citations}</p>
            </div>
            <div class="metric">
                <h4>Average Citations</h4>
                <p>${(data.metrics.total_citations / data.metrics.total_papers).toFixed(2)}</p>
            </div>
        `
    }
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initTabs()
    initTheme()
    initExport()
    initFilters()
})
