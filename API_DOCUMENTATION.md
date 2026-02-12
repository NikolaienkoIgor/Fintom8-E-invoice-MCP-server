# API Documentation: e-invoice-mcp

This document provides detailed information about the tools provided by the Fintom8 E-Invoicing MCP Server.

## 🛠 Available Tools

### 1. `convert_pdf_to_invoice`
Converts a PDF invoice to a structured UBL/Peppol XML format.

*   **Endpoint**: `https://fintom8converter-prod.ey.r.appspot.com/backend/converter-workflowv2/`
*   **Parameters**:
    *   `pdf_path` (string): Absolute path to the local PDF file.
    *   `pdf_base64` (string): Alternatively, send the file as a base64 string.
    *   `invoice_format` (default: `"ubl"`): The target e-invoice format.
    *   `gemini_model` (default: `"gemini-3-flash-preview"`): The model used for extraction.
    *   `max_iterations` (default: `3`): Number of AI passes to refine the result.
    *   `version` (default: `"v1"`): Workflow version.

### 2. `validate_invoice_v2`
Validates an XML invoice against EN16931 and Peppol compliance rules.

*   **Endpoint**: `https://fintom8converter-prod.ey.r.appspot.com/backend/validator-workflow/`
*   **Parameters**:
    *   `xml_path` (string): Path to the XML file.
    *   `xml_content` (string): Raw XML content.
    *   `include_comparison` (boolean, default: `false`): Compare with original if applicable.
    *   `include_explanation` (boolean, default: `false`): Provide AI explanations for errors.

### 3. `correct_invoice_xml`
Uses AI to automatically fix errors in an existing XML invoice.

*   **Endpoint**: `https://fintom8converter-prod.ey.r.appspot.com/backend/converter-workflowv2/`
*   **Parameters**:
    *   `xml_path` (string): Path to the XML file that needs fixing.
    *   `xml_content` (string): Raw XML content.
    *   `max_iterations` (default: `3`): AI refinement cycles.

---

## 🚦 Error Handling
The server returns descriptive error messages in case of failure:
*   **422 Unprocessable Entity**: Usually means a required field (like `file`) is missing or the format is invalid.
*   **ReadTimeout**: The operation took longer than 300 seconds. (Fixed in v0.1.6).
*   **307 Redirect**: Automatically handled by the client.

## 🔗 Production Endpoints
All tools now point to the production environment:
`https://fintom8converter-prod.ey.r.appspot.com/backend/`

---
*For business inquiries or custom integrations, visit [fintom8.com](https://fintom8.com)*
