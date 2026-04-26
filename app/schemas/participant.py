from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ParticipantCreate:
    company_id: int
    name: str


@dataclass(slots=True)
class ParticipantUpdate:
    name: str


@dataclass(slots=True)
class ParticipantRead:
    id: int
    company_id: int
    name: str

