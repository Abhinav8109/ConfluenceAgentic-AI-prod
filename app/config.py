import os
import json
import logging
from pydantic_settings import BaseSettings
from typing import Optional

logger = logging.getLogger("cloudops.config")

class Settings(BaseSettings):
    # GCP Configuration
    gcp_project_id: str = os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_CLOUD_PROJECT") or "project-4d6820e9-87df-40e6-92a"
    gcp_region: str = os.getenv("GCP_REGION") or "us-central1"
    
    # Gemini / Vertex AI Configuration
    gemini_model: str = os.getenv("GEMINI_MODEL") or "gemini-2.5-flash"
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY") or None
    
    # Confluence Configuration
    confluence_base_url: str = os.getenv("CONFLUENCE_BASE_URL") or "https://abhinavclouds.atlassian.net"
    confluence_user_email: str = os.getenv("CONFLUENCE_USER_EMAIL") or "abhinavclouds@gmail.com"
    confluence_api_token: Optional[str] = os.getenv("CONFLUENCE_API_TOKEN") or None
    confluence_space_key: str = os.getenv("CONFLUENCE_SPACE_KEY") or "AITEST"
    confluence_secret_name: str = os.getenv("CONFLUENCE_SECRET_NAME") or "confluence-credentials"
    
    # Retrieval Settings
    retrieval_top_k: int = 5
    max_context_length: int = 12000
    
    # Operation Mode
    # If Confluence credentials are not set, fallback automatically to mock mode
    use_mock_confluence: bool = os.getenv("USE_MOCK_CONFLUENCE", "").lower() in ("true", "1")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL") or "INFO"
    environment: str = os.getenv("ENVIRONMENT") or "development"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

def load_secrets_from_gcp():
    """
    Attempts to load Confluence credentials securely from Google Secret Manager
    if running in GCP or if ADC (Application Default Credentials) is configured.
    """
    global settings
    if settings.confluence_api_token and not settings.use_mock_confluence:
        logger.info("Confluence API token already supplied via environment.")
        return

    secret_name = settings.confluence_secret_name
    project_id = settings.gcp_project_id
    
    if not project_id or not secret_name:
        return

    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
        logger.info(f"Attempting to fetch secret from Secret Manager: {name}")
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        
        # Payload can be JSON: {"url": "...", "email": "...", "token": "..."} or raw token string
        try:
            creds = json.loads(payload)
            if isinstance(creds, dict):
                if creds.get("token"):
                    settings.confluence_api_token = creds["token"]
                if creds.get("url"):
                    settings.confluence_base_url = creds["url"]
                if creds.get("email"):
                    settings.confluence_user_email = creds["email"]
                if creds.get("space_key"):
                    settings.confluence_space_key = creds["space_key"]
                logger.info("Successfully loaded Confluence credentials from Secret Manager JSON payload.")
            else:
                settings.confluence_api_token = payload.strip()
                logger.info("Successfully loaded Confluence API token from Secret Manager string.")
        except json.JSONDecodeError:
            settings.confluence_api_token = payload.strip()
            logger.info("Successfully loaded Confluence API token from Secret Manager.")

        settings.use_mock_confluence = False
    except Exception as e:
        logger.warning(f"Could not load secret from Secret Manager ({e}). Using existing config (mock fallback enabled if no token).")
        if not settings.confluence_api_token:
            settings.use_mock_confluence = True

# Execute secret lookup
load_secrets_from_gcp()
