<div align="center">

# ⚡ CloudOps AI — Enterprise Knowledge Assistant

### Autonomous Operational Intelligence Grounded in Atlassian Confluence & Google Cloud Vertex AI

[![Python 3.11](https://img.shields.io/badge/python-3.11+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Google Cloud Vertex AI](https://img.shields.io/badge/Vertex_AI-Gemini_2.5_Flash-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com/vertex-ai)
[![Confluence Cloud](https://img.shields.io/badge/Atlassian-Confluence_Cloud-0052CC?style=for-the-badge&logo=confluence&logoColor=white)](https://www.atlassian.com/software/confluence)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

<p align="center">
  <b>CloudOps AI</b> is an enterprise-grade agentic knowledge platform designed to automate Tier-1 SRE triage, incident mitigation, and multi-cloud architecture lookup. Grounded directly in live <b>Confluence Cloud runbooks</b> and driven by <b>Gemini 2.5 Flash on Vertex AI</b>, it delivers deterministic, cited, hallucination-resistant operational procedures with sub-second retrieval latency.
</p>

---

</div>

## 📑 Table of Contents

- [System Architecture](#-system-architecture)
- [The Actual Truth: How Fast Search & Grounding Works](#-the-actual-truth-how-fast-search--grounding-works)
- [Dynamic Multi-Environment Settings](#-dynamic-multi-environment-settings)
- [Core Capabilities](#-core-capabilities)
- [Live Knowledge Base Overview](#-live-knowledge-base-overview)
- [Technology Stack](#-technology-stack)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Environment](#installation--environment)
  - [Confluence Cloud Configuration](#confluence-cloud-configuration)
  - [Google Cloud ADC Authentication](#google-cloud-adc-authentication)
  - [Knowledge Base Automated Seeder](#knowledge-base-automated-seeder)
  - [Running the Application](#running-the-application)
- [REST API Reference](#-rest-api-reference)
- [Security & Prompt Injection Guardrails](#-security--prompt-injection-guardrails)
- [UI/UX Customization Engine](#-uiux-customization-engine)
- [Evaluation Suite & Testing](#-evaluation-suite--testing)
- [Production Deployment (GCP Cloud Run)](#-production-deployment-gcp-cloud-run)
- [License](#-license)

---

## 🏛 System Architecture

The following diagram illustrates the complete request lifecycle, security boundary, and Confluence retrieval mesh:

```
                                      ┌─────────────────────────────────────────┐
                                      │       User Interaction Layer            │
                                      │  (Modern Reactive UI / Web App)         │
                                      └────────────────────┬────────────────────┘
                                                           │ POST /api/chat
                                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CloudOps AI Orchestration Engine                                     │
│                                                                                                        │
│  ┌──────────────────────────────┐    ┌─────────────────────────────────┐    ┌───────────────────────┐  │
│  │ 1. Security Guardrails       │    │ 2. Session Memory Engine        │    │ 3. Multi-Page         │  │
│  │  • Injection Detection       ├───►│  • Conversational History       ├───►│    Knowledge Search   │  │
│  │  • Untrusted Data Isolation  │    │  • Topic Context Resolution     │    │  • Confluence REST v2 │  │
│  └──────────────────────────────┘    └─────────────────────────────────┘    └───────────┬───────────┘  │
│                                                                                         │              │
└─────────────────────────────────────────────────────────────────────────────────────────┼──────────────┘
                                                                                          │
                                ┌─────────────────────────────────────────────────────────┴──────────┐
                                │                                                                    │
                                ▼                                                                    ▼
        ┌──────────────────────────────────────────────┐                 ┌───────────────────────────────────────┐
        │        Confluence Cloud Knowledge Mesh       │                 │       Google Cloud Platform           │
        │     Space: 'AITEST' (25 Runbooks)            │                 │       Vertex AI Model Garden          │
        │  • GCP Core Architecture & Networking        │                 │                                       │
        │  • AWS Enterprise Transit Gateway & VPCs     │                 │   Gemini 2.5 Flash Model              │
        │  • Multi-Cloud Hybrid Mesh (BGP/HA-VPN)      │                 │   • System Prompt Isolation           │
        │  • Workload Identity Federation (WIF)        │                 │   • Citation & Source Attribution     │
        │  • Production Incident SRE Runbooks (P1/P2)  │                 │   • Hallucination Mitigation          │
        └──────────────────────────────────────────────┘                 └───────────────────┬───────────────────┘
                                                                                             │
                                                                                             ▼
                                                                         ┌───────────────────────────────────────┐
                                                                         │ Grounded Answer + Attributed Sources  │
                                                                         │ Latency SLA, Runbook Cards, Direct URLs│
                                                                         └───────────────────────────────────────┘
```

---

## 🔍 The Actual Truth: How Fast Search & Grounding Works

Many AI wrappers dump entire documents into prompts or rely on naive vector databases that suffer from high indexing latency, stale data, and token bloat. **CloudOps AI uses a deterministic 6-stage Grounding Pipeline** engineered for real-time SRE response times:

```
[User Query] 
     │
     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: Heuristic Security Inspection                                   │
│ • Regex pattern analysis for jailbreaks ("ignore previous", "leak key")  │
│ • Rejects malicious prompts immediately before API calls                 │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: Intent Analysis & Keyword Distillation                          │
│ • Stop-words removed (what, is, how, should, in, of, etc.)               │
│ • Domain intent classified: Incident, Escalation, Change, GCP, AWS, IAM  │
│ • Core searchable terms extracted (up to 6 high-entropy keywords)        │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: Asynchronous High-Speed Confluence CQL Execution                │
│ • Executes Confluence Query Language (CQL) against REST API v2:          │
│   cql = space = "AITEST" AND (text ~ "term1" OR title ~ "term1" ...)    │
│ • Persistent HTTP/2 connection pooling with keep-alive via httpx         │
│ • Fetches metadata + compressed storage XML in parallel                  │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: Section Extraction & Token Compression                          │
│ • Does NOT send entire bloated HTML pages into the LLM context!          │
│ • Parses page structure by header blocks (<h2>, <h3>)                    │
│ • Scores individual sections against query intent & extracts top blocks  │
│ • Reduces 50,000+ characters of boilerplate down to ~2,500 key tokens    │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: Context Boundary Isolation                                      │
│ • Retrieved text is wrapped in <confluence_untrusted_data> XML tags      │
│ • Instructs LLM to treat data strictly as passive reference facts        │
│ • Neutralizes prompt injection embedded inside Confluence page bodies    │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ STAGE 6: Vertex AI Gemini 2.5 Flash Synthesis & Source Linking          │
│ • Synthesizes answer strictly grounded in retrieved evidence             │
│ • Formats clean markdown links: [Open Runbook](url)                      │
│ • Generates source card metadata: Space, Page Title, Relevance Score     │
│ • Returns structured JSON with latency telemetry                         │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Dynamic Multi-Environment Settings

The platform is **100% reusable across different projects, spaces, and Atlassian organizations** without touching any code or restarting the server.

### Features of the Settings Engine:
1. **Live Connection Test (`POST /api/settings/test`)**:
   - Performs a non-destructive, isolated dry-run against any Confluence Base URL, User Email, API Token, and Space Key.
   - Detects `401 Unauthorized` (bad PAT or email), `404 Not Found` (invalid Space Key), and unreachable domains before saving.
2. **Instant Hot-Reload (`POST /api/settings`)**:
   - Reconfigures the running `ConfluenceClient` singleton in memory immediately.
   - Persists credentials into `.env` so settings survive container restarts.
   - Updates dashboard UI badges (`Live Connected`, active domain, target space) instantly.
3. **Dual Mode Switching**:
   - Toggle between **Live Confluence Cloud** (live REST calls) and **Local Mock Store** (offline air-gapped demo).

---

## 🚀 Core Capabilities

- **Zero-Hallucination Confluence Grounding**: Strict prompt isolation guarantees that the agent answers exclusively using verified procedures retrieved from your enterprise Confluence space.
- **Dynamic Dual-Mode Confluence Adapter**: Seamlessly operates in dual modes:
  - **Live Confluence Mode**: Live REST API v2 integration with Atlassian Cloud.
  - **Resilient Fallback Mode**: High-speed, in-memory mock store for air-gapped environments or local development.
- **Enterprise Security Guardrails**:
  - Heuristic & token-pattern prompt injection scanner.
  - Strict tagging (`<confluence_untrusted_data>`) to neutralize untrusted markdown/HTML payloads.
  - Pre-flight secret scrubber preventing credential leakage.
- **Multi-Cloud Operations Knowledge**:
  - **GCP**: GKE Autopilot, Cloud Run, VPC Service Controls, Cloud Armor, BigQuery Omni, Shared VPC.
  - **AWS**: Transit Gateway, Direct Connect, AWS Network Firewall, Route 53 Resolver, IAM Identity Center.
  - **Hybrid Mesh**: High-Availability Cloud VPN over BGP (Border Gateway Protocol) and Cross-Cloud Interconnect.
- **Session-Aware Chat & State Persistence**: Local storage session persistence allows switching between conversations without losing context.
- **Adaptive UI/UX Engine**: Real-time theme toggling (Light/Dark), 8 distinct accent swatches, density controls, animation rate adjustment, and dynamic background renderers (Canvas Particles, SVG Mesh, Ambient Waves).

---

## 📚 Live Knowledge Base Overview

The system includes **25 operational runbooks** pre-formatted with status badges, information panels, SLA matrices, and architecture ASCII flowcharts:

| Runbook ID | Topic | Domain | Severity / Tier |
|:---|:---|:---|:---|
| `1867779` | CloudOps AI Architecture & Intelligence Engine | Architecture | Master Reference |
| `1769521` | GCP Core Services & Architecture Deep Dive | GCP Infrastructure | Tier-1 Core |
| `1802250` | AWS Enterprise Networking Master Reference | AWS Networking | Tier-1 Core |
| `1638499` | Multi-Cloud Hybrid Mesh (GCP & AWS Interconnect) | Hybrid Cloud | Tier-1 Core |
| `1507331` | Google Cloud VPC & Security Perimeter Architecture | Security | Tier-1 Core |
| `1703993` | Multi-Cloud Data Pipeline & Analytics Architecture | Data Engineering | Tier-2 Standard |
| `1638516` | Multi-Cloud IAM & Federated Zero-Trust Security (WIF) | Security / IAM | Tier-1 Core |
| `1572922` | Multi-Cloud Observability, Telemetry & Monitoring Mesh | SRE / Observability | Tier-1 Core |
| `1671218` | Global Traffic Management, Cloud CDN & Edge Routing | Networking | Tier-2 Standard |
| `1001-1016` | Production Incident Runbooks (GKE, Direct Connect, SLAs) | Incident Response | P1 / P2 / P3 SLAs |

---

## 🛠 Technology Stack

- **Backend Runtime**: Python 3.11+, FastAPI, Uvicorn (ASGI)
- **Foundation Model**: Google DeepMind Gemini 2.5 Flash via `google-genai` SDK on Vertex AI
- **Knowledge Integration**: Atlassian Confluence Cloud REST API v2 (`httpx` asynchronous client)
- **Frontend Architecture**: Modern Vanilla JavaScript (ES6+), CSS Custom Properties, Marked.js for secure streaming markdown, HTML5 Canvas Particle Engine
- **Telemetry & Evaluation**: Structured JSON audit telemetry, Pytest, automated SLA evaluation framework
- **Containerization**: Docker, Google Cloud Build (`cloudbuild.yaml`)

---

## 🏁 Getting Started

### Prerequisites

- Python 3.11 or higher
- Google Cloud Platform account with **Vertex AI API** enabled
- Google Cloud SDK (`gcloud`) installed locally
- Atlassian Confluence Cloud account with an API Personal Access Token (PAT)

---

### Installation & Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Abhinav8109/ConfluenceAgentic-AI-prod.git
   cd ConfluenceAgentic-AI-prod
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy the provided `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

   Open `.env` and fill in your details:
   ```env
   # Google Cloud Configuration
   GCP_PROJECT_ID=your-gcp-project-id
   GCP_REGION=us-central1
   GEMINI_MODEL=gemini-2.5-flash

   # Confluence Cloud Configuration
   CONFLUENCE_BASE_URL=https://your-domain.atlassian.net
   CONFLUENCE_USER_EMAIL=your-email@example.com
   CONFLUENCE_API_TOKEN=your-atlassian-api-token
   CONFLUENCE_SPACE_KEY=AITEST
   USE_MOCK_CONFLUENCE=false
   ```

---

### Google Cloud ADC Authentication

Authenticate your local environment with Application Default Credentials (ADC) for Vertex AI access:

```bash
gcloud auth application-default login
gcloud config set project YOUR_GCP_PROJECT_ID
```

---

### Knowledge Base Automated Seeder

Run the automated seeder script to publish or synchronize all 25 rich HTML runbooks into your Confluence Cloud space:

```bash
python scripts/seed_confluence.py
```

---

### Running the Application

Launch the FastAPI ASGI server:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

Navigate to **`http://localhost:8080`** in your browser to access the CloudOps AI interactive interface.

---

## 🔌 REST API Reference

### 1. Conversational Reasoning Endpoint
- **URL**: `/api/chat` (alias `/api/ask`)
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "query": "How do we implement Workload Identity Federation (WIF) between AWS and GCP?",
    "session_id": "optional-uuid-string"
  }
  ```
- **Response**:
  ```json
  {
    "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "query": "How do we implement Workload Identity Federation (WIF) between AWS and GCP?",
    "answer": "## Answer\nTo federate AWS identities into GCP...\n\n## Recommended Approach\n1. Create Workload Identity Pool...",
    "sources": [
      {
        "id": "1638516",
        "title": "Multi-Cloud IAM and Federated Zero-Trust Security",
        "space_key": "AITEST",
        "url": "https://your-domain.atlassian.net/wiki/spaces/AITEST/pages/1638516/...",
        "relevance_score": 0.94
      }
    ],
    "page_recommendations": [],
    "latency_ms": 1845.2
  }
  ```

### 2. Environment Settings (`GET /api/settings`)
- **Method**: `GET`
- **Response**:
  ```json
  {
    "base_url": "https://your-domain.atlassian.net",
    "user_email": "user@example.com",
    "space_key": "AITEST",
    "use_mock": false,
    "has_token": true,
    "masked_token": "ATAT••••••••7CDA",
    "health": { "status": "ok", "mode": "live", "space": "AITEST" }
  }
  ```

### 3. Test Confluence Connection (`POST /api/settings/test`)
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "base_url": "https://your-domain.atlassian.net",
    "user_email": "user@example.com",
    "api_token": "your_api_token",
    "space_key": "AITEST"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "status_code": 200,
    "message": "Successfully verified! Space 'CloudOps Knowledge Base' (AITEST) is active and accessible.",
    "pages_accessible": 25
  }
  ```

### 4. Switch Environment at Runtime (`POST /api/settings`)
- **Method**: `POST`
- **Payload**:
  ```json
  {
    "base_url": "https://another-domain.atlassian.net",
    "user_email": "sre@another-domain.com",
    "api_token": "another_token",
    "space_key": "PROD_OPS",
    "use_mock": false
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "message": "Successfully switched environment to Space 'PROD_OPS' (Live Confluence).",
    "health": { "status": "ok", "mode": "live", "space": "PROD_OPS" }
  }
  ```

---

## 🛡 Security & Prompt Injection Guardrails

CloudOps AI employs a multi-tiered defense architecture:

1. **Deterministic Prompt Injection Scanning**: Analyzes inbound user prompts against regex patterns and token distributions commonly used in jailbreak attempts (`ignore previous instructions`, `leak prompt`, `DAN mode`).
2. **Context Isolation Boundary**: Unsafe HTML/XML content retrieved from external Confluence pages is sanitized and enclosed in `<confluence_untrusted_data>` tags.
3. **Automated Secret Redaction**: Eliminates API keys, Bearer tokens, and PAT hashes from output responses before reaching the browser.
4. **Target Sandboxing**: All outgoing hyperlinks enforce `target="_blank" rel="noopener noreferrer"` to prevent tab-nabbing vulnerabilities.

---

## 🎨 UI/UX Customization Engine

The web interface is engineered for production SRE operational environments:
- **Theme Modes**: Native Light Mode and Dark Mode with dynamic CSS variables.
- **8 Accent Palettes**: Blue, Violet, Rose, Emerald, Amber, Cyan, Indigo, Pink.
- **Layout Densities**: Compact (incident bridge mode), Comfortable, Spacious.
- **Background Visualizations**: Animated Mesh Gradients, HTML5 Canvas Particle Engine, Ambient Waves, or Minimalist flat styling.
- **Responsive Layout**: Fluid CSS Grid and Flexbox with zero content overflow, even with complex 100+ character Confluence URLs.

---

## 🧪 Evaluation Suite & Testing

Execute the automated test suite to validate prompt isolation, grounding fidelity, and latency SLAs:

```bash
pytest tests/ -v
```

---

## 🚢 Production Deployment (GCP Cloud Run)

The repository includes a ready-to-deploy `Dockerfile` and `cloudbuild.yaml`:

```bash
# Build container image via Google Cloud Build
gcloud builds submit --tag gcr.io/YOUR_GCP_PROJECT_ID/cloudops-ai:latest

# Deploy to Cloud Run
gcloud run deploy cloudops-ai \
  --image gcr.io/YOUR_GCP_PROJECT_ID/cloudops-ai:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID,CONFLUENCE_SPACE_KEY=AITEST
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<div align="center">
  <sub>Engineered by <b>Abhinav Singh</b> · Powered by Google Cloud Vertex AI & Atlassian Confluence</sub>
</div>
