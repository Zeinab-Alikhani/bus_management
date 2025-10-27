from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
import logging
from app.core.db import init_db
from app.routes import (
    auth_routes, user_routes, trip_routes, bus_routes,
    booking_routes, admin_trip_routes, admin_bus_routes,
    wallet_routes, transaction_routes
)
from app.routes import report_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bus Management System 🚍",
    description="Bus Management API with JWT Authentication",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

# ✅ ساخت openapi اختصاصی برای نمایش باکس JWT
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Bus Management System 🚍",
        version="1.0.0",
        description="Bus Management API with JWT Authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Paste your JWT token here (e.g. Bearer eyJhbGci...)"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ✅ روترها
app.include_router(auth_routes.router, prefix="/api", tags=["Authentication"])
app.include_router(user_routes.router, prefix="/api/users", tags=["Users"])
app.include_router(trip_routes.router, prefix="/api", tags=["Trips"])
app.include_router(bus_routes.router, prefix="/api", tags=["Buses"])
app.include_router(booking_routes.router, prefix="/api", tags=["Bookings"])
app.include_router(admin_trip_routes.router, prefix="/api")
app.include_router(admin_bus_routes.router)
app.include_router(wallet_routes.router)
app.include_router(transaction_routes.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(report_routes.router)

@app.on_event("startup")
async def on_startup():
    print("🚀 App starting without DB check")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
