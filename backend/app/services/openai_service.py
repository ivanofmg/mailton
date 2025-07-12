from openai import OpenAI
import os
from typing import List, Dict
import logging
import random
from collections import defaultdict
import re

from app.services.airtable_service import airtable_service
from app.services.memory_service import ChatMemoryService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SALUDOS_INICIALES = [
    "Hola! Soy Mario Hernández, Asesor Comercial del canal de ventas online de MAILTON KANAZO. Es un placer saludarte. ¿Cómo te puedo ayudar?",
    "¡Bienvenido! Soy Mario Hernández, Asesor Comercial de MAILTON KANAZO y te voy a atender el día de hoy. ¿En qué te puedo ayudar?",
    "¡Bienvenido a la tienda de Mailton Kanazo! Soy Mario Hernández, Asesor Comercial del canal online, y estoy aquí para servirte. Solo dime qué necesitas y empezamos."
]

CATALOGO_COLORES = {
    "ANDORRA": ["NEGRO", "MARRON", "BEIGE", "BLANCO"],
    "BARBUDA": ["NEGRO", "MARRON", "BEIGE", "MOSTAZA", "GRIS", "BLANCO", "AZUL"],
    "BORA": ["NEGRO", "MARRON", "MOSTAZA", "GRIS", "BLANCO"],
    "HOBART": ["NEGRO", "MARRON", "BEIGE"],
    "MILAN": ["NEGRO", "MARRON", "BEIGE", "GRIS", "BLANCO"],
    "SANTORY": ["NEGRO", "MARRON", "MOSTAZA", "GRIS", "BLANCO"]
}

IMAGENES_MODELOS = {
    "ANDORRA": "https://i.imgur.com/S9ctWUN.png",
    "BARBUDA": "https://i.imgur.com/vnBqZoq.png",
    "BORA": "https://i.imgur.com/odVNk55.png",
    "HOBART": "https://i.imgur.com/whDv56s.png",
    "MILAN": "https://i.imgur.com/4rmEV98.png",
    "SANTORY": "https://i.imgur.com/Sdg0JZU.png"
}

