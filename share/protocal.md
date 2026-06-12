# 旅游业务管理系统 — 协议文档 v2.2

> 对应后端 FastAPI + SQLAlchemy，前端 React + Ant Design
> 本协议定义前后端开发的所有接口约定、数据模型和业务规则。

---

## 1. 系统概述

旅游业务管理系统是一个面向旅行社的 B 端管理平台，核心业务流程：

```
创建路线 → 创建旅游团 → 发布团 → 客户申请 → 付订金 → 录入参加者 → 付尾款 → 完成
                                                                         ↘ 取消/退款（手续费阶梯计算）
```

**技术栈：**
- 后端：FastAPI 0.136 + SQLAlchemy 2.0 + PostgreSQL + JWT (HS256, 8h)
- 前端：React 18 + TypeScript + Vite 5 + Ant Design 5 + React Router 6
- 定时任务：APScheduler（每日 01:00 催款单生成、09:00 提醒发送、23:59 财务导出）

---

## 2. 数据模型

### 2.1 用户 (users)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| username | String(50), unique | 登录名 |
| password_hash | String(255) | bcrypt 哈希 |
| name | String(100) | 真实姓名 |
| role | Enum: admin/frontdesk/finance | 角色 |
| email | String(100), nullable | 邮箱 |
| phone | String(30), nullable | 电话 |
| is_active | Boolean, default=true | 是否启用 |
| created_at | DateTime | 创建时间 |

### 2.2 路线 (routes)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| code | String(12), unique | 自动编号 `RT` + 10位顺序数字（如 `RT0000000001`） |
| name | String(200) | 路线名称 |
| descr | Text, nullable | 路线描述 |
| is_active | Boolean, default=true | 是否启用 |
| created_at | DateTime | 创建时间 |

**关联：** groups（一对多）、history（RouteHistory 一对多，级联删除）

**历史表 route_history：**
- route_id (FK), code, name, descr, is_active, changed_at
- 编辑路线时自动记录快照，批量操作和停用时也会记录

### 2.3 旅游团 (groups)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| route_id | Integer FK → routes.id | 所属路线 |
| code | String(50), unique | 团代码 |
| departure_date | Date | 出发日期 |
| deadline | Date | 截止报名日期（必须 < departure_date） |
| max_pax | Integer | 最大人数（必须 > 0） |
| adult_price | Numeric(10,2), nullable | 大人价 |
| child_price | Numeric(10,2), nullable | 小孩价 |
| is_published | Boolean, default=false | 是否已发布（发布后不可修改价格） |
| created_at | DateTime | 创建时间 |

**约束：** `deadline < departure_date`, `max_pax > 0`

**虚拟字段（计算属性）：**
- `occupied` — 非取消状态的申请人数总和（adults + children）
- `available` — `max_pax - occupied`

### 2.4 申请 (applications)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| group_id | Integer FK → groups.id | 所属团 |
| name | String(100) | 申请人姓名 |
| phone | String(30) | 联系电话 |
| email | String(100), nullable | 邮箱 |
| address | Text, nullable | 联系地址 |
| zip_code | String(20), nullable | 邮编 |
| adults | Integer | 大人数（必须 > 0） |
| children | Integer, default=0 | 小孩数（必须 >= 0） |
| deposit | Numeric(10,2) | 应付订金 |
| total_price | Numeric(10,2) | 总旅费 |
| paid_deposit | Numeric(10,2), default=0 | 已付订金 |
| paid_balance | Numeric(10,2), default=0 | 已付尾款 |
| state | Enum: draft/deposit_paid/confirmed/cancelled | 申请状态 |
| info_completed | Boolean, default=false | 参加者信息是否已录入 |
| cancelled_at | DateTime, nullable | 取消时间 |
| created_at | DateTime | 创建时间 |

**状态流转：**
```
draft ──(付订金)──→ deposit_paid ──(付尾款)──→ confirmed
                                ↘──(取消)──→ cancelled
draft ──(取消)──→ cancelled
```

