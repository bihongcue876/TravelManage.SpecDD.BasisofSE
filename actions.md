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
    - FastAPI: 0.109.0 → 0.136.1
    - Uvicorn: 0.27.0 → 0.40.0
    - SQLAlchemy: 2.0.25 → 2.0.48
    - psycopg2-binary: 2.9.9 → 2.9.12
    - Pydantic: 2.5.3 → 2.13.3
    - APScheduler: 3.10.4 → 3.11.2
    - python-multipart: 0.0.6 → 0.0.27

16. 创建 pyproject.toml 文件，采用现代 Python 项目标准
    - 配置项目元数据和依赖
    - 设置 Python 3.14+ 要求
    - 配置 hatch 构建系统

17. 生成 uv.lock 文件，锁定依赖版本确保团队环境一致

18. 更新 README.md 快速启动部分
    - 使用 uv 命令替代 pip
    - 优化文档结构和格式

## 问题与诊断

