理解你的顾虑，过度设计确实容易写出“屎山”。这套系统核心并不算庞大，我们应该用 **刚好够用、直接清晰** 的思路来架构，砍掉不必要分层和辅助表，让代码一眼就能看懂业务流程。

下面给你一个**极简但完全满足需求**的方案，同样基于 PostgreSQL + FastAPI + React。

---

## 一、极简数据结构（6 张核心表）

> 拆表的原则是：**一个业务对象一张表**，不对日志、导出等做过度建模，能靠查询和视图解决的绝不建表。

### 1. `routes` —— 旅游路线

```sql
CREATE TABLE routes (
    id         SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    descr      TEXT,
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

> 路线变更历史不再单独建表，每次更新路线时将旧值写入一个 `change_log` JSONB 字段即可（甚至可以直接用 `routes` 表加一条记录，只做软更新，用 `superseded_by` 自关联，实现简单版本链）。

---

### 2. `groups` —— 旅游团 / 活动

```sql
CREATE TABLE groups (
    id               SERIAL PRIMARY KEY,
    route_id         INT NOT NULL REFERENCES routes(id),
    code             TEXT NOT NULL UNIQUE,
    departure_date   DATE NOT NULL,
    deadline         DATE NOT NULL CHECK (deadline < departure_date),
    max_pax          INT NOT NULL CHECK (max_pax > 0),
    adult_price      DECIMAL(10,2),
    child_price      DECIMAL(10,2),
    is_published     BOOLEAN NOT NULL DEFAULT FALSE,   -- 只有一个开关，价格一旦发布不可改（应用控制）
    created_at       TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 3. `applications` —— 申请单（所有核心信息放一起）

```sql
CREATE TYPE app_state AS ENUM (
    'draft',           -- 刚创建，未付订金
    'deposit_paid',    -- 订金已付
    'confirmed',       -- 全款已付（或信息已齐全，无需区分）
    'cancelled'
);

CREATE TABLE applications (
    id               SERIAL PRIMARY KEY,
    group_id         INT NOT NULL REFERENCES groups(id),
    -- 申请责任人信息
    name             TEXT NOT NULL,
    phone            TEXT NOT NULL,
    email            TEXT,
    address          TEXT,
    -- 人数
    adults           INT NOT NULL DEFAULT 1,
    children         INT NOT NULL DEFAULT 0,
    -- 金额（全部预计算好，避免多处重复计算）
    deposit          DECIMAL(10,2) NOT NULL,   -- 订金
    total_price      DECIMAL(10,2) NOT NULL,   -- 总旅费
    -- 支付情况（简化：直接记录实收金额）
    paid_deposit     DECIMAL(10,2) DEFAULT 0,
    paid_balance     DECIMAL(10,2) DEFAULT 0,
    -- 状态与时间
    state            app_state NOT NULL DEFAULT 'draft',
    cancelled_at     TIMESTAMPTZ,
    created_at       TIMESTAMPTZ DEFAULT NOW()
);
```

> 把支付金额直接记在申请单上，省去 payments 表。财务导出时，直接 `SELECT * FROM applications WHERE paid_deposit > 0 OR paid_balance > 0 AND date = ...` 即可。

---

### 4. `participants` —— 参加人

```sql
CREATE TABLE participants (
    id              SERIAL PRIMARY KEY,
    application_id  INT NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    name            TEXT NOT NULL,
    gender          CHAR(1),
    birth_date      DATE,
    phone           TEXT,
    email           TEXT,
    address         TEXT,
    is_leader       BOOLEAN NOT NULL DEFAULT FALSE,
    -- 其他字段可以全部放在一个 JSONB extra 里，避免字段爆炸
    extra           JSONB
);
```

---

### 5. `refunds` —— 退款记录（取消时生成）

```sql
CREATE TABLE refunds (
    id              SERIAL PRIMARY KEY,
    application_id  INT NOT NULL REFERENCES applications(id),
    cancel_fee      DECIMAL(10,2) NOT NULL,
    refund_amount   DECIMAL(10,2) NOT NULL,
    refunded_at     TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 6. `financial_exports` (可选，也可用文件系统替代)

```sql
CREATE TABLE financial_exports (
    id          SERIAL PRIMARY KEY,
    export_date DATE NOT NULL,
    total_count INT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

> 导出文件直接存本地，表里只记一笔元数据。

---

**至此，表结构只有 6 张核心表，外加一个可选的导出记录表。所有核心业务数据高度内聚，几乎不用 JOIN 太多表就能完成 CRUD。**

---

## 二、极简后端架构（扁平化模块）

不要过多的分层，**router 直接调用 service 函数，service 函数直接写 SQL 或调用 ORM 简单方法**。目录可以精简为：

```
backend/
├── main.py             # 应用启动，挂载路由，定时任务
├── database.py         # 数据库连接，sessionmaker
├── models.py           # 所有ORM模型写在一个文件，可快速通览
├── schemas.py          # 请求/响应模型（Pydantic）
├── routers/
│   ├── routes.py
│   ├── groups.py
│   ├── applications.py
│   └── tasks.py
├── services/           # 仅负责复杂业务逻辑，非CRUD包装
│   ├── pricing.py     # 订金计算、手续费计算（纯函数）
│   ├── application.py # 创建申请、支付、取消等核心流程
│   └── exports.py     # 财务导出、催款单生成
└── tasks.py            # APScheduler 定时任务定义
```

**核心思想**：
- **CRUD 操作**直接写在 router 里，用 `db.query(Model).filter(...)` 完成，不要加一层无用的 Service 包装。
- **只有涉及事务、多表更新、复杂规则的地方**才抽进 `services/` 里，并且函数参数明确，返回值简单。
- **pricing.py** 里面只放纯函数：`calc_deposit(depart: date, adults: int, children: int, base_prices) -> float`，极易测试。
- **application.py** 中的函数如 `create_application(...)`、`pay_deposit(app_id)`、`cancel_application(app_id)` 等，每个函数不超过 100 行，逻辑一目了然。

---

## 三、极简前端架构（页面驱动）

```
frontend/
├── src/
│   ├── main.jsx
│   ├── api.js              # 统一 axios 实例 + 所有接口函数（一个文件）
│   ├── App.jsx             # 路由
│   ├── pages/
│   │   ├── GroupList.jsx   # 旅游团列表/查询
│   │   ├── ApplicationCreate.jsx
│   │   ├── ApplicationDetail.jsx
│   │   ├── Payment.jsx
│   │   ├── Cancel.jsx
│   │   └── AdminGroups.jsx
│   ├── components/         # 少量可复用组件（状态标签、金额展示）
│   └── utils.js            # 日期格式化、金额计算预览等
```

**原则**：
- 不用 zustand 等全局状态库，**页面自己管理状态**，通过 `api.js` 直接请求后端，极少的跨页面共享状态可以放在 `App.jsx` 的 Context 里（如当前登录员工角色）。
- 表单直接使用 Ant Design 的 `Form` 组件，逻辑就写在页面文件里，不多封装。
- 接口函数全部放在 `api.js`，一眼可见系统有哪些后端调用。

---

## 四、技术栈定位（仍然适用，但更轻）

| 层 | 选型 | 理由 |
|----|------|------|
| 后端框架 | FastAPI | 接口文档自动生成，适合前后端分离开发 |
| ORM | SQLAlchemy 2.0 (Core优先) | 复杂查询用原生 SQL + `text()`，简单的用 ORM，避免过度封装 |
| 数据库 | PostgreSQL | 日期函数、CHECK约束、枚举类型，让数据库帮你保障一致性 |
| 定时任务 | APScheduler | 一个文件就能配好，无需额外服务 |
| 前端 | React + Vite + Ant Design | 快速构建后台页面，AntD 的 Form Table 能解决绝大部分需求 |
| HTTP | axios | 最基本的封装 |
| 类型 | TypeScript (可选，如果觉得增加复杂度就只用 JS) | 建议至少给 `api.js` 加 JSDoc，降低联调成本 |

---