TALLAS_DISPONIBLES = ["35", "36", "37", "38", "39", "40", "41", "42", "43", "44"]

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

    def get_mailton_system_prompt(self, catalog: List[Dict] = None, customer_data: Dict = None) -> str:
        try:
            saludo = random.choice(SALUDOS_INICIALES)

            catalog_text = ""
            
            # TEMPORAL: Usar siempre el catálogo hardcodeado hasta que arreglemos Airtable
            logger.info("📦 Usando catálogo hardcodeado temporalmente")
            for modelo, colores in CATALOGO_COLORES.items():
                imagen_url = IMAGENES_MODELOS.get(modelo, "")
                catalog_text += f"- {modelo}: {', '.join(colores)}\n"
                if imagen_url:
                    catalog_text += f"  Imagen: {imagen_url}\n"
            
            logger.info(f"📝 Catálogo generado:\n{catalog_text}")

            return f"""{saludo}

👟 Marca colombiana especializada en calzado de cuero de alta calidad.
📍 Ubicados en Colombia. Atendemos clientes por WhatsApp provenientes de campañas Meta.

🧠 Tu trabajo consiste en:
- Detectar el idioma del cliente (español o inglés) en el primer mensaje.
- Si el primer mensaje es ambiguo o en inglés, confirma el idioma así:
  👋 ¡Hola! Veo que escribiste en inglés. ¿Prefieres continuar en español o en inglés? / I noticed you're writing in English. Would you like to continue in Spanish or English?
- Mantén ese idioma toda la conversación. Si empieza en español, no preguntes.

🧑‍💼 Estilo Conversacional:
- Profesional, natural, realista. No uses un tono robótico ni excesivamente amable. Evita emoticones salvo en saludos o despedidas. Nunca repitas la misma estructura. 
- IMPORTANTE: Siempre te identificas como Mario Hernández, Asesor Comercial del canal de ventas online de Mailton Kanazo
- Eres un asistente virtual, pero te presentas como Mario Hernández directamente
- Mantienes la personalidad de un asesor comercial experimentado y confiable

❗ Casos especiales:
- Si el cliente envía una foto, puedes responder: "Esa es nuestra referencia [MODELO], viene en [COLORES DISPONIBLES], manejamos tallaje desde el 35 hasta el 44."
- Si pregunta por el catálogo o por modelos disponibles, debes listar TODOS los modelos disponibles con sus colores
- Si pregunta por modelos en un color específico (ej: "modelos en azul"), lista SOLO los modelos que tienen ese color disponible
- Si dice "tallaje", entiende que se refiere a las tallas disponibles
- Si menciona un color sin modelo, sugiere varios modelos específicos que tengan ese color y pide talla
- Si no sabes el modelo, pero menciona un color, sugiere modelos disponibles en ese color CON NOMBRES ESPECÍFICOS
- Si solicita ver una imagen o hace un pedido final, SIEMPRE muestra la imagen del modelo usando el formato: ![Modelo NOMBRE](URL)
- **Si la dirección es zona rural:** "Como es zona rural, te ofrezco enviarlo a la oficina de la transportadora de tu elección más cercana (Servientrega, Inter Rapidísimo, Coordinadora, TCC, Envía, etc.). El pago contra entrega sigue disponible para recoger en la oficina. ¿Cuál transportadora prefieres y cuál es la oficina más cercana a ti?"
- Si preguntan por Ivanof Mercado, responde: "Ivanof Mercado es el Arquitecto de la solución de Agentes Inteligentes para diversos sectores económicos. Puedes contactarlo a info@intelinetworks.com"
- Si preguntan quién eres, tu nombre, o si eres una persona real, responde con variaciones como:
  "Soy Mario Hernández, Asesor Comercial del canal de ventas online de Mailton Kanazo. De hecho soy su asistente virtual y puedo ayudarte en todo lo que necesites. Si hay algo que quieras hablar personalmente conmigo y yo no lo puedo resolver, solo dime y te pongo en línea enseguida. Mientras tanto, siéntete confiado en que te puedo guiar en todo el proceso hasta el final. Solo pruébame."
  O variaciones creativas pero SIEMPRE identificándote como Mario Hernández, Asesor Comercial.
- Si preguntan por Mario Hernández, responde: "Ese soy yo. Soy Mario Hernández, Asesor Comercial a cargo del canal de ventas online de Mailton Kanazo."
- Si preguntan quién desarrolló o implementó este sistema, explica: "Esta solución fue desarrollada por InteliNetworks IT & AI Automation (intelinetworks.com). Se especializan en automatizaciones basadas en IA para diversos sectores como Retail, Ventas Online, Centros Educativos, Clínicas, etc. ¿En qué sector trabajas? Podrían hacer una evaluación sin costo para tu negocio."
- Si mencionan algún sector específico o muestran interés, pregunta más detalles y sugiere que contacten a info@intelinetworks.com para una evaluación gratuita.

🎯 IMPORTANTE - Cuando pregunten por modelos en un color específico:
Ejemplo: "modelos en azul" → Responde: "En azul tenemos disponible: BARBUDA. ¿Qué talla necesitas?"
Ejemplo: "modelos en negro" → Responde: "En negro tenemos: ANDORRA, BARBUDA, BORA, HOBART, MILAN, SANTORY. ¿Cuál te interesa y en qué talla?"

🎯 IMPORTANTE - Manejo de precios:
NUNCA des el precio directamente. Cuando pregunten por precio, SIEMPRE sigue este flujo:
1. Reconoce la pregunta con frases como "Claro que sí" o "Por supuesto"
2. Explica las bondades del producto primero (sé creativo pero menciona los beneficios clave)
3. Luego da el precio en mensaje separado o al final
Ejemplos de respuestas sobre precio:
- "Claro que sí. Antes quiero que sepas que nuestros zapatos están elaborados en 100% cuero legítimo NOBU, con una suela ergonómica que garantiza durabilidad, comodidad y salud."
- "Por supuesto! El sistema ergonómico de nuestras suelas ayuda a la correcta postura de la columna, previene varices y dolores lumbares. Es ideal para personas que duran largas jornadas de pie."
💳 IMPORTANTE - Opciones de pago:
Cuando pregunten por opciones de pago o crédito, SIEMPRE menciona TODAS las opciones:
"Tenemos varios métodos de pago disponibles: pagos contra entrega, crédito con ADDI, crédito con Wompi, y pagos de contado. ¿Cuál prefieres?"

💵 Detalles del producto:
- Precio estándar: $179.900 COP (NUNCA menciones el precio sin explicar primero las bondades)
- Envío gratuito a toda Colombia
- Cuero NOBU 100% legítimo + suela ergonómica inyectada en PU lineal con 23% Xpanson
- Beneficios: mejora la postura de la columna, previene varices, reduce dolores lumbares y cansancio, ideal para largas jornadas de pie
- Garantiza: durabilidad, comodidad y salud

💳 Métodos de pago disponibles:
- Pagos contra entrega
- Crédito con ADDI
- Crédito con Wompi  
- Pagos de contado

🖼️ Imágenes:
- Cuando confirmes modelo, talla y color, o cuando el cliente solicite ver una imagen, envía SOLO la URL directa de la imagen
- NO uses formato markdown ![Modelo NOMBRE](URL)
- Envía la imagen así: "Aquí tienes el modelo BARBUDA: https://i.imgur.com/vnBqZoq.png"
- SIEMPRE muestra la imagen cuando el cliente haga el pedido final o solicite ver el producto

🔄 Flujo ideal:
1. Saluda solo al inicio
2. Confirma idioma si aplica
3. Si menciona color, pregunta por modelo y talla
4. Si menciona modelo, pregunta por talla y color
5. Una vez confirmado modelo + talla + color, ofrece info del producto
6. **IMPORTANTE - Si pregunta por precio:** NUNCA des el precio directamente. SIEMPRE explica primero las bondades del producto usando una de estas variaciones:
   - "Claro que sí. Antes quiero que sepas que nuestros zapatos están elaborados en 100% cuero legítimo NOBU, con una suela ergonómica inyectada en PU lineal con 23% de Xpanson, para garantizar durabilidad, comodidad y salud."
   - "Por supuesto! Antes quiero que conozcas los beneficios de la suela ergonómica: El sistema ergonómico de nuestras suelas te ayuda a la correcta postura de la columna y es útil para personas que caminan mucho o duran largas jornadas de pie. Su estructura ayuda a prevenir problemas de varices, dolores lumbares y cansancio."
   - Sé creativo con las palabras pero SIEMPRE resalta los beneficios antes del precio.
   - Luego, en mensaje separado, da el precio: "El precio es de $179.900 COP"
7. Si pregunta por opciones de pago, menciona TODOS los métodos disponibles: contra entrega, crédito con ADDI, crédito con Wompi, y pagos de contado
8. Si desea comprar, solicita: nombre, cédula, celular, dirección completa, ciudad, correo, modelo, talla y color. **Si es zona rural, ofrece envío a oficina de transportadora.**
9. Si no compra, despídete cordialmente: "Gracias por escribirnos 😊. Espero que pronto pruebes la calidad y confort de nuestros productos."

🔐 Importante:
- Si la dirección de envío es una zona rural, ofrece la opción de recoger en la oficina de la transportadora de su elección más cercana, ya que no podemos llegar directamente a esas zonas
- El pago contra entrega sigue disponible para la recolección en la oficina de la transportadora
- El cliente debe nombrar la oficina de su transportadora de confianza o la más cercana
- Ejemplos de transportadoras: Servientrega, Inter Rapidísimo, Coordinadora, TCC, Envía
- El pedido se despachará a través de esa compañía hacia su oficina más cercana

💼 IMPORTANTE - Identificación y Lead Generation:
- Mantén un tono natural y conversacional
- Si el cliente menciona que tiene un negocio o trabaja en algún sector específico, muestra interés genuino
- Pregunta sutilmente sobre su sector: "¿En qué sector trabajas?" o "¿Qué tipo de negocio tienes?"
- Si es Retail/Ventas: "InteliNetworks tiene soluciones específicas para ventas online y por catálogo"
- Si es Educación: "Tienen automatizaciones especiales para centros educativos"  
- Si es Salud: "Desarrollan sistemas para clínicas, consultorios médicos, odontológicos, estética"
- Si muestra interés: "Podrían hacer una evaluación gratuita de tu negocio. ¿Te gustaría que te contacten?"

🧾 Modelos disponibles:
{catalog_text}

🔥 RECUERDA: 
- Siempre responde en español, salvo que el cliente pida inglés
- CUANDO MENCIONEN UN COLOR ESPECÍFICO, LISTA LOS MODELOS POR NOMBRE
- Sé natural al identificar oportunidades de negocio para InteliNetworks
- No fuerces la conversación hacia InteliNetworks, hazlo de forma orgánica
"""
        except Exception as e:
            logger.error(f"❌ Error generando prompt: {e}")
            return f"{saludo}\n\n¿En qué puedo ayudarte hoy?"

    def _detect_products_mentioned(self, message: str, response: str) -> List[str]:
        """Detecta productos mencionados en el mensaje y respuesta"""
        try:
            products = []
            message_upper = message.upper() if message else ""
            response_upper = response.upper() if response else ""
            
            # Buscar modelos en CATALOGO_COLORES
            for modelo in CATALOGO_COLORES.keys():
                if modelo in message_upper or modelo in response_upper:
                    products.append(modelo)
            
            # Buscar variaciones comunes de nombres
            variaciones = {
                "BARBUDA": ["BARBUDAS"],
                "ANDORRA": ["ANDORRAS"],
                "BORA": ["BORAS"],
                "HOBART": ["HOBARTS"],
                "MILAN": ["MILANS", "MILÁN"],
                "SANTORY": ["SANTORYS", "SANTORI"]
            }
            
            for modelo, vars in variaciones.items():
                for var in vars:
                    if var in message_upper or var in response_upper:
                        if modelo not in products:
                            products.append(modelo)
            
            return products
        except Exception as e:
            logger.warning(f"⚠️ Error detectando productos: {e}")
            return []

    def _detect_intent(self, message: str) -> str:
        """Detecta la intención del mensaje"""
        try:
            if not message:
                return "general_inquiry"
                
            message_lower = message.lower()
            
            # Palabras clave para diferentes intenciones
            price_keywords = ['precio', 'costo', 'valor', 'cuanto', 'cuánto', 'vale', 'costar']
            purchase_keywords = ['comprar', 'quiero', 'necesito', 'pedido', 'orden', 'llevar', 'adquirir']
            product_keywords = ['color', 'talla', 'modelo', 'disponible', 'catalogo', 'catálogo', 'referencia']
            greeting_keywords = ['hola', 'buenas', 'saludos', 'buenos días', 'buenas tardes', 'buenas noches']
            shipping_keywords = ['envío', 'envio', 'entrega', 'delivery', 'despacho', 'domicilio']
            payment_keywords = ['pago', 'contra entrega', 'efectivo', 'tarjeta', 'transferencia']
            
            # Análisis de intención
            if any(word in message_lower for word in price_keywords):
                return "price_inquiry"
            elif any(word in message_lower for word in purchase_keywords):
                return "purchase_intent"
            elif any(word in message_lower for word in product_keywords):
                return "product_inquiry"
            elif any(word in message_lower for word in greeting_keywords):
                return "greeting"
            elif any(word in message_lower for word in shipping_keywords):
                return "shipping_inquiry"
            elif any(word in message_lower for word in payment_keywords):
                return "payment_inquiry"
            else:
                return "general_inquiry"
        except Exception as e:
            logger.warning(f"⚠️ Error detectando intención: {e}")
            return "general_inquiry"

    def _detect_colors_mentioned(self, message: str, response: str) -> List[str]:
        """Detecta colores mencionados en el mensaje y respuesta"""
        try:
            colors = []
            all_colors = ["NEGRO", "MARRON", "BEIGE", "MOSTAZA", "GRIS", "BLANCO", "AZUL"]
            
            text = ((message or "") + " " + (response or "")).upper()
            
            for color in all_colors:
                if color in text:
                    colors.append(color)
            
            # Variaciones de colores
            color_variations = {
                "NEGRO": ["NEGRO", "BLACK"],
                "MARRON": ["MARRÓN", "CAFÉ", "BROWN"],
                "AZUL": ["BLUE"],
                "BLANCO": ["WHITE"],
                "GRIS": ["GRAY", "GREY"]
            }
            
            for color, variations in color_variations.items():
                for variation in variations:
                    if variation in text and color not in colors:
                        colors.append(color)
            
            return colors
        except Exception as e:
            logger.warning(f"⚠️ Error detectando colores: {e}")
            return []

    def _detect_sizes_mentioned(self, message: str, response: str) -> List[str]:
        """Detecta tallas mencionadas en el mensaje y respuesta"""
        try:
            sizes = []
            text = (message or "") + " " + (response or "")
            
            # Buscar números que correspondan a tallas
            for size in TALLAS_DISPONIBLES:
                if re.search(r'\b' + size + r'\b', text):
                    sizes.append(size)
            
            return sizes
        except Exception as e:
            logger.warning(f"⚠️ Error detectando tallas: {e}")
            return []

    def _get_product_image_url(self, model_name: str) -> str:
        """Obtiene la URL de imagen para un modelo específico"""
        try:
            model_upper = model_name.upper()
            return IMAGENES_MODELOS.get(model_upper, "")
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo imagen para {model_name}: {e}")
            return ""

    def _calculate_confidence(self, message: str, intent: str, products: List[str]) -> float:
        """Calcula un score de confianza basado en el análisis"""
        try:
            confidence = 0.5  # Base
            
            # Aumentar confianza si hay productos específicos
            if products:
                confidence += 0.3
            
            # Aumentar confianza basada en intención
            intent_confidence = {
                "greeting": 0.9,
                "price_inquiry": 0.8,
                "purchase_intent": 0.9,
                "product_inquiry": 0.7,
                "shipping_inquiry": 0.8,
                "payment_inquiry": 0.8,
                "general_inquiry": 0.5,
                "error": 0.1
            }
            
            confidence = min(1.0, confidence + intent_confidence.get(intent, 0.5) - 0.5)
            
            return round(confidence, 2)
        except Exception as e:
            logger.warning(f"⚠️ Error calculando confianza: {e}")
            return 0.5

    async def chat_with_agent(self, message: str, catalog: List[Dict], customer_email: str) -> Dict:
        if not self.client:
            logger.error("❌ OpenAI client no está configurado.")
            return {
                "response": "Lo sentimos. Estamos teniendo dificultades técnicas. Intenta de nuevo más tarde.",
                "products_mentioned": [],
                "colors_mentioned": [],
                "sizes_mentioned": [],
                "intent": "error",
                "confidence": 0.0
            }

        try:
            logger.info(f"📥 Iniciando procesamiento para: {customer_email}")
            
            # Generar prompt de forma segura
            prompt = self.get_mailton_system_prompt(catalog)
            logger.info(f"📝 Prompt generado exitosamente")
            
            # Obtener memoria de forma segura
            try:
                memory = self.chat_memory.get_memory(customer_email)
            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo memoria: {e}")
                memory = []
            
            messages = [{"role": "system", "content": prompt}]

            # Si hay historial previo, se agrega
            if memory:
                messages.extend(memory)

            # Agrega el mensaje actual del usuario
            messages.append({"role": "user", "content": message})

            logger.info(f"📥 Mensaje recibido: {message}")

            # Llamada a OpenAI
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            response = completion.choices[0].message.content.strip()
            logger.info(f"🤖 Respuesta generada por IA: {response}")

            # Actualiza memoria de forma segura
            try:
                self.chat_memory.update_memory(customer_email, {"role": "user", "content": message})
                self.chat_memory.update_memory(customer_email, {"role": "assistant", "content": response})
                logger.info(f"💾 Memoria actualizada exitosamente")
            except Exception as e:
                logger.warning(f"⚠️ Error actualizando memoria: {e}")

            # Análisis inteligente del contenido
            products_mentioned = self._detect_products_mentioned(message, response)
            colors_mentioned = self._detect_colors_mentioned(message, response)
            sizes_mentioned = self._detect_sizes_mentioned(message, response)
            intent = self._detect_intent(message)
            confidence = self._calculate_confidence(message, intent, products_mentioned)

            # Log de análisis
            logger.info(f"🔍 Productos detectados: {products_mentioned}")
            logger.info(f"🎨 Colores detectados: {colors_mentioned}")
            logger.info(f"📏 Tallas detectadas: {sizes_mentioned}")
            logger.info(f"🎯 Intención detectada: {intent} (confianza: {confidence:.2f})")

            return {
                "response": response,
                "products_mentioned": products_mentioned,
                "colors_mentioned": colors_mentioned,
                "sizes_mentioned": sizes_mentioned,
                "intent": intent,
                "confidence": confidence
            }

        except Exception as e:
            logger.error(f"❌ Error durante chat_with_agent: {e}")
            logger.error(f"❌ Error details: {str(e)}")
            return {
                "response": "Lo sentimos. Estamos teniendo dificultades técnicas. Intenta de nuevo más tarde.",
                "products_mentioned": [],
                "colors_mentioned": [],
                "sizes_mentioned": [],
                "intent": "error",
                "confidence": 0.0
            }