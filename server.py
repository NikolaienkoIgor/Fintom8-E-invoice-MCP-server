from fastmcp import FastMCP
import httpx
import os
from pathlib import Path
import base64

# Initialize the MCP server
mcp = FastMCP("Fintom8 E-Invoicing Agent")

# Configuration
# Using production environment by default
FINTOM_API_URL = os.getenv("FINTOM_API_URL", "https://fintom8converter-prod.ey.r.appspot.com/backend/invoice-agent/")
FINTOM_CONVERTER_URL = os.getenv("FINTOM_CONVERTER_URL", "https://fintom8converter-prod.ey.r.appspot.com/backend/converter-workflowv2/")
FINTOM_VALIDATOR_URL = os.getenv("FINTOM_VALIDATOR_URL", "https://fintom8converter-prod.ey.r.appspot.com/backend/validator-workflow/")
FINTOM_API_KEY = os.getenv("FINTOM_API_KEY")

AUTH_REQUIRED_MESSAGE = """
⚠️ Authentication Required

An API Key is required to use Fintom8 services. 

How to get access:
1. Visit our contact form: https://fintom8.com/#contact
2. Submit a request using the template below.

---
MESSAGE TEMPLATE FOR CONTACT FORM:
Subject: MCP API Key Request
Message: "Hi Fintom8 Team, I would like to request an API key for the Fintom8 E-Invoice Agent. My organization name is [Your Organization Name]."
---
"""

@mcp.tool()
async def convert_invoice(
    file_path: str = None
) -> str:
    """
    Generate compliant e-invoices from any format, including PDF, XML, JSON, and CSV.
    
    This tool uses advanced AI to extract invoice data from various formats and convert them to 
    compliant UBL/Peppol format.
    
    Args:
        file_path: Path to the file to convert (PDF, XML, JSON, or CSV)
        
    Returns:
        JSON string containing the converted invoice in UBL format and conversion metadata.
    """
    if not file_path:
        return "Error: file_path must be provided"
    
    try:
        # Prepare the file content
        if file_path:
            path_obj = Path(file_path)
            if not path_obj.exists():
                return f"Error: File not found at {file_path}"
            file_content = path_obj.read_bytes()
            filename = path_obj.name
            
            # Determine MIME type based on extension
            ext = path_obj.suffix.lower()
            mime_type = 'application/octet-stream'
            if ext == '.pdf':
                mime_type = 'application/pdf'
            elif ext == '.xml':
                mime_type = 'text/xml'
            elif ext == '.json':
                mime_type = 'application/json'
            elif ext == '.csv':
                mime_type = 'text/csv'
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Prepare multipart form data
            files = {
                'file': (filename, file_content, mime_type)
            }
            
            data = {}
            
            headers = {}
            if FINTOM_API_KEY:
                headers["Authorization"] = f"Bearer {FINTOM_API_KEY}"
            
            response = await client.post(
                FINTOM_CONVERTER_URL,
                files=files,
                data=data,
                headers=headers,
                timeout=300.0  # Conversion might take longer (up to 5 mins)
            )
            response.raise_for_status()
            
            # Return a cleaned JSON with only XML and validation summary
            try:
                resp_json = response.json()
                clean_result = {
                    "xml": resp_json.get("xml") or resp_json.get("ubl_xml"),
                    "validation_summary": resp_json.get("validation_summary")
                }
                import json
                return json.dumps(clean_result, indent=2, ensure_ascii=False)
            except:
                return response.text
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return AUTH_REQUIRED_MESSAGE
        return f"Error converting invoice: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error converting PDF to invoice: {type(e).__name__}: {str(e)}"

@mcp.tool()
async def validate_invoice(
    xml_content: str = None,
    xml_path: str = None
) -> str:
    """
    Validate a Peppol/UBL invoice XML against EN16931 and Peppol compliance rules.
    
    Args:
        xml_content: The raw XML string of the invoice (either xml_content or xml_path must be provided)
        xml_path: Path to the XML file to validate (either xml_content or xml_path must be provided)
        
    Returns:
        JSON string containing the validation result.
    """
    if not xml_content and not xml_path:
        return "Error: Either xml_content or xml_path must be provided"

    try:
        if xml_path:
            file_path = Path(xml_path)
            if not file_path.exists():
                return f"Error: File not found at {xml_path}"
            xml_data = file_path.read_bytes()
            filename = file_path.name
        else:
            xml_data = xml_content.encode('utf-8')
            filename = "invoice.xml"

        headers = {}
        if FINTOM_API_KEY:
            headers["Authorization"] = f"Bearer {FINTOM_API_KEY}"
            
        async with httpx.AsyncClient(follow_redirects=True) as client:
            files = {
                'file': (filename, xml_data, 'text/xml')
            }
            data = {}
            
            response = await client.post(
                FINTOM_API_URL,
                files=files,
                data=data,
                headers=headers,
                timeout=300.0
            )
            response.raise_for_status()
            return response.text
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return AUTH_REQUIRED_MESSAGE
        return f"Error validating invoice: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error validating invoice: {type(e).__name__}: {str(e)}"

