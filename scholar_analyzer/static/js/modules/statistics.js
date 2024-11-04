// statistics.js - Advanced statistical analysis
class ScholarStatistics {
    constructor(analytics) {
        this.analytics = analytics
        this.stats = null
    }

    calculateStatistics() {
        const papers = this.analytics.processedData.papers

        this.stats = {
            basic: this.calculateBasicStats(papers),
            temporal: this.analyzeTemporalTrends(papers),
            network: this.analyzeCollaborationNetwork(papers),
            impact: this.analyzeResearchImpact(papers),
            topics: this.analyzeResearchTopics(papers)
        }

        return this.stats
    }

    calculateBasicStats(papers) {
        const citations = papers.map((p) => p.citations)
        const years = papers.map((p) => p.year)

        return {
            papers: {
                total: papers.length,
                withCitations: papers.filter((p) => p.citations > 0).length,
                averageAuthors: this.mean(papers.map((p) => p.authors.length))
            },
            citations: {
                total: this.sum(citations),
                mean: this.mean(citations),
                median: this.median(citations),
                stdDev: this.standardDeviation(citations),
                hIndex: this.calculateHIndex(citations)
            },
            temporal: {
                yearRange: {
                    min: Math.min(...years),
                    max: Math.max(...years)
                },
                averagePublicationsPerYear: papers.length / (Math.max(...years) - Math.min(...years) + 1)
            }
        }
    }

    analyzeTemporalTrends(papers) {
        // Group papers by year
        const yearlyStats = {}
        papers.forEach((paper) => {
            const year = paper.year
            if (!yearlyStats[year]) {
                yearlyStats[year] = {
                    papers: 0,
                    citations: 0,
                    venues: new Set(),
                    authors: new Set()
                }
            }
            yearlyStats[year].papers++
            yearlyStats[year].citations += paper.citations
            yearlyStats[year].venues.add(paper.venue)
            paper.authors.forEach((author) => yearlyStats[year].authors.add(author))
        })

        // Calculate growth rates and trends
        const years = Object.keys(yearlyStats).sort()
        const trends = years.map((year, i) => {
            const current = yearlyStats[year]
            const previous = i > 0 ? yearlyStats[years[i - 1]] : null

            return {
                year: parseInt(year),
                papers: current.papers,
                citations: current.citations,
                venueCount: current.venues.size,
                authorCount: current.authors.size,
                growthRate: previous ? ((current.papers - previous.papers) / previous.papers) * 100 : 0,
                citationGrowth: previous ? ((current.citations - previous.citations) / previous.citations) * 100 : 0
            }
        })

        return {
            yearly: yearlyStats,
            trends: trends,
            growthAnalysis: this.calculateGrowthMetrics(trends)
        }
    }

    analyzeCollaborationNetwork(papers) {
        const collaborations = new Map()
        const authorStats = new Map()

        // Build collaboration network
        papers.forEach((paper) => {
            // Update author statistics
            paper.authors.forEach((author) => {
                if (!authorStats.has(author)) {
                    authorStats.set(author, {
                        papers: 0,
                        citations: 0,
                        collaborators: new Set(),
                        venues: new Set()
                    })
                }
                const stats = authorStats.get(author)
                stats.papers++
                stats.citations += paper.citations
                stats.venues.add(paper.venue)
            })

            // Update collaboration edges
            for (let i = 0; i < paper.authors.length; i++) {
                for (let j = i + 1; j < paper.authors.length; j++) {
                    const pair = [paper.authors[i], paper.authors[j]].sort().join('|')
                    if (!collaborations.has(pair)) {
                        collaborations.set(pair, {
                            count: 0,
                            papers: []
                        })
                    }
                    const collab = collaborations.get(pair)
                    collab.count++
                    collab.papers.push({
                        title: paper.title,
                        year: paper.year,
                        citations: paper.citations
                    })

                    // Update collaborator sets
                    authorStats.get(paper.authors[i]).collaborators.add(paper.authors[j])
                    authorStats.get(paper.authors[j]).collaborators.add(paper.authors[i])
                }
            }
        })

        return {
            collaborationNetwork: {
                nodes: Array.from(authorStats.entries()).map(([author, stats]) => ({
                    id: author,
                    papers: stats.papers,
                    citations: stats.citations,
                    collaboratorCount: stats.collaborators.size,
                    venues: Array.from(stats.venues)
                })),
                edges: Array.from(collaborations.entries()).map(([pair, data]) => ({
                    source: pair.split('|')[0],
                    target: pair.split('|')[1],
                    weight: data.count,
                    papers: data.papers
                }))
            },
            metrics: {
                averageCollaboratorsPerAuthor: this.mean(
                    Array.from(authorStats.values()).map((stats) => stats.collaborators.size)
                ),
                largestCollaborationGroup: Math.max(
                    ...Array.from(collaborations.values()).map((collab) => collab.papers.length)
                ),
                mostCollaborativeAuthors: Array.from(authorStats.entries())
                    .sort((a, b) => b[1].collaborators.size - a[1].collaborators.size)
                    .slice(0, 10)
                    .map(([author, stats]) => ({
                        author,
                        collaborators: stats.collaborators.size,
                        papers: stats.papers
                    }))
            }
        }
    }

