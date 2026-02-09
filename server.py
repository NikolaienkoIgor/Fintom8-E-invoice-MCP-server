from fastmcp import FastMCP
import httpx
import os
from pathlib import Path
import base64

# Initialize the MCP server
mcp = FastMCP("Fintom8 E-Invoicing Agent")

# Configuration
# Default to the dev environment for now, can be overridden
FINTOM_API_URL = os.getenv("FINTOM_API_URL", "https://fintom8platform-dev.ey.r.appspot.com/backend/invoice-agent")
FINTOM_CONVERTER_URL = os.getenv("FINTOM_CONVERTER_URL", "https://fintom8converter-prod.ey.r.appspot.com/backend/converter-workflowv2/")
FINTOM_API_KEY = os.getenv("FINTOM_API_KEY")

@mcp.tool()
async def convert_pdf_to_invoice(
    pdf_path: str = None,
    pdf_base64: str = None,
    invoice_format: str = "ubl",
    gemini_model: str = "gemini-3-flash-preview",
    max_iterations: int = 3,
    verbose_output: bool = False
) -> str:
    """
    Convert a PDF invoice to structured e-invoice format (UBL) using Fintom8's AI-powered converter.
    
    This tool uses advanced AI to extract invoice data from PDF files and convert them to 
    compliant UBL/Peppol format.
    
    Args:
        pdf_path: Path to the PDF file to convert (either pdf_path or pdf_base64 must be provided)
        pdf_base64: Base64-encoded PDF content (either pdf_path or pdf_base64 must be provided)
        invoice_format: Output format for the invoice (default: "ubl")
        gemini_model: The Gemini model to use for conversion (default: "gemini-3-flash-preview")
        max_iterations: Maximum number of AI iterations for refinement (default: 3)
        verbose_output: Whether to include verbose processing details (default: False)
        
    Returns:
        JSON string containing the converted invoice in UBL format and conversion metadata.
    """
    if not pdf_path and not pdf_base64:
        return "Error: Either pdf_path or pdf_base64 must be provided"
    
    try:
        # Prepare the PDF file content
        if pdf_path:
            file_path = Path(pdf_path)
            if not file_path.exists():
                return f"Error: File not found at {pdf_path}"
            pdf_content = file_path.read_bytes()
            filename = file_path.name
        else:
            # Decode base64
            import base64
            pdf_content = base64.b64decode(pdf_base64)
            filename = "invoice.pdf"
        
        async with httpx.AsyncClient() as client:
            # Prepare multipart form data
            files = {
                'file': (filename, pdf_content, 'application/pdf')
            }
            
            data = {
                'invoice_format': invoice_format,
                'verbose_output': str(verbose_output).lower(),
                'gemini_model': gemini_model,
                'max_iterations': str(max_iterations)
            }
            
            headers = {}
            if FINTOM_API_KEY:
                headers["Authorization"] = f"Bearer {FINTOM_API_KEY}"
            
            response = await client.post(
                FINTOM_CONVERTER_URL,
                files=files,
                data=data,
                headers=headers,
                timeout=120.0  # Conversion might take longer
            )
            response.raise_for_status()
            
            # Return the raw JSON response from the Fintom8 Converter API
            return response.text
            
    except httpx.HTTPStatusError as e:
        return f"Error converting PDF to invoice: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error converting PDF to invoice: {str(e)}"

@mcp.tool()
async def validate_invoice(xml_content: str) -> str:
    """
    Validate a Peppol/UBL invoice XML content against EN16931 and Peppol compliance rules.
    
    This tool proxies the validation request to the Fintom8 engine, ensuring checks 
    against the latest rules (including Peppol BIS 3.0.20).
    
    Args:
        xml_content: The raw XML string of the invoice to validate.
        
    Returns:
        JSON string containing the validation result: is_valid boolean and a list of errors/warnings.
    """
    headers = {}
    if FINTOM_API_KEY:
        headers["Authorization"] = f"Bearer {FINTOM_API_KEY}"
        # Some endpoints might prefer "X-API-KEY", but Bearer is standard. 
        # If IAP is involved, it might need "Authorization: Bearer <OIDC_TOKEN>" 
        # or "Proxy-Authorization".
        
    async with httpx.AsyncClient() as client:
        try:
            # The API expects multipart/form-data
            response = await client.post(
                FINTOM_API_URL,
                data={"xml_content": xml_content},
                headers=headers,
                timeout=60.0 # Validation might take a moment
            )
            response.raise_for_status()
            
            # Return the raw JSON response from the Fintom8 API
            return response.text
            
        except httpx.HTTPStatusError as e:
            return f"Error validating invoice: HTTP {e.response.status_code} - {e.response.text}"
        except Exception as e:
            return f"Error validating invoice: {str(e)}"

if __name__ == "__main__":
    mcp.run()
