from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.company import CompanyRepository
from app.repositories.game import GameRepository
from app.repositories.participant import ParticipantRepository
from app.schemas.game import GameResultCreate, GameResultRead, GameSessionCreate, GameSessionRead, GameSessionStatusUpdate

router = APIRouter(tags=["games"])


@router.post("/companies/{company_id}/game-sessions", response_model=GameSessionRead, status_code=status.HTTP_201_CREATED)
async def create_game_session(company_id: int, payload: GameSessionCreate, db: AsyncSession = Depends(get_db)):
    if await CompanyRepository(db).get_by_id(company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return await GameRepository(db).create_session(company_id, payload.game_type)


@router.get("/companies/{company_id}/game-sessions", response_model=list[GameSessionRead])
async def list_game_sessions(company_id: int, db: AsyncSession = Depends(get_db)):
    if await CompanyRepository(db).get_by_id(company_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return await GameRepository(db).list_sessions_by_company(company_id)


@router.get("/game-sessions/{session_id}", response_model=GameSessionRead)
async def get_game_session(session_id: int, db: AsyncSession = Depends(get_db)):
    game_session = await GameRepository(db).get_session(session_id)
    if game_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found")
    return game_session


@router.patch("/game-sessions/{session_id}/status", response_model=GameSessionRead)
async def set_game_session_status(session_id: int, payload: GameSessionStatusUpdate, db: AsyncSession = Depends(get_db)):
    game_session = await GameRepository(db).set_session_status(session_id, payload.status)
    if game_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found")
    return game_session


@router.post("/game-sessions/{session_id}/results", response_model=GameResultRead, status_code=status.HTTP_201_CREATED)
async def add_game_result(session_id: int, payload: GameResultCreate, db: AsyncSession = Depends(get_db)):
    game_repo = GameRepository(db)
    game_session = await game_repo.get_session(session_id)
    if game_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found")

    participant = await ParticipantRepository(db).get_by_id(payload.participant_id)
    if participant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")
    if participant.company_id != game_session.company_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Participant must belong to session company")

    return await game_repo.add_result(session_id, payload.participant_id, payload.result_value, payload.result_data)


@router.get("/game-sessions/{session_id}/results", response_model=list[GameResultRead])
async def list_game_results(session_id: int, db: AsyncSession = Depends(get_db)):
    game_repo = GameRepository(db)
    if await game_repo.get_session(session_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found")
    return await game_repo.list_results(session_id)
