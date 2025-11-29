from typing import Union
from db import get_db
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from models.user import User

from schemas.user import UserResponse

from routes.generate import router as generate_router
from routes.transactions import router as transactions_router
from routes.invoices import router as invoices_router
from routes.summary import router as summary_router
from routes.ai_assistant import router as ai_assistant_router
from routes.agent_logs import router as agent_logs_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate_router)
app.include_router(transactions_router)
app.include_router(invoices_router)
app.include_router(summary_router)
app.include_router(ai_assistant_router)
app.include_router(agent_logs_router)

@app.get("/")
def read_root():
    return {"Server Status": "Healthy"}

