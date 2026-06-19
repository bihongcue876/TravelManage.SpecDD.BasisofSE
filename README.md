# 旅游业务管理系统

## 环境配置

### 后端依赖

- **Python**: 3.14+
- **数据库**: PostgreSQL（连接驱动使用 psycopg v3）
- **包管理**: uv

#### `.env` 配置

复制 `backend/.env.example` 为 `backend/.env`，把里面的密码改成你的 PostgreSQL 密码。`.env` 已被 `.gitignore` 忽略，不会提交。

#### 数据库初始化

确保 PostgreSQL 服务运行后，创建业务数据库：

```bash
cd backend
uv run python -c "
import psycopg
conn = psycopg.connect(host='localhost', user='postgres', password='你的密码', dbname='postgres', autocommit=True)
cur = conn.cursor()
cur.execute('SELECT 1 FROM pg_database WHERE datname = %s', ('travel_management',))
if not cur.fetchone():
    cur.execute('CREATE DATABASE travel_management ENCODING UTF8')
    print('数据库已创建')
else:
    print('数据库已存在')
conn.close()
"
```
> 将命令中的 `你的密码` 替换为实际密码

### 前端依赖

- **Node.js**: 18+
- **包管理**: pnpm

## 快速启动

### 后端

```bash
cd backend
uv sync                # 安装依赖
uv run python main.py  # 启动服务（默认 http://localhost:8000）
```

### 前端

```bash
cd frontend
pnpm install           # 安装依赖
pnpm dev               # 启动开发服务器（默认 http://localhost:5173）
```

> 前端运行在 `http://localhost:5173`，首次访问会自动跳转登录页。

---

## 默认账户

系统启动后自动创建以下测试账户：

| 用户名 | 密码 | 角色 | 功能范围 |
|--------|------|------|----------|
| `admin` | `admin123` | 系统管理员 | 所有模块：管理路线/旅游团、催款报表、用户管理、退款审批 |
| `frontdesk` | `123456` | 前台员工 | 旅游团查询、创建申请、支付订金/尾款、录入参加者 |
| `finance` | `123456` | 财务人员 | 催款清单、财务流水、导出报表、催款提醒、审批退款 |

> 首次登录建议使用 `admin` / `admin123`，然后在「用户管理」中创建其他角色账户。

---

## 测试

项目分前后端独立测试。后端采用 BDD（pytest-bdd）+ 单元测试（unittest）+ coverage，前端采用 Vitest + Testing Library。

### 后端测试

**技术栈**：pytest-bdd（场景驱动）+ unittest（服务层单元）+ coverage
**测试目录**：`backend/tests/`

```bash
cd backend

# 安装依赖（含测试依赖）
uv sync --extra dev

# 全部测试（BDD + unittest，共 322 个）
uv run pytest tests/ -v

# 仅运行 unittest（跳过 BDD）
uv run pytest tests/ --ignore=tests/test_applications.py --ignore=tests/test_cancellations.py --ignore=tests/test_groups.py --ignore=tests/test_payments.py --ignore=tests/test_pricing.py -v

# 或用 python 直接跑单个 unittest 文件（Windows 下推荐此方式）
uv run python tests/test_pricing_service.py
uv run python tests/test_coverage_infra.py

# 覆盖率报告
uv run coverage run -m pytest tests/ -v
uv run coverage report
uv run coverage html
```

> 当前状态：**322 个测试全部通过**，覆盖率 **86%**。
> PDF 生成、定时任务、催款路由等基础设施模块已从覆盖率统计中排除。
> 所有命令须用 `uv run` 执行，直接运行 `coverage run -m pytest` 会因缺少 venv 依赖报错。

**测试文件说明：**

| 类型 | 文件 | 运行方式 | 说明 |
|------|------|----------|------|
| BDD | `test_applications.py` | `uv run pytest` | 申请 CRUD、支付、取消 HTTP 端点 |
| BDD | `test_cancellations.py` | `uv run pytest` | 取消与退款 HTTP 端点 |
| BDD | `test_groups.py` | `uv run pytest` | 旅游团 CRUD、发布、名额查询 |
| BDD | `test_payments.py` | `uv run pytest` | 支付流水、凭证上传 HTTP 端点 |
| BDD | `test_pricing.py` | `uv run pytest` | 订金/取消费用/尾款截止日 HTTP 端点 |
| unittest | `test_*service.py` (8 个) | `pytest` 或 `python` | 各服务层业务逻辑单元测试 |
| unittest | `test_coverage_infra.py` | `pytest` 或 `python` | 基础设施补测 |
| unittest | `test_coverage_routers.py` | `pytest` 或 `python` | 路由/服务覆盖补测 |
| 基类 | `test_base.py` | 无独立用例 | SQLite :memory: + TestClient 封装 |

