# Deploying Fintom8 E-Invoice MCP Server to Google Cloud (HTTP Transport)

This document describes how to run the MCP server with **HTTP transport** on **Google Cloud Run**, so clients can connect over the network instead of stdio.

---

## Implementation overview

| Layer | Choice | Notes |
|-------|--------|--------|
| **Transport** | HTTP (SSE) | MCP over HTTP; clients use SSE + POST. |
| **Platform** | **Cloud Run** | Serverless, scale-to-zero, pay-per-request; good fit for MCP. |
| **Trigger** | HTTP | One service URL; clients point to `https://<service-url>/mcp` (or path your framework uses). |
| **Config** | Env vars | `MCP_TRANSPORT=http`, `PORT` (Cloud Run sets `PORT` and `K_SERVICE`). |

The server automatically uses **HTTP transport** when:

- `MCP_TRANSPORT=http`, or  
- Running on Cloud Run (env `K_SERVICE` is set).

Otherwise it uses **stdio** (e.g. for Claude Desktop).

---

## 1. Prerequisites

- Google Cloud project with billing enabled.
- **gcloud** CLI installed and logged in: `gcloud auth login` and `gcloud config set project PROJECT_ID`.
- **Docker** (for local build) or use Cloud Build.

---

## 2. Build the container image

From the repo root:

```bash
# Build (optionally tag for Artifact Registry or GCR)
docker build -t gcr.io/PROJECT_ID/e-invoice-mcp:latest .
# Or for Artifact Registry:
# docker build -t REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/e-invoice-mcp:latest .
```

Or use **Cloud Build** (no local Docker needed):

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/e-invoice-mcp:latest
```

---

## 3. Deploy to Cloud Run

### Option A: Deploy with gcloud (recommended)

```bash
gcloud run deploy e-invoice-mcp \
  --image gcr.io/PROJECT_ID/e-invoice-mcp:latest \
  --platform managed \
  --region REGION \
  --allow-unauthenticated \
  --set-env-vars "FINTOM_API_KEY=your-api-key"
```

- Replace `PROJECT_ID`, `REGION`, and `your-api-key`.
- To require authentication (e.g. IAM or identity token), use `--no-allow-unauthenticated` and configure your client to send the token.

### Option B: Deploy with a service YAML (reproducible / GitOps)

Create `cloudrun-service.yaml` (example):

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: e-invoice-mcp
spec:
  template:
    spec:
      containerConcurrency: 80
      containers:
        - image: gcr.io/PROJECT_ID/e-invoice-mcp:latest
          ports:
            - containerPort: 8080
          env:
            - name: MCP_TRANSPORT
              value: "http"
            - name: FINTOM_API_KEY
              valueFrom:
                secretKeyRef:
                  name: fintom-api-key
                  key: api-key
          resources:
            limits:
              memory: "512Mi"
              cpu: "1"
```

Then:

```bash
gcloud run services replace cloudrun-service.yaml --region REGION
```

Store `FINTOM_API_KEY` in **Secret Manager**, create a secret, and grant the Cloud Run service account access to it.

---

## 4. MCP HTTP endpoint

After deployment, Cloud Run gives you a URL like:

`https://e-invoice-mcp-XXXXX-REGION.run.app`

- **MCP endpoint path**: typically `/mcp` (FastMCP default). Full URL:  
  `https://e-invoice-mcp-XXXXX-REGION.run.app/mcp`
- Confirm the exact path in FastMCP’s HTTP docs (e.g. SSE URL and POST path).

Clients that support MCP over HTTP (e.g. Cursor, custom agents) should be pointed at this base URL or at the `/mcp` path, depending on the client’s configuration.

### Stateless REST API (single curl, no session)

The same deployment exposes **stateless REST endpoints** so you can call tools with **one curl**, no session ID:

| Endpoint | Method | Body | Description |
|----------|--------|------|-------------|
| `/api/validate_invoice` | POST | `{"xml_content": "<Invoice>...</Invoice>"}` | Validate UBL/Peppol XML |
| `/api/validate_invoice_v2` | POST | `{"xml_content": "..."}` | Advanced validation |
| `/api/correct_invoice_xml` | POST | `{"xml_content": "..."}` | Correct invalid XML |
| `/api/convert_invoice` | POST | `{"pdf_content": "Visualisierung eRechnung\\n..."}` | Convert PDF text to UBL |

**Example (validate with a single curl):**

```bash
curl -X POST "https://YOUR-SERVICE-URL/api/validate_invoice" \
  -H "Content-Type: application/json" \
  -d '{"xml_content": "<Invoice xmlns=\"urn:oasis:names:specification:ubl:schema:xsd:Invoice-2\">...</Invoice>"}'
```

Response: `{"result": "<validation output>"}`. No MCP session or `Mcp-Session-Id` required.

### Testing the deployment

**1. Smoke test (server responds)**  
Replace with your service URL (App Engine or Cloud Run):

```bash
curl -s -o /dev/null -w "%{http_code}" -X POST "https://YOUR-SERVICE-URL/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}'
```

A successful response includes a 200 and an `Mcp-Session-Id` header.

**2. Full MCP test (initialize + list tools)**  
From the repo root, using the script:

