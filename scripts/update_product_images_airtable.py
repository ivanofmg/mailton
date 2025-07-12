import os
from pyairtable import Table
from dotenv import load_dotenv

load_dotenv(dotenv_path="/opt/mailton/backend/.env")

API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = "Products"

IMAGE_URLS = {
    "ANDORRA": "https://drive.google.com/uc?export=view&id=1OXHBUBhJ0xKzW2HrSGSAInEoKhHB7j26",
    "BARBUDA": "https://drive.google.com/uc?export=view&id=1fr0YF_7oojFfkjrXVZjAPhMYhE_zKbd1",
    "BORA":    "https://drive.google.com/uc?export=view&id=1UgaOaDGcoHjYs5vtLZSEeZFZZOC3TL7P",
    "HOBART":  "https://drive.google.com/uc?export=view&id=149-RnL46jZrLoM1jwssO0IM5jv_BLHzE",
    "MILAN":   "https://drive.google.com/uc?export=view&id=1yzs5CBuY5UXJ0j5_jBIOyEFIYXvATggA",
    "SANTORI": "https://drive.google.com/uc?export=view&id=1yp5tnju5g9tN92Mlq2ri1bcNmnOiSuRR"
}

def normalize(text):
    return str(text or "").strip().upper()

def update_image_urls():
    table = Table(API_KEY, BASE_ID, TABLE_NAME)
    records = table.all()
    updated = 0

    for record in records:
        fields = record.get("fields", {})
        record_id = record.get("id")
        model = normalize(fields.get("model"))
        current_url = fields.get("image_url")

        if model in IMAGE_URLS:
            new_url = IMAGE_URLS[model]
            if current_url != new_url:
                table.update(record_id, {"image_url": new_url})
                print(f"✅ {model} actualizado con: {new_url}")
                updated += 1
            else:
                print(f"🟡 {model} ya estaba actualizado.")
        else:
            print(f"🔴 Modelo no encontrado en lista: {model}")

    print(f"\n🎯 Total productos actualizados: {updated}")

if __name__ == "__main__":
    update_image_urls()
