# Scholar Analyzer Testing & Publishing Guide

## 1. 本地测试流程

### 1.1 环境准备

```bash
# 创建新的虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# 安装开发依赖
pip install -r requirements-dev.txt

# 安装pre-commit hooks
pre-commit install
```

### 1.2 运行完整测试套件

```bash
# 运行所有测试
pytest

# 生成覆盖率报告
pytest --cov=scholar_analyzer --cov-report=html

# 运行特定测试组
pytest tests/unit/
pytest tests/integration/
pytest tests/frontend/

# 运行带标记的测试
pytest -v -m "not slow"
```

### 1.3 代码质量检查

```bash
# 运行静态类型检查
mypy scholar_analyzer

# 运行代码风格检查
flake8 scholar_analyzer
black --check scholar_analyzer

# 运行安全检查
bandit -r scholar_analyzer
```

### 1.4 文档测试

```bash
# 构建文档
cd docs
make html

# 检查文档链接
make linkcheck
```

## 2. CI/CD 流水线验证

### 2.1 GitHub Actions 工作流配置

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
        pip install -e .
    
    - name: Run tests
      run: |
        pytest --cov=scholar_analyzer --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### 2.2 本地验证 CI 流程

```bash
# 安装 act 工具 (https://github.com/nektos/act)
# 运行 GitHub Actions 工作流
act -j test
```

## 3. 打包和发布流程

### 3.1 准备发布

```bash
# 更新版本号
bump2version minor  # 或 major/patch

# 构建分发包
python -m build

# 检查分发包
twine check dist/*
```

### 3.2 测试发布

```bash
# 创建测试 PyPI 账号
# 发布到测试 PyPI
python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# 测试安装
pip install --index-url https://test.pypi.org/simple/ scholar-analyzer
```

### 3.3 正式发布

```bash
# 发布到 PyPI
python -m twine upload dist/*

# 验证安装
pip install scholar-analyzer
```

## 4. 发布后验证

### 4.1 安装测试

```bash
# 创建新的虚拟环境
python -m venv test-env
source test-env/bin/activate

# 安装包
pip install scholar-analyzer

# 运行基本测试
python -c "import scholar_analyzer; print(scholar_analyzer.__version__)"
```

### 4.2 功能验证

```python
# test_installation.py
from scholar_analyzer import analyze_publications

def test_basic_functionality():
    # 基本分析功能测试
    analysis = analyze_publications("quantum computing", years=[2020, 2024])
    assert analysis is not None
    
    # 生成报告测试
    analysis.generate_report("test_report.html")
    assert os.path.exists("test_report.html")
    
    # 导出功能测试
    analysis.export("test_results.json")
    assert os.path.exists("test_results.json")

# 运行验证
pytest test_installation.py
```

## 5. 持续监控

### 5.1 设置监控

```bash
# 设置 GitHub 议题模板
mkdir -p .github/ISSUE_TEMPLATE
touch .github/ISSUE_TEMPLATE/bug_report.md
touch .github/ISSUE_TEMPLATE/feature_request.md

# 设置依赖机器人
# Dependabot 配置
touch .github/dependabot.yml
```

### 5.2 自动化测试报告

```yaml
# .github/workflows/report.yml
name: Test Report

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * *'  # 每天运行

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Generate test report
      run: |
        pytest --html=report.html --self-contained-html
    - name: Upload report
      uses: actions/upload-artifact@v3
      with:
        name: test-report
        path: report.html
```

## 6. 版本发布检查清单

```markdown
### 发布前检查清单
- [ ] 所有测试通过
- [ ] 代码覆盖率达标 (>90%)
- [ ] 文档更新完成
- [ ] CHANGELOG.md 更新
- [ ] 版本号更新
- [ ] README.md 更新
- [ ] 依赖列表更新
- [ ] API 文档生成
- [ ] 性能测试完成
- [ ] 安全检查通过

### 发布后检查清单
- [ ] PyPI 包可以正常安装
- [ ] 示例代码可以运行
- [ ] CI/CD 通过
- [ ] 文档网站更新
- [ ] GitHub Release 创建
- [ ] 标签已推送
```

## 7. 问题排查指南

```bash
# 安装问题排查
pip install scholar-analyzer -v  # 详细安装日志

# 依赖冲突排查
pip check

# 运行诊断
scholar-analyzer --debug analyze --query "test"

# 日志检查
scholar-analyzer --log-level DEBUG analyze --query "test"
```
