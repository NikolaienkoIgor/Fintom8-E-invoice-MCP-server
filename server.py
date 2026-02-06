from fastmcp import FastMCP
import httpx
import os

# Initialize the MCP server
mcp = FastMCP("Fintom8 E-Invoicing Agent")

# Configuration
# Default to the dev environment for now, can be overridden
FINTOM_API_URL = os.getenv("FINTOM_API_URL", "https://fintom8platform-dev.ey.r.appspot.com/backend/validate-schematron/")

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
    async with httpx.AsyncClient() as client:
        try:
            # The API expects multipart/form-data
            response = await client.post(
                FINTOM_API_URL,
                data={"xml_content": xml_content},
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
