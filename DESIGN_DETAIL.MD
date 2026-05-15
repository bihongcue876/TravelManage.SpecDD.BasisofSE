基于之前确定的极简架构，下面给出可直接指导开发的详细设计。

---

## 一、系统总体架构

采用典型的前后端分离架构，通过 RESTful API 通信。

```
[React + Vite 前端]  <--HTTP/JSON-->  [FastAPI 后端]  <--SQLAlchemy-->  [PostgreSQL]
                         |
                    [APScheduler]  (定时任务：催款单生成、财务导出)
```

---

## 二、数据库详细设计

### 2.1 枚举类型定义

```sql
CREATE TYPE app_state AS ENUM (
    'draft',            -- 草稿（已创建，未支付订金）
    'deposit_paid',     -- 订金已支付
    'confirmed',        -- 已确认（信息齐全且尾款已付清）
    'cancelled'         -- 已取消
);
```

### 2.2 表结构

#### ① `routes` 路线

```sql
CREATE TABLE routes (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(200) NOT NULL,
    descr      TEXT,
    is_active  BOOLEAN NOT NULL DEFAULT true,   -- 停用则 false
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

变更历史通过 `route_versions` 表（可选）或直接在路线名称后加版本号处理，此处简化，不单独建表。

#### ② `groups` 旅游团

```sql
CREATE TABLE groups (
    id               SERIAL PRIMARY KEY,
    route_id         INT NOT NULL REFERENCES routes(id),
    code             VARCHAR(50) NOT NULL UNIQUE,    -- 团代码
    departure_date   DATE NOT NULL,
    deadline         DATE NOT NULL CHECK (deadline < departure_date),
    max_pax          INT NOT NULL CHECK (max_pax > 0),
    adult_price      DECIMAL(10,2),
    child_price      DECIMAL(10,2),
    is_published     BOOLEAN NOT NULL DEFAULT false,  -- 是否对外公开，一旦 true 不可再改价格
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### ③ `applications` 申请单（核心聚集）

```sql
CREATE TABLE applications (
    id              SERIAL PRIMARY KEY,
    group_id        INT NOT NULL REFERENCES groups(id),
    -- 申请人信息
    name            VARCHAR(100) NOT NULL,
    phone           VARCHAR(30) NOT NULL,
    email           VARCHAR(100),
    address         TEXT,
    zip_code        VARCHAR(20),
    -- 人数
    adults          INT NOT NULL CHECK (adults > 0),
    children        INT NOT NULL CHECK (children >= 0),
    -- 金额（创建时计算好，不可变更）
    deposit         DECIMAL(10,2) NOT NULL,    -- 应付订金
    total_price     DECIMAL(10,2) NOT NULL,    -- 旅费总额
    -- 实收金额
    paid_deposit    DECIMAL(10,2) NOT NULL DEFAULT 0,
    paid_balance    DECIMAL(10,2) NOT NULL DEFAULT 0,
    -- 状态与时间
    state           app_state NOT NULL DEFAULT 'draft',
    info_completed  BOOLEAN NOT NULL DEFAULT false,   -- 参加者信息是否已全部录入
    cancelled_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

支付明细不再单独建表，通过 `paid_deposit` 和 `paid_balance` 记录累计实收金额；财务导出时直接查询当日发生支付的申请。

> 索引建议：`CREATE INDEX idx_app_group ON applications(group_id);`  
> `CREATE INDEX idx_app_state ON applications(state);`

#### ④ `participants` 参加人

```sql
CREATE TABLE participants (
    id              SERIAL PRIMARY KEY,
    application_id  INT NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name            VARCHAR(100) NOT NULL,
    gender          CHAR(1) CHECK (gender IN ('M','F','O')),
    birth_date      DATE,
    phone           VARCHAR(30),
    email           VARCHAR(100),
    address         TEXT,
    is_leader       BOOLEAN NOT NULL DEFAULT false,   -- 是否为责任人
    extra           JSONB,   -- 旅游途中联络地址等信息放这里
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### ⑤ `refunds` 退款记录

```sql
CREATE TABLE refunds (
    id              SERIAL PRIMARY KEY,
    application_id  INT NOT NULL REFERENCES applications(id),
    cancel_fee      DECIMAL(10,2) NOT NULL,
    refund_amount   DECIMAL(10,2) NOT NULL,
    reason          TEXT,
    refunded_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

#### ⑥ `financial_exports` 导出历史（可选，便于对账）

```sql
CREATE TABLE financial_exports (
    id          SERIAL PRIMARY KEY,
    export_date DATE NOT NULL,
    file_path   VARCHAR(500),
    record_count INT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

## 三、后端详细设计

### 3.1 目录结构

```
backend/
├── main.py              # FastAPI 实例，注册路由，启动调度器
├── database.py          # engine, SessionLocal
├── models.py            # 所有 ORM 模型
├── schemas.py           # Pydantic 模型
├── routers/
│   ├── routes.py        # 路线 CRUD
│   ├── groups.py        # 旅游团管理
│   ├── applications.py  # 申请、支付、取消
│   └── tasks.py         # 查询催款单、导出等
├── services/
│   ├── pricing.py       # 纯函数：计算订金、手续费、支付期限
│   ├── application.py   # 复杂流程：创建申请、支付、取消、信息补全、变更取消
│   └── export.py        # 生成催款单数据、财务数据
├── tasks_scheduler.py   # APScheduler 定时任务定义
└── requirements.txt
```

### 3.2 接口端点设计

#### 旅游团管理 `/api/groups`

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/groups?status=published` | 前台查询可选公开团 |
| `GET` | `/api/groups/{id}` | 团详情 |
| `POST` | `/api/groups` | 新增团（管理） |
| `PUT` | `/api/groups/{id}` | 修改团信息（管理，仅未公开时可改价格） |
| `POST` | `/api/groups/{id}/publish` | 公开价格（管理） |

#### 路线管理 `/api/routes`

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/routes` | 列表 |
| `POST` | `/api/routes` | 新增 |
| `PUT` | `/api/routes/{id}` | 修改（停用/启用），自动记录版本（可选） |

#### 申请与支付 `/api/applications`

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/applications` | 创建申请（含计算订金） |
| `GET` | `/api/applications/{id}` | 申请详情 |
| `POST` | `/api/applications/{id}/pay-deposit` | 支付订金 |
| `POST` | `/api/applications/{id}/participants` | 批量录入参加者信息（完成 info_complete） |
| `POST` | `/api/applications/{id}/pay-balance` | 支付尾款（确认已完成信息录入） |
| `POST` | `/api/applications/{id}/cancel` | 取消申请，自动计算退款 |
| `GET` | `/api/applications/search?code=&departure=&name=` | 根据团代码、出发日期、申请人名查询 |

#### 催款与报表 `/api/tasks`

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/tasks/daily-reminders?date=YYYY-MM-DD` | 获取某天的催款清单（确认书+交款单数据） |
| `GET` | `/api/tasks/daily-finance?date=YYYY-MM-DD` | 获取某天资金流水数据 |
| `POST` | `/api/tasks/mark-printed` | 标记已打印（可选） |

### 3.3 核心 Service 实现设计

#### `services/pricing.py` 纯函数

```python
from datetime import date

def calc_deposit(departure: date, adults: int, children: int, adult_price: Decimal, child_price: Decimal) -> Decimal:
    total = adults * adult_price + children * child_price
    days = (departure - date.today()).days
    if days >= 60:
        return total * Decimal('0.1')
    elif days >= 30:
        return total * Decimal('0.2')
    else:
        return total
```

```python
def calc_cancel_fee(departure: date, paid_total: Decimal) -> tuple[Decimal, Decimal]:
    """
    返回 (手续费, 退款金额)
    """
    days = (departure - date.today()).days
    if days >= 30:
        rate = 0
    elif 10 <= days < 30:
        rate = Decimal('0.2')
    elif 1 <= days < 10:
        rate = Decimal('0.5')
    else:  # 0天或已出发
        rate = 1.0
    fee = paid_total * rate
    return fee, paid_total - fee
```

```python
def calc_balance_deadline(departure: date, today: date) -> date:
    """
    尾款支付期限：出发日30天前，或交款单发送日起10天后（取更晚）
    假设调用时 today = 交款单生成日期
    """
    base = departure - timedelta(days=30)
    fallback = today + timedelta(days=10)
    return max(base, fallback)
```

#### `services/application.py` 复杂流程

**创建申请 (`create_application`)**  
1. 校验团存在且已公开、截止日期未过、人数未满。  
2. 计算 `deposit` 和 `total_price`（调用 pricing）。  
3. INSERT 一条 `applications` (state='draft')，返回申请 ID。

**支付订金 (`pay_deposit`)**  
1. 开启事务，`SELECT ... FOR UPDATE` 锁定该申请行。  
2. 校验状态为 'draft' 且未付订金。  
3. 更新 `paid_deposit = deposit`，状态改为 'deposit_paid'。  

**录入参加者 (`add_participants`)**  
1. 接收人员列表，校验总数与申请中 adults+children 一致，且至少有一个 is_leader=true。  
2. INSERT 所有参加者。  
3. 更新 `info_completed = true`。  
4. 注意：如果申请状态尚为 'deposit_paid'，信息录入后状态不变，待尾款支付后再变为 'confirmed'。

**支付尾款 (`pay_balance`)**  
1. 校验 info_completed = true 且 state 为 'deposit_paid' 或 'confirmed'（可重复付？实际先付后可能不会再付，但允许补差额）。  
2. 检查余额：应付款 = total_price - paid_deposit，支付金额 <= 应付款。  
3. 更新 `paid_balance += amount`，若剩余应付为0，状态改为 'confirmed'。

**取消申请 (`cancel_application`)**  
1. 校验状态非 'cancelled'。  
2. 计算已支付总额 = paid_deposit + paid_balance。  
3. 调用 `calc_cancel_fee` 得出手续费和退款。  
4. 插入 refunds 记录。  
5. 更新状态为 'cancelled'，写入 cancelled_at。  
6. 返回退款金额。

#### 催款单生成逻辑

定时任务（每天凌晨1点执行）：
```sql
SELECT * FROM applications
WHERE state = 'deposit_paid' AND info_completed = true
AND created_at::date = CURRENT_DATE - INTERVAL '1 day'
  -- 或者其他条件：status变为completed的前一天？
```
根据需求：**每天打印前一天已完成申请的旅游确认书、余额交款单**。已完成申请在此系统中对应 info_completed = true 且尾款未付的情况（或状态待确认）。我们定义：当 info_completed = true 且 paid_balance = 0（即未付尾款）时，为需要催款的状态。

定时任务伪代码：
```python
def generate_reminders():
    yesterday = date.today() - timedelta(days=1)
    # 前一天 info_completed 变为 true 的申请（需要催款）
    apps = db.query(Application).filter(
        Application.info_completed == True,
        Application.paid_balance == 0,
        func.date(Application.updated_at) == yesterday  # 假设录入完毕会更新 updated_at
    ).all()
    for app in apps:
        # 生成确认书和交款单的数据，可存储到文件或仅返回给前端打印
        reminder_data = {
            "app_id": app.id,
            "tour_code": app.group.code,
            "departure": app.group.departure_date,
            "total": app.total_price,
            "paid": app.paid_deposit,
            "balance": app.total_price - app.paid_deposit,
            "balance_deadline": calc_balance_deadline(app.group.departure_date, date.today())
        }
        # 可将此数据存储到某张临时表或直接由前端查询时动态生成
```

#### 财务导出定时任务

每晚23:59执行：
```sql
SELECT 'deposit' as type, id, paid_deposit as amount, created_at
FROM applications WHERE paid_deposit > 0 AND created_at::date = CURRENT_DATE
UNION ALL
SELECT 'balance' as type, id, paid_balance - COALESCE(prev_paid_balance,0)
FROM ...  -- 实际上需要记录每次支付，但我们简化了支付记录。
```
由于我们只有一个累计字段，无法知道当天新增的尾款数额，因此需要调整：**引入支付日志对财务至关重要**。建议极简情况下增加一张 `payment_logs` 表，只记录每次支付的时间和金额，不破坏简单性。

```sql
CREATE TABLE payment_logs (
    id              SERIAL PRIMARY KEY,
    application_id  INT NOT NULL REFERENCES applications(id),
    type            VARCHAR(10) NOT NULL, -- 'deposit' or 'balance'
    amount          DECIMAL(10,2) NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

然后财务导出直接查询 `payment_logs` 当日记录即可。这样保留简单，数据更可靠。采纳此调整。

#### 申请完成后的变更

- 参加者信息变更：允许修改 participants 表中记录，但如果变更了责任人（is_leader），需要选定新的 is_leader = true，且原责任人取消。无需复杂的申请状态变更。
- 取消整个申请：已提供 cancel 接口。
- 新增参加者：创建新申请，关联同一个团即可。

### 3.4 状态流转图

```
draft  --[付订金]--> deposit_paid --[录入信息]--> (仍为 deposit_paid, info_completed=true)
deposit_paid --[付尾款]--> confirmed
任意非 cancelled 状态 --[取消]--> cancelled
```

其中尾款付清后变为 confirmed，此时才可视为“申请完成”（对应需求中的“申请完成”）。催款单在 info_completed=true 且未付尾款时生成。

---

## 四、前端详细设计

### 4.1 路由与页面

```jsx
<Routes>
  <Route path="/" element={<GroupList />} />            // 前台查询旅游团
  <Route path="/apply/:groupId" element={<ApplyCreate />} /> // 创建申请
  <Route path="/applications/:id" element={<AppDetail />} /> // 申请详情（支付、录入参加者、取消）
  <Route path="/admin/groups" element={<AdminGroups />} />    // 管理旅游团
  <Route path="/admin/routes" element={<AdminRoutes />} />    // 管理路线
  <Route path="/admin/tasks" element={<DailyTasks />} />      // 催款单打印 / 财务导出查看
</Routes>
```

### 4.2 主要页面说明

#### 前台查询与申请流程

- **GroupList**：展示 `is_published=true` 的旅游团列表，支持按出发日期、路线名筛选。点击某个团进入申请。
- **ApplyCreate**：表单填入责任人信息、大人/小孩数量，自动计算并显示订金（前端调用 `/api/pricing/preview` 或直接在后端创建时返回）。提交后跳转到申请详情。
- **AppDetail**：展示申请状态，分步骤：
  1. **付订金**：如果 state=draft，显示应付订金，点击支付。
  2. **录入参加者**：表单动态增加人员，需满足人数一致，提交后 info_completed=true。
  3. **付尾款**：当 info_completed=true 且 paid_balance < total_price - deposit 时，显示剩余应付，输入支付金额完成支付。
  4. **取消**：任何时刻可点击取消，弹窗展示预计扣除手续费和退款金额（调用预览接口），确认后取消。
  5. **查看确认书/交款单**：如果是 'confirmed' 或已催款，可显示单据内容（PDF预览）。

#### 管理与报表

- **AdminGroups**：表格展示所有团，可新增、修改、发布。价格一旦公开不可再改。
- **AdminRoutes**：路线管理。
- **DailyTasks**（催款员工）：
  - 选择日期，点击查询，返回该日需催款的列表。
  - 列表展示确认书、交款单数据，提供“已打印”按钮。
  - 同样页面可查看某日财务流水（包含订金和尾款支付），并提供导出CSV功能。

### 4.3 API 封装（`api.js`）

所有后端接口调用集中，使用 `axios` 实例，统一错误拦截。方法如：

```javascript
export const fetchGroups = (params) => axios.get('/api/groups', { params });
export const createApplication = (data) => axios.post('/api/applications', data);
export const payDeposit = (id, amount) => axios.post(`/api/applications/${id}/pay-deposit`, { amount });
// ... 其余类似
```

前端使用 Ant Design 的 `Table`, `Form`, `Modal`, `Steps` 等组件快速搭建。

---

## 五、关键业务细节重述与实现提醒

1. **订金计算的时间基点**：统一使用服务器当前日期 `date.today()`，防止客户端时区问题。
2. **取消手续费的起算点**：距出发日天数按 `(departure_date - today).days`，注意边界处理（≥1个月、10天~1个月、1天~10天、出发当天）。
3. **尾款支付期限**：推送后的 10 天与出发前30天中取较晚者。
4. **价格公开锁定**：`groups.is_published` 字段控制，接口 `publish` 设置该字段为 true 后，前端禁用价格修改按钮，后端再次校验。
5. **名额控制**：支付订金时检查当前已确认人数（可查询 applications 中非 cancelled 的 adults+children 之和），必须 ≤ max_pax。为保证并发安全，使用 `SELECT ... FOR UPDATE` 锁定团记录。
6. **财务导出**：依赖 `payment_logs`，导出格式为 CSV 或简单的 Excel，存到 `financial_exports` 表并记日志。

---

## 六、安全性建议

- 所有接口均加入简单的角色验证（例如请求头携带员工类型），后端根据角色限制管理类接口。无需复杂 RBAC，用中间件检查一个自定义 Header `X-Role: admin / frontdesk / collector` 即可。
- 支付操作加事务，保证金额一致性。
- 输入校验全部放在 Pydantic schema 中。

---

这份设计足够详细，能够支撑起整个系统的开发，同时保持架构清晰、代码简洁。若有需要进一步细化（例如某个 service 函数的完整代码），请随时告知。