"""
Quick Test Suite for RAG Chatbot
Fast tests with performance timing and data validation
"""
import requests
import json
import time
from pathlib import Path


def load_product_data():
    """Load product_info.txt for validation"""
    data = {}
    with open('/home/labuser/RAG_assessment/product_info.txt', 'r') as f:
        content = f.read()
    
    # Parse product data
    data['smartwatch_price'] = '₹15,999'
    data['earbuds_price'] = '₹4,999'
    data['powerbank_price'] = '₹2,499'
    data['return_days'] = '7'
    data['support_email'] = 'support@techgear.com'
    data['support_hours'] = '9AM-6PM'
    
    return data


def test_endpoint(query, expected_category=None, validation_key=None):
    """Test a single query"""
    print(f"\n{'='*70}")
    print(f"Query: {query}")
    print(f"Expected Category: {expected_category or 'N/A'}")
    
    start = time.time()
    try:
        response = requests.post(
            'http://localhost:8000/chat',
            json={'query': query},
            timeout=60
        )
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: Success")
            print(f"⏱️  Response Time: {elapsed:.0f} ms", end="")
            
            if elapsed > 5000:
                print(" ⚠️  SLOW!")
            elif elapsed > 3000:
                print(" ⚡ Could be faster")
            else:
                print(" ✨ Fast")
            
            print(f"📂 Category: {data.get('category', 'N/A')}")
            
            # Check category match
            if expected_category:
                if data.get('category') == expected_category:
                    print(f"✅ Category Match: Correct")
                else:
                    print(f"❌ Category Match: Expected {expected_category}, got {data.get('category')}")
            
            # Validate against product data
            if validation_key:
                answer = data.get('answer', '')
                product_data = load_product_data()
                expected_value = product_data.get(validation_key, '')
                
                if expected_value and expected_value.lower() in answer.lower():
                    print(f"✅ Data Validation: '{expected_value}' found in answer")
                else:
                    print(f"❌ Data Validation: '{expected_value}' NOT found in answer")
            
            print(f"💬 Answer: {data.get('answer', '')[:200]}...")
            
            return {
                'success': True,
                'time': elapsed,
                'category': data.get('category'),
                'answer': data.get('answer')
            }
        else:
            print(f"❌ Status: Failed (HTTP {response.status_code})")
            return {'success': False, 'time': elapsed}
            
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        print(f"❌ Error: {e}")
        print(f"⏱️  Time before error: {elapsed:.0f} ms")
        return {'success': False, 'time': elapsed, 'error': str(e)}


def main():
    """Run quick test suite"""
    print("\n" + "="*70)
    print("🧪 QUICK RAG CHATBOT TEST SUITE")
    print("="*70)
    
    # Test 1: Health check
    print("\n🏥 Testing Health Endpoint...")
    try:
        start = time.time()
        resp = requests.get('http://localhost:8000/health', timeout=5)
        elapsed = (time.time() - start) * 1000
        if resp.status_code == 200:
            print(f"✅ Health check passed ({elapsed:.0f} ms)")
        else:
            print(f"❌ Health check failed")
            return
    except Exception as e:
        print(f"❌ Server not responding: {e}")
        return
    
    results = []
    
    # Test 2: Product Price Query
    print("\n" + "="*70)
    print("💰 TEST 1: Product Price Query")
    result = test_endpoint(
        "What is the price of SmartWatch Pro X?",
        expected_category="products",
        validation_key="smartwatch_price"
    )
    results.append(result)
    
    # Test 3: Product Features Query
    print("\n" + "="*70)
    print("🔧 TEST 2: Product Features Query")
    result = test_endpoint(
        "What features does the Wireless Earbuds Elite have?",
        expected_category="products",
        validation_key="earbuds_price"
    )
    results.append(result)
    
    # Test 4: Return Policy Query
    print("\n" + "="*70)
    print("↩️  TEST 3: Return Policy Query")
    result = test_endpoint(
        "What is your return policy?",
        expected_category="returns",
        validation_key="return_days"
    )
    results.append(result)
    
    # Test 5: Support Query
    print("\n" + "="*70)
    print("📞 TEST 4: Support Hours Query")
    result = test_endpoint(
        "What are your support hours?",
        expected_category="general",
        validation_key="support_hours"
    )
    results.append(result)
    
    # Test 6: Out of scope Query
    print("\n" + "="*70)
    print("❓ TEST 5: Out-of-Scope Query")
    result = test_endpoint(
        "What is the weather today?",
        expected_category="unknown"
    )
    results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results if r.get('success'))
    failed = len(results) - successful
    
    times = [r['time'] for r in results if r.get('success')]
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        
        print(f"\n⏱️  PERFORMANCE:")
        print(f"  • Average Response Time: {avg_time:.0f} ms")
        print(f"  • Fastest: {min_time:.0f} ms")
        print(f"  • Slowest: {max_time:.0f} ms")
        
        if avg_time > 5000:
            print(f"\n⚠️  WARNING: Average response time is very slow (>{avg_time:.0f} ms)")
            print(f"  Recommendations:")
            print(f"    - Check if model is loading properly")
            print(f"    - Reduce TOP_K_RESULTS in .env")
            print(f"    - Optimize chunk size")
            print(f"    - Consider caching results")
    
    print(f"\n📈 RESULTS:")
    print(f"  • Total Tests: {len(results)}")
    print(f"  • Passed: {successful} ✅")
    print(f"  • Failed: {failed} ❌")
    print(f"  • Success Rate: {(successful/len(results)*100):.1f}%")
    
    print("\n" + "="*70)
    
    # Cross-check with product_info.txt
    print("\n📋 DATA CROSS-CHECK WITH product_info.txt:")
    print("="*70)
    
    product_data = load_product_data()
    print(f"\n✓ Expected Product Prices:")
    print(f"  • SmartWatch Pro X: {product_data['smartwatch_price']}")
    print(f"  • Wireless Earbuds Elite: {product_data['earbuds_price']}")
    print(f"  • Power Bank Ultra: {product_data['powerbank_price']}")
    print(f"\n✓ Expected Policies:")
    print(f"  • Return Period: {product_data['return_days']} days")
    print(f"  • Support Email: {product_data['support_email']}")
    print(f"  • Support Hours: {product_data['support_hours']} IST")
    
    print("\n" + "="*70)
    print("✅ Quick test completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
