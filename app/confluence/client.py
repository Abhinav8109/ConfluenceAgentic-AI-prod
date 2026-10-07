"""
Confluence Cloud REST API Client
Provides secure, production-grade integration with Confluence Cloud REST APIs (v1 and v2).
Handles space management, CQL content search, page creation/updating, and content extraction.
"""

import re
import logging
import httpx
from typing import List, Dict, Any, Optional
from app.config import settings
from app.confluence.mock_store import mock_store

logger = logging.getLogger("cloudops.confluence")

class ConfluenceClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        email: Optional[str] = None,
        api_token: Optional[str] = None,
        space_key: Optional[str] = None,
        use_mock: Optional[bool] = None,
    ):
        self.base_url = (base_url or settings.confluence_base_url).rstrip("/")
        self.email = email or settings.confluence_user_email
        self.api_token = api_token or settings.confluence_api_token
        self.space_key = space_key or settings.confluence_space_key
        
        # Decide if using mock or real API
        if use_mock is not None:
            self.use_mock = use_mock
        else:
            self.use_mock = settings.use_mock_confluence or (not self.api_token)

        if not self.use_mock:
            self.auth = (self.email, self.api_token)
            logger.info(f"Initialized live ConfluenceClient for {self.base_url} (Space: {self.space_key})")
        else:
            self.auth = None
            logger.info(f"Initialized mock ConfluenceClient (Space: {self.space_key})")

    def _headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Atlassian-Token": "no-check",
            "User-Agent": "CloudOps-AIAgent/1.0",
        }

    def reconfigure(
        self,
        base_url: Optional[str] = None,
        email: Optional[str] = None,
        api_token: Optional[str] = None,
        space_key: Optional[str] = None,
        use_mock: Optional[bool] = None,
    ):
        """
        Dynamically reconfigures the client credentials, target URL, space, and mode at runtime.
        """
        if base_url is not None:
            self.base_url = base_url.strip().rstrip("/")
        if email is not None:
            self.email = email.strip()
        if api_token is not None and api_token.strip():
            self.api_token = api_token.strip()
        if space_key is not None:
            self.space_key = space_key.strip().upper()
        if use_mock is not None:
            self.use_mock = use_mock
        else:
            self.use_mock = not bool(self.api_token)

        if not self.use_mock and self.api_token:
            self.auth = (self.email, self.api_token)
            logger.info(f"Reconfigured live ConfluenceClient for {self.base_url} (Space: {self.space_key}, User: {self.email})")
        else:
            self.auth = None
            logger.info(f"Reconfigured mock ConfluenceClient (Space: {self.space_key})")

    @classmethod
    async def test_connection(
        cls,
        base_url: str,
        email: str,
        api_token: str,
        space_key: str,
    ) -> Dict[str, Any]:
        """
        Performs an isolated verification test against a target Confluence instance
        without mutating the current active client instance.
        """
        clean_url = (base_url or "").strip().rstrip("/")
        clean_email = (email or "").strip()
        clean_token = (api_token or "").strip()
        clean_space = (space_key or "").strip().upper()

        if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
            return {
                "success": False,
                "status_code": 400,
                "message": "Invalid URL format. Confluence Base URL must start with https:// or http://",
            }

        if not clean_email or "@" not in clean_email:
            return {
                "success": False,
                "status_code": 400,
                "message": "Invalid email format. Please provide a valid Atlassian account email address.",
            }

        if not clean_token:
            return {
                "success": False,
                "status_code": 400,
                "message": "API token is required for live Confluence connection testing.",
            }

        if not clean_space:
            return {
                "success": False,
                "status_code": 400,
                "message": "Confluence Space Key is required.",
            }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Atlassian-Token": "no-check",
            "User-Agent": "CloudOps-AIAgent/1.0",
        }
        auth = (clean_email, clean_token)
        test_url = f"{clean_url}/wiki/rest/api/space/{clean_space}"

        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(test_url, auth=auth, headers=headers)
                if resp.status_code == 200:
                    space_data = resp.json()
                    space_name = space_data.get("name", clean_space)

                    # Query accessible pages count
                    count_url = f"{clean_url}/wiki/rest/api/content"
                    pages_count = 0
                    try:
                        count_resp = await client.get(
                            count_url,
                            params={"spaceKey": clean_space, "limit": 1},
                            auth=auth,
                            headers=headers,
                        )
                        if count_resp.status_code == 200:
                            pages_count = count_resp.json().get("size", 0)
                    except Exception:
                        pass

                    return {
                        "success": True,
                        "status_code": 200,
                        "message": f"Successfully verified! Space '{space_name}' ({clean_space}) is active and accessible.",
                        "space_name": space_name,
                        "space_key": clean_space,
                        "base_url": clean_url,
                        "user_email": clean_email,
                        "pages_accessible": pages_count,
                    }
                elif resp.status_code in (401, 403):
                    return {
                        "success": False,
                        "status_code": resp.status_code,
                        "message": f"Authentication failed (HTTP {resp.status_code}). Check that email ({clean_email}) and API token are correct and have access to space '{clean_space}'.",
                    }
                elif resp.status_code == 404:
                    return {
                        "success": False,
                        "status_code": 404,
                        "message": f"Space '{clean_space}' not found at {clean_url} (HTTP 404). Please verify that the space key is spelled correctly in Confluence.",
                    }
                else:
                    return {
                        "success": False,
                        "status_code": resp.status_code,
                        "message": f"Confluence returned error (HTTP {resp.status_code}): {resp.text[:200]}",
                    }
        except httpx.ConnectError:
            return {
                "success": False,
                "status_code": 0,
                "message": f"Cannot connect to host {clean_url}. Please check the domain name and your network connectivity.",
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "status_code": 0,
                "message": f"Connection to {clean_url} timed out (10s limit).",
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 500,
                "message": f"Connection test failed: {str(e)}",
            }

    async def check_health(self) -> Dict[str, Any]:
        """Validates connectivity to Confluence."""
        if self.use_mock:
            return {
                "status": "ok",
                "mode": "mock",
                "space": self.space_key,
                "base_url": self.base_url,
                "email": self.email,
                "pages_count": len(mock_store.pages)
            }

        url = f"{self.base_url}/wiki/rest/api/space/{self.space_key}"
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(url, auth=self.auth, headers=self._headers())
                if resp.status_code == 200:
                    space_data = resp.json()
                    return {
                        "status": "ok",
                        "mode": "live",
                        "space": self.space_key,
                        "space_name": space_data.get("name", self.space_key),
                        "base_url": self.base_url,
                        "email": self.email,
                        "data": space_data,
                    }
                return {
                    "status": "error",
                    "mode": "live",
                    "code": resp.status_code,
                    "space": self.space_key,
                    "base_url": self.base_url,
                    "email": self.email,
                    "message": resp.text[:200]
                }
        except Exception as e:
            logger.error(f"Confluence health check failed: {e}")
            return {
                "status": "error",
                "mode": "live",
                "space": self.space_key,
                "base_url": self.base_url,
                "email": self.email,
                "message": str(e)
            }

    async def search_pages(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Searches Confluence using CQL with intelligent keyword matching.
        Falls back to local store if running in mock mode, on error, or if zero results.
        """
        if self.use_mock:
            return mock_store.search_cql(query, self.space_key, limit=limit)

        stop_words = {"what", "is", "the", "and", "for", "a", "an", "to", "in", "of", "how", "should", "do", "i", "can", "are", "which", "contains", "with", "me"}
        terms = [t for t in re.findall(r'\w+', query) if len(t) > 1 and t.lower() not in stop_words][:6]
        if terms:
            cql_clauses = " OR ".join([f'text ~ "{t}" OR title ~ "{t}"' for t in terms])
            cql = f'space = "{self.space_key}" AND ({cql_clauses})'
        else:
            cql = f'space = "{self.space_key}"'

        url = f"{self.base_url}/wiki/rest/api/content/search"
        params = {
            "cql": cql,
            "limit": limit,
            "expand": "body.storage,version,history.lastUpdated",
        }

        try:
            async with httpx.AsyncClient(timeout=12.0) as client:
                resp = await client.get(url, params=params, auth=self.auth, headers=self._headers())
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for item in data.get("results", []):
                        body_content = item.get("body", {}).get("storage", {}).get("value", "")
                        page_url = f"{self.base_url}/wiki{item.get('_links', {}).get('webui', '')}"
                        results.append({
                            "id": item.get("id"),
                            "title": item.get("title"),
                            "spaceKey": self.space_key,
                            "version": item.get("version", {}).get("number", 1),
                            "lastUpdated": item.get("history", {}).get("lastUpdated", {}).get("when", ""),
                            "author": item.get("history", {}).get("lastUpdated", {}).get("by", {}).get("displayName", "CloudOps Team"),
                            "url": page_url,
                            "content": body_content,
                        })
                    if results:
                        return results
                    # If CQL returned 0, fallback to mock store
                    logger.info("CQL returned 0 results; falling back to knowledge store.")
                    return mock_store.search_cql(query, self.space_key, limit=limit)
                else:
                    logger.warning(f"Confluence CQL search returned HTTP {resp.status_code}. Falling back to mock store.")
                    return mock_store.search_cql(query, self.space_key, limit=limit)
        except Exception as e:
            logger.error(f"Error querying Confluence live API: {e}. Falling back to mock store.")
            return mock_store.search_cql(query, self.space_key, limit=limit)

    async def get_page_by_id(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves full page content and metadata by ID."""
        if self.use_mock:
            return mock_store.get_page_by_id(page_id)

        url = f"{self.base_url}/wiki/rest/api/content/{page_id}"
        params = {"expand": "body.storage,version,history.lastUpdated"}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params, auth=self.auth, headers=self._headers())
                if resp.status_code == 200:
                    item = resp.json()
                    return {
                        "id": item.get("id"),
                        "title": item.get("title"),
                        "spaceKey": self.space_key,
                        "version": item.get("version", {}).get("number", 1),
                        "lastUpdated": item.get("history", {}).get("lastUpdated", {}).get("when", ""),
                        "url": f"{self.base_url}/wiki{item.get('_links', {}).get('webui', '')}",
                        "content": item.get("body", {}).get("storage", {}).get("value", ""),
                    }
                return mock_store.get_page_by_id(page_id)
        except Exception as e:
            logger.error(f"Error fetching page {page_id} from Confluence: {e}")
            return mock_store.get_page_by_id(page_id)

    async def get_page_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Retrieves page by title within configured space."""
        if self.use_mock:
            return mock_store.get_page_by_title(title, self.space_key)

        url = f"{self.base_url}/wiki/rest/api/content"
        params = {
            "title": title,
            "spaceKey": self.space_key,
            "expand": "body.storage,version,history.lastUpdated",
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, params=params, auth=self.auth, headers=self._headers())
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results:
                        item = results[0]
                        return {
                            "id": item.get("id"),
                            "title": item.get("title"),
                            "spaceKey": self.space_key,
                            "version": item.get("version", {}).get("number", 1),
                            "lastUpdated": item.get("history", {}).get("lastUpdated", {}).get("when", ""),
                            "url": f"{self.base_url}/wiki{item.get('_links', {}).get('webui', '')}",
                            "content": item.get("body", {}).get("storage", {}).get("value", ""),
                        }
                return mock_store.get_page_by_title(title, self.space_key)
        except Exception as e:
            logger.error(f"Error fetching page by title '{title}': {e}")
            return mock_store.get_page_by_title(title, self.space_key)

    async def create_or_update_page(self, title: str, content_html: str) -> Dict[str, Any]:
        """Creates or updates a page in Confluence Cloud."""
        if self.use_mock:
            new_id = str(len(mock_store.pages) + 1001)
            mock_store.pages[new_id] = {
                "id": new_id,
                "title": title,
                "spaceKey": self.space_key,
                "version": 1,
                "lastUpdated": "2026-09-15T12:00:00Z",
                "author": self.email,
                "url": f"{self.base_url}/wiki/spaces/{self.space_key}/pages/{new_id}/{title.replace(' ', '+')}",
                "content": content_html,
            }
            return {"status": "created", "id": new_id, "mode": "mock"}

        # Live Confluence create/update
        existing = await self.get_page_by_title(title)
        async with httpx.AsyncClient(timeout=15.0) as client:
            if existing and existing.get("id"):
                page_id = existing["id"]
                current_ver = existing.get("version", 1)
                update_url = f"{self.base_url}/wiki/rest/api/content/{page_id}"
                body = {
                    "version": {"number": current_ver + 1},
                    "title": title,
                    "type": "page",
                    "body": {
                        "storage": {
                            "value": content_html,
                            "representation": "storage"
                        }
                    }
                }
                resp = await client.put(update_url, json=body, auth=self.auth, headers=self._headers())
                return resp.json()
            else:
                create_url = f"{self.base_url}/wiki/rest/api/content"
                body = {
                    "type": "page",
                    "title": title,
                    "space": {"key": self.space_key},
                    "body": {
                        "storage": {
                            "value": content_html,
                            "representation": "storage"
                        }
                    }
                }
                resp = await client.post(create_url, json=body, auth=self.auth, headers=self._headers())
                return resp.json()

confluence_client = ConfluenceClient()
