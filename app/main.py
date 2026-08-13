from fastapi import FastAPI
from app.db import Base, engine
from app.api.routes import task_router, user_router


app = FastAPI(
    title="Docker Task API",
    description="Task management API built with FastAPI, SQLAlchemy and PostgreSQL",
    version="1.0.0",
)

Base.metadata.create_all(bind=engine)

app.include_router(task_router)
app.include_router(user_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "API is running"
    }