### 2.5 参加者 (participants)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| application_id | Integer FK → applications.id (CASCADE) | 所属申请 |
| name | String(100) | 姓名 |
| gender | String(1), nullable | 性别：`M`/`F`/`O` |
| birth_date | Date, nullable | 出生日期 |
| phone | String(30), nullable | 电话 |
| email | String(100), nullable | 邮箱 |
| address | Text, nullable | 联系地址 |
| is_leader | Boolean, default=false | 是否负责人（每个申请至少一个） |
| extra | JSON, nullable | 扩展字段 |
| created_at | DateTime | 创建时间 |

**约束：** `gender IN ('M','F','O')`

### 2.6 支付记录 (payment_logs)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| application_id | Integer FK → applications.id | 所属申请 |
| type | String(10) | `deposit` 或 `balance` |
| amount | Numeric(10,2) | 金额 |
| payment_method | String(20), nullable | 支付方式：cash/bank_transfer/wechat/alipay |
| voucher_path | String(500), nullable | 凭证路径 |
| created_at | DateTime | 创建时间 |

> 支付记录**不可修改或删除**，仅追加。

### 2.7 支付凭证 (payment_vouchers)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| payment_log_id | Integer FK → payment_logs.id | 所属支付记录 |
| file_name | String(200) | 文件名 |
| file_path | String(500) | 服务器路径 |
| file_size | Integer, nullable | 文件大小（字节） |
| created_at | DateTime | 创建时间 |

### 2.8 参加者编辑历史 (participant_edit_history)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| participant_id | Integer FK → participants.id | 参加者 |
| field_name | String(50) | 修改字段名 |
| old_value | Text, nullable | 旧值 |
| new_value | Text, nullable | 新值 |
| edited_by | String(100) | 编辑人 |
| created_at | DateTime | 修改时间 |

### 2.9 退款 (refunds)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| application_id | Integer FK → applications.id | 所属申请 |
| participant_id | Integer FK → participants.id, nullable | 部分取消时指向具体参加者 |
| cancel_fee | Numeric(10,2) | 扣除的手续费 |
| refund_amount | Numeric(10,2) | 实际退款金额 |
| reason | Text, nullable | 取消原因 |
| channel | String(20), nullable | original/cash/bank_transfer |
| status | String(20), default=pending | pending/approved/rejected/completed |
| approved_by | String(100), nullable | 审核人 |
| approved_at | DateTime, nullable | 审核时间 |
| refunded_at | DateTime | 退款时间 |

> **退款审批流程：**
> - 退款 < 5000 元：自动通过，status 直接设为 `completed`
> - 退款 >= 5000 元：初始为 `pending`，需 admin/finance 审批
>   - **批准** → status 变为 `completed`
>   - **拒绝** → status 变为 `rejected`

### 2.10 催款记录 (reminder_logs)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| application_id | Integer FK → applications.id | 所属申请 |
| reminder_type | String(10) | email/sms/print |
| content | Text, nullable | 催款内容 |
| sent_at | DateTime | 发送时间 |
| success | Boolean, default=true | 是否成功 |

### 2.11 交款单 (payment_orders)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| application_id | Integer FK → applications.id | 所属申请 |
| order_no | String(50), unique | 交款单编号 |
| order_type | String(20) | 类型（如 payment_order） |
| created_at | DateTime | 创建时间 |

### 2.12 财务导出记录 (financial_exports)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| export_date | Date | 导出日期 |
| file_path | String(500), nullable | 服务器文件路径 |
| file_format | String(10), nullable | csv/excel/json |
| record_count | Integer, nullable | 记录数 |
| created_at | DateTime | 创建时间 |

### 2.13 银行对账 (bank_reconciliations / bank_reconciliation_items)

**主表 bank_reconciliations：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| import_date | Date | 导入日期 |
| file_name | String(200) | 文件名 |
| total_records | Integer | 总记录数 |
| matched_count | Integer | 已匹配数 |
| unmatched_count | Integer | 未匹配数 |
| created_at | DateTime | 创建时间 |

**明细表 bank_reconciliation_items：**
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 自增主键 |
| reconciliation_id | Integer FK | 所属对账批次 |
| bank_date | Date, nullable | 银行交易日期 |
| bank_amount | Numeric(10,2) | 银行金额 |
| bank_ref | String(100), nullable | 银行参考号 |
| matched_payment_id | Integer FK → payment_logs.id, nullable | 匹配的支付记录 |
| is_matched | Boolean, default=false | 是否已匹配 |
| created_at | DateTime | 创建时间 |

