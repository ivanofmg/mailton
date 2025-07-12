from fastapi import APIRouter
from app.services.airtable_service import airtable_service

router = APIRouter()

@router.get("/debug")
def debug_catalog():
    try:
        products = airtable_service.get_all_products()
        return {
            "total_products": len(products),
            "products": products[:5],  # Solo los primeros 5 para ver estructura
            "all_product_names": [p.get("fields", {}).get("name", "NO NAME") for p in products]
        }
    except Exception as e:
        return {"error": str(e)}