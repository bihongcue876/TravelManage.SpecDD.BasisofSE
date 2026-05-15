# SPEC DRIVEN DEVELOPMENT流程

## 总体思路：双规范驱动

- **业务行为规范**：用 Gherkin 编写 Feature 文件，描述系统对外的业务行为（如“成功申请旅游团”、“逾期取消扣费”等），这些场景会被自动化执行，作为验收测试。
- **API 契约规范**：用 OpenAPI 3.0 编写接口定义，明确前后端交互的请求/响应结构、状态码等，通过代码生成工具同步后端接口骨架和前端类型定义。

两个规范互相关联但各司其职：Feature 文件驱动业务流程和验收标准，OpenAPI 驱动接口实现与对接。最终所有实现代码都从这两类规范中生长出来，并持续保持同步。


## SDD 实施流程（共 7 个阶段）

### 阶段 1：需求实例化——从需求书到用户故事 & 场景大纲
**目标**：将需求书中的流程性描述转化为结构化的用户故事和具体示例，为编写 Feature 文件做准备。

**做法**：
- 拆解业务流程，识别出核心角色（顾客、前台员工、催款员工、路线管理员、系统）。
- 为每个业务能力编写用户故事卡片，格式：`As a <角色>, I want <功能>, so that <价值>`。
- 对每个故事列出 **具体场景**（正常、异常、边界），用表格形式整理关键输入输出。

**示例**：  
*故事：前台员工为顾客办理旅游申请*  
- 场景1：可申请的团 – 团未满，截止日期未到，距出发≥2个月，计算10%订金。  
- 场景2：人数已满 – 申请被拒绝。  
- 场景3：距出发<1个月 – 需要支付全款。  
- 场景4：申请责任人信息录入，生成订金收据和申请书。

**产出物**：用户故事地图 + 场景实例表（可放入项目文档库）。

---

### 阶段 2：编写业务行为规范（Gherkin Feature 文件）
**目标**：用 Gherkin 语法将场景固化为可执行、无歧义的规格说明。

**做法**：
- 按业务模块划分 Feature 文件，例如：
  - `applications.feature`：涵盖申请提交、订金计算、参加者信息录入、申请完成。
  - `payments.feature`：余款支付、催款单生成、支付期限计算。
  - `cancellations.feature`：取消申请、手续费计算、责任人变更。
  - `route_management.feature`：路线增删、价格设定与公开。
- 每个 Scenario 严格使用 `Given / When / Then` 描述前置条件、操作和预期结果。
- 使用**具体数据**（如出发日期、人数、金额），避免模糊表达。

**示例 – `applications.feature` 片段**：
```gherkin
Feature: 旅游申请办理
  作为前台员工
  我想要为顾客办理旅游申请
  以便于确认团位并收取订金

  Background:
    Given 系统中存在旅游团 "武汉-三亚 3日游"，团代码 "WH-SY-001"
    And 该团出发日期为 "2026-08-20"
    And 该团大人价格 2000 元，小孩价格 1000 元
    And 该团人数限额 30 人，当前已报名 10 人

  Scenario: 提前超过两个月申请，成功并计算 10% 订金
    Given 今天是 "2026-05-13"
    When 员工录入申请责任人姓名 "张三"，电话 "13800138000"
    And 员工录入参加者：大人 2 人，小孩 1 人
    And 员工提交申请
    Then 申请被接受
    And 订金计算为 500 元 （(2000*2 + 1000*1) * 10%）
    And 系统记录订金支付情况
    And 系统生成订金收据和旅游申请书

  Scenario: 人数已满时申请被拒绝
    Given 该团当前已报名 30 人
    When 员工提交一份包含 1 人的申请
    Then 申请被拒绝，提示 "该团人数已满"

  Scenario: 距出发不足一个月，需付全款
    Given 今天是 "2026-07-25"
    When 员工录入申请责任人 "李四"，大人 1 人
    And 提交申请
    Then 申请被接受
    And 订金计算为 2000 元（全款）
    And 系统记录全款支付
```

