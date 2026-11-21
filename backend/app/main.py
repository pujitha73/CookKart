"""CookKart backend application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.cart import router as cart_router
from app.api.catalog import router as catalog_router
from app.api.kitchen import router as kitchen_router
from app.api.orders import router as orders_router
from app.api.recipes import router as recipes_router
from app.core.config import settings

app = FastAPI(title="CookKart API", version="0.1.0")

origins = [o.strip() for o in settings.backend_cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog_router, prefix="/api")
app.include_router(recipes_router, prefix="/api")
app.include_router(kitchen_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(orders_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}

