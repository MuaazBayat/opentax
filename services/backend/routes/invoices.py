from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db import get_db
from models.invoice import Invoice
from typing import List

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.get("/")
def get_invoices(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * page_size

    # Get total count
    total = db.query(Invoice).count()

    # Get paginated results
    invoices = db.query(Invoice).offset(offset).limit(page_size).all()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    return {
        "data": invoices,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

@router.delete("/")
def delete_all_invoices(db: Session = Depends(get_db)):
    # Count invoices before deletion
    count = db.query(Invoice).count()

    # Delete all invoices
    db.query(Invoice).delete()
    db.commit()

    return {
        "success": True,
        "message": f"Successfully deleted {count} invoices"
    }