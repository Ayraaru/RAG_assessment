"""
Test script to verify the RAG chatbot setup
"""
import requests
import json
from typing import List, Dict


def test_chatbot(base_url: str = "http://localhost:8000"):
    """Test the RAG chatbot with various queries"""
    
    print("\n" + "="*70)
    print("🧪 Testing RAG Chatbot")
    print("="*70)
    
    # Test queries for different categories
    test_queries = [
        # Product queries
        {
            "query": "What is the price of SmartWatch Pro X?",
            "expected_category": "products"
        },
        {
            "query": "What features does the Power Bank have?",
            "expected_category": "products"
        },
        {
            "query": "Tell me about the Wireless Earbuds Elite",
            "expected_category": "products"
        },
        {
            "query": "What is the warranty period for SmartWatch?",
            "expected_category": "products"
        },
        # Return policy queries
        {
            "query": "How long do I have to return a product?",
            "expected_category": "returns"
        },
        {
            "query": "What is your refund policy?",
            "expected_category": "returns"
        },
        # General queries
        {
            "query": "What are your support hours?",
            "expected_category": "general"
        },
        {
            "query": "How can I contact support?",
            "expected_category": "general"
        },
        # Unknown queries
        {
            "query": "Can you help me fix my laptop?",
            "expected_category": "unknown"
        }
    ]
    
    # Check health first
    print("\n📍 Checking service health...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Service is healthy")
        else:
            print(f"❌ Service health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to service: {e}")
        print(f"Make sure the server is running at {base_url}")
        return
    
    # Test each query
    print("\n" + "-"*70)
    print("Testing queries...")
    print("-"*70)
    
    results = []
    for i, test in enumerate(test_queries, 1):
        query = test["query"]
        expected_category = test["expected_category"]
        
        print(f"\n[{i}/{len(test_queries)}] Query: \"{query}\"")
        print(f"Expected category: {expected_category}")
        
        try:
            response = requests.post(
                f"{base_url}/chat",
                json={"query": query},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                actual_category = data.get("category", "unknown")
                answer = data.get("answer", "")
                
                # Check if category matches
                category_match = actual_category == expected_category
                status = "✅" if category_match else "⚠️"
                
                print(f"{status} Actual category: {actual_category}")
                print(f"📝 Answer: {answer[:150]}{'...' if len(answer) > 150 else ''}")
                
                results.append({
                    "query": query,
                    "expected": expected_category,
                    "actual": actual_category,
                    "match": category_match,
                    "answer": answer
                })
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    
    total = len(results)
    matched = sum(1 for r in results if r["match"])
    
    print(f"\nTotal queries tested: {total}")
    print(f"Category matches: {matched}/{total} ({matched/total*100:.1f}%)")
    
    # Category breakdown
    print("\n📈 Category Breakdown:")
    categories = {}
    for result in results:
        cat = result["actual"]
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    print("\n" + "="*70)
    print("✅ Testing complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    test_chatbot(base_url)
