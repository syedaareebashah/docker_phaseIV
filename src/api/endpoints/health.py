from fastapi import APIRouter
from typing import Dict

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint to verify the service is running."""
    return {"status": "healthy", "service": "todo-chatbot-api"}

@router.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint with service information."""
    return {
        "message": "Welcome to Todo AI Chatbot API",
        "status": "running",
        "version": "1.0.0"
    }