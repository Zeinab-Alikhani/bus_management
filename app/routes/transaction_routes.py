from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import AsyncSessionLocal
from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionCreate, TransactionRead
from typing import List

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=TransactionRead)
async def create_transaction(data: TransactionCreate, db: AsyncSession = Depends(get_db)):
    service = TransactionService(db)
    return await service.create_transaction(data)

@router.get("/{wallet_id}", response_model=List[TransactionRead])
async def list_transactions(wallet_id: int, db: AsyncSession = Depends(get_db)):
    service = TransactionService(db)
    return await service.list_transactions(wallet_id)
