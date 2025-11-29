from sqlalchemy import Column, Integer, String, Text, Uuid, JSON
from db import Base
import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime

class AssistantQuery(Base):
    __tablename__ = "assistant_queries"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    user_query = Column(Text, nullable=False)
    assistant_response = Column(Text)
    structured_data = Column(JSON)
    tools_used = Column(JSON)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    total_tokens = Column(Integer)
    execution_time_ms = Column(Integer)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
