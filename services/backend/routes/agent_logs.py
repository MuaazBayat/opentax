from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from db import get_db
from models.assistant_query import AssistantQuery
from datetime import datetime, timezone, timedelta
from typing import Optional
from logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["agent-logs"])

@router.get("/agent-logs")
def get_agent_logs(
    start_date: Optional[str] = Query(None, description="Start date (ISO format or natural language)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format or natural language)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get AI assistant activity logs with metrics and detailed query history.
    Defaults to last 24 hours if no date range provided.
    """
    log.info("Agent logs request received", extra={
        "start_date": start_date,
        "end_date": end_date,
        "page": page,
        "page_size": page_size
    })

    # Parse dates with defaults
    from routes.ai_assistant import parse_date

    try:
        start = parse_date(start_date) if start_date else datetime.now(timezone.utc) - timedelta(hours=24)
        end = parse_date(end_date) if end_date else datetime.now(timezone.utc)
    except Exception as e:
        log.error(f"Date parsing failed: {e}")
        # Fallback to defaults
        start = datetime.now(timezone.utc) - timedelta(hours=24)
        end = datetime.now(timezone.utc)

    log.debug(f"Using date range: {start} to {end}")

    # Base query for the time range
    base_query = db.query(AssistantQuery).filter(
        AssistantQuery.created_at >= start,
        AssistantQuery.created_at <= end
    )

    # Calculate summary metrics
    total_queries = base_query.count()

    # Queries with errors (assistant_response contains error indicators or structured_data has errors)
    error_queries = base_query.filter(
        (AssistantQuery.assistant_response.ilike('%error%')) |
        (AssistantQuery.assistant_response.ilike('%failed%'))
    ).count()

    # Average execution time
    avg_exec_time = base_query.with_entities(
        func.avg(AssistantQuery.execution_time_ms)
    ).scalar() or 0

    # Total tokens used
    total_tokens = base_query.with_entities(
        func.sum(AssistantQuery.total_tokens)
    ).scalar() or 0

    # Average tokens per query
    avg_tokens = base_query.with_entities(
        func.avg(AssistantQuery.total_tokens)
    ).scalar() or 0

    # Get paginated logs
    offset = (page - 1) * page_size
    logs = base_query.order_by(desc(AssistantQuery.created_at)).offset(offset).limit(page_size).all()

    total_pages = (total_queries + page_size - 1) // page_size if total_queries > 0 else 0

    # Format logs
    formatted_logs = []
    for query in logs:
        # Extract tool names from tools_used
        tools = []
        if query.tools_used:
            tools = [tool.get("name") if isinstance(tool, dict) else str(tool) for tool in query.tools_used]

        formatted_logs.append({
            "query_id": str(query.id),
            "timestamp": query.created_at.isoformat() if query.created_at else None,
            "user_query": query.user_query,
            "assistant_response": query.assistant_response,
            "tools_used": tools,
            "execution_time_ms": query.execution_time_ms,
            "tokens": {
                "prompt": query.prompt_tokens,
                "completion": query.completion_tokens,
                "total": query.total_tokens
            },
            "structured_data": query.structured_data
        })

    log.info(f"Returning {len(formatted_logs)} logs", extra={
        "total_queries": total_queries,
        "error_count": error_queries,
        "avg_exec_time_ms": avg_exec_time
    })

    return {
        "period": {
            "start_date": start.isoformat(),
            "end_date": end.isoformat()
        },
        "summary": {
            "total_queries": total_queries,
            "error_count": error_queries,
            "error_rate": round(error_queries / total_queries * 100, 2) if total_queries > 0 else 0,
            "avg_execution_time_ms": round(avg_exec_time, 2),
            "total_tokens_used": int(total_tokens),
            "avg_tokens_per_query": round(avg_tokens, 2)
        },
        "logs": formatted_logs,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total_queries,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }
