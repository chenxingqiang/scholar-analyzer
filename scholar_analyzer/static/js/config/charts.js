// charts.js - Chart configurations and utilities
const chartConfig = {
    // Common chart options
    commonOptions: {
        animation: true,
        responsive: true,
        maintainAspectRatio: false,
        theme: {
            textStyle: {
                fontFamily: getComputedStyle(document.body).getPropertyValue('--font-primary')
            }
        }
    },

    // Year trend chart configuration
    yearTrendChart: {
        createChart(container, data) {
            const chart = echarts.init(container)
            const option = {
                ...this.commonOptions,
                title: {
                    text: 'Publications by Year',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis',
                    formatter: '{b}: {c} publications'
                },
                xAxis: {
                    type: 'category',
                    data: data.years,
                    axisTick: {
                        alignWithLabel: true
                    }
                },
                yAxis: {
                    type: 'value',
                    name: 'Publications',
                    nameLocation: 'middle',
                    nameGap: 50
                },
                series: [
                    {
                        type: 'line',
                        data: data.counts,
                        smooth: true,
                        lineStyle: {
                            width: 3,
                            color: getComputedStyle(document.body).getPropertyValue('--color-primary')
                        },
                        areaStyle: {
                            opacity: 0.1
                        }
                    }
                ]
            }
            chart.setOption(option)
            return chart
        }
    },

    // Citation distribution chart
    citationChart: {
        createChart(container, data) {
            const chart = echarts.init(container)
            const option = {
                ...this.commonOptions,
                title: {
                    text: 'Citation Distribution',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                xAxis: {
                    type: 'category',
                    name: 'Citations',
                    data: data.ranges
                },
                yAxis: {
                    type: 'value',
                    name: 'Number of Papers'
                },
                series: [
                    {
                        type: 'bar',
                        data: data.counts,
                        itemStyle: {
                            color: getComputedStyle(document.body).getPropertyValue('--color-primary')
                        }
                    }
                ]
            }
            chart.setOption(option)
            return chart
        }
    },

    // Venue distribution chart
    venueChart: {
        createChart(container, data) {
            const chart = echarts.init(container)
            const option = {
                ...this.commonOptions,
                title: {
                    text: 'Top Publication Venues',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'axis',
                    axisPointer: {
                        type: 'shadow'
                    }
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'value',
                    boundaryGap: [0, 0.01]
                },
                yAxis: {
                    type: 'category',
                    data: data.venues,
                    axisLabel: {
                        interval: 0,
                        rotate: 30
                    }
                },
                series: [
                    {
                        type: 'bar',
                        data: data.counts,
                        itemStyle: {
                            color: getComputedStyle(document.body).getPropertyValue('--color-primary')
                        }
                    }
                ]
            }
            chart.setOption(option)
            return chart
        }
    },

    // Utility functions
    utils: {
        // Resize handler for responsive charts
        handleResize(charts) {
            window.addEventListener('resize', () => {
                charts.forEach((chart) => chart.resize())
            })
        },

        // Theme updater for charts
        updateTheme(charts, theme) {
            charts.forEach((chart) => {
                chart.dispose()
                // Reinitialize with new theme
                this.initializeCharts()
            })
        }
    }
}

export default chartConfig