---

## 3. API 端点完整清单

### 3.1 路线管理 `/api/routes`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/routes` | 获取所有路线 | 登录 |
| GET | `/api/routes/search?q=` | 模糊搜索（名称/编号/描述） | 登录 |
| GET | `/api/routes/template` | 下载导入模板 (.xlsx) | admin |
| POST | `/api/routes/import` | 批量导入路线 | admin |
| PUT | `/api/routes/batch` | 批量启用/停用 | admin |
| GET | `/api/routes/{id}` | 获取单条路线 | 登录 |
| POST | `/api/routes` | 创建路线（自动编号 RT+10位） | admin |
| PUT | `/api/routes/{id}` | 更新路线（记录历史） | admin |
| DELETE | `/api/routes/{id}` | 软删除（标记 is_active=false） | admin |
| DELETE | `/api/routes/{id}/force` | 硬删除（无关联团时可删除） | admin |
| GET | `/api/routes/{id}/history` | 获取修改历史 | admin |

### 3.2 旅游团管理 `/api/groups`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/groups` | 列表（支持筛选 status/route_id/departure_from/to） | 登录 |
| GET | `/api/groups/template` | 下载导入模板 (.xlsx) | admin |
| POST | `/api/groups/import` | 批量导入旅游团 | admin |
| GET | `/api/groups/{id}` | 详情（含路线信息） | 登录 |
| POST | `/api/groups` | 创建 | admin |
| PUT | `/api/groups/{id}` | 更新（已发布不可改） | admin |
| POST | `/api/groups/{id}/publish` | 发布（需设置价格） | admin |
| GET | `/api/groups/{id}/availability` | 查看可用名额 | 登录 |
| GET | `/api/groups/{id}/pricing-preview` | 订金预览（参数：adults, children） | 登录 |
| GET | `/api/groups/{id}/balance-deadline` | 尾款截止日计算（参数：today） | 登录 |

### 3.3 申请管理 `/api/applications`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/applications` | 创建申请 | frontdesk/admin |
| GET | `/api/applications/search` | 搜索（code/departure/name） | frontdesk/admin |
| GET | `/api/applications/{id}` | 详情（含参加者和团信息） | frontdesk/admin |
| GET | `/{id}/deposit-preview` | 订金支付预览 | 登录 |
| POST | `/{id}/pay-deposit` | 支付订金 | frontdesk/admin |
| POST | `/{id}/pay-balance` | 支付尾款 | frontdesk/admin |
| GET | `/{id}/remaining-balance` | 剩余应付（含截止日） | 登录 |
| GET | `/{id}/payment-logs` | 支付记录列表（含凭证） | 登录 |
| POST | `/{id}/payment-voucher` | 上传支付凭证 | 登录 |
| POST | `/{id}/participants` | 批量录入参加者 | frontdesk/admin |
| GET | `/{id}/participants` | 参加者列表 | 登录 |
| PUT | `/participants/{id}` | 更新参加者（记录历史） | frontdesk/admin |
| GET | `/participants/{id}/edit-history` | 编辑历史 | 登录 |
| GET | `/{id}/duplicate-check` | 重复参加者检测 | 登录 |
| POST | `/{id}/participants/import` | Excel 导入参加者 | frontdesk/admin |
| GET | `/participants/template` | 参加者导入模板 | 登录 |
| POST | `/{id}/cancel` | 取消申请 | frontdesk/admin |
| POST | `/{id}/partial-cancel` | 部分取消（指定参加者） | frontdesk/admin |
| GET | `/{id}/cancel-preview` | 取消预览（手续费计算） | 登录 |
| GET | `/{id}/refunds` | 退款记录 | 登录 |
| PUT | `/refunds/{id}/approve` | 审核退款 | finance/admin |
| GET | `/{id}/reminder-logs` | 催款记录 | 登录 |
| POST | `/{id}/generate-order-no` | 生成交款单编号 | frontdesk/admin |
| GET | `/{id}/confirmation-pdf` | 下载旅行确认书 PDF | 登录 |
| GET | `/{id}/payment-notice-pdf` | 下载余额缴款单 PDF | 登录 |

