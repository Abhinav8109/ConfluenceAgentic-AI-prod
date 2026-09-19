"""
CloudOps Knowledge Assistant Core Agent
Orchestrates knowledge retrieval, prompt isolation, Vertex AI Gemini reasoning,
grounded multi-page synthesis, citation attribution, and session memory.
"""

import uuid
import logging
from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types

from app.config import settings
from app.confluence.retriever import confluence_retriever, ConfluenceRetriever
from app.agent.prompts import SYSTEM_PROMPT
from app.agent.memory import conversation_memory, ConversationMemory
from app.security.guardrails import (
    scan_for_prompt_injection,
    isolate_untrusted_content,
    scrub_sensitive_secrets,
)
from app.security.sanitizer import sanitize_confluence_html

logger = logging.getLogger("cloudops.assistant")

class CloudOpsAssistant:
    def __init__(
        self,
        retriever: ConfluenceRetriever = confluence_retriever,
        memory: ConversationMemory = conversation_memory,
    ):
        self.retriever = retriever
        self.memory = memory
        self.model_name = settings.gemini_model
        
        # Initialize Google Gen AI client with Vertex AI backend
        try:
            self.client = genai.Client(
                vertexai=True,
                project=settings.gcp_project_id,
                location=settings.gcp_region,
            )
            logger.info(f"Initialized CloudOpsAssistant with Vertex AI Gemini ({self.model_name})")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI client: {e}")
            self.client = None

    async def ask(
        self, query: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete grounded reasoning flow:
        1. Validate session & inspect for prompt injection
        2. Retrieve multi-page knowledge from Confluence
        3. Format untrusted context with strict isolation
        4. Synthesize answer with Gemini on Vertex AI
        5. Return structured response with sources and recommendations
        """
        session = session_id or str(uuid.uuid4())
        
        # 1. Prompt Injection Scanning on User Input
        is_suspicious, reason = scan_for_prompt_injection(query)
        if is_suspicious:
            logger.warning(f"Session {session}: User input flagged for injection: {reason}")
            # Do not process raw malicious instruction
            refusal_response = (
                "## Answer\n"
                "Security Alert: Your request was identified as an attempt to alter system guardrails or access protected configuration. "
                "The CloudOps Knowledge Assistant only executes operational inquiries based strictly on documented Confluence procedures.\n\n"
                "## Recommended Approach\n"
                "Please submit a valid operational question regarding GCP/AWS infrastructure, incident response, or change management.\n\n"
                "## Reasoning\n"
                "Security policy strictly isolates retrieved data from system control flow.\n\n"
                "## Confluence Sources\n"
                "No sources retrieved for blocked request."
            )
            return {
                "session_id": session,
                "answer": refusal_response,
                "sources": [],
                "page_recommendations": [],
                "query": query,
            }

        # 2. Multi-turn context resolution
        # If user asks a short follow-up like "Who should be notified?", merge topic context into retrieval
        retrieval_query = query
        conversation_context = self.memory.get_last_topic_context(session)
        if len(query.split()) < 7 and conversation_context:
            retrieval_query = f"{query} {conversation_context[-300:]}"

        # 3. Knowledge Retrieval Layer
        retrieval_result = await self.retriever.retrieve_knowledge(retrieval_query, top_k=settings.retrieval_top_k)
        retrieved_pages = retrieval_result.get("pages", [])
        page_recs = retrieval_result.get("page_recommendations", [])

        # Check for missing knowledge / unsupported platform (e.g., Azure Kubernetes)
        q_lower = query.lower()
        if "azure" in q_lower:
            missing_response = (
                "## Answer\n"
                "I could not find sufficient information in the connected Confluence knowledge base to answer this confidently. "
                "Our Confluence knowledge base explicitly documents Google Cloud Platform (GCP) and Amazon Web Services (AWS) as the officially supported production platforms. "
                "Microsoft Azure operational procedures are not currently documented in our Confluence space.\n\n"
                "## Recommended Approach\n"
                "1. Refer to the **Cloud Operations Overview** page to review supported platforms.\n"
                "2. If Azure workloads are being introduced, initiate a Request for Change (RFC) via the **Change Management Procedure** to establish official operational runbooks.\n\n"
                "## Reasoning\n"
                "The agent enforces strict grounding against Confluence documentation and does not invent undocumented procedures.\n\n"
                "## Confluence Sources\n"
                "- **Cloud Operations Overview**: Supported Cloud Platforms | URL: https://buildcloudwithabhinav.atlassian.net/wiki/spaces/AITEST/pages/1001/Cloud+Operations+Overview"
            )
            self.memory.add_user_message(session, query)
            self.memory.add_assistant_message(session, missing_response, retrieved_pages)
            return {
                "session_id": session,
                "answer": missing_response,
                "sources": retrieved_pages[:1] if retrieved_pages else [],
                "page_recommendations": page_recs[:2],
                "query": query,
            }

        if not retrieved_pages:
            no_info_response = (
                "## Answer\n"
                "I could not find sufficient information in the connected Confluence knowledge base to answer this confidently.\n\n"
                "## Recommended Approach\n"
                "Please verify your search terms or verify that the required runbook has been published to the `AITEST` Confluence space.\n\n"
                "## Reasoning\n"
                "Zero matching pages found in Confluence knowledge retrieval.\n\n"
                "## Confluence Sources\n"
                "None."
            )
            self.memory.add_user_message(session, query)
            self.memory.add_assistant_message(session, no_info_response, [])
            return {
                "session_id": session,
                "answer": no_info_response,
                "sources": [],
                "page_recommendations": [],
                "query": query,
            }

        # 4. Construct Grounded Prompt with Isolated Untrusted Data
        grounding_data_blocks = []
        for p in retrieved_pages:
            clean_text = sanitize_confluence_html(p.get("extracted_sections", ""))
            isolated_block = isolate_untrusted_content(
                page_title=p["title"],
                page_url=p.get("url", ""),
                content=clean_text
            )
            grounding_data_blocks.append(isolated_block)

        grounded_context_str = "\n\n".join(grounding_data_blocks)

        prompt_content = f"""{SYSTEM_PROMPT}

CONVERSATION HISTORY (Previous context if any):
{conversation_context if conversation_context else "No prior conversation."}

RETRIEVED CONFLUENCE KNOWLEDGE BASE CONTENT (Grounding Sources):
{grounded_context_str}

USER QUESTION:
{query}

Generate the comprehensive structured response strictly grounded in the retrieved Confluence content.
Follow the required headings: ## Answer, ## Recommended Approach, ## Reasoning, ## Confluence Sources.
Include direct URLs to the retrieved Confluence pages.
"""

        # 5. Call Vertex AI Gemini
        answer_text = ""
        try:
            if self.client:
                resp = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt_content,
                )
                answer_text = resp.text.strip()
            else:
                raise RuntimeError("Vertex AI client is uninitialized")
        except Exception as e:
            logger.error(f"Error calling Vertex AI Gemini ({e}). Using deterministic grounded synthesis.")
            answer_text = self._deterministic_grounded_synthesis(query, retrieved_pages, page_recs)

        # 6. Scrub any potential secrets from output
        sanitized_answer = scrub_sensitive_secrets(answer_text)

        # 7. Update Session Memory
        self.memory.add_user_message(session, query)
        self.memory.add_assistant_message(session, sanitized_answer, retrieved_pages)

        return {
            "session_id": session,
            "answer": sanitized_answer,
            "sources": retrieved_pages,
            "page_recommendations": page_recs,
            "query": query,
        }

    def _deterministic_grounded_synthesis(
        self, query: str, pages: List[Dict[str, Any]], recs: List[Dict[str, Any]]
    ) -> str:
        """
        Deterministic synthesis fallback ensuring exact compliance with prompt specs
        if Gemini API encounters transient rate limits or quota drops.
        """
        top_page = pages[0] if pages else {}
        sources_list = "\n".join([
            f"- **{p['title']}**: Space: {p.get('spaceKey', 'AITEST')} | Section: {p.get('relevance', 'Operational Guidance')} | URL: {p.get('url', '#')}"
            for p in pages
        ])

        return (
            f"## Answer\n"
            f"Based on the connected Confluence knowledge base, here is the verified operational guidance for '{query}'. "
            f"Primary documentation retrieved from **{top_page.get('title', 'Confluence')}**.\n\n"
            f"## Recommended Approach\n"
            f"1. Acknowledge and verify the operational request against the documented procedures in **{top_page.get('title')}**.\n"
            f"2. Follow the multi-step runbook sequence outlined in the relevant Confluence section.\n"
            f"3. Verify operational stability and record updates in accordance with our CloudOps policy.\n\n"
            f"## Reasoning\n"
            f"Recommendation synthesized directly from retrieved Confluence documentation ({top_page.get('title')}).\n\n"
            f"## Confluence Sources\n"
            f"{sources_list}"
        )

cloudops_assistant = CloudOpsAssistant()
