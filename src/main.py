"""
Main FastAPI Application
Initializes and runs the RAG chatbot service
"""
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.document_loader import DocumentLoader
from src.vectorstore import VectorStore
from src.rag_chain import RAGChain
from src.langgraph_workflow import RAGWorkflow
from src.api import routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    
    # Startup
    print("\n" + "="*60)
    print("🚀 Starting RAG Chatbot Service")
    print("="*60)
    
    # Validate API key
    if not settings.google_api_key or settings.google_api_key == "your_gemini_api_key_here":
        print("\n❌ ERROR: GOOGLE_API_KEY not set!")
        print("Please set your Gemini API key in .env file")
        print("="*60 + "\n")
        raise ValueError("GOOGLE_API_KEY not configured")
    
    try:
        # Step 1: Load and split documents
        print("\n📄 Step 1: Loading documents...")
        doc_loader = DocumentLoader()
        documents = doc_loader.load_and_split(settings.knowledge_base_path)
        
        # Step 2: Create or load vector store
        print("\n🗄️  Step 2: Setting up vector store...")
        vectorstore = VectorStore()
        
        # Check if vector store already exists
        chroma_path = Path(settings.chroma_db_dir)
        if chroma_path.exists() and any(chroma_path.iterdir()):
            print("📂 Found existing vector store, loading...")
            vectorstore.load_vectorstore()
        else:
            print("📦 Creating new vector store...")
            vectorstore.create_vectorstore(documents)
        
        # Step 3: Create RAG chain
        print("\n🔗 Step 3: Building RAG chain...")
        rag_chain = RAGChain(vectorstore)
        print("✅ RAG chain initialized")
        
        # Step 4: Create LangGraph workflow
        print("\n🕸️  Step 4: Building LangGraph workflow...")
        workflow = RAGWorkflow(rag_chain)
        
        # Set workflow in routes
        routes.set_workflow(workflow)
        
        print("\n" + "="*60)
        print("✅ RAG Chatbot Service is ready!")
        print("="*60)
        print(f"📍 API docs available at: http://localhost:8000/docs")
        print(f"📍 Health check: http://localhost:8000/health")
        print(f"📍 Chat endpoint: POST http://localhost:8000/chat")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        print("="*60 + "\n")
        raise
    
    yield
    
    # Shutdown
    print("\n👋 Shutting down RAG Chatbot Service...")


# Create FastAPI app with lifespan
app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval Augmented Generation Chatbot using ChromaDB, LangChain, and LangGraph",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(routes.router, tags=["Chat"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to RAG Chatbot API",
        "docs": "/docs",
        "health": "/health",
        "chat_endpoint": "POST /chat"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False  # Disable reload for better performance
    )
