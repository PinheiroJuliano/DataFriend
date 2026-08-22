from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.datasets import router as datasets_router
from app.api.connect import router as connect_router
from app.api.kaggle import router as kaggle_router

app = FastAPI(
    title="DataFriend API",
    description="Backend API para o MVP do DataFriend",
    version="0.1.0"
)

# Configuração de CORS
origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos routers sob o prefixo /api
app.include_router(chat_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(datasets_router, prefix="/api")
app.include_router(connect_router, prefix="/api")
app.include_router(kaggle_router, prefix="/api")

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
