from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import get_db
from models.transaction import Transaction
from models.invoice import Invoice
from models.assistant_query import AssistantQuery
from groq import Groq
import os
import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import time
from logger import get_logger

# Initialize logger for this module
log = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["ai-assistant"])

# Request model
class AssistantRequest(BaseModel):
    query: str

# Tool definitions for Groq function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_transactions",
            "description": "Get transactions with optional filters. Returns list of transactions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date filter. Supports natural language like 'yesterday', 'last week', 'last month', 'last 7 days' or ISO format dates."},
                    "end_date": {"type": "string", "description": "End date filter. Supports natural language like 'today', 'now', 'end of last week' or ISO format dates."},
                    "status": {"type": "string", "enum": ["PENDING", "COMPLETED", "FAILED"]},
                    "currency": {"type": "string", "description": "3-letter currency code"},
                    "sender": {"type": "integer", "description": "User ID of sender"},
                    "receiver": {"type": "integer", "description": "User ID of receiver"},
                    "limit": {"type": "integer", "default": 50, "maximum": 50}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_invoices",
            "description": "Get invoices with optional filters. Returns list of invoices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date filter. Supports natural language like 'yesterday', 'last week', 'last month', 'last 7 days' or ISO format dates."},
                    "end_date": {"type": "string", "description": "End date filter. Supports natural language like 'today', 'now', 'end of last week' or ISO format dates."},
                    "status": {"type": "string", "enum": ["PAID", "UNPAID"]},
                    "sender": {"type": "integer", "description": "User ID of sender"},
                    "payer": {"type": "integer", "description": "User ID of payer"},
                    "limit": {"type": "integer", "default": 50, "maximum": 50}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_summary",
            "description": "Get aggregated summary of transactions and invoices with totals, averages, and breakdowns by status and currency.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date for summary. Supports natural language like 'beginning of this month', 'last month', '30 days ago' or ISO format dates."},
                    "end_date": {"type": "string", "description": "End date for summary. Supports natural language like 'today', 'now', 'end of month' or ISO format dates."}
                }
            }
        }
    }
]

