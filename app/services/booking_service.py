import logging
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from app.models.booking import Booking, BookingStatus
from app.models.transaction import TransactionType
from app.models.trip import Trip
from app.repositories.booking_repository import BookingRepository
from app.repositories.wallet_repository import WalletRepository
from app.repositories.transaction_repository import TransactionRepository

logger = logging.getLogger(__name__)

class BookingService:
    def __init__(self, db):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.wallet_repo = WalletRepository(db)
        self.transaction_repo = TransactionRepository(db)

    async def create_booking(self, data, current_user):
        logger.info(f"🎫 Starting booking for user={current_user.id}, trip={data.trip_id}")

        # بررسی صندلی
        existing = await self.booking_repo.get_booking_by_trip_and_seat(data.trip_id, data.seat_number)
        if existing:
            raise HTTPException(status_code=400, detail="Seat already booked for this trip")

        # بررسی کیف پول
        wallet = await self.wallet_repo.get_wallet_by_user_id(current_user.id)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found for this user")

        # بررسی سفر و قیمت
        trip = await self.db.get(Trip, data.trip_id)
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        if wallet.balance < trip.price:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")

        # ایجاد رزرو
        booking = Booking(
            user_id=current_user.id,
            trip_id=data.trip_id,
            seat_number=data.seat_number,
            status=BookingStatus.confirmed,
            total_price=trip.price,
        )

        # کم کردن از کیف پول
        wallet.balance -= trip.price

        # ثبت تراکنش
        await self.transaction_repo.create_transaction(
            wallet_id=wallet.id,
            amount=-trip.price,
            transaction_type=TransactionType.payment,
            description=f"Booking trip #{trip.id}, seat {data.seat_number}"
        )

        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        await self.db.refresh(wallet)

        logger.info(f"✅ Booking completed: trip={data.trip_id}, seat={data.seat_number}")

        return {
            "message": "Booking successful",
            "booking_id": booking.id,
            "remaining_balance": float(wallet.balance),
        }

    async def get_booking(self, booking_id: int):
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        return booking

    async def cancel_booking(self, booking_id: int):
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.status == BookingStatus.cancelled:
            raise HTTPException(status_code=400, detail="Booking already cancelled")

        wallet = await self.wallet_repo.get_wallet_by_user_id(booking.user_id)
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found")

        # بازپرداخت
        wallet.balance += booking.total_price
        booking.status = BookingStatus.cancelled

        await self.transaction_repo.create_transaction(
            wallet_id=wallet.id,
            amount=booking.total_price,
            transaction_type=TransactionType.refund,
            description=f"Refund for booking #{booking.id}"
        )

        await self.db.commit()
        await self.db.refresh(wallet)
        await self.db.refresh(booking)

        return {"message": "Booking cancelled and refund processed successfully"}

    async def get_bookings_by_user(self, user_id: int):
        result = await self.db.execute(select(Booking).where(Booking.user_id == user_id))
        return result.scalars().all()


 