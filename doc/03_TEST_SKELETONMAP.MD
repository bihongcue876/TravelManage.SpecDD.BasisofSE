# 步骤函数对应清单
步骤函数与.feature文件对应清单。

---

## 测试骨架结构

本项目采用 pytest-bdd 框架实现 BDD 自动化测试，所有测试骨架文件位于 `backend/tests/` 目录下。

### 目录结构

```
project_root/
├── features/                    # Gherkin Feature 文件（项目根目录）
│   ├── applications.feature     # 旅游申请管理
│   ├── groups.feature          # 旅游团管理
│   ├── pricing.feature         # 价格计算
│   ├── cancellations.feature   # 取消申请
│   └── payments.feature        # 支付管理
├── backend/
│   ├── tests/                   # 测试骨架文件
│   │   ├── conftest.py         # 全局测试夹具
│   │   ├── test_applications.py    # 申请管理测试
│   │   ├── test_groups.py          # 旅游团测试
│   │   ├── test_pricing.py         # 价格计算测试
│   │   ├── test_cancellations.py   # 取消申请测试
│   │   └── test_payments.py        # 支付管理测试
```

**路径说明**：Feature 文件实际位于项目根目录 `features/` 下，测试文件中引用路径为 `../../features/<name>.feature`（从 `backend/tests/` 出发）。

---

## Feature 文件与测试文件映射

### 1. applications.feature ↔ test_applications.py

**Feature**: 旅游申请管理

**测试场景数量**: 27 个

**主要步骤函数**:

| 步骤类型 | 步骤函数名 | 描述 |
|---------|-----------|------|
| Given | `route_exists` | 系统中存在旅游路线 |
| Given | `group_exists` | 系统中存在旅游团 |
| Given | `group_departure_date` | 设置旅游团出发日期 |
| Given | `group_deadline` | 设置旅游团截止日期 |
| Given | `application_exists_with_deposit` | 存在申请（含订金信息） |
| When | `create_application_with_table` | 创建申请（表格参数） |
| When | `pay_deposit` | 支付订金 |
| When | `add_participants_with_table` | 录入参加者信息 |
| When | `pay_balance` | 支付尾款 |
| When | `get_application_detail` | 查询申请详情 |
| Then | `application_created_successfully` | 申请创建成功 |
| Then | `deposit_is` | 验证订金金额 |
| Then | `application_state_is` | 验证申请状态 |
| Then | `payment_successful` | 支付成功 |
| Then | `participants_count_is` | 验证参加者数量 |

---

### 2. groups.feature ↔ test_groups.py

**Feature**: 旅游团管理

**测试场景数量**: 24 个

**主要步骤函数**:

| 步骤类型 | 步骤函数名 | 描述 |
|---------|-----------|------|
| Given | `group_exists_with_status` | 存在指定状态的旅游团 |
| Given | `group_with_capacity` | 存在指定容量的旅游团 |
| Given | `group_current_enrollment` | 设置当前报名人数 |
| When | `create_group_with_table` | 创建旅游团 |
| When | `update_group_with_table` | 更新旅游团信息 |
| When | `publish_group` | 发布旅游团 |
| When | `list_all_groups` | 查询所有旅游团 |
| When | `check_group_availability` | 检查可用名额 |
| When | `preview_pricing` | 预览订金计算 |
| When | `calculate_balance_deadline` | 计算尾款截止日期 |
| Then | `group_created_successfully` | 旅游团创建成功 |
| Then | `group_status_is` | 验证旅游团状态 |
| Then | `returned_availability_info` | 返回可用名额信息 |
| Then | `returned_pricing_preview` | 返回价格预览 |
| Then | `returned_deadline_info` | 返回截止日期信息 |

---

### 3. pricing.feature ↔ test_pricing.py

**Feature**: 价格计算

**测试场景数量**: 25 个

**主要步骤函数**:

| 步骤类型 | 步骤函数名 | 描述 |
|---------|-----------|------|
| Given | `set_departure_date` | 设置出发日期 |
| Given | `set_current_date` | 设置当前日期 |
| Given | `set_prices` | 设置大人小孩价格 |
| Given | `set_paid_total` | 设置已支付总额 |
| When | `calculate_deposit` | 计算订金 |
| When | `calculate_cancel_fee` | 计算取消手续费 |
| When | `calculate_balance_deadline` | 计算尾款截止日期 |
| Then | `deposit_amount_is` | 验证订金金额 |
| Then | `deposit_rate_is` | 验证订金比例 |
| Then | `total_price_is` | 验证总价 |
| Then | `cancel_fee_amount_is` | 验证取消手续费 |
| Then | `refund_amount_is` | 验证退款金额 |
| Then | `balance_deadline_is` | 验证尾款截止日期 |

---

### 4. cancellations.feature ↔ test_cancellations.py

**Feature**: 取消申请

**测试场景数量**: 20 个

**主要步骤函数**:

