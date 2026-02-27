from fastmcp import FastMCP
import httpx
import os
from pathlib import Path


mcp = FastMCP("Fintom8 E-Invoicing Agent")

# Configuration
# Using production environment by default
FINTOM_CONVERTER_URL = os.getenv("FINTOM_CONVERTER_URL",
                                 "https://fintom8converter-prod.ey.r.appspot.com/backend/converter-workflowv2/")
FINTOM_VALIDATOR_URL = os.getenv("FINTOM_VALIDATOR_URL",
                                 "https://fintom8converter-prod.ey.r.appspot.com/backend/validator-workflow/")
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
        pdf_content: str = None,
        iterations: int = 1
) -> str:
    """
    Generate compliant e-invoices from PDF text content using the converter workflow.

    Sends the given PDF text (e.g. extracted or visualisation text) to the backend
    to produce compliant UBL/Peppol format.

    Args:
        pdf_content: The PDF content as string (e.g. text extracted from PDF or visualisation).
        iterations: Maximum number of conversion iterations (default 1).

    Returns:
        JSON string containing the converted invoice in UBL format and conversion metadata.
    """
    return await _convert_invoice_impl(pdf_content, iterations)


async def _convert_invoice_impl(pdf_content: str = None, iterations: int = 1) -> str:
    """Shared implementation for convert_invoice (MCP tool and REST API)."""
    if not pdf_content or not pdf_content.strip():
        return "Error: pdf_content must be provided (non-empty string)"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            data = {
                "invoice_format": "ubl",
                "verbose_output": "false",
                "gemini_model": "gemini-3-flash-preview",
                "max_iterations": str(iterations),
                "version": "v1",
                "pdf_content": pdf_content.strip(),
            }
            headers = {}
            if FINTOM_API_KEY:
                headers["Authorization"] = f"Bearer {FINTOM_API_KEY}"

            response = await client.post(
                FINTOM_CONVERTER_URL,
                data=data,
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()

            try:
                resp_json = response.json()
                clean_result = {
                    "xml": resp_json.get("xml") or resp_json.get("ubl_xml"),
                    "validation_summary": resp_json.get("validation_summary"),
                }
                import json
                return json.dumps(clean_result, indent=2, ensure_ascii=False)
            except Exception as e:
                return response.text

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return AUTH_REQUIRED_MESSAGE
        return f"Error converting invoice: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error converting invoice: {type(e).__name__}: {str(e)}"


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
    return await _validate_invoice_impl(xml_content=xml_content, xml_path=xml_path)


async def _validate_invoice_impl(xml_content: str = None, xml_path: str = None) -> str:
    """Shared implementation for validate_invoice (MCP tool and REST API)."""
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

        async with httpx.AsyncClient(timeout=30) as client:
            files = {
                'en16931_xml': (filename, xml_data, 'text/xml')
            }
            data = {}

            response = await client.post(
                FINTOM_VALIDATOR_URL,
                files=files,
                data=data,
                headers=headers,
                timeout=30,
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
    return await _validate_invoice_v2_impl(xml_content=xml_content, xml_path=xml_path)


async def _validate_invoice_v2_impl(xml_content: str = None, xml_path: str = None) -> str:
    """Shared implementation for validate_invoice_v2 (MCP tool and REST API)."""
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

        async with httpx.AsyncClient(timeout=30) as client:
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
                timeout=30,
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
    return await _correct_invoice_xml_impl(xml_content=xml_content, xml_path=xml_path)


async def _correct_invoice_xml_impl(xml_content: str = None, xml_path: str = None) -> str:
    """Shared implementation for correct_invoice_xml (MCP tool and REST API)."""
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

        async with httpx.AsyncClient(timeout=30) as client:
            files = {
                'file': (filename, xml_data, 'text/xml')
            }

            data = {}

            headers = {}
            if FINTOM_API_KEY:
                headers["Authorization"] = f"Bearer {FINTOM_API_KEY}"

            response = await client.post(
                FINTOM_CONVERTER_URL,  # Using the same converter URL as it supports XML correction
                files=files,
                data=data,
                headers=headers,
                timeout=30,
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
            except Exception:
                return response.text

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return AUTH_REQUIRED_MESSAGE
        return f"Error in correction workflow: HTTP {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error in correction workflow: {type(e).__name__}: {str(e)}"


# ASGI app for App Engine / uvicorn (production HTTP)
# Compose MCP (session-based at /mcp) with stateless REST API (single-curl at /api/*)
mcp_app = mcp.http_app(path="/")

from fastapi import FastAPI, HTTPException, Body
from typing import Optional

try:
    from fastmcp.utilities.lifespan import combine_lifespans
    _lifespan = combine_lifespans(mcp_app.lifespan)
except Exception:
    _lifespan = mcp_app.lifespan

app = FastAPI(title="Fintom8 E-Invoice MCP", lifespan=_lifespan)
app.mount("/mcp", mcp_app)


# ----- Stateless REST API: single curl, no session ID -----

@app.post("/api/validate_invoice")
async def api_validate_invoice(
    xml_content: Optional[str] = Body(None),
    xml_path: Optional[str] = Body(None),
):
    """Validate UBL/Peppol XML. POST JSON: {"xml_content": "<Invoice>...</Invoice>"}"""
    result = await _validate_invoice_impl(xml_content=xml_content, xml_path=xml_path)
    return {"result": result}


@app.post("/api/validate_invoice_v2")
async def api_validate_invoice_v2(
    xml_content: Optional[str] = Body(None),
    xml_path: Optional[str] = Body(None),
):
    """Advanced validation. POST JSON: {"xml_content": "<Invoice>...</Invoice>"}"""
    result = await _validate_invoice_v2_impl(xml_content=xml_content, xml_path=xml_path)
    return {"result": result}


@app.post("/api/correct_invoice_xml")
async def api_correct_invoice_xml(
    xml_content: Optional[str] = Body(None),
    xml_path: Optional[str] = Body(None),
):
    """Correct invalid XML. POST JSON: {"xml_content": "<Invoice>...</Invoice>"}"""
    result = await _correct_invoice_xml_impl(xml_content=xml_content, xml_path=xml_path)
    return {"result": result}


@app.post("/api/convert_invoice")
async def api_convert_invoice(
    pdf_content: Optional[str] = Body(
        None,
        embed=True
    ),
    iterations: Optional[int] = Body(1, embed=True),
):
    """Convert PDF text content to UBL. POST JSON: {"pdf_content": "Visualisierung eRechnung\\n...", "iterations": 1}"""
    result = await _convert_invoice_impl(pdf_content=pdf_content, iterations=iterations or 1)
    return {"result": result}


def main():
    transport = (os.getenv("MCP_TRANSPORT") or "").strip().lower()
    port = int(os.getenv("PORT", "8080"))
    if transport == "http" or os.getenv("K_SERVICE"):
        # HTTP transport for cloud (Cloud Run sets K_SERVICE and PORT)
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        # Default: stdio for local/Claude Desktop
        mcp.run()


if __name__ == "__main__":
    # main()
    import uvicorn
    uvicorn.run(app="main:app", host="0.0.0.0", port=8080, reload=True)