**工具建议**：  
- Gherkin 语法支持（VSCode 插件）  
- 未来执行使用 `pytest-bdd`（与 Python 技术栈匹配）

**产出物**：一套完整的 `.feature` 文件，存放在 `features/` 目录下，作为项目**唯一的业务需求真相来源**。

---

### 阶段 3：编写 API 契约规范（OpenAPI 3.0）
**目标**：定义后端所有 API 的接口细节，使前后端能并行开发，并自动生成文档和类型定义。

**做法**：
- 根据业务场景梳理所需的 API 端点，例如：
  - `POST /applications` – 创建申请（含订金计算）
  - `POST /applications/{id}/participants` – 录入参加者
  - `POST /applications/{id}/confirm` – 完成申请
  - `POST /applications/{id}/cancel` – 取消申请
  - `GET /tour-groups` – 查询旅游团
  - `PUT /tour-groups/{code}/pricing` – 设定价格
  - ……
- 编写 `openapi.yaml`，定义每个端点的请求体、路径参数、查询参数、响应结构，并编写详细的 `description` 和 `example`。
- 将复杂业务规则（如订金计算、支付期限）用 **注释** 或 **扩展属性** 描述清楚，确保契约本身即文档。

**示例 – 申请创建 API 片段**：
```yaml
paths:
  /applications:
    post:
      summary: 提交旅游申请
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                tour_group_code:
                  type: string
                  example: "WH-SY-001"
                responsible_person:
                  $ref: '#/components/schemas/Person'
                participants_summary:
                  type: object
                  properties:
                    adults:
                      type: integer
                      example: 2
                    children:
                      type: integer
                      example: 1
      responses:
        201:
          description: 申请已创建
          content:
            application/json:
              schema:
                type: object
                properties:
                  application_id:
                    type: string
                  deposit_amount:
                    type: number
                    example: 500.0
                  deposit_receipt_url:
                    type: string
        422:
          description: 申请不满足条件（已满、截止等）
```

**工具**：  
- 编辑器：VSCode + OpenAPI 插件  
- 代码生成：后续用 `datamodel-code-generator` 生成 Pydantic 模型，用 `openapi-generator` 或 FastAPI 内置方式生成路由骨架。

**产出物**：`openapi.yaml`，作为前后端唯一交互契约。

---

### 阶段 4：搭建自动化测试框架与骨架生成
**目标**：让规范可执行，并生成初始工程结构，确保红灯状态。

**做法**：
1. **初始化 BDD 框架**：  
   - 选用 `pytest-bdd`，安装依赖。  
   - 编写 `conftest.py` 提供 Fixture（如数据库连接、测试客户端）。  
   - 为每个 Feature 创建空的步骤定义文件（`test_applications.py` 等），所有步骤函数体用 `raise NotImplementedError` 占位。

2. **生成 API 骨架代码**：  
   - 利用 `openapi.yaml` 生成 Pydantic schemas 和 FastAPI 路由存根。  
   - 例如，使用 `fastapi-code-generator` 或手动根据 OpenAPI 创建路由文件，所有端点暂时返回 `501 Not Implemented`。

3. **验证红灯**：  
   - 运行 `pytest`，所有 Gherkin 场景标记为失败（步骤未实现）。  
   - 访问 API 文档（Swagger UI）看到所有端点存在但未实现。

**产出物**：  
- 可执行的测试套件（全红）  
- FastAPI 工程骨架  
- 前后端均可根据 OpenAPI 开始并行开发（前端生成 TypeScript 类型）

---

### 阶段 5：迭代实现——红灯→绿灯→重构
**目标**：以单个场景为单位，逐步实现业务逻辑，让规约逐一通过。

