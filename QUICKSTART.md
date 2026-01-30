# 🚀 Quick Start Guide

## Prerequisites Setup

### 1. Get Your Google Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 2. Configure the Application

Edit the `.env` file and replace the placeholder with your actual API key:

```bash
# Before:
GOOGLE_API_KEY=your_gemini_api_key_here

# After (example):
GOOGLE_API_KEY=AIzaSyD...your_actual_key_here
```

## Running the Application

### Method 1: Using the run script (Recommended)

```bash
./run.sh
```

### Method 2: Direct Python command

```bash
python -m src.main
```

The server will start at: **http://localhost:8000**

## Using the API

### 1. Check API Documentation

Open in browser: http://localhost:8000/docs

### 2. Test with curl

**Product Query:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the price of SmartWatch Pro X?"}'
```

**Return Policy Query:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "How long do I have to return a product?"}'
```

**Support Hours Query:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are your support hours?"}'
```

### 3. Test with Python

Run the test script:
```bash
python test_chatbot.py
```

### 4. Test with Web Interface

Visit: http://localhost:8000/docs and use the interactive Swagger UI

## Example Queries

### Products Category
- "What features does the SmartWatch have?"
- "Tell me about the Wireless Earbuds Elite"
- "What is the battery life of Power Bank?"
- "Compare SmartWatch and Earbuds warranties"

### Returns Category
- "What is your return policy?"
- "How long do I have to return items?"
- "How quickly will I get my refund?"

### General Category
- "What are your support hours?"
- "How can I contact support?"
- "What is the support email?"

### Unknown (Escalation)
- "Can you help me with my laptop?"
- "I need help with a different product"

## Expected Response Format

```json
{
  "query": "What is the price of SmartWatch Pro X?",
  "answer": "The SmartWatch Pro X is priced at ₹15,999.",
  "category": "products",
  "metadata": {
    "classifier": "success",
    "rag": {
      "sources": [...],
      "context_used": true
    }
  }
}
```

## Workflow Process

```
User Query
    ↓
Classifier Node (categorizes query)
    ↓
    ├─→ Products/Returns → RAG Responder (retrieves & generates answer)
    └─→ General/Unknown → Escalation (provides support contact)
    ↓
JSON Response
```

## Troubleshooting

### API Key Error
```
❌ ERROR: GOOGLE_API_KEY not set!
```
**Solution:** Edit `.env` file and add your actual API key

### Import Errors
```
ModuleNotFoundError: No module named 'xxx'
```
**Solution:** Run `pip install -r requirements.txt`

### Port Already in Use
```
ERROR: [Errno 98] Address already in use
```
**Solution:** Change port in `src/main.py` or kill the process using port 8000

### Vector Store Issues
**Solution:** Delete `chroma_db/` folder and restart to rebuild

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running

## Next Steps

1. ✅ Set up API key
2. ✅ Run the server
3. ✅ Test with example queries
4. ✅ Check the Swagger UI at /docs
5. ✅ Run the test script
6. 🎉 Start customizing for your use case!

---

For full documentation, see [README.md](README.md)
