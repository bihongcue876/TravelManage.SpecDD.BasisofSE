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
uv sync
uv run python main.py
```
安装：`uv sync`
启动：`uv run python main.py`

### 前端

```bash
cd frontend
pnpm install
pnpm dev
```
安装：`pnpm install`
启动：`pnpm dev`

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

项目分前后端独立测试。后端采用 BDD（pytest-bdd） + 单元测试（unittest），前端采用 Vitest + Testing Library。

### 总体测试

```bash
# 后端测试
cd backend && uv run pytest tests/ -v

# 前端测试
cd frontend && pnpm test
```

---

### 后端测试

**技术栈**：pytest-bdd（场景驱动） + unittest（服务层单元） + coverage（覆盖率）
**测试目录**：`backend/tests/`

```bash
# 安装测试依赖
cd backend
uv pip install -r requirements-dev.txt

# 运行全部测试
uv run pytest tests/ -v

# 运行特定测试文件
uv run pytest tests/test_applications.py -v

# 查看测试收集
uv run pytest tests/ --collect-only -q

# 运行测试 + 覆盖率报告
cd backend
coverage run -m pytest tests/ -v
coverage html
# 打开 htmlcov/index.html

# 仅运行单元测试（unittest，跳过 BDD）
uv run python -m unittest discover tests/ -v
```

> 测试当前处于 SDD 第三阶段"红灯"状态：共 **137 个测试场景**，所有步骤函数均未实现（预期行为）。详细进度见 [doc/04_TEST_WORKINGPROCESS.MD](doc/04_TEST_WORKINGPROCESS.MD)。

**测试文件说明：**

| 层级 | 文件 | 类型 | 说明 |
|------|------|------|------|
| 路由层 | `test_applications.py` | 集成测试 | 申请 CRUD、支付、取消 HTTP 端点 |
| 路由层 | `test_cancellations.py` | 集成测试 | 取消与退款 HTTP 端点 |
| 路由层 | `test_groups.py` | 集成测试 | 旅游团 CRUD、发布、名额查询 |
| 路由层 | `test_payments.py` | 集成测试 | 支付流水、凭证上传 HTTP 端点 |
| 路由层 | `test_pricing.py` | 集成测试 | 订金/取消费用/尾款截止日 HTTP 端点 |
| 服务层 | `test_application_service.py` | 单元测试 | 创建申请、支付、取消业务逻辑 |
| 服务层 | `test_auth_service.py` | 单元测试 | 密码哈希、JWT、登录、用户管理 |
| 服务层 | `test_cancellation_service.py` | 单元测试 | 全额/部分取消、退款审核 |
| 服务层 | `test_dashboard_service.py` | 单元测试 | 前台/财务/管理面板数据 |
| 服务层 | `test_export_service.py` | 单元测试 | 催款列表、财务导出、银行对账 |
| 服务层 | `test_group_service.py` | 单元测试 | 旅游团 CRUD 操作 |
| 服务层 | `test_payment_service.py` | 单元测试 | 订金/尾款支付、凭证、支付记录 |
| 服务层 | `test_pricing_service.py` | 单元测试 | 订金计算、取消手续费、尾款截止日 |
| 服务层 | `test_route_service.py` | 单元测试 | 路线 CRUD、搜索、批量操作 |
| 基础设施 | `test_base.py` | 基类 | SQLite :memory: 数据库 + TestClient 封装 |

---

### 前端测试

**技术栈**：Vitest + @testing-library/react + jsdom
**测试目录**：`frontend/src/`

```bash
# 运行全部测试
cd frontend
pnpm test

# 监听模式（开发时使用）
pnpm test:watch
```

**测试文件说明：**

| 文件 | 用例数 | 说明 |
|------|--------|------|
| `utils.test.ts` | 13 | 日期格式化函数（formatDateTime/Date/MonthDay/Weekday） |
| `auth.test.tsx` | 6 | 认证 Context（login/logout/hasRole/Token过期） |
| `api.test.ts` | 6 | axios 拦截器（自动带 token、401 处理、错误信息提取） |

**测试设计文档：** [doc/07_TEST_DESIGN.MD](doc/07_TEST_DESIGN.MD)

---

### 测试结果分析

详细的测试用例设计、核心方法测试代码及执行结果见：
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