def normalize_date_phrase(date_str: str) -> str:
    """Normalize common date phrases to more explicit forms for better dateparser compatibility."""
    if not date_str:
        return date_str

    # Normalize to lowercase for comparison
    normalized = date_str.lower().strip()

    # Map common phrases to explicit date expressions that dateparser understands better
    phrase_map = {
        # Today/Yesterday/Tomorrow - these work as-is
        'today': 'today',
        'yesterday': 'yesterday',
        'tomorrow': 'tomorrow',

        # This week - use "7 days ago" as approximation for start of week
        'this week': '7 days ago',

        # Last week
        'last week': '14 days ago',

        # This month - use first day
        'this month': 'first day of this month',
        'beginning of this month': 'first day of this month',
        'start of this month': 'first day of this month',

        # Last month
        'last month': 'first day of last month',
        'beginning of last month': 'first day of last month',

        # This year
        'this year': 'january 1 this year',
        'beginning of this year': 'january 1 this year',

        # Last year
        'last year': 'january 1 last year',
        'beginning of last year': 'january 1 last year',

        # End of periods - use last/end day variations
        'end of this week': 'today',  # Approximate end of this week as today
        'end of this month': 'last day of this month',
        'end of this year': 'december 31 this year',
        'end of last week': '7 days ago',
        'end of last month': 'last day of last month',
        'end of last year': 'december 31 last year',

        # Now/current
        'now': 'now',
        'current': 'now',

        # Days ago - these work as-is
        '1 day ago': 'yesterday',
        '2 days ago': '2 days ago',
        '3 days ago': '3 days ago',
        '7 days ago': '7 days ago',
        '30 days ago': '30 days ago',

        # Weeks ago
        '1 week ago': '7 days ago',
        '2 weeks ago': '14 days ago',
        '3 weeks ago': '21 days ago',
        '4 weeks ago': '28 days ago',

        # Months ago
        '1 month ago': '30 days ago',
        '2 months ago': '60 days ago',
        '3 months ago': '90 days ago',
        '6 months ago': '180 days ago',
    }

    # Check for exact match
    if normalized in phrase_map:
        result = phrase_map[normalized]
        log.debug(f"Normalized '{date_str}' to '{result}'")
        return result

    # Return original if no match found
    return date_str

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string using dateparser for natural language support."""
    if not date_str:
        return None

    log.debug(f"Parsing date string: {date_str}")

    try:
        # Try parsing as ISO format first
        parsed = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        log.debug(f"Successfully parsed ISO date: {parsed}")
        return parsed
    except Exception as e:
        log.debug(f"ISO format parsing failed: {e}, trying natural language parsing")

    # Normalize common phrases before parsing
    normalized_str = normalize_date_phrase(date_str)

    # Use dateparser for natural language
    try:
        import dateparser
        parsed = dateparser.parse(
            normalized_str,
            settings={
                'TIMEZONE': 'UTC',
                'RETURN_AS_TIMEZONE_AWARE': True,
                'PREFER_DATES_FROM': 'past',  # For queries like "last month"
                'RELATIVE_BASE': datetime.now(timezone.utc),
                'STRICT_PARSING': False,  # Allow flexible parsing
            }
        )

        if parsed is None:
            log.error(f"dateparser returned None for: {date_str} (normalized: {normalized_str})")
            raise HTTPException(status_code=400, detail=f"Could not understand date: {date_str}")

        log.debug(f"Successfully parsed natural language date '{date_str}' (normalized: '{normalized_str}') to {parsed}")
        return parsed
    except ImportError:
        log.error("dateparser library not installed")
        raise HTTPException(status_code=500, detail="Date parsing library not available")
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to parse date '{date_str}': {e}")
        raise HTTPException(status_code=400, detail=f"Could not parse date: {date_str}")

def execute_tool(tool_name: str, tool_args: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Execute a tool function and return results."""
    log.info(f"Executing tool: {tool_name}", extra={"tool_args": tool_args})

    if tool_name == "get_transactions":
        query = db.query(Transaction)

        # Apply filters
        if tool_args.get("start_date"):
            start_date = parse_date(tool_args["start_date"])
            if start_date:
                query = query.filter(Transaction.created_at >= start_date)

        if tool_args.get("end_date"):
            end_date = parse_date(tool_args["end_date"])
            if end_date:
                query = query.filter(Transaction.created_at <= end_date)

        if tool_args.get("status"):
            query = query.filter(Transaction.status == tool_args["status"])

        if tool_args.get("currency"):
            query = query.filter(Transaction.currency == tool_args["currency"])

        if tool_args.get("sender"):
            query = query.filter(Transaction.sender == tool_args["sender"])

        if tool_args.get("receiver"):
            query = query.filter(Transaction.receiver == tool_args["receiver"])

        limit = min(tool_args.get("limit", 50), 50)
        transactions = query.limit(limit).all()

        result = {
            "transactions": [
                {
                    "id": str(t.id),
                    "sender": t.sender,
                    "receiver": t.receiver,
                    "currency": t.currency,
                    "amount": float(t.amount),
                    "status": t.status,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                }
                for t in transactions
            ],
            "count": len(transactions)
        }
        log.info(f"get_transactions returned {len(transactions)} results")
        return result

    elif tool_name == "get_invoices":
        query = db.query(Invoice)

        # Apply filters
        if tool_args.get("start_date"):
            start_date = parse_date(tool_args["start_date"])
            if start_date:
                query = query.filter(Invoice.created_at >= start_date)

        if tool_args.get("end_date"):
            end_date = parse_date(tool_args["end_date"])
            if end_date:
                query = query.filter(Invoice.created_at <= end_date)

        if tool_args.get("status"):
            query = query.filter(Invoice.status == tool_args["status"])

        if tool_args.get("sender"):
            query = query.filter(Invoice.sender == tool_args["sender"])

        if tool_args.get("payer"):
            query = query.filter(Invoice.payer == tool_args["payer"])

        limit = min(tool_args.get("limit", 50), 50)
        invoices = query.limit(limit).all()

        result = {
            "invoices": [
                {
                    "id": i.id,
                    "sender": i.sender,
                    "payer": i.payer,
                    "amount": float(i.amount),
                    "status": i.status,
                    "lineItems": i.lineItems,
                    "created_at": i.created_at.isoformat() if i.created_at else None
                }
                for i in invoices
            ],
            "count": len(invoices)
        }
        log.info(f"get_invoices returned {len(invoices)} results")
        return result

    elif tool_name == "get_summary":
        start_date = parse_date(tool_args.get("start_date")) if tool_args.get("start_date") else None
        end_date = parse_date(tool_args.get("end_date")) if tool_args.get("end_date") else None

        # Use defaults if not provided
        if not start_date:
            from datetime import timedelta
            start_date = datetime.now(timezone.utc) - timedelta(days=30)
        if not end_date:
            end_date = datetime.now(timezone.utc)

        # Transaction queries
        transaction_query = db.query(Transaction).filter(
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        )

        # Invoice queries
        invoice_query = db.query(Invoice).filter(
            Invoice.created_at >= start_date,
            Invoice.created_at <= end_date
        )

        # Get aggregated data
        total_transactions = transaction_query.count()
        total_transaction_amount = transaction_query.with_entities(func.sum(Transaction.amount)).scalar() or 0

        total_invoices = invoice_query.count()
        total_invoice_amount = invoice_query.with_entities(func.sum(Invoice.amount)).scalar() or 0
        unpaid_invoices = invoice_query.filter(Invoice.status == "UNPAID").count()
        unpaid_amount = invoice_query.filter(Invoice.status == "UNPAID").with_entities(func.sum(Invoice.amount)).scalar() or 0

        result = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "transactions": {
                "total_count": total_transactions,
                "total_amount": float(total_transaction_amount)
            },
            "invoices": {
                "total_count": total_invoices,
                "total_amount": float(total_invoice_amount),
                "unpaid_count": unpaid_invoices,
                "unpaid_amount": float(unpaid_amount)
            }
        }
        log.info(f"get_summary returned data for period {start_date} to {end_date}")
        return result

    else:
        log.error(f"Unknown tool requested: {tool_name}")
        raise ValueError(f"Unknown tool: {tool_name}")

