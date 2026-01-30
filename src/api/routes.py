"""
FastAPI Routes Module
API endpoints for the RAG chatbot
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    query: str = Field(..., description="User's question", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the price of SmartWatch Pro X?"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    query: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Chatbot's answer")
    category: Optional[str] = Field(None, description="Classified category")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the price of SmartWatch Pro X?",
                "answer": "The SmartWatch Pro X is priced at ₹15,999.",
                "category": "products",
                "metadata": {"classifier": "success", "rag": {"context_used": True}}
            }
        }


# Create router
router = APIRouter()


# This will be set by the main app
workflow = None


def set_workflow(workflow_instance):
    """Set the workflow instance"""
    global workflow
    workflow = workflow_instance


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint for RAG chatbot
    
    Args:
        request: ChatRequest with user query
        
    Returns:
        ChatResponse with answer and metadata
    """
    if workflow is None:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service is not initialized. Please try again later."
        )
    
    try:
        # Process query through LangGraph workflow
        result = workflow.invoke(request.query)
        
        # Return response
        return ChatResponse(
            query=result["query"],
            answer=result["answer"],
            category=result.get("category"),
            metadata=result.get("metadata")
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "RAG Chatbot",
        "workflow_initialized": workflow is not None
    }
