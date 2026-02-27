# Fintom8 E-Invoicing Agent (MCP)

[![PyPI version](https://img.shields.io/pypi/v/e-invoice-mcp.svg)](https://pypi.org/project/e-invoice-mcp/)
[![MCP Certified](https://img.shields.io/badge/MCP-Certified-blue)](https://mcpmarket.com)
[![Peppol Ready](https://img.shields.io/badge/Peppol-3.0.20-green)](https://fintom8.com)

**The official Model Context Protocol (MCP) server for Fintom8.**

This server acts as an intelligent bridge to the AI-driven Fintom8 E-Invoice Platform. It enables autonomous agents to validate, audit, and correct e-invoices against the latest European standards (EN16931) and Peppol regulations.

---

## 🚀 Features

-   **PDF to UBL Conversion:** Generate compliant e-invoices from any format, including PDF, XML, JSON and CSV.
-   **Automated Validation:** Validate your ZUGFeRD and UBL e-invoices against 300+ EN16931 rules. AI-driven PDF–XML comparison ensures your invoices meet compliance standards.
-   **Correction:** Automatically correct errors in XML files to ensure seamless integration with your system.

---

## 🛠️ Installation

The easiest way to use the server is to install it via pip:

```bash
pip install e-invoice-mcp
```

### Run the Server
Once installed, you can start the server with:
```bash
e-invoice-mcp
```

---

## 🔑 AI Client Configuration

### Claude Desktop (Action required)
To use these tools in Claude, add the following to your configuration file:
**File:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fintom8": {
      "command": "e-invoice-mcp"
    }
  }
}
```

---

## 📦 Included Tools

### 1. `convert_pdf_to_invoice`
Converts PDF invoices to structured UBL format.
-   **Args**: `pdf_path` (path).
-   **Output**: UBL XML.

### 2. `validate_invoice` (Basic Validation)
Validates UBL/Peppol XML invoices against compliance rules.
-   **Args**: `xml_content` (string) or `xml_path` (path).
-   **Output**: Simple JSON report (is_valid, errors).

### 3. `validate_invoice_v2` (Advanced Validation)
Deep validation with optional AI explanations.
-   **Args**: `xml_content` (string) or `xml_path` (path).
-   **Output**: Detailed compliance report.

### 4. `correct_invoice_xml`
AI-powered correction of invalid XML invoices.
-   **Args**: `xml_content` (string) or `xml_path` (path).
-   **Output**: Fixed XML content.

---

## Deploy to Google Cloud (HTTP transport)

To run the server over **HTTP** (e.g. for remote MCP clients), deploy to **Google Cloud Run** or **App Engine**. The server uses HTTP when `MCP_TRANSPORT=http` or when running on Cloud Run / App Engine.

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for the full guide: Cloud Run, **App Engine Standard** (`app.yaml`) and **App Engine Flexible** (Docker), env vars, and security.

When deployed over HTTP, you can also call tools **without a session** via REST: `POST /api/validate_invoice`, `/api/validate_invoice_v2`, `/api/correct_invoice_xml`, `/api/convert_invoice` — see DEPLOYMENT.md for single-curl examples.

---

## � Privacy & Security
This server acts as a thin client proxy. Data is processed on secure Fintom8 production servers and is not used for AI model training. 

**License:** MIT
**Website:** [fintom8.com](https://fintom8.com)