// analytics.js - Data processing and analysis utilities
class ScholarAnalytics {
    constructor(data) {
        this.rawData = data
        this.processedData = null
        this.metrics = null
    }

    // Initialize and process data
    async initialize() {
        try {
            this.processedData = await this.processRawData()
            this.metrics = this.calculateMetrics()
            return true
        } catch (error) {
            console.error('Failed to initialize analytics:', error)
            return false
        }
    }

    // Process raw data into useful formats
    processRawData() {
        return {
            papers: this.processPapers(),
            citations: this.processCitations(),
            venues: this.processVenues(),
            years: this.processYearlyTrends()
        }
    }

    // Calculate key metrics
    calculateMetrics() {
        return {
            totalPapers: this.rawData.length,
            averageCitations: this.calculateAverageCitations(),
            uniqueVenues: this.calculateUniqueVenues(),
            yearRange: this.calculateYearRange(),
            topAuthors: this.calculateTopAuthors(),
            topVenues: this.calculateTopVenues()
        }
    }

    // Individual processing methods
    processPapers() {
        return this.rawData.map((paper) => ({
            id: paper.id,
            title: paper.title,
            authors: paper.authors,
            year: paper.year,
            venue: paper.venue,
            citations: paper.citations,
            url: paper.url
        }))
    }

    processCitations() {
        const citations = this.rawData.map((paper) => paper.citations)
        return {
            distribution: this.calculateDistribution(citations),
            total: citations.reduce((a, b) => a + b, 0),
            average: citations.reduce((a, b) => a + b, 0) / citations.length,
            median: this.calculateMedian(citations),
            max: Math.max(...citations),
            min: Math.min(...citations)
        }
    }

    processVenues() {
        const venueCount = {}
        this.rawData.forEach((paper) => {
            venueCount[paper.venue] = (venueCount[paper.venue] || 0) + 1
        })
        return Object.entries(venueCount)
            .sort(([, a], [, b]) => b - a)
            .reduce(
                (obj, [key, value]) => ({
                    ...obj,
                    [key]: value
                }),
                {}
            )
    }

    processYearlyTrends() {
        const yearCount = {}
        this.rawData.forEach((paper) => {
            yearCount[paper.year] = (yearCount[paper.year] || 0) + 1
        })
        return Object.entries(yearCount)
            .sort(([a], [b]) => a - b)
            .reduce(
                (obj, [key, value]) => ({
                    ...obj,
                    [key]: value
                }),
                {}
            )
    }

    // Utility methods
    calculateDistribution(numbers, bins = 10) {
        const min = Math.min(...numbers)
        const max = Math.max(...numbers)
        const range = max - min
        const binSize = range / bins

        const distribution = Array(bins).fill(0)
        numbers.forEach((num) => {
            const binIndex = Math.min(Math.floor((num - min) / binSize), bins - 1)
            distribution[binIndex]++
        })

        return {
            bins: Array.from({ length: bins }, (_, i) => min + i * binSize),
            counts: distribution
        }
    }

    calculateMedian(numbers) {
        const sorted = numbers.slice().sort((a, b) => a - b)
        const middle = Math.floor(sorted.length / 2)

        if (sorted.length % 2 === 0) {
            return (sorted[middle - 1] + sorted[middle]) / 2
        }

        return sorted[middle]
    }

    // Export methods
    exportToCSV() {
        // Implementation for CSV export
    }

    exportToBIBTEX() {
        // Implementation for BibTeX export
    }
}

export default ScholarAnalytics