### 3.4 任务/财务 `/api/tasks`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/tasks/daily-reminders` | 每日催款列表 | finance/admin |
| GET | `/api/tasks/daily-finance` | 每日财务记录 | finance/admin |
| POST | `/api/tasks/daily-finance/export` | 导出财务数据（CSV/Excel/JSON） | finance/admin |
| GET | `/api/tasks/finance-report` | 财务报告（daily/monthly/quarterly） | finance/admin |
| POST | `/api/tasks/batch-print` | 批量生成文档（JSON） | finance/admin |
| POST | `/api/tasks/batch-print/pdf` | 批量打印 PDF（合并为一个文件） | finance/admin |
| POST | `/api/tasks/send-reminder` | 发送催款提醒（email/sms/print） | finance/admin |
| GET | `/api/tasks/reminder-logs` | 催款日志列表 | finance/admin |
| POST | `/api/tasks/bank-reconciliation/import` | 导入 JSON 对账单 | finance/admin |
| POST | `/api/tasks/bank-reconciliation/import/excel` | 导入 Excel 对账单 | finance/admin |
| GET | `/api/tasks/bank-reconciliation` | 对账记录列表 | finance/admin |
| GET | `/api/tasks/bank-reconciliation/{id}` | 对账记录详情 | finance/admin |
| GET | `/api/tasks/bank-reconciliation/{id}/items` | 对账明细项 | finance/admin |

### 3.5 认证 `/api/auth`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | `/api/auth/login` | 登录获取 JWT Token | 公开 |
| GET | `/api/auth/me` | 当前用户信息 | 登录 |
| PUT | `/api/auth/change-password` | 修改密码 | 登录 |
| GET | `/api/auth/predefined-users` | 获取预设用户列表 | 登录 |

### 3.6 用户管理 `/api/users`（仅 admin）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users` | 用户列表 |
| POST | `/api/users` | 创建用户 |
| GET | `/api/users/{id}` | 用户详情 |
| PUT | `/api/users/{id}` | 更新用户 |
| PUT | `/api/users/{id}/reset-password` | 重置密码 |
| DELETE | `/api/users/{id}` | 停用用户（不可停用自己） |

### 3.7 工作台面板 `/api/dashboard`

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| GET | `/api/dashboard/frontdesk` | 前台面板 | 任意登录 |
| GET | `/api/dashboard/collector` | 收款面板 | 任意登录 |
| GET | `/api/dashboard/product` | 产品面板 | 任意登录 |
| GET | `/api/dashboard/finance` | 财务面板 | finance/admin |
| GET | `/api/dashboard/admin` | 管理面板 | admin |

### 3.8 根路由

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | API 基本信息 |
| GET | `/health` | 健康检查 |

---

## 4. 角色与权限映射

### 4.1 角色定义

| 角色 | 枚举值 | 说明 |
|------|--------|------|
| 管理员 | admin | 系统管理、路线/团管理、用户管理 |
| 前台 | frontdesk | 创建申请、录入参加者、浏览数据 |
| 财务 | finance | 催款、财务报表、退款审核、对账 |

### 4.2 权限标签映射

| 权限标签 | 可用角色 | 说明 |
|----------|---------|------|
| `admin` | admin | 用户管理 |
| `dashboard:finance` | finance, admin | 财务面板 |
| `group:manage` | admin | 管理旅游团 |
| `route:manage` | admin | 管理路线 |
| `task:manage` | finance, admin | 催款与报表 |
| `application:create` | frontdesk, admin | 创建申请 |
| `application:read` | frontdesk, admin | 查看申请 |
| `group:read` | frontdesk, admin | 查看旅游团 |

---

## 5. 核心业务规则

### 5.1 订金计算
- 总旅费 = 大人数 × 大人价 + 小孩数 × 小孩价
- 距出发天数 D = 出发日期 - 今天
- 订金比例：
  - D ≥ 60 → 10%
  - 30 ≤ D < 60 → 20%
  - D < 30 → 100%（全款）
- 金额四舍五入到分。

### 5.2 尾款支付期限
- 最终期限 = max(出发日期 - 30 天, 交款单生成日期 + 10 天)
- 若已全款支付则仅生成确认书，无交款单。

