from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
load_dotenv()
import os
print("✅ OPENAI_API_KEY from .env:", os.getenv("OPENAI_API_KEY"))

from app.routes.chat_routes import router as chat_router
from app.routes.catalog_routes import router as catalog_router

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="InteliNetworks - Mailton Kanazo API", version="1.0")

# CORS Middleware (modo desarrollo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(catalog_router, prefix="/catalog", tags=["Catálogo"])

# Endpoint de salud
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "intelinetworks-backend"}
