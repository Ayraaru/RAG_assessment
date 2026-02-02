"""
Comprehensive Test Script for RAG Chatbot API
Tests all endpoints and various query types
"""
import requests
import json
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_result(success: bool, message: str):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")


def test_health_endpoint() -> bool:
    """Test the health check endpoint"""
    print_header("Test 1: Health Check Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Service: {data.get('service')}")
            print(f"Workflow Initialized: {data.get('workflow_initialized')}")
            
            if data.get('workflow_initialized'):
                print_result(True, "Health check passed - Service is ready")
                return True
            else:
                print_result(False, "Service is running but workflow not initialized")
                return False
        else:
            print_result(False, f"Health check failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print_result(False, f"Health check failed: {str(e)}")
        return False


def test_chat_endpoint(query: str, expected_category: str = None) -> Dict[str, Any]:
    """Test the chat endpoint with a specific query"""
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"query": query},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📝 Query: {query}")
            print(f"📂 Category: {data.get('category', 'N/A')}")
            print(f"💬 Answer: {data.get('answer', 'N/A')[:200]}...")
            
            if expected_category and data.get('category') == expected_category:
                print_result(True, f"Correctly classified as '{expected_category}'")
            elif expected_category:
                print_result(False, f"Expected '{expected_category}' but got '{data.get('category')}'")
            else:
                print_result(True, "Query processed successfully")
            
            return data
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print_result(False, f"Request failed: {str(e)}")
        return None


def test_product_queries():
    """Test product-related queries"""
    print_header("Test 2: Product Queries")
    
    queries = [
        ("What is the price of SmartWatch Pro X?", "products"),
        ("What features does the SmartWatch have?", "products"),
        ("Tell me about the Wireless Earbuds Elite", "products"),
        ("What is the battery life of the Power Bank?", "products"),
    ]
    
    passed = 0
    total = len(queries)
    
    for query, expected_category in queries:
        result = test_chat_endpoint(query, expected_category)
        if result and result.get('category') == expected_category:
            passed += 1
        time.sleep(1)  # Small delay between requests
    
    print(f"\n📊 Product Queries: {passed}/{total} passed")
    return passed == total


def test_return_policy_queries():
    """Test return policy queries"""
    print_header("Test 3: Return Policy Queries")
    
    queries = [
        ("What is your return policy?", "returns"),
        ("How long do I have to return a product?", "returns"),
        ("How quickly will I get my refund?", "returns"),
        ("Can I return an opened product?", "returns"),
    ]
    
    passed = 0
    total = len(queries)
    
    for query, expected_category in queries:
        result = test_chat_endpoint(query, expected_category)
        if result and result.get('category') == expected_category:
            passed += 1
        time.sleep(1)
    
    print(f"\n📊 Return Policy Queries: {passed}/{total} passed")
    return passed == total


def test_general_queries():
    """Test general support queries"""
    print_header("Test 4: General Support Queries")
    
    queries = [
        ("What are your support hours?", "general"),
        ("How can I contact support?", "general"),
        ("What is the support email?", "general"),
    ]
    
    passed = 0
    total = len(queries)
    
    for query, expected_category in queries:
        result = test_chat_endpoint(query, expected_category)
        if result and result.get('category') == expected_category:
            passed += 1
        time.sleep(1)
    
    print(f"\n📊 General Queries: {passed}/{total} passed")
    return passed == total


def test_escalation_queries():
    """Test queries that should be escalated"""
    print_header("Test 5: Escalation/Unknown Queries")
    
    queries = [
        ("Can you help me with my laptop?", "unknown"),
        ("I need help with a different product", "unknown"),
        ("What's the weather today?", "unknown"),
    ]
    
    passed = 0
    total = len(queries)
    
    for query, expected_category in queries:
        result = test_chat_endpoint(query, expected_category)
        if result and result.get('category') == expected_category:
            passed += 1
        time.sleep(1)
    
    print(f"\n📊 Escalation Queries: {passed}/{total} passed")
    return passed == total


def test_response_time():
    """Test response time for queries"""
    print_header("Test 6: Response Time")
    
    query = "What is the price of SmartWatch Pro X?"
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"query": query},
            timeout=30
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        print(f"Query: {query}")
        print(f"Response Time: {response_time:.2f} seconds")
        
        if response.status_code == 200 and response_time < 10:
            print_result(True, f"Response time acceptable ({response_time:.2f}s)")
            return True
        elif response.status_code == 200:
            print_result(False, f"Response time too slow ({response_time:.2f}s)")
            return False
        else:
            print_result(False, "Request failed")
            return False
            
    except Exception as e:
        print_result(False, f"Response time test failed: {str(e)}")
        return False


def test_api_validation():
    """Test API validation with invalid requests"""
    print_header("Test 7: API Input Validation")
    
    print("\n🔍 Testing empty query...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"query": ""},
            timeout=5
        )
        
        if response.status_code == 422:
            print_result(True, "Correctly rejected empty query")
        else:
            print_result(False, f"Expected 422 but got {response.status_code}")
    except Exception as e:
        print_result(False, f"Validation test failed: {str(e)}")
    
    print("\n🔍 Testing missing query field...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={},
            timeout=5
        )
        
        if response.status_code == 422:
            print_result(True, "Correctly rejected missing query field")
        else:
            print_result(False, f"Expected 422 but got {response.status_code}")
    except Exception as e:
        print_result(False, f"Validation test failed: {str(e)}")


def run_all_tests():
    """Run all tests and provide summary"""
    print("\n" + "=" * 70)
    print("  RAG CHATBOT API - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run all tests
    results.append(("Health Check", test_health_endpoint()))
    
    if results[0][1]:  # Only continue if health check passes
        results.append(("Product Queries", test_product_queries()))
        results.append(("Return Policy Queries", test_return_policy_queries()))
        results.append(("General Queries", test_general_queries()))
        results.append(("Escalation Queries", test_escalation_queries()))
        results.append(("Response Time", test_response_time()))
        
        test_api_validation()
    else:
        print("\n⚠️  Skipping remaining tests - Health check failed")
        print("   Make sure the server is running: python -m src.main")
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n📊 Total: {passed}/{total} test groups passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The RAG chatbot is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test group(s) failed. Please review the results above.")
    
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_all_tests()