---

### 前端测试

**技术栈**：Vitest + @testing-library/react + jsdom  
**测试目录**：`frontend/src/`

```bash
cd frontend

# 安装依赖
pnpm install

# 运行全部测试（共 25 个）
pnpm test

# 监听模式（开发时使用）
pnpm test:watch

# 覆盖率报告（首次需安装 @vitest/coverage-v8）
pnpm exec vitest run --coverage
```

**测试文件说明：**

| 文件 | 用例数 | 说明 |
|------|--------|------|
| `utils.test.ts` | 13 | 日期格式化函数（formatDateTime/Date/MonthDay/Weekday） |
| `auth.test.tsx` | 6 | 认证 Context（login/logout/hasRole/Token过期） |
| `api.test.ts` | 6 | axios 拦截器（自动带 token、401 处理、错误信息提取） |

**测试设计文档：** [doc/07_TEST_DESIGN.MD](doc/07_TEST_DESIGN.MD)
[share/测试结果分析.md](share/测试结果分析.md)



## 项目简介
本系统为武汉 XXX 旅行社的业务申请信息系统，用于替代手工流程，实现旅游团查询、申请、订金与余款管理、参加者信息维护、取消/变更、旅游路线与价格管理等功能。系统包括员工使用的后台管理界面，并支持与财务系统的数据导出对接。

## 需求分析

### 1. 业务流程概述
- **顾客咨询与申请**：前台员工根据顾客要求查询旅游团，满足截止日期未过且名额未满时可办理申请。
- **录入申请信息**：录入申请责任人姓名、电话，成人与儿童人数，系统根据距出发日期天数自动计算订金比例（≥2 个月 10%，≥1 个月且 <2 个月 20%，<1 个月全款）。
- **收取订金与出具凭据**：记录订金缴纳情况，打印订金收据和旅游申请书（一式多份，用于所有参加者）。
- **参加者信息回邮与补录**：顾客将其他参加者签署的旅游申请书邮寄回旅行社，员工在空闲时录入所有参加者信息，完成后申请状态变为“完成”。
- **催款与邮寄确认书**：每天打印前一日完成申请的旅游确认书及余额交款单（若已全款则只打印确认书），邮寄给申请责任人。
- **余款缴纳**：支付截止日为出发前 30 天，若交款单发出日距截止日不足 10 天，则截止日顺延至发出日后 10 天。顾客交余款时，员工通过交款单号等查询并记录支付完成。
- **财务导出**：每晚自动导出当日现金收支（订金、余款）数据到待开发的财务系统。
- **售后业务**：
  - 可变更参加者信息或取消整笔申请。
  - 新增参加者视为新申请。
  - 若取消/变更涉及申请责任人，必须选定新责任人。
  - 取消手续费按距出发天数计算：>1 个月免费，1 个月~10 天 20%，10 天~1 天 50%，出发当天全款扣费。
- **路线与活动管理**：
  - 每季度由路线管理员设计旅游路线和旅游活动。
  - 路线可取消但记录保留，变更视为新路线并保留变更历史。
  - 旅游活动价格（成人/儿童/优惠）由管理员设定，未定价的活动不可对顾客公开，一旦公开不可更改。

### 2. 关键业务规则
- 订金比例仅与距出发日期天数相关，与参加者年龄无关。
- 参加者信息包含：姓名、性别、出生日期、电话、联系地址、Email、邮编、旅游途中联络地址、与责任人关系等。
- 所有金额操作（订金、取消手续费）均需记录并供财务导出。

### 3. 非功能性需求
- 支持员工日常高效操作，界面清晰。
- 每日自动触发财务数据导出。
- 保留路线变更历史，数据不可物理删除（逻辑删除）。
- 价格公开后锁定不可修改。