@mcp.tool()
async def validate_invoice_v2(
    xml_content: str = None,
    xml_path: str = None
) -> str:
    """
    Validate an EN16931 XML invoice using Fintom8's validator workflow.
    
    Args:
        xml_content: The raw XML content of the invoice (either xml_content or xml_path must be provided)
        xml_path: Path to the XML file to validate (either xml_content or xml_path must be provided)
        
    Returns:
        JSON string containing the validation results.
    """
    if not xml_content and not xml_path:
        return "Error: Either xml_content or xml_path must be provided"
    
    try:
        if xml_path:
            file_path = Path(xml_path)
            if not file_path.exists():
                return f"Error: File not found at {xml_path}"
            xml_data = file_path.read_bytes()
            filename = file_path.name
        else:
            xml_data = xml_content.encode('utf-8')
            filename = "invoice.xml"
            
        async with httpx.AsyncClient(follow_redirects=True) as client:
            files = {
                'en16931_xml': (filename, xml_data, 'text/xml')
            }
            
            data = {}
            
            headers = {}
            if FINTOM_API_KEY:
                headers["Authorization"] = f"Bearer {FINTOM_API_KEY}"
                
            response = await client.post(
                FINTOM_VALIDATOR_URL,
                files=files,
                data=data,
                headers=headers,
                timeout=300.0
            )
            response.raise_for_status()
            
            return response.text
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return AUTH_REQUIRED_MESSAGE
        return f"Error in validation workflow: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error in validation workflow: {type(e).__name__}: {str(e)}"

@mcp.tool()
async def correct_invoice_xml(
    xml_content: str = None,
    xml_path: str = None
) -> str:
    """
    Correct or refine an XML invoice using Fintom8's AI-powered converter workflow.
    
    This tool takes an existing XML invoice and applies AI-driven corrections to ensure 
    compliance and accuracy.
    
    Args:
        xml_content: The raw XML content of the invoice (either xml_content or xml_path must be provided)
        xml_path: Path to the XML file to correct (either xml_content or xml_path must be provided)
        
    Returns:
        JSON string containing the corrected invoice and processing metadata.
    """
    if not xml_content and not xml_path:
        return "Error: Either xml_content or xml_path must be provided"
    
    try:
        if xml_path:
            file_path = Path(xml_path)
            if not file_path.exists():
                return f"Error: File not found at {xml_path}"
            xml_data = file_path.read_bytes()
            filename = file_path.name
        else:
            xml_data = xml_content.encode('utf-8')
            filename = "invoice.xml"
            
        async with httpx.AsyncClient(follow_redirects=True) as client:
            files = {
                'file': (filename, xml_data, 'text/xml')
            }
            
            data = {}
            
            headers = {}
            if FINTOM_API_KEY:
                headers["Authorization"] = f"Bearer {FINTOM_API_KEY}"
            
            response = await client.post(
                FINTOM_CONVERTER_URL, # Using the same converter URL as it supports XML correction
                files=files,
                data=data,
                headers=headers,
                timeout=300.0
            )
            response.raise_for_status()
            
            # Return a cleaned JSON with only XML and validation summary
            try:
                resp_json = response.json()
                clean_result = {
                    "xml": resp_json.get("xml") or resp_json.get("ubl_xml"),
                    "validation_summary": resp_json.get("validation_summary")
                }
                import json
                return json.dumps(clean_result, indent=2, ensure_ascii=False)
            except:
                return response.text
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return AUTH_REQUIRED_MESSAGE
        return f"Error in correction workflow: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error in correction workflow: {type(e).__name__}: {str(e)}"

def main():
    mcp.run()

if __name__ == "__main__":
    main()