| 步骤类型 | 步骤函数名 | 描述 |
|---------|-----------|------|
| Given | `application_exists_with_state` | 存在指定状态的申请 |
| Given | `application_payment_status` | 设置申请支付状态 |
| Given | `group_with_enrollment` | 存在指定报名人数的旅游团 |
| When | `cancel_application_with_reason` | 取消申请（含原因） |
| When | `cancel_application` | 取消申请 |
| When | `preview_cancel_application` | 预览取消申请 |
| Then | `cancellation_successful` | 取消成功 |
| Then | `cancel_fee_is` | 验证取消手续费 |
| Then | `refund_amount_is` | 验证退款金额 |
| Then | `refund_record_created` | 生成退款记录 |
| Then | `group_enrollment_decreased` | 旅游团报名人数减少 |
| Then | `refund_record_contains_reason` | 退款记录包含原因 |

---

### 5. payments.feature ↔ test_payments.py

**Feature**: 支付管理

**测试场景数量**: 22 个

**主要步骤函数**:

| 步骤类型 | 步骤函数名 | 描述 |
|---------|-----------|------|
| Given | `application_state_is` | 设置申请状态 |
| Given | `application_deposit_is` | 设置订金金额 |
| Given | `application_payment_status` | 设置支付状态 |
| Given | `application_multiple_payment_records` | 存在多条支付记录 |
| When | `pay_deposit` | 支付订金 |
| When | `pay_balance` | 支付尾款 |
| When | `query_payment_records` | 查询支付记录 |
| When | `query_application_detail` | 查询申请详情 |
| Then | `payment_successful` | 支付成功 |
| Then | `paid_deposit_is` | 验证已付订金 |
| Then | `paid_balance_is` | 验证已付尾款 |
| Then | `payment_record_created` | 生成支付记录 |
| Then | `returned_payment_records_list` | 返回支付记录列表 |
| Then | `remaining_balance_is` | 验证剩余尾款 |

---

## 测试夹具配置 (conftest.py)

### 核心夹具

| 夹具名称 | 作用域 | 描述 |
|---------|--------|------|
| `event_loop` | session | 异步事件循环 |
| `db` | function | 测试数据库会话（SQLite内存库） |
| `client` | function | 异步HTTP测试客户端 |
| `test_date` | function | 测试日期固定值 |

#### 1. event_loop

异步事件循环夹具，提供异步测试环境。

```python
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
```

#### 2. db

测试数据库会话夹具，每个测试函数独立数据库实例。

```python
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
```

#### 3. client

异步HTTP测试客户端夹具，用于测试API端点。

```python
@pytest.fixture
async def client(db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

#### 4. test_date

测试日期固定值夹具，确保测试结果可预测。

```python
@pytest.fixture
def test_date():
    return date(2026, 5, 13)
```

### 数据库配置

测试使用 SQLite 内存数据库，与生产环境的 PostgreSQL 隔离。

**配置详情**：

- **数据库类型**: SQLite 内存数据库
- **连接字符串**: `sqlite:///:memory:`
- **异步支持**: aiosqlite
- **隔离策略**: 每个测试函数独立的数据库实例
- **表创建**: 测试前自动创建所有表
- **表销毁**: 测试后自动销毁所有表

**注意事项**：

1. PostgreSQL 特有的枚举类型在 SQLite 中需要特殊处理
2. 测试环境与生产环境的数据库差异需要在实现步骤时考虑
3. 使用内存数据库确保测试速度快且不污染生产数据

### API 客户端配置

- **客户端类型**: `httpx.AsyncClient`
- **Base URL**: `http://test`
- **依赖注入**: 自动覆盖 FastAPI 的 `get_db` 依赖

---

## 统计汇总

| Feature 文件 | 测试文件 | 场景数 | 步骤函数数 |
|-------------|---------|--------|-----------|
| applications.feature | test_applications.py | 28 | 58 |
| groups.feature | test_groups.py | 24 | 52 |
| pricing.feature | test_pricing.py | 43 | 28 |
| cancellations.feature | test_cancellations.py | 20 | 32 |
| payments.feature | test_payments.py | 22 | 42 |
| **总计** | **5个文件** | **137** | **212** |

---

## 运行测试

### 安装依赖

```bash
cd backend
uv pip install -r requirements-dev.txt
```

### 运行所有测试

```bash
cd backend
uv run pytest tests/ -v
```

### 运行特定测试文件

```bash
uv run pytest tests/test_applications.py -v
uv run pytest tests/test_groups.py -v
uv run pytest tests/test_pricing.py -v
uv run pytest tests/test_cancellations.py -v
uv run pytest tests/test_payments.py -v
```

### 预期结果

所有测试均应失败，输出类似：

```
FAILED tests/test_applications.py::test_create_application_over_2_months - NotImplementedError
FAILED tests/test_groups.py::test_create_group_success - NotImplementedError
...
=== 137 failed in 7.04s ===
这表明测试骨架已正确配置，所有步骤函数均未实现（红灯状态）。
```

---

## 结论

SDD 第三阶段测试骨架搭建完成：

✅ **测试框架配置完成**：pytest-bdd 8.1.0

✅ **测试夹具配置完成**：SQLite 内存数据库、异步 HTTP 客户端

✅ **测试文件创建完成**：5 个测试文件，137 个测试场景

✅ **红灯状态验证通过**：所有测试均因 NotImplementedError 失败

测试骨架已准备就绪，可以进入 SDD 第四阶段：迭代实现。
