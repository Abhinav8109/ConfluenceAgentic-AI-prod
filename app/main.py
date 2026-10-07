"""
FastAPI Server for CloudOps AI Knowledge Assistant
Provides REST endpoints for chat reasoning, health checks, Confluence sources discovery,
and static frontend hosting for Cloud Run deployment.
"""

import time
import uuid
import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import settings
from app.utils.logger import setup_cloud_logging, log_operational_event
from app.confluence.client import confluence_client
from app.confluence.seed_data import SEED_PAGES
from app.agent.assistant import cloudops_assistant
from app.agent.memory import conversation_memory

# Configure logging
setup_cloud_logging()
logger = logging.getLogger("cloudops.api")

app = FastAPI(
    title="CloudOps AI Knowledge Assistant",
    description="Production-grade AI Knowledge Assistant on GCP grounded in Confluence Cloud",
    version="1.0.0",
)

# CORS middleware for open web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request & Response schemas
class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    query: str
    answer: str
    sources: List[Dict[str, Any]]
    page_recommendations: List[Dict[str, Any]]
    latency_ms: float

class ClearRequest(BaseModel):
    session_id: str

class SettingsTestRequest(BaseModel):
    base_url: str
    user_email: str
    api_token: Optional[str] = None
    space_key: str

class SettingsUpdateRequest(BaseModel):
    base_url: str
    user_email: str
    api_token: Optional[str] = None
    space_key: str
    use_mock: Optional[bool] = False

@app.get("/api/settings")
async def get_settings_endpoint():
    """Returns active Confluence configuration and connectivity diagnostics."""
    health = await confluence_client.check_health()
    
    masked_token = ""
    if settings.confluence_api_token:
        tok = settings.confluence_api_token
        if len(tok) > 10:
            masked_token = f"{tok[:4]}••••••••{tok[-4:]}"
        else:
            masked_token = "••••••••"

    return {
        "base_url": settings.confluence_base_url,
        "user_email": settings.confluence_user_email,
        "space_key": settings.confluence_space_key,
        "use_mock": settings.use_mock_confluence,
        "has_token": bool(settings.confluence_api_token),
        "masked_token": masked_token,
        "gcp_project_id": settings.gcp_project_id,
        "gemini_model": settings.gemini_model,
        "health": health,
    }

@app.post("/api/settings/test")
async def test_settings_endpoint(req: SettingsTestRequest):
    """Tests connectivity to a target Confluence instance without mutating active state."""
    token = req.api_token
    # If token was masked or omitted, fallback to currently stored token
    if (not token or "••••" in token or "..." in token) and settings.confluence_api_token:
        token = settings.confluence_api_token

    from app.confluence.client import ConfluenceClient
    result = await ConfluenceClient.test_connection(
        base_url=req.base_url,
        email=req.user_email,
        api_token=token or "",
        space_key=req.space_key,
    )
    return result

@app.post("/api/settings")
async def update_settings_endpoint(req: SettingsUpdateRequest):
    """Dynamically updates active Confluence configuration at runtime and persists to .env."""
    token = req.api_token
    if (not token or "••••" in token or "..." in token):
        token = settings.confluence_api_token

    from app.config import update_runtime_settings
    update_runtime_settings(
        confluence_base_url=req.base_url,
        confluence_user_email=req.user_email,
        confluence_api_token=token,
        confluence_space_key=req.space_key,
        use_mock_confluence=req.use_mock,
        persist=True,
    )

    confluence_client.reconfigure(
        base_url=req.base_url,
        email=req.user_email,
        api_token=token,
        space_key=req.space_key,
        use_mock=req.use_mock,
    )

    health = await confluence_client.check_health()
    return {
        "success": True,
        "message": f"Successfully switched environment to Space '{req.space_key}' ({'Mock' if req.use_mock else 'Live Confluence'}).",
        "health": health,
    }

@app.get("/api/health")
async def health_check():
    """Service health & operational telemetry check."""
    confluence_status = await confluence_client.check_health()
    return {
        "status": "healthy",
        "service": "CloudOps-AI-Knowledge-Assistant",
        "gcp_project": settings.gcp_project_id,
        "region": settings.gcp_region,
        "model": settings.gemini_model,
        "confluence": confluence_status,
        "knowledge_base_pages_available": len(SEED_PAGES),
    }

@app.get("/api/sources")
async def list_sources():
    """Lists all operational knowledge pages currently registered in the knowledge base."""
    return {
        "space": settings.confluence_space_key,
        "pages": [
            {
                "id": p["id"],
                "title": p["title"],
                "version": p["version"],
                "lastUpdated": p["lastUpdated"],
                "author": p["author"],
                "url": p["url"],
            }
            for p in SEED_PAGES
        ]
    }

@app.post("/api/chat", response_model=ChatResponse)
@app.post("/api/ask", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main conversational endpoint:
    Retrieves grounded Confluence content -> Synthesizes with Vertex AI Gemini -> Returns structured answer & sources.
    """
    start_time = time.time()
    req_id = str(uuid.uuid4())
    session = request.session_id or str(uuid.uuid4())
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logger.info(f"Incoming query (Session: {session}, Req: {req_id}): '{request.query[:80]}...'")

    try:
        result = await cloudops_assistant.ask(query=request.query, session_id=session)
        elapsed_ms = (time.time() - start_time) * 1000.0

        # Log operational audit telemetry without logging credentials
        log_operational_event(
            event_type="chat_query_completed",
            session_id=session,
            request_id=req_id,
            duration_ms=elapsed_ms,
            status="SUCCESS",
            details={
                "retrieved_pages_count": len(result.get("sources", [])),
                "model": settings.gemini_model,
            }
        )

        return ChatResponse(
            session_id=session,
            query=request.query,
            answer=result["answer"],
            sources=result.get("sources", []),
            page_recommendations=result.get("page_recommendations", []),
            latency_ms=round(elapsed_ms, 2),
        )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000.0
        logger.error(f"Error processing query in session {session}: {e}", exc_info=True)
        log_operational_event(
            event_type="chat_query_error",
            session_id=session,
            request_id=req_id,
            duration_ms=elapsed_ms,
            status="ERROR",
            details={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail="Internal assistant error. Please try again.")

@app.post("/api/clear")
async def clear_session(request: ClearRequest):
    """Clears conversation history for the specified session."""
    conversation_memory.clear_session(request.session_id)
    return {"status": "cleared", "session_id": request.session_id}

@app.post("/api/seed")
async def seed_confluence():
    """Seeds the 8 knowledge pages to Confluence Cloud or mock store."""
    results = []
    for page in SEED_PAGES:
        res = await confluence_client.create_or_update_page(
            title=page["title"],
            content_html=f"<p>{page['content']}</p>"
        )
        results.append({"title": page["title"], "result": res})
    return {"status": "completed", "count": len(results), "details": results}

# Mount static web directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def serve_ui():
    """Serves the CloudOps AI Knowledge Assistant web chat interface."""
    return FileResponse("app/static/index.html")
