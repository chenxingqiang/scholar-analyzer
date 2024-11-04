# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="scholar-analyzer",
    version="0.1.0",
    author="Chen Xingqiang",
    author_email="chen.xingqiang@iechor.com",
    description="A comprehensive Google Scholar research analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chenxingqiang/scholar-analyzer",
    packages=find_packages(),
    package_data={
        'scholar_analyzer': [
            'templates/*.html',
            'static/css/*.css',
            'static/js/*.js',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "scholarly>=1.7.0",
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "tqdm>=4.62.0",
        "beautifulsoup4>=4.9.3",
        "requests>=2.26.0",
        "nltk>=3.6.0",
        "wordcloud>=1.8.1",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
    ],
    entry_points={
        "console_scripts": [
            "scholar-analyzer=scholar_analyzer.cli:main",
        ],
    },
)
