import csv
import os
from pyairtable import Table
from dotenv import load_dotenv

# Load .env variables from backend directory
load_dotenv(dotenv_path="/opt/mailton/backend/.env")

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
PRODUCTS_TABLE = "Products"

# Constantes
IMAGE_BASE_URL = "http://154.38.185.250:8000/static/images/"
DEFAULT_PRICE = 180000

table = Table(API_KEY, BASE_ID, PRODUCTS_TABLE)

# 🧹 Limpiar tabla existente
print("Borrando productos existentes en Airtable...")
for record in table.all():
    table.delete(record['id'])
print("✅ Tabla limpiada")

# 📦 Cargar inventario y agrupar por model (ya que no hay product_id)
inventory = {}
with open("/opt/mailton/scripts/inventory_final_for_airtable.csv", newline="", encoding="utf-8") as inv_file:
    reader = csv.DictReader(inv_file)
    for row in reader:
        pid = row["model"]
        color = row["color"].strip()
        size = row["talla"].strip()
        stock = int(row["cantidad"])

        if pid not in inventory:
            inventory[pid] = {"color": set(), "sizes": set(), "total_stock": 0}

        inventory[pid]["color"].add(color)
        inventory[pid]["sizes"].add(size)
        inventory[pid]["total_stock"] += stock

# 🗂 Cargar productos y subir a Airtable
with open("/opt/mailton/scripts/products_final_for_airtable.csv", newline="", encoding="utf-8") as prod_file:
    reader = csv.DictReader(prod_file)
    for row in reader:
        pid = row["model"]
        name = row["name"]
        description = row.get("description", "")
        category = row.get("category", "General")
        brand = row.get("brand", "Mailton Kanazo")
        image_filename = row["image"]
        image_url = IMAGE_BASE_URL + image_filename

        inv = inventory.get(pid, {})
        colors = sorted(list(inv.get("color", [])))
        sizes = sorted(list(inv.get("sizes", [])))
        stock = inv.get("total_stock", 0)

        record = {
            "name": name,
            "description": description,
            "brand": brand,
            "category": category,
            "price_cop": DEFAULT_PRICE,
            "color": ", ".join(colors),
            "available_sizes": [str(s) for s in sizes],
            "in_stock": stock > 0,
            "image": [{"url": image_url}]
        }

        table.create(record)
        print(f"✅ Producto subido: {name}")

print("Inventario cargado completamente a Airtable.")
