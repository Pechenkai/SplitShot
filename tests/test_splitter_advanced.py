from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.splitter import (
    calculate_detailed_split,
    calculate_quick_split,
    format_debt_message,
    save_company_debts,
)
from app.repositories import DebtRepository


class TestQuickSplit:   
    def test_quick_split_two_participants(self):
        debts = calculate_quick_split(
            total_amount=Decimal("100.00"),
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2],
            payer_id=1,
        )
        
        assert len(debts) == 1
        assert debts[0].debtor_id == 2
        assert debts[0].creditor_id == 1
        assert debts[0].amount == Decimal("50.00")
    
    def test_quick_split_payer_owes_nothing(self):
        debts = calculate_quick_split(
            total_amount=Decimal("100.00"),
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2, 3],
            payer_id=1,
        )
        
        assert all(debt.debtor_id != 1 for debt in debts)
    
    def test_quick_split_with_zero_total(self):
        debts = calculate_quick_split(
            total_amount=Decimal("0.00"),
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2],
            payer_id=1,
        )
        
        if debts:
            assert len(debts) == 1
            assert debts[0].amount == Decimal("0.00")
        else:
            assert debts == []
    
    def test_quick_split_with_tips_only(self):
        debts = calculate_quick_split(
            total_amount=Decimal("0.00"),
            tips_amount=Decimal("100.00"),
            participant_ids=[1, 2],
            payer_id=1,
        )
        
        assert len(debts) == 1
        assert debts[0].amount == Decimal("50.00")
    
    def test_quick_split_many_participants(self):
        debts = calculate_quick_split(
            total_amount=Decimal("1000.00"),
            tips_amount=Decimal("0.00"),
            participant_ids=list(range(1, 11)), 
            payer_id=1,
        )
        
        assert len(debts) == 9
        assert all(debt.amount == Decimal("100.00") for debt in debts)
    
    def test_quick_split_rounding_with_remainder(self):
        debts = calculate_quick_split(
            total_amount=Decimal("100.00"),
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2, 3, 4],
            payer_id=1,
        )
        
        assert all(debt.amount == Decimal("25.00") for debt in debts)


class TestDetailedSplit:   
    def test_detailed_split_single_item_multiple_participants(self):
        debts = calculate_detailed_split(
            items=[(Decimal("120.00"), [1, 2, 3])],
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2, 3],
            payer_id=3,
        )
        
        assert len(debts) == 2
        assert all(debt.amount == Decimal("40.00") for debt in debts)
        assert all(debt.creditor_id == 3 for debt in debts)
    
    def test_detailed_split_item_assigned_to_payer_only(self):
        debts = calculate_detailed_split(
            items=[(Decimal("100.00"), [1])],
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2],
            payer_id=1,
        )
        
        assert debts == []
    
    def test_detailed_split_complex_items(self):
        debts = calculate_detailed_split(
            items=[
                (Decimal("100.00"), [1, 2]),
                (Decimal("60.00"), [2]),
                (Decimal("40.00"), [3]),
            ],
            tips_amount=Decimal("20.00"),
            participant_ids=[1, 2, 3],
            payer_id=1,
        )
        
        debt_2 = next(d for d in debts if d.debtor_id == 2)
        debt_3 = next(d for d in debts if d.debtor_id == 3)
        
        assert debt_2.creditor_id == 1
        assert debt_3.creditor_id == 1
        assert debt_2.amount in [Decimal("121.00"), Decimal("120.99")]
        assert debt_3.amount in [Decimal("44.00"), Decimal("44.01")]
    
    def test_detailed_split_no_items_with_tips(self):
        debts = calculate_detailed_split(
            items=[],
            tips_amount=Decimal("50.00"),
            participant_ids=[1, 2, 3],
            payer_id=1,
        )
        
        assert debts == []
    
    def test_detailed_split_zero_price_item(self):
        debts = calculate_detailed_split(
            items=[(Decimal("0.00"), [1, 2])],
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2],
            payer_id=1,
        )
        
        assert debts == []
    
    def test_detailed_split_with_custom_rounding(self):
        debts = calculate_detailed_split(
            items=[(Decimal("10.00"), [1, 2, 3])],
            tips_amount=Decimal("0.00"),
            participant_ids=[1, 2, 3],
            payer_id=1,
        )
        
        assert len(debts) == 2
        assert all(debt.amount in [Decimal("3.33"), Decimal("3.34")] for debt in debts)


class TestDebtMessage:  
    def test_format_debt_message_with_names(self):
        from collections import namedtuple
        DebtMock = namedtuple('Debt', ['debtor_id', 'creditor_id', 'amount'])
        
        debts = [
            DebtMock(1, 2, Decimal("50.00")),
            DebtMock(3, 2, Decimal("30.00")),
        ]
        names = {1: "Alice", 2: "Bob", 3: "Charlie"}
        
        message = format_debt_message(debts, names)
        
        assert "Alice -> Bob: 50.00 ₽" in message
        assert "Charlie -> Bob: 30.00 ₽" in message
    
    def test_format_debt_message_without_names(self):
        from collections import namedtuple
        DebtMock = namedtuple('Debt', ['debtor_id', 'creditor_id', 'amount'])
        
        debts = [DebtMock(1, 2, Decimal("50.00"))]
        
        message = format_debt_message(debts)
        
        assert "Участник #1 -> Участник #2: 50.00 ₽" in message
    
    def test_format_debt_message_no_debts(self):
        message = format_debt_message([])
        
        assert "Долгов нет" in message


class TestSaveDebts:    
    @pytest.mark.asyncio
    async def test_save_company_debts_replaces_existing(self, db_session, seeded_company, seeded_participants):
        from app.services.splitter import CalculatedDebt
        
        debt_repo = DebtRepository(db_session)
        debts = [
            CalculatedDebt(debtor_id=seeded_participants[0].id, creditor_id=seeded_participants[1].id, amount=Decimal("10.00")),
            CalculatedDebt(debtor_id=seeded_participants[2].id, creditor_id=seeded_participants[1].id, amount=Decimal("20.00")),
        ]
        
        saved = await save_company_debts(debt_repo, seeded_company.id, debts)
        
        assert len(saved) == 2
        assert saved[0].amount == Decimal("10.00")
        assert saved[1].amount == Decimal("20.00")
    
    @pytest.mark.asyncio
    async def test_save_company_debts_clears_old(self, db_session, seeded_company, seeded_participants):
        from app.services.splitter import CalculatedDebt
        
        debt_repo = DebtRepository(db_session)
        
        old_debt = await debt_repo.create(seeded_company.id, seeded_participants[0].id, seeded_participants[1].id, Decimal("100.00"))
        
        new_debts = [
            CalculatedDebt(debtor_id=seeded_participants[2].id, creditor_id=seeded_participants[3].id, amount=Decimal("30.00")),
        ]
        
        await save_company_debts(debt_repo, seeded_company.id, new_debts)
        
        old = await debt_repo.get_by_id(old_debt.id)
        assert old is None
        
        all_debts = await debt_repo.list_by_company(seeded_company.id)
        assert len(all_debts) == 1
        assert all_debts[0].amount == Decimal("30.00")