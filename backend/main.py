import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import engine, Base, SessionLocal
from routers import routes, groups, applications, tasks, dashboard
from routers.auth import auth_router, users_router
from tasks_scheduler import init_scheduler
from auth import hash_password
from models import User, Role

scheduler = None


def seed_initial_data():
    """初始化种子数据：创建默认用户"""
    db = SessionLocal()
    try:
        default_users = [
            {"username": "admin", "password": "admin123", "name": "系统管理员", "role": Role.ADMIN, "email": "admin@travel.com"},
            {"username": "frontdesk", "password": "123456", "name": "张前台", "role": Role.FRONTDESK, "email": "frontdesk@travel.com"},
            {"username": "finance", "password": "123456", "name": "李财务", "role": Role.FINANCE, "email": "finance@travel.com"},
        ]
        created = 0
        for u in default_users:
            existing = db.query(User).filter(User.username == u["username"]).first()
            if not existing:
                user = User(
                    username=u["username"],
                    password_hash=hash_password(u["password"]),
                    name=u["name"],
                    role=u["role"],
                    email=u["email"],
                )
                db.add(user)
                created += 1
        if created > 0:
            db.commit()
            print(f"[Seed] Created {created} default users")
    except Exception as e:
        db.rollback()
        print(f"[Seed] Skip: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    scheduler = init_scheduler()
    seed_initial_data()
    yield
    if scheduler:
        scheduler.shutdown()


os.makedirs("uploads/vouchers", exist_ok=True)
os.makedirs("exports", exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Travel Management API",
    description="旅游业务管理系统 API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)
app.include_router(groups.router)
app.include_router(applications.router)
app.include_router(tasks.router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(dashboard.router)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/exports", StaticFiles(directory="exports"), name="exports")


@app.get("/")
def root():
    return {"message": "Travel Management API", "version": "2.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
