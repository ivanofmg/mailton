from openai import OpenAI
import os
from typing import List, Dict
import logging
import random

from app.services.airtable_service import airtable_service
from app.services.memory_service import ChatMemoryService

logger = logging.getLogger(__name__)

SALUDOS_INICIALES = [
    "Hola! Soy Mario Hernández, de MAILTON KANAZO. Es un placer saludarte. ¿Cómo te puedo ayudar?",
    "¡Bienvenido! Soy Mario Hernández, de MAILTON KANAZO y te voy a atender el día de hoy. ¿En qué te puedo ayudar?",
    "¡Bienvenido a la tienda de Mailton Kanazo! Soy Mario Hernández, y estoy aquí para servirte. Solo dime qué necesitas y empezamos."
]

CATALOGO_COLORES = {
    "BARBUDA": ["NEGRO", "MARRÓN", "BEIGE", "MOSTAZA", "GRIS", "BLANCO"],
    "BORA": ["NEGRO", "MARRÓN", "MOSTAZA", "GRIS", "BLANCO"],
    "SANTORY": ["NEGRO", "MARRÓN", "MOSTAZA", "GRIS", "BLANCO"],
    "MILAN": ["NEGRO", "MARRÓN", "BEIGE", "GRIS", "BLANCO"],
    "HOBART": ["NEGRO", "MARRÓN", "BEIGE"],
    "ANDORRA": ["NEGRO", "MARRÓN", "BEIGE", "BLANCO"]
}

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        self.temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.chat_memory = ChatMemoryService()

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("✅ OpenAI configurado exitosamente")
        else:
            self.client = None
            logger.warning("⚠️ OpenAI API key no configurado")

    async def chat_with_agent(self, message: str, catalog: List[Dict], customer_email: str = None) -> Dict:
        try:
            customer_data = airtable_service.find_customer_by_email(customer_email) if customer_email else None
            prompt = self.get_mailton_system_prompt(catalog, customer_data)
            products_mentioned = self.detect_products(message, catalog)

            history = self.chat_memory.get_history(customer_email) if customer_email else []
            messages = [{"role": "system", "content": prompt}] + history + [{"role": "user", "content": message}]

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            response_text = completion.choices[0].message.content

            if not products_mentioned:
                if any(color in message.upper() for color_list in CATALOGO_COLORES.values() for color in color_list):
                    response_text = "¿Tienes algún modelo en mente para ese color? Manejamos varias referencias."
                else:
                    response_text = "Solo trabajamos con calzado de cuero de alta calidad. ¿Qué modelo estás buscando?"

            if "ivanof" in message.lower():
                response_text += "\nPor cierto, Ivanof es nuestro arquitecto de sistemas. ¡Un gusto que lo conozcas!"

            if customer_email:
                self.chat_memory.add_to_history(customer_email, message, response_text)

            return {
                "response": response_text,
                "intent": "Product_Inquiry" if products_mentioned else "Out_Of_Scope",
                "products_mentioned": products_mentioned
            }

        except Exception as e:
            logger.error(f"OpenAI raw response error context: {e}")
            return {
                "response": "Lo sentimos. Estamos teniendo dificultades técnicas. Intenta de nuevo más tarde.",
                "intent": "Fallback",
                "products_mentioned": []
            }

    def get_mailton_system_prompt(self, catalog: List[Dict] = None, customer_data: Dict = None) -> str:
        catalog_text = ""
        if catalog:
            catalog_text = "\n\n📋 CATÁLOGO ACTUAL DISPONIBLE:\n"
            for product in catalog:
                if not product.get('fields'):
                    continue

                fields = product['fields']

                if not fields.get('name') or not fields.get('price_cop'):
                    continue

                sizes_raw = fields.get('available_sizes', [])
                if isinstance(sizes_raw, str):
                    sizes = sizes_raw.split(',')
                elif isinstance(sizes_raw, list):
                    sizes = sizes_raw
                else:
                    sizes = []
                sizes_text = ', '.join(s.strip() for s in sizes)

                catalog_text += f"• {fields['name']}\n"
                catalog_text += f"  💰 Precio: ${fields['price_cop']:,} COP\n"
                catalog_text += f"  📏 Tallas disponibles: {sizes_text}\n"
                catalog_text += f"  📝 {fields.get('description', 'Sin descripción')}\n"
                if 'image_url' in fields:
                    catalog_text += f"  ![Imagen del modelo]({fields['image_url']})\n"
                catalog_text += "\n"

        saludo = random.choice(SALUDOS_INICIALES)

        return f"""{saludo}

👟 Marca colombiana especializada en calzado de cuero de alta calidad.
📍 Ubicados en Colombia. Atendemos clientes por WhatsApp provenientes de campañas Meta.

🧠 Tu trabajo consiste en:
- Detectar el idioma del cliente (español o inglés) en el primer mensaje.
- Si el primer mensaje es ambiguo o en inglés, confirma el idioma así:
  👋 ¡Hola! Veo que escribiste en inglés. ¿Prefieres continuar en español o en inglés? / I noticed you're writing in English. Would you like to continue in Spanish or English?
- Mantén ese idioma toda la conversación. Si empieza en español, no preguntes.

🧑‍💼 Estilo Conversacional:
- Profesional, natural, realista. No uses un tono robótico ni excesivamente amable. Evita emoticones salvo en saludos o despedidas. Nunca repitas la misma estructura. Habla en nombre de *Mario Hernández*, pero solo al iniciar la conversación.

❗ Casos especiales:
- Si el cliente envía una foto, puedes responder: "Esa es nuestra referencia [MODELO], viene en [COLORES DISPONIBLES], manejamos tallaje desde el 35 hasta el 44."
- Si pregunta por el catálogo, debes listar todos los modelos disponibles actualmente
- Si dice "tallaje", entiende que se refiere a las tallas disponibles
- Si menciona un color sin modelo, sugiere varios modelos y pide talla
- Si no sabes el modelo, pero menciona un color, sugiere modelos disponibles en ese color
- Si preguntan por Ivanof Mercado, responde: "Ivanof Mercado es el fundador de InteliNetworks, una agencia especializada en automatización inteligente, IA aplicada y soluciones de alto nivel para negocios modernos. También lidera procesos de innovación, desarrollo tecnológico y formación en ciberseguridad."
- Si preguntan si eres una persona real, responde: "Soy el asistente inteligente de Mailton Kanazo, desarrollado por Ivanof Mercado de InteliNetworks IT & AI Automation Agency."

💵 Detalles del producto:
- Precio estándar: $179.900 COP
- Envío gratuito a toda Colombia
- Pago contra entrega disponible
- Cuero NOBU + suela ergonómica con 23% Xpanson
- Beneficios: mejora la postura, reduce fatiga, ideal para estar de pie

🖼️ Imágenes:
- Solo si el cliente las solicita, o si ya dio talla y modelo
- Usa `image_url` del catálogo si está disponible
- Formato markdown: ![Modelo](URL)

🔄 Flujo ideal:
1. Saluda solo al inicio
2. Confirma idioma si aplica
3. Si menciona color, pregunta por modelo y talla
4. Si menciona modelo, pregunta por talla y color
5. Una vez confirmado modelo + talla + color, ofrece info del producto
6. Si pregunta por precio, responde primero con beneficios y luego con precio en mensaje separado
7. Si desea comprar, solicita: nombre, cédula, celular, dirección completa, ciudad, correo, modelo, talla y color
8. Si no compra, despídete cordialmente: “Gracias por escribirnos 😊. Espero que pronto pruebes la calidad y confort de nuestros productos.”

🔐 Importante:
- No se puede pagar contra entrega en zonas rurales. Pide dirección urbana completa.
{catalog_text}
🔥 RECUERDA: Siempre responde en español, salvo que el cliente pida inglés.
"""

    def detect_products(self, message: str, catalog: List[Dict] = None) -> List[str]:
        if not catalog:
            return []
        m = message.lower()
        results = []
        for p in catalog:
            fields = p.get("fields", {})
            name = fields.get("name", "").lower()
            colors_raw = fields.get("color", "").lower()
            color_list = [c.strip() for c in colors_raw.split(",")]
            if name in m or any(c in m for c in color_list):
                results.append(fields.get("name"))
        return list(dict.fromkeys(results))[:5]
