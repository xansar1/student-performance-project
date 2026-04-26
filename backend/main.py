from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# IMPORTANT: correct import path nokku
from backend.routes import router  

app = FastAPI(
    title="AI Coaching SaaS API",
    version="1.0"
)

# ✅ CORS (frontend connect cheyyan MUST)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # production il restrict cheyyanam
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Routes include cheyyunnu
app.include_router(router)

# ✅ Root check
@app.get("/")
def home():
    return {"message": "API is running 🚀"}
