# 测试用例设计文档

> 对应后端 unittest + mock + coverage，前端 Vitest + testing-library

---

## 一、测试总体策略

### 1.1 分层测试

```
API 端点层 (TestClient)        → 集成测试
         ↑
业务服务层 (mock DB)            → 服务单元测试
         ↑
纯函数层 (直接调用)              → 纯函数单元测试
```

### 1.2 自动缩放（测试发现）

- 后端：`unittest.TestLoader().discover()` 自动扫描 `tests/test_*.py`
- 前端：`vitest` 自动扫描 `src/**/*.test.{ts,tsx}`
- 覆盖率：`coverage.py` + `@vitest/coverage-v8`

### 1.3 mock 策略

| 依赖 | mock 方式 | 说明 |
|------|----------|------|
| 数据库 | SQLite `:memory:` + `create_all/drop_all` | 每函数级隔离 |
| `date.today()` | `unittest.mock.patch('datetime.date.today')` | 控制时间轴 |
| FastAPI 请求 | `TestClient(app)` + dependency override | 绕过真实 HTTP |
| 文件 I/O (导出) | `unittest.mock.patch('builtins.open')` + `tempfile` | 避免写磁盘 |
| Axios (前端) | `vitest` mock + axios mock adapter | 拦截 HTTP 请求 |

---

## 二、后端测试用例设计

### 2.1 定价服务 `services/pricing.py`

#### `calc_deposit()` — 订金计算

| 用例ID | 场景 | 输入 | 预期 | 边界类型 |
|--------|------|------|------|---------|
| PRICE-001 | 距出发≥60天 | D=60, total=10000 | deposit=1000 (10%) | 边界值 |
| PRICE-002 | 距出发59天 | D=59, total=10000 | deposit=2000 (20%) | 边界值 |
| PRICE-003 | 距出发=30天 | D=30, total=10000 | deposit=2000 (20%) | 边界值 |
| PRICE-004 | 距出发29天 | D=29, total=10000 | deposit=10000 (100%) | 边界值 |
| PRICE-005 | 仅大人 | adults=2, children=0 | total=2*adult_price | 等价类 |
| PRICE-006 | 仅小孩 | adults=0, children=2 | total=2*child_price | 等价类 |
| PRICE-007 | 零价格 | adult_price=0, child_price=0 | deposit=0 | 异常 |
| PRICE-008 | 小数精度 | price=123.45, D≥60 | deposit四舍五入到分 | 精度 |

#### `calc_cancel_fee()` — 取消手续费

| 用例ID | 场景 | 输入 | 预期 | 边界类型 |
|--------|------|------|------|---------|
| CANCEL-001 | D≥30 | D=30, paid=5000 | fee=0 (0%) | 边界值 |
| CANCEL-002 | 10<D<30 | D=29, paid=5000 | fee=1000 (20%) | 边界值 |
| CANCEL-003 | 10<D<30 | D=11, paid=5000 | fee=1000 (20%) | 内部 |
| CANCEL-004 | 1≤D≤10 | D=10, paid=5000 | fee=2500 (50%) | 边界值 |
| CANCEL-005 | 1≤D≤10 | D=1, paid=5000 | fee=2500 (50%) | 边界值 |
| CANCEL-006 | D=0（当天） | D=0, paid=5000 | fee=5000 (100%) | 边界值 |
| CANCEL-007 | 已支付0元 | paid=0, D=20 | fee=0, refund=0 | 异常 |
| CANCEL-008 | 部分支付 | paid=2000, D=20 | fee=400, refund=1600 | 等价类 |

#### `calc_balance_deadline()` — 尾款截止日

| 用例ID | 场景 | 输入 | 预期 | 边界类型 |
|--------|------|------|------|---------|
| DEAD-001 | 出发-30天 ≥ today+10天 | 标准情况 | balance_deadline = base | 等价类 |
| DEAD-002 | 出发-30天正好=今日+10天 | 准确边界 | balance_deadline = base | 边界 |
| DEAD-003 | 出发-30天 < today+10天 | 不足10天 | balance_deadline = fallback | 边界 |

### 2.2 申请服务 `services/application.py`

#### `create_application()` — 创建申请

| 用例ID | 场景 | 验证点 |
|--------|------|--------|
| APP-001 | 成功创建（距出发≥60天） | 订金10%、状态draft |
| APP-002 | 成功创建（30≤D<60） | 订金20% |
| APP-003 | 成功创建（D<30） | 订金100% |
| APP-004 | 团未发布 | 拒绝创建 |
| APP-005 | 已过截止日 | 拒绝创建 |
| APP-006 | 人数满 | 拒绝创建 |
| APP-007 | 团不存在 | ValueError |

#### `pay_deposit()` — 支付订金

| 用例ID | 场景 | 验证点 |
|--------|------|--------|
| DEP-001 | 支付成功 | 状态→deposit_paid, paid_deposit=订金 |
| DEP-002 | 申请状态不为draft | ValueError |
| DEP-003 | 订金已支付 | ValueError |
| DEP-004 | 金额不足 | ValueError |

#### `pay_balance()` / `cancel_application()` / `approve_refund()`

覆盖全部27个BBD场景，每个场景对应一个 `test_` 方法。

### 2.3 旅游团服务（路由层）

通过 TestClient 直接测试 HTTP 响应。

