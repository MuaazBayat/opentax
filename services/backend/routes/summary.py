from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from db import get_db
from models.transaction import Transaction
from models.invoice import Invoice
from datetime import datetime, timezone, timedelta
from typing import Optional
from currency_converter import convert_currency, get_supported_currencies
from logger import get_logger

log = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["summary"])

@router.get("/summary")
def get_summary(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering (ISO format). Defaults to 30 days ago."),
    end_date: Optional[datetime] = Query(None, description="End date for filtering (ISO format). Defaults to now."),
    target_currency: str = Query("USD", description="Target currency for conversion (USD, EUR, GBP, JPY, CNY, CAD)"),
    db: Session = Depends(get_db)
):
    # Set default date range to last 30 days if not provided
    if start_date is None:
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
    if end_date is None:
        end_date = datetime.now(timezone.utc)

    # Validate and normalize target currency
    target_currency = target_currency.upper()
    if target_currency not in get_supported_currencies():
        log.warning(f"Unsupported currency requested: {target_currency}, defaulting to USD")
        target_currency = "USD"

    log.info(f"Generating summary with target currency: {target_currency}")
    log.info(f"Date range filter: {start_date} to {end_date}")

    # Build base queries
    transaction_query = db.query(Transaction)
    invoice_query = db.query(Invoice)

    # Apply date filters
    transaction_query = transaction_query.filter(Transaction.created_at >= start_date)
    invoice_query = invoice_query.filter(Invoice.created_at >= start_date)
    transaction_query = transaction_query.filter(Transaction.created_at <= end_date)
    invoice_query = invoice_query.filter(Invoice.created_at <= end_date)

    log.info(f"Applied date filters: created_at >= {start_date} AND created_at <= {end_date}")

    # Fetch all transactions for conversion
    all_transactions = transaction_query.all()
    total_transactions = len(all_transactions)

    # Convert and aggregate transactions
    total_transaction_amount = 0
    transaction_status_map = {}

    for txn in all_transactions:
        # Convert amount to target currency
        try:
            converted_amount = convert_currency(float(txn.amount), txn.currency, target_currency)
            total_transaction_amount += converted_amount

            # Aggregate by status
            if txn.status not in transaction_status_map:
                transaction_status_map[txn.status] = {"count": 0, "total_amount": 0}
            transaction_status_map[txn.status]["count"] += 1
            transaction_status_map[txn.status]["total_amount"] += converted_amount
        except Exception as e:
            log.error(f"Failed to convert transaction {txn.id}: {e}")

    avg_transaction_amount = total_transaction_amount / total_transactions if total_transactions > 0 else 0

    # Format transaction by status
    transaction_by_status = [
        {
            "status": status,
            "count": data["count"],
            "total_amount": data["total_amount"]
        }
        for status, data in transaction_status_map.items()
    ]

    # Keep original currency breakdown (not converted)
    transaction_by_currency = db.query(
        Transaction.currency,
        func.count(Transaction.id).label('count'),
        func.sum(Transaction.amount).label('total_amount'),
        func.avg(Transaction.amount).label('avg_amount')
    ).filter(
        Transaction.created_at >= start_date,
        Transaction.created_at <= end_date
    ).group_by(Transaction.currency).all()

    # Fetch all invoices for conversion
    all_invoices = invoice_query.all()
    total_invoices = len(all_invoices)

    # Convert and aggregate invoices
    total_invoice_amount = 0
    unpaid_invoices_amount = 0
    unpaid_invoices_count = 0
    invoice_status_map = {}

    for inv in all_invoices:
        # Convert amount to target currency
        try:
            converted_amount = convert_currency(float(inv.amount), inv.currency, target_currency)
            total_invoice_amount += converted_amount

            # Track unpaid
            if inv.status == "UNPAID":
                unpaid_invoices_count += 1
                unpaid_invoices_amount += converted_amount

            # Aggregate by status
            if inv.status not in invoice_status_map:
                invoice_status_map[inv.status] = {"count": 0, "total_amount": 0}
            invoice_status_map[inv.status]["count"] += 1
            invoice_status_map[inv.status]["total_amount"] += converted_amount
        except Exception as e:
            log.error(f"Failed to convert invoice {inv.id}: {e}")

    avg_invoice_amount = total_invoice_amount / total_invoices if total_invoices > 0 else 0

    # Format invoice by status
    invoice_by_status = [
        {
            "status": status,
            "count": data["count"],
            "total_amount": data["total_amount"]
        }
        for status, data in invoice_status_map.items()
    ]

    # Calculate daily breakdown
    from collections import defaultdict
    daily_data = defaultdict(lambda: {
        "transaction_count": 0,
        "transaction_value": 0.0,
        "invoice_count": 0,
        "invoice_value": 0.0
    })

    # Aggregate transactions by day
    for txn in all_transactions:
        date_key = txn.created_at.date().isoformat()
        try:
            converted_amount = convert_currency(float(txn.amount), txn.currency, target_currency)
            daily_data[date_key]["transaction_count"] += 1
            daily_data[date_key]["transaction_value"] += converted_amount
        except Exception as e:
            log.error(f"Failed to process transaction {txn.id} for daily breakdown: {e}")

    # Aggregate invoices by day
    for inv in all_invoices:
        date_key = inv.created_at.date().isoformat()
        try:
            converted_amount = convert_currency(float(inv.amount), inv.currency, target_currency)
            daily_data[date_key]["invoice_count"] += 1
            daily_data[date_key]["invoice_value"] += converted_amount
        except Exception as e:
            log.error(f"Failed to process invoice {inv.id} for daily breakdown: {e}")

    # Format daily breakdown as sorted list
    daily_breakdown = [
        {
            "date": date,
            "transaction_count": data["transaction_count"],
            "transaction_value": float(data["transaction_value"]),
            "invoice_count": data["invoice_count"],
            "invoice_value": float(data["invoice_value"])
        }
        for date, data in sorted(daily_data.items())
    ]

    log.info(f"Generated {len(daily_breakdown)} days of data. Date range: {daily_breakdown[0]['date'] if daily_breakdown else 'N/A'} to {daily_breakdown[-1]['date'] if daily_breakdown else 'N/A'}")
    log.info(f"Total transactions: {total_transactions}, Total invoices: {total_invoices}")

    # Format response
    return {
        "filters": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "target_currency": target_currency
        },
        "transactions": {
            "total_count": total_transactions,
            "total_amount": float(total_transaction_amount),
            "average_amount": float(avg_transaction_amount),
            "by_status": transaction_by_status,
            "by_currency": [
                {
                    "currency": currency,
                    "count": count,
                    "total_amount": float(total_amount or 0),
                    "average_amount": float(avg_amount or 0)
                }
                for currency, count, total_amount, avg_amount in transaction_by_currency
            ]
        },
        "invoices": {
            "total_count": total_invoices,
            "total_amount": float(total_invoice_amount),
            "average_amount": float(avg_invoice_amount),
            "unpaid_count": unpaid_invoices_count,
            "unpaid_amount": float(unpaid_invoices_amount),
            "by_status": invoice_by_status
        },
        "daily_breakdown": daily_breakdown
    }
