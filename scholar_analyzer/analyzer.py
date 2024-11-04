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


class ScholarAnalyzer:
    """论文分析器"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.plots_dir = data_dir / 'plots'
        self.plots_dir.mkdir(exist_ok=True)

        # 下载必要的NLTK数据
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            print(f"Warning: NLTK数据下载失败: {e}")

    def generate_word_cloud(self, text_data: List[str], filename: str):
        """生成词云图"""
        text = ' '.join(text_data)
        wordcloud = WordCloud(width=1600, height=800,
                              background_color='white').generate(text)

        plt.figure(figsize=(20, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(self.plots_dir / filename)
        plt.close()

    def plot_yearly_trend(self, df: pd.DataFrame):
        """绘制年度趋势图"""
        plt.figure(figsize=(15, 8))
        year_counts = df['year'].value_counts().sort_index()
        sns.lineplot(x=year_counts.index, y=year_counts.values)
        plt.title('Publication Trend Over Years')
        plt.xlabel('Year')
        plt.ylabel('Number of Publications')
        plt.savefig(self.plots_dir / 'yearly_trend.png')
        plt.close()

    def analyze_citations(self, df: pd.DataFrame):
        """分析引用情况"""
        plt.figure(figsize=(15, 8))
        sns.histplot(data=df, x='citations', bins=50)
        plt.title('Citation Distribution')
        plt.xlabel('Number of Citations')
        plt.ylabel('Count')
        plt.savefig(self.plots_dir / 'citation_distribution.png')
        plt.close()

    def extract_topics(self, texts: List[str], num_topics: int = 10) -> List[str]:
        """使用关键词提取主题"""
        # 分词和清理
        tokens = []
        stop_words = set(stopwords.words('english'))
        for text in texts:
            if isinstance(text, str):
                words = word_tokenize(text.lower())
                words = [w for w in words if w.isalnum()
                         and w not in stop_words]
                tokens.extend(words)

        # 获取最常见的词作为主题
        return [word for word, _ in Counter(tokens).most_common(num_topics)]
