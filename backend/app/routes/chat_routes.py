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

    result = await openai_service.chat_with_agent(message, products, customer_email)

    # Manejar tanto string como dict
    if isinstance(result, str):
        response_text = result
        logger.info(f"🤖 Respuesta generada por IA: {response_text}")
    elif isinstance(result, dict):
        response_text = result.get("response", "")
        logger.info(f"🤖 Respuesta generada por IA: {response_text}")
        
        # Log adicional del análisis
        if result.get("products_mentioned"):
            logger.info(f"🛍️ Productos detectados: {result.get('products_mentioned')}")
        if result.get("colors_mentioned"):
            logger.info(f"🎨 Colores detectados: {result.get('colors_mentioned')}")
        if result.get("sizes_mentioned"):
            logger.info(f"📏 Tallas detectadas: {result.get('sizes_mentioned')}")
        logger.info(f"🎯 Intención: {result.get('intent')} (confianza: {result.get('confidence', 0):.2f})")
    else:
        response_text = "Error en procesamiento"
        logger.error(f"❌ Tipo de resultado no esperado: {type(result)}")

    # Registrar interacción
    try:
        airtable_service.register_interaction(customer_email, message, result)
    except Exception as e:
        logger.error(f"❌ Error registrando interacción: {e}")
        # Continuar con la respuesta aunque falle el registro

    return {
        "reply": result
    }