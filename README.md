# RAG Chatbot with ChromaDB, LangChain & LangGraph

A production-ready Retrieval Augmented Generation (RAG) chatbot built with ChromaDB, LangChain, LangGraph, and Google's Gemini model.

## 🏗️ Architecture

### LangGraph Workflow
```
START → CLASSIFIER → [products/returns] → RAG RESPONDER → END
                   → [general/unknown] → ESCALATION → END
```

### Components
- **Node 1: Classifier** - Categorizes queries (products/returns/general/unknown)
- **Node 2: RAG Responder** - Retrieves context and generates answers using RAG
- **Node 3: Escalation** - Handles out-of-scope queries with support information

## 📋 Features

- ✅ Document loading and chunking with LangChain
- ✅ Vector embeddings with ChromaDB
- ✅ Context-aware retrieval
- ✅ Google Gemini LLM integration
- ✅ Multi-node LangGraph workflow
- ✅ FastAPI REST API
- ✅ Query classification and routing
- ✅ Escalation handling

## 🚀 Setup

### Prerequisites
- Python 3.9+
- Google Gemini API key ([Get it here](https://makersuite.google.com/app/apikey))

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your Gemini API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

3. **Run the application:**
```bash
python -m src.main
```

The API will start at `http://localhost:8000`

## 📡 API Endpoints

### POST /chat
Send a query to the chatbot.

**Request:**
```json
{
  "query": "What is the price of SmartWatch Pro X?"
}
```

**Response:**
```json
{
  "query": "What is the price of SmartWatch Pro X?",
  "answer": "The SmartWatch Pro X is priced at ₹15,999.",
  "category": "products",
  "metadata": {
    "classifier": "success",
    "rag": {
      "context_used": true
    }
  }
}
```

### GET /health
Check service health.

### GET /docs
Interactive API documentation (Swagger UI).

## 🧪 Test Queries

### Product Queries
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What features does the SmartWatch have?"}'
```

### Return Policy Queries
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "How long do I have to return a product?"}'
```

### General Support Queries
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are your support hours?"}'
```

## 📁 Project Structure

```
RAG_assessment/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Configuration
│   ├── document_loader.py         # Document loading & splitting
│   ├── vectorstore.py             # ChromaDB vector store
│   ├── rag_chain.py               # RAG chain implementation
│   ├── langgraph_workflow.py      # LangGraph workflow
│   └── api/
│       ├── __init__.py
│       └── routes.py              # API routes
├── chroma_db/                     # ChromaDB storage (auto-created)
├── product_info.txt               # Knowledge base
├── requirements.txt               # Dependencies
├── .env                           # Environment variables
└── README.md                      # This file
```

## 🔧 Configuration

Edit `.env` to customize:

- `GOOGLE_API_KEY` - Your Gemini API key
- `CHUNK_SIZE` - Text chunk size (default: 200)
- `CHUNK_OVERLAP` - Chunk overlap (default: 50)
- `TOP_K_RESULTS` - Number of retrieved documents (default: 3)
- `TEMPERATURE` - LLM temperature (default: 0.7)

## 🎯 Query Categories

The classifier categorizes queries into:

1. **products** - Product features, prices, warranties
2. **returns** - Return policy, refunds, exchanges
3. **general** - Support hours, contact info
4. **unknown** - Out of scope queries (escalated)

## 🛠️ Tech Stack

- **LangChain** - Document processing & RAG pipeline
- **LangGraph** - Multi-node workflow orchestration
- **ChromaDB** - Vector database
- **Google Gemini** - LLM for classification & generation
- **FastAPI** - REST API framework
- **Pydantic** - Data validation

## 📝 Notes

- The vector store is created on first run and persisted to `chroma_db/`
- Subsequent runs will load the existing vector store
- To rebuild the vector store, delete the `chroma_db/` directory

## 🐛 Troubleshooting

**Error: GOOGLE_API_KEY not configured**
- Make sure you've added your API key to `.env` file

**Import errors**
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**Vector store errors**
- Delete `chroma_db/` folder and restart to rebuild

## 📄 License

MIT License