### 5.3 取消手续费
- 距出发天数 D：
  - D ≥ 30 → 0%
  - 10 < D < 30 → 20%
  - 1 ≤ D ≤ 10 → 50%
  - D = 0（出发当天）→ 100%
- 已付总额 = 已付订金 + 已付尾款
- 退款金额 = 已付总额 - (已付总额 × 比例)
- 部分取消：按取消人数比例计算退款，同样适用手续费率。
- **退款 >= 5000 元需审核**（admin/finance 审批），批准后直接完成。

### 5.4 名额控制
- 付订金时检查：团内非取消申请总人数 + 当前申请人数 ≤ `max_pax`
- 使用数据库行锁保证并发安全。

### 5.5 价格锁定
- 团 `is_published = false` 时价格可改；发布后价格不可变更。

### 5.6 重复参加者检查
- 录入参加者时可按手机号或身份证号检查同团是否已存在，返回警告。

---

## 6. 催款与财务任务

### 6.1 定时任务（APScheduler）

| 任务 | 触发时间 | 说明 |
|------|---------|------|
| 催款单生成 | 每日 01:00 | 筛选需催款申请（info_completed=true，尾款未付），生成确认书和交款单 |
| 自动短信/邮件提醒 | 每日 09:00 | 尾款截止前 3 天发短信，7 天内发邮件（若有邮箱） |
| 财务导出 | 每日 23:59 | 导出当日全部支付记录为 CSV/Excel/JSON |

### 6.2 催款条件
- 申请状态：`info_completed=true` 且 `paid_balance < total_price - paid_deposit`
- 按尾款截止日倒排，优先催款紧急的

### 6.3 财务导出格式
- 支持导出为 CSV、Excel（.xlsx）、JSON
- 导出的字段可自定义选择

### 6.4 银行对账
- 支持 JSON 数组和 Excel 文件两种导入方式
- 系统自动匹配银行记录和支付记录（按金额和参考号）
- 提供未匹配项列表供人工核对

---

## 7. 认证与安全

- JWT 认证，8 小时过期，使用 HS256 算法。
- 密码使用 bcrypt（passlib）哈希存储。
- 后端通过依赖注入校验角色/权限（`require_role` / `require_permission`）。
- 前端 axios 拦截器处理 401 清空 Token，通过自定义事件 `auth:logout` 让路由守卫渲染登录页。
- **注意**：登录接口返回的 Token 与角色信息，前端必须同步更新状态，避免异步竞态导致误判未登录。

---

## 8. 预设用户

系统启动时自动创建以下测试账户（仅开发环境）：

| 用户名 | 密码 | 角色 | 姓名 |
|--------|------|------|------|
| admin | admin123 | admin | 系统管理员 |
| frontdesk | 123456 | frontdesk | 张前台 |
| finance | 123456 | finance | 李财务 |

> 后端不提供暴露用户密码的接口，仅通过 `/api/auth/predefined-users` 返回用户名和角色。

---

## 9. 前端页面结构

| 路由 | 页面 | 组件 | 权限 |
|------|------|------|------|
| `/` 或 `/home` | 首页/仪表盘 | HomePage | 登录 |
| `/groups` | 旅游团查询（前台卡片视图） | GroupList | frontdesk/admin |
| `/apply/:groupId` | 创建申请 | ApplyCreate | 登录 |
| `/applications/:id` | 申请详情（Steps + 操作面板） | AppDetail | 登录 |
| `/admin/groups` | 管理旅游团（后台表格视图） | AdminGroups | admin |
| `/admin/routes` | 管理路线 | AdminRoutes | admin |
| `/admin/tasks` | 催款与报表（4 个 Tab） | DailyTasks | finance/admin |
| `/admin/users` | 用户管理 | UserManagement | admin |
| `/user/profile` | 个人中心/修改密码 | UserProfile | 登录 |
| `/help` | 使用帮助 | HelpPage | 登录 |

### 9.1 导航菜单（按角色过滤）

| 角色 | 可见菜单 |
|------|---------|
| admin | 全部菜单 |
| frontdesk | 首页、旅游团查询 |
| finance | 首页、催款与报表 |

---

## 10. 导入导出模板

### 10.1 路线导入模板（3 列）

