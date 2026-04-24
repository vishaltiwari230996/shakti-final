from collections import deque
from datetime import datetime
from typing import Deque, Dict, List, Optional
import uuid

from app.models import OptimizationHistoryEntry, ListingResult

HISTORY_DB: Dict[str, Deque[OptimizationHistoryEntry]] = {}
HISTORY_LIMIT = 50

class HistoryService:
    """Simple in-memory storage for optimization history per user."""

    @staticmethod
    def record_entry(
        user_id: str,
        *,
        mode: str,
        prev_title: str = "",
        prev_desc: str = "",
        product_link: Optional[str] = "",
        final: Optional[ListingResult] = None,
        row_id: Optional[int] = None,
    ) -> OptimizationHistoryEntry:
        entry = OptimizationHistoryEntry(
            entry_id=str(uuid.uuid4()),
            mode=mode,
            created_at=datetime.utcnow().isoformat(),
            prev_title=prev_title,
            prev_desc=prev_desc,
            product_link=product_link,
            final=final,
            row_id=row_id,
        )

        history = HISTORY_DB.setdefault(user_id, deque(maxlen=HISTORY_LIMIT))
        history.appendleft(entry)
        return entry

    @staticmethod
    def get_history(user_id: str) -> List[OptimizationHistoryEntry]:
        history = HISTORY_DB.get(user_id)
        if not history:
            return []
        return list(history)