| 用例ID | 场景 | 方法 | 路径 |
|--------|------|------|------|
| GRP-001 | 创建成功 | POST | /api/groups |
| GRP-002 | 路线不存在 | POST | /api/groups |
| GRP-003 | 截止日≥出发日 | POST | /api/groups |
| GRP-004 | 更新未发布团 | PUT | /api/groups/{id} |
| GRP-005 | 更新已发布团 | PUT | /api/groups/{id}（拒绝） |
| GRP-006 | 发布成功 | POST | /api/groups/{id}/publish |
| GRP-007 | 已发布再发布 | POST | /api/groups/{id}/publish（拒绝） |
| GRP-008 | 发布但价格未设 | POST | /api/groups/{id}/publish（拒绝） |
| GRP-009 | 查询名额 | GET | /api/groups/{id}/availability |

### 2.4 取消与退款

| 用例ID | 场景 |
|--------|------|
| CNL-001 | 全额取消（D≥30）→ 无手续费 |
| CNL-002 | 全额取消（D=20）→ 20%手续费 |
| CNL-003 | 全额取消（D=5）→ 50%手续费 |
| CNL-004 | 全额取消（D=0）→ 100%手续费 |
| CNL-005 | 仅付订金时取消 |
| CNL-006 | 部分取消（取消部分参加者） |
| CNL-007 | 部分取消（含责任人→拒绝） |
| CNL-008 | 退款≥5000需审核 |
| CNL-009 | 退款<5000自动通过 |
| CNL-010 | 审核批准→退款完成 |

### 2.5 支付

| 用例ID | 场景 |
|--------|------|
| PAY-001 | 支付订金成功 |
| PAY-002 | 支付超过订金 → 成功（不退多付） |
| PAY-003 | 支付订金失败（状态不对） |
| PAY-004 | 支付订金失败（金额不足） |
| PAY-005 | 支付尾款（部分付） |
| PAY-006 | 支付尾款（结清 → confirmed） |
| PAY-007 | 支付尾款失败（信息未完成） |
| PAY-008 | 支付尾款失败（超额） |
| PAY-009 | 带支付方式支付 |
| PAY-010 | 支付凭证上传 |

---

## 三、前端测试用例设计

### 3.1 工具函数 `utils.ts`

| 用例ID | 函数 | 输入 | 预期输出 |
|--------|------|------|---------|
| UTIL-001 | formatDateTime | "2026-06-07T14:30:00" | "2026年6月7日 14:30" |
| UTIL-002 | formatDateTime | null | "-" |
| UTIL-003 | formatDateTime | undefined | "-" |
| UTIL-004 | formatDate | "2026-06-07T00:00:00" | "2026年6月7日" |
| UTIL-005 | formatDate | null | "-" |
| UTIL-006 | formatMonthDay | "2026-06-07" | "6月7日" |
| UTIL-007 | formatMonthDay | null | "-" |
| UTIL-008 | formatWeekday | "2026-06-07" (周日) | "星期日" |
| UTIL-009 | formatWeekday | "2026-06-08" (周一) | "星期一" |
| UTIL-010 | formatWeekday | null | "-" |

### 3.2 认证 Context `auth.tsx`

| 用例ID | 场景 | 验证点 |
|--------|------|--------|
| AUTH-001 | login 成功 | 设置 token、更新 user、isAuthenticated=true |
| AUTH-002 | login 失败（401） | 抛错误、不设置 user |
| AUTH-003 | logout | 清除 token、user→null、isAuthenticated=false |
| AUTH-004 | hasRole 匹配 | 正确角色返回 true |
| AUTH-005 | hasRole 不匹配 | 错误角色返回 false |
| AUTH-006 | hasRole 多角色 | 其中一个匹配即 true |
| AUTH-007 | Token 过期（me 返回 401） | 自动 logout、跳登录 |
| AUTH-008 | 初始未登录 | loading=true, user=null |

### 3.3 API 层 `api.ts`

| 用例ID | 场景 | 验证点 |
|--------|------|--------|
| API-001 | 请求自动带 token | Authorization header 正确 |
| API-002 | 无 token 请求 | 无 Bearer header |
| API-003 | 401 非登录接口 | 清除 token、触发 auth:logout 事件 |
| API-004 | 401 登录接口 | 不触发 logout |
| API-005 | 成功响应 | 返回 response.data |

### 3.4 登录页 `Login.tsx`

| 用例ID | 场景 | 验证点 |
|--------|------|--------|
| LOGIN-001 | 渲染登录表单 | 用户名/密码输入框、登录按钮可见 |
| LOGIN-002 | 空值提交 | 显示验证错误提示 |
| LOGIN-003 | 登录成功 | 调用 login、跳转 /home |
| LOGIN-004 | 登录失败 | 显示错误 message |

---

## 四、覆盖率目标

| 模块 | 目标覆盖率 | 关键覆盖点 |
|------|-----------|-----------|
| `services/pricing.py` | 100% | 所有边界值分支 |
| `services/application.py` | ≥90% | 所有分支、异常路径 |
| `frontend/src/utils.ts` | 100% | 所有函数、null/undefined |
| `frontend/src/auth.tsx` | ≥85% | 所有状态转换 |
| `frontend/src/api.ts` | ≥80% | 拦截器逻辑 |

---

## 五、运行方式

```bash
# 后端全部测试 + 覆盖率
cd backend
coverage run -m unittest discover tests/ -v
coverage html
# 打开 htmlcov/index.html

# 前端全部测试
cd frontend
npx vitest run

# 前端测试（watch 模式）
npx vitest
```
