import asyncio
import httpx
import os
from pathlib import Path

# Mocking the call that the MCP tool would make
async def test_validation_v2():
    url = "https://fintom8platform-dev.ey.r.appspot.com/backend/validator-workflow/"
    xml_path = "converted_invoice.xml"
    
    if not os.path.exists(xml_path):
        print(f"File {xml_path} not found. Please run the converter test first or provide an XML.")
        return

    with open(xml_path, "rb") as f:
        xml_data = f.read()
        
    print(f"Validating {xml_path}...")
    
    async with httpx.AsyncClient() as client:
        files = {
            'en16931_xml': ('converted_invoice.xml', xml_data, 'text/xml')
        }
        
        data = {
            'include_comparison': 'false',
            'include_explanation': 'false'
        }
        
        # Add API Key if available
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
                timeout=60.0
            )
            print(f"Status: {response.status_code}")
            print("Response:")
            print(response.text)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_validation_v2())
