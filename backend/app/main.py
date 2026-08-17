import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings

from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.datasets import router as datasets_router

class Settings(BaseSettings):
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

app = FastAPI(
    title="Data Copilot API",
    description="Backend API para o MVP do Data Copilot",
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
# Note: chat_router já tem prefixo /chat no arquivo
# upload_router já tem prefixo /datasets/upload no arquivo
# datasets_router já tem prefixo /datasets no arquivo
app.include_router(chat_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(datasets_router, prefix="/api")

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}
