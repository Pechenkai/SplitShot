from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/split")
async def split_bill(amount: float):
    if not amount:
        raise HTTPException(status_code=400, detail="Amount is required")
    return {"amount": amount}