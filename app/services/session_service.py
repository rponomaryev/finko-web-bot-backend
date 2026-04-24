from collections import defaultdict, deque
from typing import Dict, Deque, List


MAX_TURNS_PER_SESSION = 5

_sessions: Dict[str, Deque[dict]] = defaultdict(lambda: deque(maxlen=MAX_TURNS_PER_SESSION))


def add_user_message(session_id: str, content: str) -> None:
    _sessions[session_id].append({
        "role": "user",
        "content": content,
    })


def add_assistant_message(session_id: str, content: str) -> None:
    _sessions[session_id].append({
        "role": "assistant",
        "content": content,
    })


def get_session_history(session_id: str) -> List[dict]:
    return list(_sessions[session_id])


def clear_session(session_id: str) -> None:
    _sessions.pop(session_id, None)