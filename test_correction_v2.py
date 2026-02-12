import asyncio
import httpx
import os
from pathlib import Path

async def test_correction_v2():
    # Use the production URL as defined in server.py
    url = "https://fintom8converter-prod.ey.r.appspot.com/backend/converter-workflowv2/"
    xml_path = "converted_invoice.xml"
    
    if not os.path.exists(xml_path):
        print(f"File {xml_path} not found.")
        return

    with open(xml_path, "rb") as f:
        xml_data = f.read()
        
    print(f"Correcting {xml_path}...")
    
    async with httpx.AsyncClient() as client:
        files = {
            'file': ('invoice.xml', xml_data, 'text/xml')
        }
        
        data = {
            'invoice_format': 'ubl',
            'verbose_output': 'false',
            'gemini_model': 'gemini-3-flash-preview',
            'max_iterations': '2', # Lower iterations for faster test
            'version': 'v1'
        }
        
        headers = {}
        api_key = os.getenv("FINTOM_API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            
        try:
            response = await client.post(
                url,
                files=files,
                data=data,
                headers=headers,
                timeout=120.0
            )
            print(f"Status: {response.status_code}")
            print("Response Snapshot (first 500 chars):")
            print(response.text[:500])
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_correction_v2())
