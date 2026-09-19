"""
Cloud Logging and Operational Observability
Configures structured JSON logging compatible with Google Cloud Logging.
Provides tracing for query latency, retrieval duration, and source attribution.
"""

import os
import sys
import time
import json
import logging
from typing import Dict, Any, Optional

def setup_cloud_logging():
    """Configures structured Cloud Logging if in GCP, or readable standard logging locally."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # If running in GCP Cloud Run, attempt to initialize Google Cloud Logging client
    if os.getenv("K_SERVICE"):
        try:
            import google.cloud.logging
            client = google.cloud.logging.Client()
            client.setup_logging()
            logging.info("Google Cloud Logging handler successfully attached.")
            return
        except Exception as e:
            sys.stderr.write(f"Could not initialize Cloud Logging client ({e}), falling back to stream handler.\n")

    # Standard stream handler with formatted output
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    root_logger.handlers = [handler]

def log_operational_event(
    event_type: str,
    session_id: str,
    request_id: str,
    duration_ms: float,
    status: str,
    details: Optional[Dict[str, Any]] = None,
):
    """
    Emits structured telemetry event without logging confidential user content or credentials.
    """
    payload = {
        "event_type": event_type,
        "session_id": session_id,
        "request_id": request_id,
        "duration_ms": round(duration_ms, 2),
        "status": status,
        "metadata": details or {},
    }
    logging.info(f"AUDIT_TELEMETRY: {json.dumps(payload)}")
