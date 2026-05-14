# API 契约规范

## 第五阶段：API 契约设计与校验

本文档定义《旅游业务管理系统》的 OpenAPI 3.0.3 规范，并描述了如何将契约校验集成到 BDD 测试框架中，实现"设计即文档、文档即测试、测试即契约"的闭环。

---

## 一、概览

### 契约文件位置
| 文件 | 说明 |
|------|------|
| `docs/spec/openapi.yaml` | OpenAPI 3.0.3 完整规范 |
| `backend/tests/conftest.py` | 契约校验夹具 |
| `doc/05_API_CONTRACT.MD` | 本文档 |

### API 基础信息
| 属性 | 值 |
|------|-----|
| 基础 URL | `http://localhost:8000` |
| 协议 | HTTP/REST |
| 格式 | JSON |
| 版本 | 1.0.0 |

---

## 二、端点一览

### 2.1 路线管理 (`/api/routes`)

| 方法 | 路径 | 描述 | 状态码 |
|------|------|------|--------|
| GET | `/api/routes` | 查询路线列表 | 200 |
| POST | `/api/routes` | 创建路线 | 201, 422 |
| GET | `/api/routes/{route_id}` | 获取路线详情 | 200, 404 |
| PUT | `/api/routes/{route_id}` | 更新路线 | 200, 404, 422 |
| DELETE | `/api/routes/{route_id}` | 停用路线（软删除） | 204, 404 |

### 2.2 旅游团管理 (`/api/groups`)

| 方法 | 路径 | 描述 | 状态码 |
|------|------|------|--------|
| GET | `/api/groups` | 查询旅游团列表 | 200 |
| POST | `/api/groups` | 创建旅游团 | 201, 400, 422 |
| GET | `/api/groups/{group_id}` | 获取旅游团详情（含路线） | 200, 404 |
| PUT | `/api/groups/{group_id}` | 更新旅游团 | 200, 400, 404, 422 |
| POST | `/api/groups/{group_id}/publish` | 发布旅游团 | 200, 400, 404 |
| GET | `/api/groups/{group_id}/availability` | 检查可用名额 | 200, 404 |
| GET | `/api/groups/{group_id}/pricing-preview` | 预览订金计算 | 200, 404 |
| GET | `/api/groups/{group_id}/balance-deadline` | 计算尾款截止日期 | 200, 404 |

### 2.3 旅游申请管理 (`/api/applications`)

| 方法 | 路径 | 描述 | 状态码 |
|------|------|------|--------|
| POST | `/api/applications` | 创建旅游申请 | 201, 400, 422 |
| GET | `/api/applications/search` | 搜索申请 | 200 |
| GET | `/api/applications/{application_id}` | 查询申请详情 | 200, 404 |
| POST | `/api/applications/{application_id}/pay-deposit` | 支付订金 | 200, 400 |
| POST | `/api/applications/{application_id}/participants` | 批量录入参加者 | 200, 400 |
| GET | `/api/applications/{application_id}/participants` | 查询参加者列表 | 200 |
| PUT | `/api/applications/participants/{participant_id}` | 更新参加者信息 | 200, 400 |
| POST | `/api/applications/{application_id}/pay-balance` | 支付尾款 | 200, 400 |
| POST | `/api/applications/{application_id}/cancel` | 取消申请 | 200, 400 |
| GET | `/api/applications/{application_id}/cancel-preview` | 预览取消结果 | 200, 400 |

### 2.4 催款与财务 (`/api/tasks`)

| 方法 | 路径 | 描述 | 状态码 |
|------|------|------|--------|
| GET | `/api/tasks/daily-reminders` | 查询催款清单 | 200 |
| GET | `/api/tasks/daily-finance` | 查询资金流水 | 200 |
| POST | `/api/tasks/daily-finance/export` | 导出资金流水 | 200 |

---

## 三、核心业务规则

### 3.1 订金计算规则

| 距出发天数 | 订金比例 |
|-----------|---------|
| >= 60天 | 10% |
| 30-59天 | 20% |
| < 30天 | 100% |

### 3.2 取消手续费规则

| 距出发天数 | 手续费率 |
|-----------|---------|
| >= 30天 | 0%（免费） |
| 11-29天 | 20% |
| 1-10天 | 50% |
| 当天（0天） | 100% |

### 3.3 尾款截止日期规则

- **基础截止日期** = 出发日期 - 30天
- **备用截止日期** = 今天 + 10天
- **最终截止日期** = max(基础截止日期, 备用截止日期)，但仅当距基础截止日期<10天时采用备用

### 3.4 申请状态机

```
DRAFT → (支付订金) → DEPOSIT_PAID → (录入参加者 + 付清尾款) → CONFIRMED
  ↓                        ↓                    ↓
  └──→ CANCELLED     └──→ CANCELLED     └──→ CANCELLED
```

---

## 四、部署测试

### 4.1 安装依赖

```bash
cd backend
uv pip install openapi-core openapi-spec-validator pyyaml
```

### 4.2 验证规范文件

```python
from openapi_core import create_spec
import yaml

with open("../docs/spec/openapi.yaml", "r", encoding="utf-8") as f:
    spec_dict = yaml.safe_load(f)
spec = create_spec(spec_dict)
print("OpenAPI 规范加载成功")
```

### 4.3 运行所有测试（含契约校验）

```bash
uv run pytest tests/ -v
```

---

## 五、交付物

| 文件 | 说明 |
|------|------|
| `docs/spec/openapi.yaml` | 完整的 API 契约规范（18个端点） |
| `doc/05_API_CONTRACT.MD` | 本文档 - 设计说明与使用指南 |
| `backend/tests/conftest.py` | 增加 `openapi_spec` 和 `response_validator` 夹具 |

---

## 六、版本记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0.0 | 2026-05-14 | 初始版本，完整定义 18 个端点 |