    analyzeResearchImpact(papers) {
        // Calculate impact metrics
        const venueImpact = new Map()
        const authorImpact = new Map()

        papers.forEach((paper) => {
            // Venue impact
            if (!venueImpact.has(paper.venue)) {
                venueImpact.set(paper.venue, {
                    papers: 0,
                    citations: 0,
                    authors: new Set()
                })
            }
            const venue = venueImpact.get(paper.venue)
            venue.papers++
            venue.citations += paper.citations
            paper.authors.forEach((author) => venue.authors.add(author))

            // Author impact
            paper.authors.forEach((author) => {
                if (!authorImpact.has(author)) {
                    authorImpact.set(author, {
                        papers: 0,
                        citations: 0,
                        venues: new Set()
                    })
                }
                const impact = authorImpact.get(author)
                impact.papers++
                impact.citations += paper.citations
                impact.venues.add(paper.venue)
            })
        })

        return {
            venues: {
                impact: Array.from(venueImpact.entries())
                    .map(([venue, stats]) => ({
                        venue,
                        papers: stats.papers,
                        citations: stats.citations,
                        impactFactor: stats.citations / stats.papers,
                        uniqueAuthors: stats.authors.size
                    }))
                    .sort((a, b) => b.impactFactor - a.impactFactor)
            },
            authors: {
                impact: Array.from(authorImpact.entries())
                    .map(([author, stats]) => ({
                        author,
                        papers: stats.papers,
                        citations: stats.citations,
                        hIndex: this.calculateAuthorHIndex(papers.filter((p) => p.authors.includes(author))),
                        venueCount: stats.venues.size
                    }))
                    .sort((a, b) => b.citations - a.citations)
            }
        }
    }

    analyzeResearchTopics(papers) {
        // Simple topic analysis based on title words
        const wordFrequency = new Map()
        const stopWords = new Set(['a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'of', 'and'])

        papers.forEach((paper) => {
            const words = paper.title
                .toLowerCase()
                .split(/\W+/)
                .filter((word) => word.length > 2 && !stopWords.has(word))

            words.forEach((word) => {
                if (!wordFrequency.has(word)) {
                    wordFrequency.set(word, {
                        count: 0,
                        papers: [],
                        citations: 0
                    })
                }
                const freq = wordFrequency.get(word)
                freq.count++
                freq.papers.push(paper.title)
                freq.citations += paper.citations
            })
        })

        const topWords = Array.from(wordFrequency.entries())
            .map(([word, stats]) => ({
                word,
                frequency: stats.count,
                papers: stats.papers.length,
                citations: stats.citations,
                averageImpact: stats.citations / stats.papers.length
            }))
            .sort((a, b) => b.frequency - a.frequency)

        return {
            topWords: topWords.slice(0, 50),
            wordConnections: this.analyzeWordCooccurrence(papers, wordFrequency),
            temporalTrends: this.analyzeTopicTrends(papers, Array.from(wordFrequency.keys()))
        }
    }

    // Helper methods
    sum(arr) {
        return arr.reduce((a, b) => a + b, 0)
    }

    mean(arr) {
        return this.sum(arr) / arr.length
    }

    median(arr) {
        const sorted = arr.slice().sort((a, b) => a - b)
        const mid = Math.floor(sorted.length / 2)
        return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2
    }

    standardDeviation(arr) {
        const mean = this.mean(arr)
        const variance = arr.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / arr.length
        return Math.sqrt(variance)
    }

    calculateHIndex(citations) {
        const sorted = citations.slice().sort((a, b) => b - a)
        let h = 0
        while (h < sorted.length && sorted[h] >= h + 1) {
            h++
        }
        return h
    }
}

export default ScholarStatistics
