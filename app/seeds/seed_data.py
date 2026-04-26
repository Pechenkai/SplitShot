from __future__ import annotations

import asyncio
from decimal import Decimal

from app.db.session import AsyncSessionFactory
from app.repositories.check_item import CheckItemRepository
from app.repositories.company import CompanyRepository
from app.repositories.debt import DebtRepository
from app.repositories.game_result import GameResultRepository
from app.repositories.game_session import GameSessionRepository
from app.repositories.participant import ParticipantRepository


async def seed() -> None:
    """Populate the database with sample SplitShot data."""

    async with AsyncSessionFactory() as session:
        company_repo = CompanyRepository(session)
        participant_repo = ParticipantRepository(session)
        check_item_repo = CheckItemRepository(session)
        debt_repo = DebtRepository(session)
        game_session_repo = GameSessionRepository(session)
        game_result_repo = GameResultRepository(session)

        friday_bar = await company_repo.create("Friday Bar")
        rooftop_club = await company_repo.create("Rooftop Club")

        alice = await participant_repo.create(friday_bar.id, "Alice")
        bob = await participant_repo.create(friday_bar.id, "Bob")
        charlie = await participant_repo.create(friday_bar.id, "Charlie")
        diana = await participant_repo.create(friday_bar.id, "Diana")

        eve = await participant_repo.create(rooftop_club.id, "Eve")
        frank = await participant_repo.create(rooftop_club.id, "Frank")
        grace = await participant_repo.create(rooftop_club.id, "Grace")

        await check_item_repo.create(friday_bar.id, "Pizza", Decimal("18.50"))
        await check_item_repo.create(friday_bar.id, "Beer", Decimal("6.40"))
        await check_item_repo.create(friday_bar.id, "Nachos", Decimal("11.90"))
        await check_item_repo.create(rooftop_club.id, "Lemonade Pitcher", Decimal("14.00"))
        await check_item_repo.create(rooftop_club.id, "Wings", Decimal("16.75"))

        await debt_repo.create(friday_bar.id, bob.id, alice.id, Decimal("9.25"))
        await debt_repo.create(friday_bar.id, charlie.id, diana.id, Decimal("4.80"))
        await debt_repo.create(rooftop_club.id, grace.id, eve.id, Decimal("7.10"))

        wheel_session = await game_session_repo.create(friday_bar.id, "wheel", "completed")
        sobriety_session = await game_session_repo.create(friday_bar.id, "sobriety_test", "active")
        tongue_twister_session = await game_session_repo.create(rooftop_club.id, "tongue_twister", "completed")

        await game_result_repo.create(wheel_session.id, alice.id, "winner")
        await game_result_repo.create(wheel_session.id, bob.id, "missed_shot")
        await game_result_repo.create(sobriety_session.id, charlie.id, "0.04")
        await game_result_repo.create(tongue_twister_session.id, eve.id, "clean_run")
        await game_result_repo.create(tongue_twister_session.id, grace.id, "two_stumbles")

        print("Seed completed successfully.")


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()