| 列名 | 说明 | 必填 |
|------|------|------|
| 路线名称 | 路线名称 | 是 |
| 描述 | 路线描述 | 否 |
| 状态 | TRUE=启用 / FALSE=停用 | 否（默认TRUE） |

### 10.2 旅游团导入模板（8 列）

| 列名 | 说明 | 必填 |
|------|------|------|
| 路线ID | 对应 routes.id | 是 |
| 团代码 | 唯一代码 | 是 |
| 出发日期(YYYY-MM-DD) | 出发日期 | 是 |
| 截止日期(YYYY-MM-DD) | 截止报名日期 | 是 |
| 最大人数 | 名额上限 | 是 |
| 成人价 | 成人价格 | 否 |
| 儿童价 | 儿童价格 | 否 |
| 是否发布(True/False) | 发布状态 | 否（默认False） |

### 10.3 参加者导入模板（7 列）

| 列名 | 说明 | 必填 |
|------|------|------|
| 姓名 | 参加者姓名 | 是 |
| 性别(M/F/O) | 性别 | 否 |
| 出生日期 | 出生日期 | 否 |
| 电话 | 联系电话 | 否 |
| Email | 邮箱 | 否 |
| 联系地址 | 地址 | 否 |
| 是否责任人(True/False) | 是否负责人 | 否（默认False） |

### 10.4 银行对账导入

**JSON 格式（数组）：**
```json
[
  {"date": "2025-07-01", "amount": 1500.00, "reference": "BANK123"},
  {"date": "2025-07-02", "amount": 2000.00, "reference": "BANK456"}
]
```

**Excel 格式：** 3 列：日期 / 金额 / 参考号（从第 2 行开始）

---

## 11. PDF 文档

使用 ReportLab 库生成，支持中文（宋体/黑体）。

### 11.1 旅行确认书
- 文件名：`confirmation_{application_id}.pdf`
- 包含内容：申请人信息、团信息、路线、费用明细、支付状态

### 11.2 余额缴款单
- 文件名：`payment_notice_{application_id}.pdf`
- 包含内容：申请人信息、欠款金额、尾款截止日、支付方式

### 11.3 批量打印
- 支持批量合并多个确认书或缴款单为一个 PDF 文件
- 使用 PyPDF2.PdfMerger

---

## 12. 仪表盘数据

### 12.1 前台面板 `/api/dashboard/frontdesk`
```json
{
  "new_applications_today": 5,
  "pending_participants": 3
}
```

### 12.2 收款面板 `/api/dashboard/collector`
```json
{
  "reminders_today": 8,
  "overdue_balance": 2
}
```

### 12.3 产品面板 `/api/dashboard/product`
```json
{
  "upcoming_groups": 10,
  "unpublished_groups": 4
}
```

### 12.4 财务面板 `/api/dashboard/finance`
```json
{
  "yesterday_income": 15000.00,
  "yesterday_exports": 3,
  "pending_refunds": 2
}
```

### 12.5 管理面板 `/api/dashboard/admin`
```json
{
  "total_users": 5,
  "total_applications": 30,
  "today_income": 5000.00,
  "pending_refunds": 1
}
```

---

## 13. 其他约定

- 所有金额计算以服务器日期为准（`date.today()`），避免时区问题。
- 支付操作、取消等关键事务在数据库事务中执行。
- 支付日志不可修改或删除，仅追加。
- 财务导出记录和催款日志长期保留。
- 路线停用后不影响已有团，但不可用于新建团。
- 路线编号规则：`RT` + 10 位顺序数字（如 `RT0000000001`），系统自动生成，不可修改。
- 前端日期格式统一为中文：`YYYY年M月D日`（通过 dayjs zh-cn locale 的 `formatDate` / `formatDateTime` 工具函数）。
- 性别字段在业务层面仅使用 `M`（男）和 `F`（女），数据库保留 `O` 选项。
- 如果数据库中仍存在旧角色值（如 `finance_admin`），需执行数据迁移：
  ```sql
  UPDATE users SET role = 'admin' WHERE role IN ('finance_admin','product_admin');
  UPDATE users SET role = 'frontdesk' WHERE role = 'frontdesk' OR role = 'collector';
  UPDATE users SET role = 'finance' WHERE role = 'finance';
  ```
