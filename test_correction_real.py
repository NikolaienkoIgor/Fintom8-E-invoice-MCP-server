import httpx
import asyncio
import os

async def test_correction():
    url = "https://fintom8converter-prod.ey.r.appspot.com/backend/converter-workflowv2/"
    xml_path = "converted_invoice.xml"
    
    if not os.path.exists(xml_path):
        print(f"Error: {xml_path} not found")
        return

    xml_data = open(xml_path, "rb").read()
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        files = {
            'file': ("invoice.xml", xml_data, 'text/xml')
        }
        
        data = {
            'invoice_format': 'ubl',
            'verbose_output': 'false',
            'gemini_model': 'gemini-3-flash-preview',
            'max_iterations': '3',
            'version': 'v1'
        }
        
        print(f"Testing correction at {url}...")
        try:
            response = await client.post(
                url,
                files=files,
                data=data,
                timeout=120.0
            )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
        except Exception as e:
            print(f"Exception: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_correction())