**做法**：
- 按功能优先级选取一个 Feature（如“旅游申请”），选择一个 Scenario。
- **写最少的代码让该场景通过**：
  1. 实现对应的 Step Definitions，调用后端 API（使用测试客户端）。
  2. 实现后端路由和业务逻辑（可能仅实现该场景所涉及的代码路径）。
  3. 运行测试，从红变绿。
- **立刻重构**：在不改变行为的前提下优化代码结构。
- **重复**：选取下一个场景，重复上述过程，直到整个 Feature 所有场景通过。
- 每通过一个场景，进行一次 Git 提交（信息可包含“绿色：xxx场景通过”）。

**重要原则**：
- 业务逻辑全部封装在领域模型或服务层，不与 FastAPI 耦合，以便在 Step Definitions 中直接测试。
- 数据库迁移脚本同步编写，使用内存数据库或 Testcontainers 保证测试独立。

**示例 – 实现“提前超过两个月申请”场景**：  
- Step Definition 调用 `POST /applications`，断言响应码和订金金额。  
- 后端实现：检查团状态、计算折扣、生成申请记录、返回订金。  
- 只处理 10% 的情况，不处理 20% 或全款，等待下一个场景驱动。

---

### 阶段 6：业务规则边缘验证与全流程串联
**目标**：确保异常、边界场景都被覆盖，同时验证跨模块的完整流程。

**做法**：
- 补全所有 Feature 文件中的异常场景（如取消申请、部分参与者变更、支付期限不足 10 天等）。
- 编写端到端场景，串联多个 API 调用，例如：“申请 → 支付订金 → 录入参加者 → 完成申请 → 打印催款单 → 支付余款”。
- 使用 `pytest-bdd` 的 Scenario Outline 处理大量数据组合（如不同天数、不同人数）。

---

### 阶段 7：活文档与持续集成
**目标**：让规约成为永不过时的系统说明书，并集成到 CI/CD。

**做法**：
- 配置 CI 流水线（如 GitHub Actions），每次 Push 执行：
  - 数据库迁移
  - 全量 BDD 测试（Feature 文件）
  - API 契约测试（用 OpenAPI 校验实际响应）
- 生成 BDD 测试报告（可使用 `pytest-html` 或 Allure），报告中直接展示 Gherkin 场景描述和执行结果，这就是**活文档**。
- 前后端均以 OpenAPI 规范为准，使用 Swagger UI 作为开发期间的实时交互文档。
- 关键业务规则（如订金比例、取消手续费率）直接写在 Feature 文件中，任何时候执行测试都能验证系统是否仍符合规范。

---

## 流程总结表

| 阶段 | 核心产物 | 状态验证 |
|------|---------|----------|
| 1. 需求实例化 | 用户故事 & 场景表 | 无 |
| 2. BDD 规范 | `.feature` 文件 | 文件评审通过 |
| 3. API 契约 | `openapi.yaml` | Swagger UI 可展示 |
| 4. 测试骨架 | 全红测试 + FastAPI 存根 | `pytest` 红，API 返回 501 |
| 5. 迭代实现 | 通过测试的场景 & 生产代码 | 场景绿，持续集成绿 |
| 6. 边缘覆盖 | 全量通过报告 | 所有 Feature 100% 通过 |
| 7. 活文档 | 测试报告 + Swagger 文档 | 每次构建自动更新 |


## 该流程在本项目中的适用性说明

- **复杂业务规则**（如订金比例、取消手续费）直接沉淀在 Gherkin 的 Then 步骤中，任何变更都会先修改规范再改代码，杜绝“代码和文档两张皮”。
- **前后端分离**通过 OpenAPI 契约保证类型安全和接口一致，前端可在 Step 2 后即用 Mock Server 开发。
- **财务导出**等后台任务，同样能通过 Gherkin 描述（“每天晚上导出当日交易”），用时间模拟触发验证。
- 整个开发过程天然留下了一条清晰的 **“规范 → 红灯 → 绿灯”** 的提交历史，无论是用于答辩演示还是日后维护，都能清晰回溯每个功能是依据哪条规格实现的。
