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

@mcp.tool()
async def convert_pdf_to_invoice(
    pdf_path: str = None,
    pdf_base64: str = None,
    invoice_format: str = "ubl",
    gemini_model: str = "gemini-3-flash-preview",
    max_iterations: int = 3,
    version: str = "v1",
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
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Prepare multipart form data
            files = {
                'file': (filename, pdf_content, 'application/pdf')
            }
            
            data = {
                'invoice_format': invoice_format,
                'verbose_output': str(verbose_output).lower(),
                'gemini_model': gemini_model,
                'max_iterations': str(max_iterations),
                'version': version
            }
            
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
            
            # Return the raw JSON response from the Fintom8 Converter API
            return response.text
            
    except httpx.HTTPStatusError as e:
        return f"Error converting PDF to invoice: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error converting PDF to invoice: {type(e).__name__}: {str(e)}"

@mcp.tool()
async def validate_invoice(
    xml_content: str = None,
    xml_path: str = None,
    version: str = "v1"
) -> str:
    """
    Validate a Peppol/UBL invoice XML against EN16931 and Peppol compliance rules.
    
    Args:
        xml_content: The raw XML string of the invoice (either xml_content or xml_path must be provided)
        xml_path: Path to the XML file to validate (either xml_content or xml_path must be provided)
        version: Workflow version to use (default: "v1")
        
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
            data = {
                'version': version
            }
            
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
        return f"Error validating invoice: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error validating invoice: {type(e).__name__}: {str(e)}"

@mcp.tool()
async def validate_invoice_v2(
    xml_content: str = None,
    xml_path: str = None,
    include_comparison: bool = False,
    include_explanation: bool = False
) -> str:
    """
    Validate an EN16931 XML invoice using Fintom8's validator workflow.
    
    Args:
        xml_content: The raw XML content of the invoice (either xml_content or xml_path must be provided)
        xml_path: Path to the XML file to validate (either xml_content or xml_path must be provided)
        include_comparison: Whether to include comparison in the validation result (default: False)
        include_explanation: Whether to include explanations in the validation result (default: False)
        
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
            
            data = {
                'include_comparison': str(include_comparison).lower(),
                'include_explanation': str(include_explanation).lower()
            }
            
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
        return f"Error in validation workflow: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error in validation workflow: {type(e).__name__}: {str(e)}"

@mcp.tool()
async def correct_invoice_xml(
    xml_content: str = None,
    xml_path: str = None,
    invoice_format: str = "ubl",
    gemini_model: str = "gemini-3-flash-preview",
    max_iterations: int = 3,
    version: str = "v1",
    verbose_output: bool = False
) -> str:
    """
    Correct or refine an XML invoice using Fintom8's AI-powered converter workflow.
    
    This tool takes an existing XML invoice and applies AI-driven corrections to ensure 
    compliance and accuracy.
    
    Args:
        xml_content: The raw XML content of the invoice (either xml_content or xml_path must be provided)
        xml_path: Path to the XML file to correct (either xml_content or xml_path must be provided)
        invoice_format: Output format for the invoice (default: "ubl")
        gemini_model: The Gemini model to use for correction (default: "gemini-3-flash-preview")
        max_iterations: Maximum number of AI iterations for refinement (default: 3)
        version: Workflow version to use (default: "v1")
        verbose_output: Whether to include verbose processing details (default: False)
        
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
            
            data = {
                'invoice_format': invoice_format,
                'verbose_output': str(verbose_output).lower(),
                'gemini_model': gemini_model,
                'max_iterations': str(max_iterations),
                'version': version
            }
            
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
            
            return response.text
            
    except httpx.HTTPStatusError as e:
        return f"Error in correction workflow: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error in correction workflow: {type(e).__name__}: {str(e)}"

def main():
    mcp.run()

if __name__ == "__main__":
    main()
