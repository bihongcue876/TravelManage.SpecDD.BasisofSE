from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from routers import routes, groups, applications, tasks
from tasks_scheduler import init_scheduler

scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    scheduler = init_scheduler()
    yield
    if scheduler:
        scheduler.shutdown()


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Travel Management API",
    description="旅游业务管理系统 API",
    version="1.0.0",
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


@app.get("/")
def root():
    return {"message": "Travel Management API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