```bash
chmod +x scripts/test_deployed_mcp.sh
MCP_ENDPOINT="https://YOUR-SERVICE-URL/mcp" ./scripts/test_deployed_mcp.sh
```

**3. MCP Inspector (GUI)**  
In [MCP Inspector](https://github.com/modelcontextprotocol/inspector), add a **Streamable HTTP** server with URL `https://YOUR-SERVICE-URL/mcp`, then connect and list/call tools.

**4. Cursor**  
In Cursor settings, add an MCP server with type `streamable-http` and URL `https://YOUR-SERVICE-URL/mcp` to use the deployed server in the IDE.

---

## 5. Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FINTOM_API_KEY` | Yes (for Fintom8 APIs) | API key for converter/validator/correction. |
| `MCP_TRANSPORT` | No | Set to `http` to force HTTP; Cloud Run sets `K_SERVICE` so HTTP is used automatically. |
| `PORT` | No | Cloud Run sets this (default 8080). |
| `FINTOM_CONVERTER_URL` | No | Override converter endpoint. |
| `FINTOM_VALIDATOR_URL` | No | Override validator endpoint. |

---

## 6. Security recommendations

1. **API key**: Prefer **Secret Manager** for `FINTOM_API_KEY`; inject via Cloud Run secret env (as in the YAML example).
2. **Access**: Use `--no-allow-unauthenticated` and enforce **IAM** or **identity tokens** so only your clients can call the service.
3. **VPC**: If the server must call private resources, use a **VPC connector** and configure the Cloud Run service to use it.
4. **HTTPS**: Cloud Run serves HTTPS only; no extra config needed.

---

## 7. Implementation checklist

- [x] Server supports HTTP when `MCP_TRANSPORT=http` or `K_SERVICE` is set.
- [x] Dockerfile builds and runs `e-invoice-mcp` with HTTP transport.
- [ ] Create GCP project and enable Cloud Run API.
- [ ] Build and push image (Docker or Cloud Build).
- [ ] Deploy to Cloud Run (gcloud or YAML).
- [ ] Set `FINTOM_API_KEY` (env or Secret Manager).
- [ ] Configure MCP client with service URL (e.g. `https://...run.app/mcp`).
- [ ] (Optional) Restrict access with IAM or identity tokens and use Secret Manager for the API key.

**App Engine**

- [x] `app.yaml` for App Engine Standard (Python 3.12 + uvicorn).
- [x] `app-flexible.yaml` for App Engine Flexible (Dockerfile).
- [ ] Run `gcloud app create` once per project, then `gcloud app deploy app.yaml` or `gcloud app deploy app-flexible.yaml`.

---

## 8. Deploy to App Engine

You can run the MCP server on **App Engine Standard** (Python runtime + `app.yaml`) or **App Engine Flexible** (same Docker image as Cloud Run).

### 8.1 App Engine Standard (recommended for App Engine)

Uses the included **`app.yaml`**: Python 3.12 runtime and **uvicorn** to serve the ASGI app (`mcp.http_app()`).

**Prerequisites**

- Enable the App Engine API:  
  `gcloud services enable appengine.googleapis.com`
- Create an App Engine application in your project (once per project):  
  `gcloud app create --region=REGION`

**Deploy**

From the repo root:

```bash
# Set your API key (or add it in App Engine > Configuration > Environment variables)
gcloud app deploy app.yaml --set-env-vars FINTOM_API_KEY=your-api-key
```

Or leave `FINTOM_API_KEY` out of the command and set it in the [App Engine Console](https://console.cloud.google.com/appengine/settings) under **Configuration > Environment variables**.

**URL**

After deploy you get a URL like:

`https://PROJECT_ID.REGION.r.appspot.com`

MCP HTTP endpoint: `https://PROJECT_ID.REGION.r.appspot.com/mcp`

**Scaling**

The included `app.yaml` uses `min_instances: 0` (scale to zero) and `instance_class: F1`. Adjust `instance_class`, `min_instances`, and `max_instances` in `app.yaml` as needed.

### 8.2 App Engine Flexible (custom runtime / Docker)

To run the **same container** as Cloud Run on App Engine Flexible, use the included **`app-flexible.yaml`** and **`Dockerfile`**:

```bash
# App Engine builds the image from Dockerfile and deploys
gcloud app deploy app-flexible.yaml
```

Set `FINTOM_API_KEY` in the [Console](https://console.cloud.google.com/appengine/settings) or:

```bash
gcloud app deploy app-flexible.yaml --set-env-vars FINTOM_API_KEY=your-api-key
```

Flexible uses the project’s `Dockerfile`; the container runs `e-invoice-mcp` with HTTP transport (same as Cloud Run).

### 8.3 Cloud Run vs App Engine

| | Cloud Run | App Engine Standard |
|--|-----------|---------------------|
| **Config** | Dockerfile + `gcloud run deploy` | `app.yaml` + `gcloud app deploy` |
| **Runtime** | Any (container) | Python 3.12 (GAE runtime) |
| **Scale to zero** | Yes | Yes (min_instances: 0) |
| **Best for** | Container-based CI/CD, multi-language | Simple Python deploy, no Docker |

Both expose the same MCP HTTP endpoint (e.g. `.../mcp`).
