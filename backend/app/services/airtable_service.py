import os
from pyairtable import Table
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AirtableService:
    def __init__(self):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID")
        self.products_table = "Products"
        self.customers_table = "Customers"
        self.interactions_table = "Interactions"

        self.products = Table(self.api_key, self.base_id, self.products_table)
        self.customers = Table(self.api_key, self.base_id, self.customers_table)
        self.interactions = Table(self.api_key, self.base_id, self.interactions_table)

        logger.info("✅ Airtable conectado exitosamente")

    def get_all_products(self):
        return self.products.all()
        
    def has_prior_interaction(self, email: str) -> bool:
        records = self.interactions.all(formula=f"{{email}} = '{email}'")
        return len(records) > 0    
    
    def find_customer_by_email(self, email):
        if not email:
            return None
        try:
            records = self.customers.all(formula=f"{{email}} = '{email}'")
            return records[0]['fields'] if records else None
        except Exception as e:
            print(f"Error buscando cliente: {e}")
            return None
    
    def update_customer(self, email: str):
        existing = self.customers.first(formula=f"{{email}} = '{email}'")
        if existing:
            self.customers.update(existing["id"], {
                "last_interaction": datetime.now().isoformat()
            })
            logger.info(f"✅ Cliente actualizado: {email} ({existing['fields'].get('interactions_count', 0) + 1} interacciones)")
            return existing["id"]
        else:
            created = self.customers.create({
                "email": email,
                #"first_seen": datetime.now().isoformat()
            })
            logger.info(f"🆕 Cliente nuevo registrado: {email}")
            return created["id"]

    def register_interaction(self, email: str, message: str, result):
        customer_id = self.update_customer(email)
        
        # Manejar tanto string como diccionario (backward compatibility)
        if isinstance(result, str):
            # Si result es un string, crear estructura básica
            interaction_data = {
                "customer_email": email,
                "customer_message": message,
                "ai_response": result,
                "products_mentioned": "",
                "intent": "general_inquiry",
                "timestamp": datetime.now().isoformat(),
                "channel": "WhatsApp"
            }
        elif isinstance(result, dict):
            # Si result es un diccionario, usar solo los campos que EXISTEN en Airtable
            # Crear un resumen enriquecido en products_mentioned
            products = result.get("products_mentioned", [])
            colors = result.get("colors_mentioned", [])
            sizes = result.get("sizes_mentioned", [])
            
            # Combinar toda la información en products_mentioned
            enriched_products = []
            if products:
                enriched_products.extend(products)
            if colors:
                enriched_products.extend([f"Color: {color}" for color in colors])
            if sizes:
                enriched_products.extend([f"Talla: {size}" for size in sizes])
            
            interaction_data = {
                "customer_email": email,
                "customer_message": message,
                "ai_response": result.get("response", ""),
                "products_mentioned": ", ".join(enriched_products),
                "intent": result.get("intent", "general_inquiry"),
                "timestamp": datetime.now().isoformat(),
                "channel": "WhatsApp"
            }
        else:
            # Caso de error: tipo no esperado
            logger.error(f"❌ Tipo de resultado no esperado: {type(result)}")
            interaction_data = {
                "customer_email": email,
                "customer_message": message,
                "ai_response": "Error en procesamiento",
                "products_mentioned": "",
                "intent": "error",
                "timestamp": datetime.now().isoformat(),
                "channel": "WhatsApp"
            }
        
        self.interactions.create(interaction_data)
        
        # Log mejorado con información del análisis
        if isinstance(result, dict):
            logger.info(f"✅ Interacción registrada: {email}")
            logger.info(f"📊 Análisis: Intent={result.get('intent', 'N/A')}, "
                       f"Productos={len(result.get('products_mentioned', []))}, "
                       f"Colores={len(result.get('colors_mentioned', []))}, "
                       f"Tallas={len(result.get('sizes_mentioned', []))}, "
                       f"Confianza={result.get('confidence', 0):.2f}")
        else:
            logger.info(f"✅ Interacción registrada: {email}")

airtable_service = AirtableService()