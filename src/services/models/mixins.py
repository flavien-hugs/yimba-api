from datetime import datetime
from typing import Optional

from beanie import after_event, Update


class TimestampModel:
    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()

    @after_event(Update)
    def set_updated_at(self):
        self.updated_at = datetime.now()
