from fastapi import APIRouter
from app.api.v1.endpoints import classification, abs, chat, corpus

api_router = APIRouter()
api_router.include_router(classification.router)
api_router.include_router(abs.router)
api_router.include_router(chat.router)
api_router.include_router(corpus.router)
