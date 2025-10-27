Bus Management API

A FastAPI-based bus booking management system with PostgreSQL and Alembic migrations.

 Features
- User authentication (JWT)
- Role-based access control (Admin / Passenger)
- Bus and Trip management
- Booking and Wallet system
- Reports and statistics

Tech Stack
- FastAPI
- SQLAlchemy (async)
- Alembic
- PostgreSQL
- JWT

 How to Run
```bash
Create virtual environment
python -m venv .venv
.venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Apply migrations
alembic upgrade head

Run the server
uvicorn app.main:app --reload
