from fastapi import APIRouter, Request
from app.services.openai_service import OpenAIService
from app.services.airtable_service import airtable_service
import logging

openai_service = OpenAIService()
logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "")
    customer_email = data.get("customer_email", "")

    logger.info(f"📨 Mensaje recibido del cliente {customer_email}: {message}")

    # Obtener productos directamente desde el servicio
    try:
        products = airtable_service.get_all_products()
    except Exception as e:
        logger.warning(f"⚠️ Error obteniendo productos: {e}")
        products = []

    logger.info(f"📨 Mensaje recibido del cliente {customer_email}: {message}")
    result = await openai_service.chat_with_agent(message, products, customer_email)

    logger.info(f"🤖 Respuesta generada por IA: {result}")

    airtable_service.register_interaction(customer_email, message, result)

    return {
    "reply": result
    }