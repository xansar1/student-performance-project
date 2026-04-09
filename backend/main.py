from fastapi import FastAPI
from routes import router

app = FastAPI(
    title="AI Academic SaaS API"
)

app.include_router(router)