@router.post("/ai-assistant")
def ai_assistant(request: AssistantRequest, db: Session = Depends(get_db)):
    """
    AI Assistant endpoint that accepts natural language queries and returns context-aware answers.
    Uses function calling to query transactions and invoices data.
    """
    start_time = time.time()
    log.info(f"AI Assistant request received", extra={"query": request.query})

    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        log.debug("Groq client initialized")

        # Initial message to LLM
        messages = [
            {
                "role": "system",
                "content": """You are a helpful financial assistant. Use the provided tools to answer questions about transactions and invoices.

IMPORTANT INSTRUCTIONS FOR DATE HANDLING:
- When users mention dates like "last week", "yesterday", "last month", "this year", etc., pass them EXACTLY as the user said them to the tool parameters
- Do NOT convert natural language dates to ISO format yourself
- Examples:
  - User says "last week" → use start_date="last week"
  - User says "yesterday" → use start_date="yesterday"
  - User says "last 30 days" → use start_date="last 30 days"
- The tools will handle parsing these natural language dates automatically

Always provide clear, concise answers with relevant data from the tools."""
            },
            {
                "role": "user",
                "content": request.query
            }
        ]

        tools_used = []
        tool_results = {}
        max_iterations = 3  # Limit to 3 tool calls
        log.debug(f"Starting LLM interaction loop (max {max_iterations} iterations)")

        for iteration in range(max_iterations):
            log.debug(f"LLM iteration {iteration + 1}/{max_iterations}")

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=1000
            )
            log.debug(f"Received LLM response for iteration {iteration + 1}")

            response_message = response.choices[0].message

            # Check if the model wants to call tools
            if not response_message.tool_calls:
                # No more tools to call, we have the final answer
                final_answer = response_message.content
                log.info(f"LLM provided final answer after {iteration + 1} iterations")
                break

            # Process tool calls
            log.info(f"LLM requested {len(response_message.tool_calls)} tool call(s)")
            messages.append(response_message)

            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                log.info(f"Processing tool call: {tool_name}")

                # Execute the tool
                try:
                    tool_result = execute_tool(tool_name, tool_args, db)
                    tools_used.append({"name": tool_name, "arguments": tool_args})
                    tool_results[tool_name] = tool_result
                    log.debug(f"Tool {tool_name} executed successfully")

                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(tool_result)
                    })
                except Exception as e:
                    # Handle tool execution errors
                    error_msg = f"Error executing {tool_name}: {str(e)}"
                    log.error(f"Tool execution failed", extra={
                        "tool_name": tool_name,
                        "error": str(e),
                        "tool_args": tool_args
                    }, exc_info=True)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps({"error": error_msg})
                    })
        else:
            # Hit max iterations
            log.warning(f"Reached max iterations ({max_iterations}) without final answer")
            final_answer = "I've gathered the data but need more iterations to complete the analysis."

        # Calculate execution time and token usage
        execution_time_ms = int((time.time() - start_time) * 1000)
        log.debug(f"Request execution time: {execution_time_ms}ms")

        # Extract token usage
        prompt_tokens = getattr(response.usage, 'prompt_tokens', None)
        completion_tokens = getattr(response.usage, 'completion_tokens', None)
        total_tokens = getattr(response.usage, 'total_tokens', None)
        log.debug(f"Token usage - Prompt: {prompt_tokens}, Completion: {completion_tokens}, Total: {total_tokens}")

        # Save query log to database
        log.debug("Saving query log to database")
        query_log = AssistantQuery(
            user_query=request.query,
            assistant_response=final_answer,
            structured_data=tool_results,
            tools_used=tools_used,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            execution_time_ms=execution_time_ms
        )
        db.add(query_log)
        db.commit()
        db.refresh(query_log)
        log.info(f"Query logged successfully", extra={"query_id": str(query_log.id)})

        return {
            "query_id": str(query_log.id),
            "natural_language": final_answer,
            "structured_data": tool_results,
            "metadata": {
                "tools_used": [t["name"] for t in tools_used],
                "execution_time_ms": execution_time_ms,
                "tokens": {
                    "prompt": prompt_tokens,
                    "completion": completion_tokens,
                    "total": total_tokens
                }
            }
        }

    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        log.error(f"AI Assistant request failed after {execution_time_ms}ms", extra={
            "query": request.query,
            "error": str(e),
            "execution_time_ms": execution_time_ms
        }, exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"AI Assistant error: {str(e)}")
