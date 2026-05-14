# 活文档与持续集成

## 第六阶段：将 BDD 测试转化为永久活文档，通过 CI 自动维护

---

## 一、活文档机制

### 1.1 原理

BDD 的 Feature 文件使用 Gherkin 自然语言描述，本身即是可读的规格文档。
通过 Allure Framework，将每次测试执行结果转化为可视化的 HTML 报告，
实现 **"文档即测试、测试即报告、报告即文档"** 的闭环。

### 1.2 架构

```
Feature 文件 (Gherkin)  
    ↓  pytest-bdd 驱动
测试执行 (137 个场景)  
    ↓  allure-pytest 收集
Allure 原始数据 (allure-results/)  
    ↓  allure generate
HTML 报告 (allure-report/)  
    ↓  GitHub Pages 部署
永久在线活文档
```

---

## 二、生成与查看报告

### 2.1 前置条件

```bash
# 安装 allure 命令行工具
npm install -g allure-commandline

# 安装 Python 依赖
cd backend
uv pip install allure-pytest
```

### 2.2 生成报告

```bash
cd backend

# 运行测试并收集 Allure 数据
uv run pytest tests/ --alluredir=allure-results

# 生成 HTML 报告
allure generate allure-results -o allure-report --clean

# 查看报告（启动本地 Web 服务器）
allure open allure-report
```

### 2.3 报告内容

| 维度 | 说明 |
|------|------|
| **Overview** | 总览：137 场景通过率、执行时间、图表 |
| **Categories** | 按测试结果分类（通过/失败/跳过/损坏） |
| **Suites** | 按测试文件分组：applications、groups、pricing、cancellations、payments |
| **Features** | 按 Gherkin Feature 分组展示业务场景 |
| **Behaviors** | 按 BDD 行为标签组织 |
| **Timeline** | 执行时序图，便于分析性能瓶颈 |

---

## 三、CI/CD 持续集成

### 3.1 Workflow 文件位置

`.github/workflows/spec-test.yml`

### 3.2 触发条件

| 事件 | 分支 |
|------|------|
| `push` | main, develop |
| `pull_request` | main |

### 3.3 流水线步骤

```yaml
1. Checkout 代码
2. 设置 Python 3.14 环境
3. 安装 uv 包管理器
4. uv sync 安装所有依赖
5. 运行 pytest 测试（含 Allure 收集）
6. 生成 Allure HTML 报告
7. 上传报告为 CI 工件（artifacts）
8. main 分支通过时部署到 GitHub Pages
```

### 3.4 CI 流程说明

- **每次 Push 到 main/develop** 或 **开启 PR** 时自动触发
- 使用 `sqlite:///:memory:` 内存数据库，无需外部服务
- 无论测试通过与否，都生成 Allure 报告并上传为 CI 工件
- main 分支测试通过时，自动将报告部署到 GitHub Pages
- 获取永久 URL：`https://<org>.github.io/<repo>/spec-report`

---

## 四、活文档的使用场景

| 场景 | 使用方式 |
|------|---------|
| **答辩演示** | 直接打开 GitHub Pages 的 Allure 报告，展示 Feature → 场景 → 步骤的完整链路 |
| **产品经理/老师审查** | 无需看代码，打开报告即可了解系统支持的所有业务场景 |
| **回归测试** | PR 合并前自动运行，任何破坏性修改即时发现 |
| **重构保护** | CI 拦截不合规的修改，防止功能退化 |
| **契约验证** | OpenAPI 规范与实现绑定，API 变更必须同步更新规范 |

---

## 五、交付物清单

| 文件/路径 | 说明 |
|-----------|------|
| `.github/workflows/spec-test.yml` | GitHub Actions CI 流水线定义 |
| `backend/requirements-dev.txt` | 开发依赖（含 allure-pytest, openapi-core, pyyaml） |
| `docs/reports/latest/` | 最新 Allure 报告 HTML 副本 |
| `doc/06_LIVING_DOCUMENTATION.MD` | 本文档 |
| `backend/allure-results/` | Allure 原始数据（.gitignore 中忽略） |

---

## 六、答辩演示要点

### 6.1 展示活文档
1. 打开 `docs/reports/latest/index.html` 或 GitHub Pages 链接
2. 展示 Overview 页面：137/137 通过
3. 按 **Features** 标签展示：左侧列出 5 个 Feature 文件
4. 点击任一 Scenario 展开详细步骤
5. 强调：报告展示的正是 Gherkin 原文 + 实际测试结果

### 6.2 展示 CI 流水线
1. 在 GitHub 仓库中打开 **Actions** 标签页
2. 展示 **Spec-Driven Test Suite** 工作流
3. 点击最近一次运行的 **Summary** 查看执行结果
4. 下载 **allure-report** 工件查看报告
5. （可选）录制现场 Push 代码的 CI 触发过程

### 6.3 展示契约校验
1. 故意修改 `services/pricing.py` 中的一个费率值
2. 运行测试，展示对应的 BDD 场景失败
3. 强调失败信息直接指出违反的业务规则

---

## 七、版本记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0.0 | 2026-05-14 | 初始版本：Allure 活文档 + GitHub Actions CI |
