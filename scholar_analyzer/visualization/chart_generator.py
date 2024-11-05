# scholar_analyzer/visualization/chart_generator.py
from pyecharts.charts import Line, Bar, Pie
import pyecharts.options as opts
from typing import Dict, Any
from pyecharts import options as opts
from pyecharts.charts import Line, Bar, Scatter, Graph
from pyecharts.globals import ThemeType
from typing import Dict, List, Any

import pyecharts

class ChartGenerator:
    def __init__(self, theme: ThemeType = ThemeType.LIGHT):
        self.theme = theme
        self.default_width = "100%"
        self.default_height = "400px"

    def generate_charts(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成所有所需的图表"""
        charts = {
            'trend': self.create_trend_chart(analysis_data['yearly_data']),
            'citations': self.create_citation_distribution(analysis_data['citation_data']),
            'venues': self.create_venue_distribution(analysis_data['venue_data']),
            'network': self.create_collaboration_network(
                analysis_data['network_nodes'],
                analysis_data['network_links']
            )
        }
        return charts

    def render_all_charts(self, charts: Dict[str, Any], output_dir: str) -> Dict[str, str]:
        """渲染所有图表到HTML文件"""
        rendered_paths = {}
        for name, chart in charts.items():
            output_path = f"{output_dir}/{name}_chart.html"
            chart.render(output_path)
            rendered_paths[name] = output_path
        return rendered_paths

    def create_trend_chart(self, data: Dict[str, int]) -> Line:
        """创建年度趋势图"""
        x_data = list(data.keys())
        y_data = list(data.values())

        line = (
            Line(
                init_opts=opts.InitOpts(
                    theme=self.theme,
                    width=self.default_width,
                    height=self.default_height
                )
            )
            .add_xaxis(x_data)
            .add_yaxis(
                "Publications",
                y_data,
                symbol_size=8,
                label_opts=opts.LabelOpts(is_show=False),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="Publication Trends",
                    subtitle="Annual publication count"
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    orient="vertical",
                    pos_left="right",
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    boundary_gap=False,
                    name="Year"
                ),
                yaxis_opts=opts.AxisOpts(
                    name="Number of Publications",
                    type_="value",
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(type_="inside"),
                    opts.DataZoomOpts()
                ],
            )
        )
        return line

        # scholar_analyzer/visualization/chart_generator.py


class ChartGenerator:
    def __init__(self, theme: str = "light"):
        """Initialize chart generator with theme."""
        self.theme = ThemeType.LIGHT if theme == "light" else ThemeType.DARK

    def generate_yearly_trend_chart(self, data: Dict[str, int]) -> str:
        """Generate yearly trend chart."""
        x_data = list(data.keys())
        y_data = list(data.values())

        c = (
            Line(init_opts=opts.InitOpts(theme=self.theme))
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(
                series_name="Publications",
                y_axis=y_data,
                is_smooth=True
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Publications by Year"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
            )
        )
        return c.render_embed()

    def generate_citation_chart(self, data: Dict[str, int]) -> str:
        """Generate citation distribution chart."""
        x_data = list(data.keys())
        y_data = list(data.values())

        c = (
            Bar(init_opts=opts.InitOpts(theme=self.theme))
            .add_xaxis(x_data)
            .add_yaxis("Citations", y_data)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Citation Distribution"),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(rotate=45)),
                datazoom_opts=[opts.DataZoomOpts()],
            )
        )
        return c.render_embed()

    def generate_venue_chart(self, data: Dict[str, int]) -> str:
        """Generate venue distribution chart."""
        items = sorted(data.items(), key=lambda x: x[1], reverse=True)[
            :10]  # Top 10 venues
        venues = [item[0] for item in items]
        counts = [item[1] for item in items]

        c = (
            Pie(init_opts=opts.InitOpts(theme=self.theme))
            .add(
                series_name="Papers",
                data_pair=[[v, c] for v, c in zip(venues, counts)],
                radius=["40%", "70%"],
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Top Publication Venues"),
                legend_opts=opts.LegendOpts(orient="vertical", pos_left="5%"),
            )
        )
        return c.render_embed()
