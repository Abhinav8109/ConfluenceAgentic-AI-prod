"""
Confluence Mock Store
Provides full offline/test fidelity with the 8 Confluence knowledge pages.
Supports CQL-like keyword search, page retrieval by ID or title, space discovery, and metadata querying.
"""

import re
from typing import List, Dict, Any, Optional
from app.confluence.seed_data import SEED_PAGES

class ConfluenceMockStore:
    def __init__(self, space_key: str = "AITEST"):
        self.space_key = space_key
        self.pages: Dict[str, Dict[str, Any]] = {p["id"]: dict(p) for p in SEED_PAGES}

    def get_space(self, space_key: Optional[str] = None) -> Dict[str, Any]:
        target = space_key or self.space_key
        return {
            "key": target,
            "name": "CloudOps AI Agent Knowledge Base",
            "type": "global",
            "description": "Primary operational documentation for CloudOps team"
        }

    def list_pages(self, space_key: Optional[str] = None) -> List[Dict[str, Any]]:
        target = space_key or self.space_key
        return [
            {
                "id": p["id"],
                "title": p["title"],
                "spaceKey": p["spaceKey"],
                "version": p["version"],
                "lastUpdated": p["lastUpdated"],
                "author": p["author"],
                "url": p["url"],
            }
            for p in self.pages.values()
            if p["spaceKey"].upper() == target.upper()
        ]

    def get_page_by_id(self, page_id: str) -> Optional[Dict[str, Any]]:
        return self.pages.get(str(page_id))

    def get_page_by_title(self, title: str, space_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
        target_space = space_key or self.space_key
        clean_target = title.strip().lower()
        for p in self.pages.values():
            if p["spaceKey"].upper() == target_space.upper() and p["title"].strip().lower() == clean_target:
                return p
        # Partial match fallback
        for p in self.pages.values():
            if p["spaceKey"].upper() == target_space.upper() and clean_target in p["title"].strip().lower():
                return p
        return None

    def search_cql(self, query: str, space_key: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Simulates Confluence CQL search: title ~ query OR text ~ query
        Ranks pages based on term occurrence, title match, and keyword presence.
        """
        target_space = space_key or self.space_key
        query_terms = [t.lower() for t in re.findall(r'\w+', query) if len(t) > 2]
        
        results = []
        for p in self.pages.values():
            if target_space and p["spaceKey"].upper() != target_space.upper():
                continue
                
            title_lower = p["title"].lower()
            content_lower = p["content"].lower()
            
            score = 0
            # Title matches are weighted heavily
            for term in query_terms:
                if term in title_lower:
                    score += 20
                # Content matches
                count = content_lower.count(term)
                score += min(count * 2, 20)

            # Extra domain-specific boosting
            if "p1" in query.lower() or "p2" in query.lower() or "p3" in query.lower() or "incident" in query.lower():
                if "incident" in title_lower:
                    score += 15
                if "escalation" in title_lower:
                    score += 10
            if "gcp" in query.lower() or "gke" in query.lower() or "cloud run" in query.lower():
                if "gcp" in title_lower:
                    score += 15
            if "aws" in query.lower() or "ec2" in query.lower() or "s3" in query.lower():
                if "aws" in title_lower:
                    score += 15
            if "rollback" in query.lower() or "change" in query.lower() or "rfc" in query.lower():
                if "change" in title_lower:
                    score += 15
            if "escalat" in query.lower() or "who" in query.lower() or "contact" in query.lower() or "team" in query.lower():
                if "escalation" in title_lower:
                    score += 15
            if "clean" in query.lower() or "disk" in query.lower() or "purge" in query.lower() or "finops" in query.lower():
                if "cleanup" in title_lower:
                    score += 15

            if score > 0:
                results.append((score, p))

        # Sort descending by score
        results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in results[:limit]]

mock_store = ConfluenceMockStore()
