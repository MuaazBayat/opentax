from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models.user import User
from models.transaction import Transaction
from models.invoice import Invoice
from groq import Groq
import os
import json
from datetime import datetime

router = APIRouter(prefix="/generate", tags=["generate"])

@router.post("/payments")
def generate_payments(db: Session = Depends(get_db), n: int = 15):
    # Get valid user IDs from the database
    users = db.query(User.id).all()
    if not users:
        raise HTTPException(status_code=400, detail="No users found in database. Please create users first.")

    user_ids = [user.id for user in users]

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"You need to generate payment transactions based on this data model, class Transaction(Base): sender = Column(Integer, ForeignKey('users.id'), index=True)  receiver = Column(Integer, ForeignKey('users.id'), index=True) currency = Column(String) amount = Column(Double)  status = Column(String) created_at = Column(DateTime). The sender and receiver MUST be selected from this list of valid user IDs: {user_ids}. The currency should be one of: USD, EUR, GBP, JPY, CNY, CAD. The amount is a positive float. The status can be PENDING, COMPLETED, or FAILED. The created_at should be a random datetime between October 1, 2025 and November 30, 2025 in ISO format (e.g., '2025-10-15T14:30:00'). Generate {n} transactions with random valid data using ONLY the user IDs provided, and spread the created_at dates across October and November 2025. BALNACE THE TRANSACTIONS EVENLY ACROSS THE MONTHS. You should only respond with a list of transaction objects. DO NOT RETURN CODE OR ANYTHING ELSE.  ONLY THE LIST",
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    # Parse the AI response
    ai_response = chat_completion.choices[0].message.content

    try:
        # Parse the JSON response
        transactions_data = json.loads(ai_response)

        # Create Transaction objects and insert them into the database
        created_transactions = []
        for transaction_data in transactions_data:
            # Parse created_at if provided
            created_at = None
            if "created_at" in transaction_data:
                created_at_str = transaction_data.get("created_at")
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                except:
                    pass  # Will use default if parsing fails

            transaction = Transaction(
                sender=transaction_data.get("sender"),
                receiver=transaction_data.get("receiver"),
                currency=transaction_data.get("currency"),
                amount=transaction_data.get("amount"),
                status=transaction_data.get("status"),
                created_at=created_at
            )
            db.add(transaction)
            created_transactions.append(transaction)

        # Commit all transactions to the database
        db.commit()

        # Refresh to get the generated IDs
        for transaction in created_transactions:
            db.refresh(transaction)

        return {
            "success": True,
            "message": f"Successfully inserted {len(created_transactions)} transactions",
            "transactions": created_transactions
        }

    except json.JSONDecodeError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to insert transactions: {str(e)}")

@router.post("/invoices")
def generate_invoices(db: Session = Depends(get_db), n: int = 15):
    # Get valid user IDs from the database
    users = db.query(User.id).all()
    if not users:
        raise HTTPException(status_code=400, detail="No users found in database. Please create users first.")

    user_ids = [user.id for user in users]

    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"You need to generate invoices based on this data model, class Invoice(Base): sender = Column(Integer, ForeignKey('users.id'), index=True)  payer = Column(Integer, ForeignKey('users.id'), index=True) amount = Column(Double) currency = Column(String) lineItems = Column(String) status = Column(String) created_at = Column(DateTime). The sender and payer MUST be selected from this list of valid user IDs: {user_ids}. The amount is a positive float. The currency should be one of: USD, EUR, GBP, JPY, CNY, CAD. The lineItems should be a JSON string containing an array of line item objects with fields like description, quantity, and price. The status can be PAID or UNPAID. The created_at should be a random datetime between October 1, 2025 and November 30, 2025 in ISO format (e.g., '2025-10-15T14:30:00'). Generate {n} invoices with random valid data using ONLY the user IDs provided, and spread the created_at dates across October and November 2025. BALANCE THE INVOCIES EVENLY ACROSS THE MONTHS. You should only respond with a list of invoice objects. DO NOT RETURN CODE OR ANYTHING ELSE.  ONLY THE LIST",
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    # Parse the AI response
    ai_response = chat_completion.choices[0].message.content

    try:
        # Parse the JSON response
        invoices_data = json.loads(ai_response)

        # Create Invoice objects and insert them into the database
        created_invoices = []
        for invoice_data in invoices_data:
            # Convert lineItems to string if it's not already
            line_items = invoice_data.get("lineItems")
            if isinstance(line_items, (list, dict)):
                line_items = json.dumps(line_items)

            # Parse created_at if provided
            created_at = None
            if "created_at" in invoice_data:
                created_at_str = invoice_data.get("created_at")
                try:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                except:
                    pass  # Will use default if parsing fails

            invoice = Invoice(
                sender=invoice_data.get("sender"),
                payer=invoice_data.get("payer"),
                amount=invoice_data.get("amount"),
                currency=invoice_data.get("currency", "USD"),
                lineItems=line_items,
                status=invoice_data.get("status", "UNPAID"),
                created_at=created_at
            )
            db.add(invoice)
            created_invoices.append(invoice)

        # Commit all invoices to the database
        db.commit()

        # Refresh to get the generated IDs
        for invoice in created_invoices:
            db.refresh(invoice)

        return {
            "success": True,
            "message": f"Successfully inserted {len(created_invoices)} invoices",
            "invoices": created_invoices
        }

    except json.JSONDecodeError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to insert invoices: {str(e)}")
