"""
Conversation Memory Manager
Maintains multi-turn context and conversational history for CloudOps Knowledge Assistant sessions.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import threading

class ConversationMemory:
    def __init__(self, max_history_turns: int = 10):
        self.max_history_turns = max_history_turns
        self._sessions: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = threading.Lock()

    def add_user_message(self, session_id: str, content: str):
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = []
            self._sessions[session_id].append({
                "role": "user",
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            self._trim_history(session_id)

    def add_assistant_message(self, session_id: str, content: str, sources: Optional[List[Dict[str, Any]]] = None):
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = []
            self._sessions[session_id].append({
                "role": "assistant",
                "content": content,
                "sources": sources or [],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            self._trim_history(session_id)

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._sessions.get(session_id, []))

    def clear_session(self, session_id: str):
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]

    def get_last_topic_context(self, session_id: str) -> str:
        """
        Extracts recent operational topics from previous turns to disambiguate follow-ups
        such as 'Who should be notified?' or 'What if it is on GKE?'.
        """
        history = self.get_history(session_id)
        if not history:
            return ""

        recent_texts = []
        for msg in reversed(history[-4:]):
            recent_texts.append(f"{msg['role'].upper()}: {msg['content']}")
        return "\n".join(reversed(recent_texts))

    def _trim_history(self, session_id: str):
        if len(self._sessions[session_id]) > self.max_history_turns * 2:
            self._sessions[session_id] = self._sessions[session_id][-self.max_history_turns * 2:]

conversation_memory = ConversationMemory()
