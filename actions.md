# actions
- 向后迭代，逐次叠加，注意行动描述简要。

## 已完成任务

1. 创建后端项目目录结构和基础文件（database.py, requirements.txt）
2. 实现数据库模型（models.py）- 包含 Route, Group, Application, Participant, Refund, PaymentLog, FinancialExport
3. 实现Pydantic schemas（schemas.py）- 请求/响应模型
4. 实现pricing服务（services/pricing.py）- 订金、手续费计算
5. 实现application服务（services/application.py）- 申请流程、支付、取消
6. 实现export服务（services/export.py）- 财务导出、催款单生成
7. 实现API路由（routers/）- routes, groups, applications, tasks
8. 实现定时任务调度器（tasks_scheduler.py）- APScheduler定时任务
9. 创建FastAPI主入口（main.py）
10. 创建前端项目结构和基础配置（TypeScript + Vite）
11. 实现前端API封装（api.ts）
12. 实现前端页面组件（GroupList, ApplyCreate, AppDetail, AdminGroups, AdminRoutes, DailyTasks）

## 问题修复

13. 修复缺失的TSX页面文件（GroupList.tsx, ApplyCreate.tsx, AppDetail.tsx）
14. 修复TypeScript类型错误（显式类型声明、移除未使用导入）

## 依赖管理升级

15. 更新 requirements.txt 到支持 Python 3.14 的最新版本
16. 创建 pyproject.toml 文件，采用现代 Python 项目标准
17. 生成 uv.lock 文件，锁定依赖版本确保团队环境一致
18. 更新 README.md 快速启动部分

## 第三阶段：BDD 测试骨架

19. 编写 5 个 Feature 文件（137 个场景）
20. 设置测试夹具（conftest.py）- TestClient + SQLite 内存数据库
21. 实现测试步骤函数（test_applications.py, test_groups.py, test_pricing.py, test_cancellations.py, test_payments.py）

## 第四阶段：Bug 修复与测试完善

22. 修复 services/application.py - data.departure_date → group.departure_date
23. 修复 services/pricing.py - calc_balance_deadline 逻辑修正
24. 修复 services/pricing.py - 取消手续费 10 天边界条件（<= 10）
25. 修复 services/application.py - pay_balance 先检查 cancelled 再检查 info_completed
26. 修复 routers/applications.py - /search 路由移到 /{id} 之前
27. 137 个场景全部通过

## 第五阶段：API 契约规范

28. 编写 docs/spec/openapi.yaml - 18 个端点的 OpenAPI 3.0.3 规范
29. 编写 doc/05_API_CONTRACT.MD - API 契约设计文档
30. 安装 openapi-core 并添加契约校验夹具到 conftest.py

## 第六阶段：活文档与持续集成

31. 安装 allure-pytest 并配置 Allure 报告生成
32. 运行全量测试生成 Allure 报告（137 passed）
33. 创建 .github/workflows/spec-test.yml CI 流水线
34. 更新 requirements-dev.txt 添加 allure-pytest, openapi-core, pyyaml
35. Allure 报告部署到 docs/reports/latest/
36. 编写 doc/06_LIVING_DOCUMENTATION.MD 活文档说明

