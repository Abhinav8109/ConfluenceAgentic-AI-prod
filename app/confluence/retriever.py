"""
Confluence Knowledge Retrieval Layer
Handles query intent analysis, multi-page retrieval, section extraction,
relevance ranking (Highly Relevant, Relevant, Related), and synthesis prep.
"""

import re
import logging
from typing import List, Dict, Any, Tuple
from app.confluence.client import confluence_client, ConfluenceClient

logger = logging.getLogger("cloudops.retriever")

class ConfluenceRetriever:
    def __init__(self, client: ConfluenceClient = confluence_client):
        self.client = client

    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyzes the user's question to determine intent, key entities,
        target domains (GCP, AWS, Incident, Change, Cleanup, Escalation),
        and whether this is a direct page recommendation inquiry.
        """
        q = query.lower()
        is_page_rec = any(phrase in q for phrase in [
            "which page", "where can i find", "recommend the best page",
            "what page contains", "which confluence page", "where is the",
            "what document", "which runbook"
        ])

        intents = []
        if any(term in q for term in ["p1", "p2", "p3", "incident", "severity", "outage", "downtime"]):
            intents.append("incident_management")
        if any(term in q for term in ["escalat", "who should be notified", "who to call", "contact", "matrix", "pager"]):
            intents.append("escalation")
        if any(term in q for term in ["rollback", "change", "rfc", "cab", "release", "deploy"]):
            intents.append("change_management")
        if any(term in q for term in ["gcp", "gke", "cloud run", "google cloud", "compute engine", "vpc", "iam"]):
            intents.append("gcp_troubleshooting")
        if any(term in q for term in ["aws", "ec2", "eks", "s3", "cloudwatch", "ssm"]):
            intents.append("aws_troubleshooting")
        if any(term in q for term in ["cleanup", "idle", "unattached", "purge", "cost", "finops", "decommission"]):
            intents.append("resource_cleanup")
        if any(term in q for term in ["difference", "compare", "comparison", "versus", "vs"]):
            intents.append("cross_domain_comparison")

        return {
            "is_page_recommendation": is_page_rec,
            "intents": intents,
            "raw_query": query,
        }

    async def retrieve_knowledge(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """
        Executes multi-page retrieval, scores candidate pages,
        ranks them by qualitative relevance, and extracts the most relevant sections.
        """
        analysis = self.analyze_query_intent(query)
        q_lower = query.lower()
        
        # 1. Primary search query
        pages = await self.client.search_pages(query, limit=10)
        
        # 2. Multi-intent expansion if needed
        # e.g., if query mentions P2 GCP incident + rollback, ensure all relevant topics are fetched
        if "rollback" in q_lower and ("p1" in q_lower or "p2" in q_lower or "incident" in q_lower):
            # Ensure Change Management & Incident Management are both fetched
            extra_pages = await self.client.search_pages("rollback change procedure", limit=3)
            seen_ids = {p["id"] for p in pages}
            for ep in extra_pages:
                if ep["id"] not in seen_ids:
                    pages.append(ep)
                    seen_ids.add(ep["id"])

        if "escalat" in q_lower or "who" in q_lower:
            matrix_pages = await self.client.search_pages("escalation matrix contact", limit=3)
            seen_ids = {p["id"] for p in pages}
            for mp in matrix_pages:
                if mp["id"] not in seen_ids:
                    pages.append(mp)
                    seen_ids.add(mp["id"])

        if not pages:
            return {
                "pages": [],
                "page_recommendations": [],
                "has_results": False,
                "analysis": analysis,
            }

        # 3. Score and rank retrieved pages
        scored_pages: List[Tuple[float, str, Dict[str, Any], str]] = []
        for page in pages:
            score, relevance_label, why = self._score_page_relevance(page, query, analysis)
            if score > 0:
                extracted_sections = self._extract_relevant_sections(page["content"], query)
                scored_pages.append((score, relevance_label, page, extracted_sections))

        # Sort descending by score
        scored_pages.sort(key=lambda x: x[0], reverse=True)
        top_candidates = scored_pages[:top_k]

        ranked_results = []
        recommendations = []
        for idx, (score, label, page, sections) in enumerate(top_candidates):
            entry = {
                "id": page["id"],
                "title": page["title"],
                "spaceKey": page.get("spaceKey", "AITEST"),
                "version": page.get("version", 1),
                "lastUpdated": page.get("lastUpdated", ""),
                "author": page.get("author", "CloudOps"),
                "url": page.get("url", ""),
                "relevance": label,
                "score": round(score, 2),
                "extracted_sections": sections,
                "summary": self._generate_page_summary(page["title"], sections),
            }
            ranked_results.append(entry)

            rec_item = {
                "rank": idx + 1,
                "title": page["title"],
                "url": page.get("url", ""),
                "relevance": label,
                "reason": self._explain_page_relevance(page["title"], query),
            }
            recommendations.append(rec_item)

        return {
            "pages": ranked_results,
            "page_recommendations": recommendations,
            "has_results": len(ranked_results) > 0,
            "analysis": analysis,
        }

    def _score_page_relevance(
        self, page: Dict[str, Any], query: str, analysis: Dict[str, Any]
    ) -> Tuple[float, str, str]:
        """
        Assigns score and qualitative label: Highly Relevant, Relevant, Related
        """
        title = page["title"].lower()
        content = page.get("content", "").lower()
        q = query.lower()
        terms = [t for t in re.findall(r'\w+', q) if len(t) > 2]

        score = 0.0
        # Title matches
        for t in terms:
            if t in title:
                score += 35.0
            if t in content:
                score += min(content.count(t) * 2.0, 20.0)

        # Domain intent weighting
        intents = analysis["intents"]
        if "incident_management" in intents and "incident" in title:
            score += 40.0
        if "escalation" in intents and "escalation" in title:
            score += 45.0
        if "change_management" in intents and "change" in title:
            score += 40.0
        if "gcp_troubleshooting" in intents and "gcp" in title:
            score += 40.0
        if "aws_troubleshooting" in intents and "aws" in title:
            score += 40.0
        if "resource_cleanup" in intents and "cleanup" in title:
            score += 40.0
        if "cross_domain_comparison" in intents:
            if ("incident" in q and "incident" in title) or ("change" in q and "change" in title):
                score += 35.0

        if score >= 60.0:
            return (score, "Highly Relevant", "Direct match with question intent and primary procedures.")
        elif score >= 30.0:
            return (score, "Relevant", "Contains supporting runbooks and cross-referenced workflows.")
        else:
            return (score, "Related", "Contains background operational context.")

    def _extract_relevant_sections(self, full_content: str, query: str, max_chars: int = 2500) -> str:
        """
        Extracts the most relevant headers and subsections from the page content.
        """
        sections = full_content.split("\n## ")
        if len(sections) <= 1:
            return full_content[:max_chars]

        q_terms = [t.lower() for t in re.findall(r'\w+', query) if len(t) > 2]
        scored_sections = []

        for sec in sections:
            sec_lower = sec.lower()
            sec_score = 0
            for term in q_terms:
                if term in sec_lower:
                    sec_score += sec_lower.count(term) * 5
            scored_sections.append((sec_score, sec))

        # Always include intro/top if present, then highest scoring sections
        scored_sections.sort(key=lambda x: x[0], reverse=True)
        selected = []
        char_count = 0
        for _, sec in scored_sections:
            formatted = f"## {sec}" if not sec.startswith("#") else sec
            if char_count + len(formatted) < max_chars:
                selected.append(formatted)
                char_count += len(formatted)

        return "\n\n".join(selected) if selected else full_content[:max_chars]

    def _generate_page_summary(self, title: str, extracted_content: str) -> str:
        lines = [line.strip() for line in extracted_content.split("\n") if line.strip().startswith("-") or line.strip().startswith("1.") or line.strip().startswith("2.")]
        if lines:
            return " ".join(lines[:3])[:200] + "..."
        return f"Operational guidance and runbook details from {title}."

    def _explain_page_relevance(self, page_title: str, query: str) -> str:
        q = query.lower()
        if "escalat" in q or "who" in q:
            if "Escalation" in page_title:
                return "Contains the escalation matrix, SLA response timelines, primary/secondary on-call rosters, and contact paths."
            if "Incident" in page_title:
                return "Outlines incident commander roles and the incident communication cadence."
        if "rollback" in q or "change" in q:
            if "Change" in page_title:
                return "Contains the formal change rollback criteria, step-by-step commands for GKE/Cloud Run, and RFC closure procedures."
            if "Incident" in page_title:
                return "Defines P1/P2 operational incident response and war room management."
        if "gke" in q or "gcp" in q:
            if "GCP" in page_title:
                return "Contains specific diagnostic sequences for GKE pods, crash loops, Cloud Run timeouts, and VPC networking."
        if "ec2" in q or "aws" in q:
            if "AWS" in page_title:
                return "Provides troubleshooting steps for EC2 status checks (0/2, 1/2), EKS node health, and S3 access issues."
        if "p1" in q or "p2" in q or "p3" in q:
            if "Incident" in page_title:
                return "Contains the definitive severity matrix (P1, P2, P3), response SLAs, and update intervals."
        return f"Authoritative documentation covering processes and procedures relevant to '{query}'."

confluence_retriever = ConfluenceRetriever()
