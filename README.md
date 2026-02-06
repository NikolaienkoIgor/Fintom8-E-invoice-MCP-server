# Fintom8 E-Invoicing Agent (MCP)

[![MCP Certified](https://img.shields.io/badge/MCP-Certified-blue)](https://mcpmarket.com)
[![Peppol Ready](https://img.shields.io/badge/Peppol-3.0.20-green)](https://fintom8.com)

**The official Model Context Protocol (MCP) server for Fintom8.**

This server acts as an intelligent bridge between LLM agents (Claude, ChatGPT, etc.) and the Fintom8 Compliance Engine. It enables autonomous agents to validate, audit, and correct e-invoices against the latest European standards (EN16931) and Peppol regulations.

**General Functionalities Provided Over MCP:**
* **Convert Peppol UBL E-Invoice from PDF**
* **Validate Peppol UBL E-Invoice**
* **Correct Peppol UBL Invoice**

*Other formats and functionalities can be requested.*

## 🚀 Features

- **Autonomous Validation:** Agents can send XML content and receive detailed compliance reports.
- **Peppol 3.0.20 Support:** Checks against the newest rules, including EAS code updates and PDF attachment handling.
- **Smart Explanations:** The server returns structured error data that LLMs can easily parse to explain issues in human-readable language.

## 🛠️ Installation & Usage

### Option 1: Using `uvx` (Recommended)

You can run this server directly without installing it globally:

```bash
uvx fintom8-mcp-server
```

### Option 2: Clone and Run

1. Clone this repository:
   ```bash
   git clone https://github.com/Fintom8/fintom8-mcp-server.git
   cd fintom8-mcp-server
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Run the server:
   ```bash
   mcp run server.py
   ```

## 🔑 Configuration

By default, the server connects to the public Fintom8 Validation endpoint.

To use a specific API environment or authenticated tier, set the environment variable:

```bash
export FINTOM_API_URL="https://api.fintom8.com/v1/validate"
export FINTOM_API_KEY="your-api-key"
```

## 📦 Tools Included

- **`validate_invoice`**: Validates a UBL/Peppol XML invoice.
  - **Input:** `xml_content` (string)
  - **Output:** JSON compliance report (Valid/Invalid, Error List)

## 🛡️ Privacy & Security

This `fintom8-mcp-server` acts as a thin client proxy. 
- **No data processing** happens within this repository's code.
- All validation logic is handled secure servers at Fintom8.
- Your data is processed solely for the purpose of validation and is not used for AI model training.

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.
