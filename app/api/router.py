from fastapi import APIRouter

from app.api import check_items, companies, content, debts, games, participants

api_router = APIRouter()
api_router.include_router(companies.router)
api_router.include_router(participants.router)
api_router.include_router(check_items.router)
api_router.include_router(debts.router)
api_router.include_router(games.router)
api_router.include_router(content.router)
