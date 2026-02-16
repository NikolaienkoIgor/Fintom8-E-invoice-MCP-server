#!/usr/bin/env python3
import asyncio
import httpx
import json
import os
from pathlib import Path
from datetime import datetime

# URLs
CONVERTER_URL = "https://fintom8converter-prod.ey.r.appspot.com/backend/converter-workflowv2/"
VALIDATOR_URL = "https://fintom8converter-prod.ey.r.appspot.com/backend/validator-workflow/"
FINTOM_API_KEY = os.getenv("FINTOM_API_KEY")

async def test_all_tools():
    pdf_path = Path("/Users/maximdoroshenko/Desktop/fintom8-mcp-server/EN16931_Physiotherapeut.pdf")
    if not pdf_path.exists():
        print(f"❌ Файл не знайдено: {pdf_path}")
        return

    print(f"🚀 Починаємо тестування для: {pdf_path.name}")
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # 1. Тест Конвертації (convert_pdf_to_invoice)
        print("\n--- [1/3] Тестуємо Конвертацію (PDF -> XML) ---")
        start = datetime.now()
        files = {'file': (pdf_path.name, pdf_path.read_bytes(), 'application/pdf')}
        data = {} # Тепер порожній, як і в сервері
        
        headers = {}
        if FINTOM_API_KEY:
            headers["Authorization"] = f"Bearer {FINTOM_API_KEY}"
            
        try:
            resp = await client.post(CONVERTER_URL, files=files, data=data, headers=headers, timeout=300.0)
            resp.raise_for_status()
            res_json = resp.json()
            xml_content = res_json.get("xml") or res_json.get("ubl_xml")
            
            if xml_content:
                print(f"✅ Успішно! Отримано XML ({len(xml_content)} байт). Час: {datetime.now()-start}")
                temp_xml = Path("test_output.xml")
                temp_xml.write_text(xml_content)
            else:
                print("❌ Помилка: XML не знайдено у відповіді.")
                return
        except Exception as e:
            print(f"❌ Помилка конвертації: {e}")
            return

        # 2. Тест Валідації (validate_invoice_v2)
        print("\n--- [2/3] Тестуємо Валідацію (Advanced) ---")
        start = datetime.now()
        files = {'en16931_xml': ('invoice.xml', temp_xml.read_bytes(), 'text/xml')}
        data = {} # Порожній data, як ми налаштували (дефолти сервера)
        
        try:
            resp = await client.post(VALIDATOR_URL, files=files, data=data, headers=headers, timeout=300.0)
            resp.raise_for_status()
            res_json = resp.json()
            status = "VALID ✅" if res_json.get("is_valid") else "INVALID ❌"
            print(f"✅ Валідація виконана! Статус: {status}. Час: {datetime.now()-start}")
        except Exception as e:
            print(f"❌ Помилка валідації: {e}")

        # 3. Тест Корекції (correct_invoice_xml)
        print("\n--- [3/3] Тестуємо Корекцію (XML -> Improved XML) ---")
        start = datetime.now()
        files = {'file': ('invoice.xml', temp_xml.read_bytes(), 'text/xml')}
        data = {} # Тепер порожній, як і в сервері
        
        try:
            resp = await client.post(CONVERTER_URL, files=files, data=data, headers=headers, timeout=300.0)
            resp.raise_for_status()
            res_json = resp.json()
            new_xml = res_json.get("xml") or res_json.get("ubl_xml")
            if new_xml:
                print(f"✅ Корекція успішна! Отримано XML ({len(new_xml)} байт). Час: {datetime.now()-start}")
            else:
                print("❌ Помилка: Виправлений XML не знайдено.")
        except Exception as e:
            print(f"❌ Помилка корекції: {e}")

    print("\n✨ Всі тести завершені успішно з новими спрощеними параметрами!")

if __name__ == "__main__":
    asyncio.run(test_all_tools())
