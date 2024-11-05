from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="scholar-analyzer",
    version="0.1.0",
    author="Xingqiang Chen",
    author_email="chenxingqiang@iechor.com",
    description="A tool for analyzing scholarly literature",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chenxingqiang/scholar-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.8",
    install_requires=required,
    extras_require={
        'dev': [
            line.strip()
            for line in open('requirements-dev.txt')
            if not line.startswith('#')
        ],
        'test': [
            line.strip()
            for line in open('requirements-test.txt')
            if not line.startswith('#')
        ],
        'docs': [
            line.strip()
            for line in open('requirements-docs.txt')
            if not line.startswith('#')
        ],
    },
    entry_points={
        'console_scripts': [
            'scholar-analyzer=scholar_analyzer.cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'scholar_analyzer': [
            'static/css/*.css',
            'static/js/*.js',
            'static/js/config/*.js',
            'static/js/modules/*.js',
            'static/themes/*.css',
            'templates/*.html',
        ],
    },
)
