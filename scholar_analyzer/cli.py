import hashlib
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
import warnings
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from typing import List, Dict, Any
import re
from bs4 import BeautifulSoup
import requests
from pathlib import Path
import json
import logging
from tqdm import tqdm
import random
import time
from datetime import datetime
import pandas as pd
import click
import asyncio
from scholarly import scholarly


class ScholarCLI:
    """Google Scholar命令行工具"""

    def __init__(self, query: str, limit: int = 1000):
        self.query = query
        self.limit = limit
        self.setup_directories()
        self.setup_logging()

    def generate_html_report(self):
        """生成HTML报告"""
        # 复制HTML模板到结果目录
        html_template = Path(__file__).parent / 'scholar_template.html'
        if not html_template.exists():
            # 如果模板文件不存在，创建一个新的
            with open(html_template, 'w', encoding='utf-8') as f:
                f.write(HTML_TEMPLATE)  # HTML_TEMPLATE 是上面的HTML内容

        # 复制到结果目录
        shutil.copy(html_template, self.base_dir / 'index.html')

        self.logger.info(f"HTML报告已生成: {self.base_dir}/index.html")

    def setup_directories(self):
        """设置目录结构"""
        # 使用查询字符串的哈希作为目录名的一部分
        query_hash = hashlib.md5(self.query.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.base_dir = Path(f"scholar_results_{query_hash}_{timestamp}")

        # 创建必要的子目录
        self.data_dir = self.base_dir / 'data'
        self.logs_dir = self.base_dir / 'logs'
        self.analysis_dir = self.base_dir / 'analysis'

        for directory in [self.data_dir, self.logs_dir, self.analysis_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # 创建分析器实例
        self.analyzer = ScholarAnalyzer(self.analysis_dir)

    def setup_logging(self):
        """配置日志系统"""
        log_file = self.logs_dir / 'scholar_cli.log'
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def fetch_papers(self) -> List[Dict[str, Any]]:
        """获取论文数据"""
        self.logger.info(f"开始获取论文数据: {self.query}")
        papers = []
        search_query = scholarly.search_pubs(self.query)

        with tqdm(total=self.limit, desc="获取论文") as pbar:
            try:
                for i in range(self.limit):
                    paper = next(search_query)
                    paper_info = self._extract_paper_info(paper)
                    if paper_info:
                        papers.append(paper_info)
                        pbar.update(1)
                    time.sleep(random.uniform(1, 3))
            except StopIteration:
                self.logger.info("没有更多结果")
            except Exception as e:
                self.logger.error(f"获取论文时出错: {str(e)}")

        return papers

    def _extract_paper_info(self, paper) -> Dict[str, Any]:
        """提取论文详细信息"""
        try:
            # 检查 paper 是否为预期的字典结构
            if isinstance(paper, dict):
                info = {
                    'title': paper.get('title', ''),
                    'authors': paper.get('author', []),
                    'year': paper.get('year', ''),
                    'venue': paper.get('venue', ''),
                    'abstract': paper.get('abstract', ''),
                    'citations': paper.get('citedby', 0),
                    'url': paper.get('url', ''),
                    'keywords': paper.get('keywords', []),
                    'doi': paper.get('doi', ''),
                    'timestamp': datetime.now().isoformat()
                }

                # 补充额外信息
                info['author_count'] = len(info['authors']) if isinstance(
                    info['authors'], list) else 0
                info['has_abstract'] = bool(info['abstract'])
                info['has_doi'] = bool(info['doi'])

                return info
            else:
                self.logger.error("Unexpected format for paper object.")
                return None
        except Exception as e:
            self.logger.error(f"提取论文信息时出错: {str(e)}")
            return None

    def analyze_results(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析论文数据"""
        df = pd.DataFrame(papers)

        # 基础统计
        analysis = {
            'total_papers': len(df),
            'years_distribution': df['year'].value_counts().to_dict(),
            'venue_distribution': df['venue'].value_counts().head(20).to_dict(),
            'top_authors': self._get_top_authors(df),
            'citation_stats': {
                'mean': float(df['citations'].mean()),
                'median': float(df['citations'].median()),
                'max': float(df['citations'].max()),
                'min': float(df['citations'].min()),
                'std': float(df['citations'].std())
            }
        }

        # 生成可视化
        try:
            self.analyzer.plot_yearly_trend(df)
            self.analyzer.analyze_citations(df)

            # 生成词云
            if 'abstract' in df.columns:
                abstracts = df['abstract'].dropna().tolist()
                self.analyzer.generate_word_cloud(
                    abstracts, 'abstract_wordcloud.png')

            # 主题分析
            if 'abstract' in df.columns:
                analysis['main_topics'] = self.analyzer.extract_topics(
                    df['abstract'].dropna().tolist())

        except Exception as e:
            self.logger.error(f"生成可视化时出错: {str(e)}")

        return analysis

    def _get_top_authors(self, df: pd.DataFrame, top_n: int = 20) -> Dict[str, int]:
        """获取发表最多的作者"""
        all_authors = []
        for authors in df['authors']:
            if isinstance(authors, list):
                all_authors.extend(authors)
        return dict(Counter(all_authors).most_common(top_n))

    def save_results(self, papers: List[Dict[str, Any]], analysis: Dict[str, Any]):
        """保存结果"""
        # 保存原始数据
        papers_df = pd.DataFrame(papers)
        papers_df.to_csv(self.data_dir / 'papers.csv',
                         index=False, encoding='utf-8')

        with open(self.data_dir / 'papers.json', 'w', encoding='utf-8') as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)

        # 保存分析结果
        with open(self.analysis_dir / 'analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)

        # 生成README
        self._generate_readme(papers, analysis)

    def _generate_readme(self, papers: List[Dict[str, Any]], analysis: Dict[str, Any]):
        """生成项目README文件"""
        readme_content = f"""# Google Scholar Research Results

## Query Information
- Query: {self.query}
- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Total Papers: {len(papers)}

## Summary
- Year Range: {min(analysis['years_distribution'].keys())} - {max(analysis['years_distribution'].keys())}
- Average Citations: {analysis['citation_stats']['mean']:.2f}
- Total Venues: {len(analysis['venue_distribution'])}

## Directory Structure
- `data/`: Raw data in CSV and JSON formats
- `analysis/`: Analysis results and visualizations
- `logs/`: Execution logs

## Top Venues
{self._format_dict(analysis['venue_distribution'], 5)}

## Most Cited Papers
{self._format_top_papers(papers, 5)}

## Main Topics
{', '.join(analysis.get('main_topics', [])[:10])}

## Visualization
Plots are available in the `analysis/plots` directory:
- Yearly trend
- Citation distribution
- Abstract word cloud

## Data Files
- `data/papers.csv`: Complete dataset in CSV format
- `data/papers.json`: Complete dataset in JSON format
- `analysis/analysis.json`: Detailed analysis results
"""
        with open(self.base_dir / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)

    def _format_dict(self, d: Dict, limit: int) -> str:
        """格式化字典为Markdown列表"""
        return '\n'.join([f"- {k}: {v}" for k, v in list(d.items())[:limit]])

    def _format_top_papers(self, papers: List[Dict[str, Any]], limit: int) -> str:
        """格式化top论文为Markdown列表"""
        sorted_papers = sorted(
            papers, key=lambda x: x['citations'], reverse=True)
        return '\n'.join([f"- {p['title']} (Citations: {p['citations']})" for p in sorted_papers[:limit]])


# 更新 main 函数
@click.command()
@click.argument('query')
@click.option('--limit', '-l', default=1000, help='Number of papers to fetch')
@click.option('--output', '-o', help='Output directory (optional)')
def main(query: str, limit: int, output: str):
    """Google Scholar论文检索和分析工具"""
    try:
        # 创建CLI实例
        cli = ScholarCLI(query, limit)

        # 获取论文
        click.echo("开始获取论文数据...")
        papers = cli.fetch_papers()

        # 分析结果
        click.echo("分析数据...")
        analysis = cli.analyze_results(papers)

        # 保存结果
        click.echo("保存结果...")
        cli.save_results(papers, analysis)

        click.echo(f"\n完成! 结果保存在: {cli.base_dir}")
        click.echo(f"详细信息请查看: {cli.base_dir}/README.md")

    except Exception as e:
        click.echo(f"错误: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    warnings.filterwarnings('ignore')
    main()
