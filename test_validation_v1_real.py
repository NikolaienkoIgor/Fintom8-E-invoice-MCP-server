import httpx
import asyncio
import os
import json

async def test_validate_invoice_v1():
    # URL який зараз прописаний в коді сервера для validate_invoice
    url = "https://fintom8converter-prod.ey.r.appspot.com/backend/invoice-agent/" 
    xml_path = "converted_invoice.xml"
    
    if not os.path.exists(xml_path):
        # Якщо немає converted_invoice, спробуємо знайти будь-який інший або створити простий
        print(f"File {xml_path} not found.")
        return

    xml_data = open(xml_path, "rb").read()
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        files = {
            'file': ("invoice.xml", xml_data, 'text/xml')
        }
        
        data = {
            'version': 'v1'
        }
        
        print(f"Testing validate_invoice (v1) at {url}...")
        try:
            response = await client.post(
                url,
                files=files,
                data=data,
                timeout=120.0
            )
            print(f"Status: {response.status_code}")
            
            # Спробуємо розпарсити JSON
            try:
                json_response = response.json()
                print(json.dumps(json_response, indent=2))
            except:
                print(f"Response text: {response.text[:500]}...")
                
        except Exception as e:
            print(f"Exception: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_validate_invoice_v1())
