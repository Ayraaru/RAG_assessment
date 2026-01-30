"""
Comprehensive Test Suite for RAG Chatbot
Tests all endpoints, measures response times, and cross-checks with product_info.txt
"""
import requests
import json
import time
from typing import List, Dict, Tuple
from pathlib import Path
import re


class ProductDataValidator:
    """Validates chatbot responses against product_info.txt"""
    
    def __init__(self, product_file_path: str):
        """Load and parse product information"""
        self.product_file_path = product_file_path
        self.products = {}
        self.return_policy = ""
        self.support_info = ""
        self._load_product_data()
    
    def _load_product_data(self):
        """Parse product_info.txt into structured data"""
        with open(self.product_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse products
        product_blocks = content.split('Product: ')[1:]  # Skip first empty split
        
        for block in product_blocks:
            lines = block.strip().split('\n')
            product_name = lines[0].strip()
            
            product_info = {
                'name': product_name,
                'price': None,
                'features': [],
                'warranty': None
            }
            
            for line in lines[1:]:
                if line.startswith('Price:'):
                    # Extract price
                    price_match = re.search(r'₹[\d,]+', line)
                    if price_match:
                        product_info['price'] = price_match.group()
                    
                    # Extract features
                    features_match = re.search(r'Features: (.+?)(?:\||\Z)', line)
                    if features_match:
                        features_text = features_match.group(1).strip()
                        product_info['features'] = [f.strip() for f in features_text.split(',')]
                    
                    # Extract warranty
                    warranty_match = re.search(r'Warranty: (.+)', line)
                    if warranty_match:
                        product_info['warranty'] = warranty_match.group(1).strip()
                
                elif line.startswith('Warranty:'):
                    product_info['warranty'] = line.replace('Warranty:', '').strip()
            
            self.products[product_name.lower()] = product_info
        
        # Parse return policy
        return_match = re.search(r'Return Policy: (.+)', content)
        if return_match:
            self.return_policy = return_match.group(1).strip()
        
        # Parse support info
        support_match = re.search(r'Support: (.+)', content)
        if support_match:
            self.support_info = support_match.group(1).strip()
    
    def validate_price(self, product_name: str, answer: str) -> Tuple[bool, str]:
        """Check if the price in answer matches product data"""
        product_key = product_name.lower()
        if product_key not in self.products:
            return False, f"Product '{product_name}' not found in data"
        
        expected_price = self.products[product_key]['price']
        if expected_price and expected_price in answer:
            return True, f"✓ Price {expected_price} found correctly"
        else:
            return False, f"✗ Expected price {expected_price} not found in answer"
    
    def validate_features(self, product_name: str, answer: str) -> Tuple[bool, str]:
        """Check if features are mentioned correctly"""
        product_key = product_name.lower()
        if product_key not in self.products:
            return False, f"Product '{product_name}' not found in data"
        
        features = self.products[product_key]['features']
        found_features = [f for f in features if any(word.lower() in answer.lower() 
                                                      for word in f.split())]
        
        if len(found_features) >= 2:  # At least 2 features mentioned
            return True, f"✓ Found {len(found_features)}/{len(features)} features"
        else:
            return False, f"✗ Only {len(found_features)}/{len(features)} features found"
    
    def validate_warranty(self, product_name: str, answer: str) -> Tuple[bool, str]:
        """Check if warranty information is correct"""
        product_key = product_name.lower()
        if product_key not in self.products:
            return False, f"Product '{product_name}' not found in data"
        
        warranty = self.products[product_key]['warranty']
        if warranty:
            # Check for key warranty terms
            warranty_terms = re.findall(r'\d+\s*(?:year|month|day)', warranty, re.IGNORECASE)
            answer_terms = re.findall(r'\d+\s*(?:year|month|day)', answer, re.IGNORECASE)
            
            if any(term in answer for term in warranty_terms):
                return True, f"✓ Warranty info found"
            else:
                return False, f"✗ Expected warranty '{warranty}' not clearly stated"
        return True, "No warranty data to validate"
    
    def validate_return_policy(self, answer: str) -> Tuple[bool, str]:
        """Check if return policy is mentioned correctly"""
        # Check for "7-day" or "7 day"
        if '7' in answer and 'day' in answer.lower():
            return True, "✓ 7-day return policy mentioned"
        else:
            return False, f"✗ Expected '7-day' return policy not clearly stated"
    
    def validate_support_info(self, answer: str) -> Tuple[bool, str]:
        """Check if support information is present"""
        has_email = 'support@techgear.com' in answer.lower()
        has_hours = ('9am' in answer.lower() or '9 am' in answer.lower()) and '6pm' in answer.lower()
        
        if has_email and has_hours:
            return True, "✓ Email and hours found"
        elif has_email:
            return True, "✓ Email found (hours may be implied)"
        else:
            return False, "✗ Support contact information incomplete"


class ChatbotTester:
    """Comprehensive testing for RAG chatbot"""
    
    def __init__(self, base_url: str = "http://localhost:8000", 
                 product_file: str = "product_info.txt"):
        self.base_url = base_url
        self.validator = ProductDataValidator(product_file)
        self.test_results = []
    
    def test_health_endpoint(self) -> Dict:
        """Test /health endpoint"""
        print("\n" + "="*70)
        print("🏥 Testing Health Endpoint")
        print("="*70)
        
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            elapsed_time = (time.time() - start_time) * 1000  # ms
            
            result = {
                'endpoint': '/health',
                'status_code': response.status_code,
                'response_time_ms': round(elapsed_time, 2),
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else None
            }
            
            print(f"Status Code: {result['status_code']}")
            print(f"Response Time: {result['response_time_ms']} ms")
            print(f"Response: {json.dumps(result['response'], indent=2)}")
            
            if result['success']:
                print("✅ Health check passed")
            else:
                print("❌ Health check failed")
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {'endpoint': '/health', 'success': False, 'error': str(e)}
    
    def test_chat_endpoint(self, query: str, expected_category: str = None,
                          validate_func=None) -> Dict:
        """Test /chat endpoint with a specific query"""
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={"query": query},
                headers={"Content-Type": "application/json"},
                timeout=60  # Increased timeout for slow queries
            )
            elapsed_time = (time.time() - start_time) * 1000  # ms
            
            result = {
                'endpoint': '/chat',
                'query': query,
                'status_code': response.status_code,
                'response_time_ms': round(elapsed_time, 2),
                'success': response.status_code == 200,
                'response': response.json() if response.status_code == 200 else None,
                'expected_category': expected_category,
                'validation': None
            }
            
            if result['success']:
                resp_data = result['response']
                result['actual_category'] = resp_data.get('category')
                result['answer'] = resp_data.get('answer')
                
                # Check category match
                if expected_category:
                    result['category_match'] = (result['actual_category'] == expected_category)
                
                # Run validation if provided
                if validate_func:
                    is_valid, msg = validate_func(result['answer'])
                    result['validation'] = {'valid': is_valid, 'message': msg}
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            result = {
                'endpoint': '/chat',
                'query': query,
                'success': False,
                'error': str(e)
            }
            self.test_results.append(result)
            return result
    
    def print_test_result(self, result: Dict):
        """Pretty print a test result"""
        print(f"\n📝 Query: {result.get('query', 'N/A')}")
        
        if not result.get('success'):
            print(f"❌ Request failed: {result.get('error', 'Unknown error')}")
            print("-" * 70)
            return
        
        print(f"⏱️  Response Time: {result.get('response_time_ms', 0)} ms", end="")
        
        # Highlight slow queries
        if result.get('response_time_ms', 0) > 5000:
            print(" ⚠️  SLOW!")
        elif result.get('response_time_ms', 0) > 3000:
            print(" ⚡ Could be faster")
        else:
            print(" ✨ Fast")
        
        print(f"📂 Category: {result.get('actual_category', 'N/A')}", end="")
        if 'category_match' in result:
            if result['category_match']:
                print(" ✅")
            else:
                print(f" ❌ (expected: {result['expected_category']})")
        else:
            print()
        
        print(f"💬 Answer: {result.get('answer', 'N/A')[:150]}...")
        
        if result.get('validation'):
            val = result['validation']
            status = "✅" if val['valid'] else "❌"
            print(f"{status} Validation: {val['message']}")
        
        print("-" * 70)
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("\n" + "="*70)
        print("🧪 COMPREHENSIVE RAG CHATBOT TEST SUITE")
        print("="*70)
        
        # Test 1: Health endpoint
        self.test_health_endpoint()
        
        # Test 2: Product price queries
        print("\n" + "="*70)
        print("💰 Testing Product Price Queries")
        print("="*70)
        
        test_cases = [
            {
                'query': "What is the price of SmartWatch Pro X?",
                'expected_category': 'products',
                'validate': lambda ans: self.validator.validate_price('SmartWatch Pro X', ans)
            },
            {
                'query': "How much does the Wireless Earbuds Elite cost?",
                'expected_category': 'products',
                'validate': lambda ans: self.validator.validate_price('Wireless Earbuds Elite', ans)
            },
            {
                'query': "What's the price of Power Bank Ultra 20000mAh?",
                'expected_category': 'products',
                'validate': lambda ans: self.validator.validate_price('Power Bank Ultra 20000mAh', ans)
            }
        ]
        
        for test_case in test_cases:
            result = self.test_chat_endpoint(
                test_case['query'],
                test_case['expected_category'],
                test_case['validate']
            )
            self.print_test_result(result)
        
        # Test 3: Product features queries
        print("\n" + "="*70)
        print("🔧 Testing Product Features Queries")
        print("="*70)
        
        feature_tests = [
            {
                'query': "What features does the SmartWatch Pro X have?",
                'expected_category': 'products',
                'validate': lambda ans: self.validator.validate_features('SmartWatch Pro X', ans)
            },
            {
                'query': "Tell me about the Power Bank features",
                'expected_category': 'products',
                'validate': lambda ans: self.validator.validate_features('Power Bank Ultra 20000mAh', ans)
            },
            {
                'query': "What can the Wireless Earbuds Elite do?",
                'expected_category': 'products',
                'validate': lambda ans: self.validator.validate_features('Wireless Earbuds Elite', ans)
            }
        ]
        
        for test_case in feature_tests:
            result = self.test_chat_endpoint(
                test_case['query'],
                test_case['expected_category'],
                test_case['validate']
            )
            self.print_test_result(result)
        
        # Test 4: Warranty queries
        print("\n" + "="*70)
        print("📜 Testing Warranty Queries")
        print("="*70)
        
        warranty_tests = [
            {
                'query': "What is the warranty for SmartWatch Pro X?",
                'expected_category': 'products',
                'validate': lambda ans: self.validator.validate_warranty('SmartWatch Pro X', ans)
            },
            {
                'query': "How long is the warranty on Wireless Earbuds?",
                'expected_category': 'products',
                'validate': lambda ans: self.validator.validate_warranty('Wireless Earbuds Elite', ans)
            }
        ]
        
        for test_case in warranty_tests:
            result = self.test_chat_endpoint(
                test_case['query'],
                test_case['expected_category'],
                test_case['validate']
            )
            self.print_test_result(result)
        
        # Test 5: Return policy queries
        print("\n" + "="*70)
        print("↩️  Testing Return Policy Queries")
        print("="*70)
        
        return_tests = [
            {
                'query': "What is your return policy?",
                'expected_category': 'returns',
                'validate': lambda ans: self.validator.validate_return_policy(ans)
            },
            {
                'query': "How many days do I have to return a product?",
                'expected_category': 'returns',
                'validate': lambda ans: self.validator.validate_return_policy(ans)
            },
            {
                'query': "Can I get a refund?",
                'expected_category': 'returns',
                'validate': lambda ans: self.validator.validate_return_policy(ans)
            }
        ]
        
        for test_case in return_tests:
            result = self.test_chat_endpoint(
                test_case['query'],
                test_case['expected_category'],
                test_case['validate']
            )
            self.print_test_result(result)
        
        # Test 6: General/Support queries
        print("\n" + "="*70)
        print("📞 Testing Support/General Queries")
        print("="*70)
        
        support_tests = [
            {
                'query': "What are your support hours?",
                'expected_category': 'general',
                'validate': lambda ans: self.validator.validate_support_info(ans)
            },
            {
                'query': "How can I contact customer support?",
                'expected_category': 'general',
                'validate': lambda ans: self.validator.validate_support_info(ans)
            }
        ]
        
        for test_case in support_tests:
            result = self.test_chat_endpoint(
                test_case['query'],
                test_case['expected_category'],
                test_case['validate']
            )
            self.print_test_result(result)
        
        # Test 7: Unknown/Out-of-scope queries
        print("\n" + "="*70)
        print("❓ Testing Unknown/Out-of-Scope Queries")
        print("="*70)
        
        unknown_tests = [
            {
                'query': "What is the weather today?",
                'expected_category': 'unknown'
            },
            {
                'query': "Tell me a joke",
                'expected_category': 'unknown'
            }
        ]
        
        for test_case in unknown_tests:
            result = self.test_chat_endpoint(
                test_case['query'],
                test_case['expected_category']
            )
            self.print_test_result(result)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary and performance analysis"""
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get('success', False))
        failed_tests = total_tests - successful_tests
        
        # Response time statistics
        chat_results = [r for r in self.test_results if r['endpoint'] == '/chat' and r.get('success')]
        if chat_results:
            response_times = [r['response_time_ms'] for r in chat_results]
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"\n⏱️  PERFORMANCE METRICS:")
            print(f"  • Average Response Time: {avg_time:.2f} ms")
            print(f"  • Fastest Response: {min_time:.2f} ms")
            print(f"  • Slowest Response: {max_time:.2f} ms")
            
            slow_queries = [r for r in chat_results if r['response_time_ms'] > 5000]
            if slow_queries:
                print(f"\n⚠️  SLOW QUERIES (>5 seconds):")
                for sq in slow_queries:
                    print(f"  • {sq['query'][:50]}... ({sq['response_time_ms']:.2f} ms)")
        
        # Category accuracy
        category_results = [r for r in self.test_results 
                          if r.get('success') and 'category_match' in r]
        if category_results:
            correct_categories = sum(1 for r in category_results if r['category_match'])
            category_accuracy = (correct_categories / len(category_results)) * 100
            print(f"\n🎯 CATEGORY CLASSIFICATION:")
            print(f"  • Accuracy: {category_accuracy:.1f}% ({correct_categories}/{len(category_results)})")
        
        # Validation results
        validation_results = [r for r in self.test_results 
                            if r.get('success') and r.get('validation')]
        if validation_results:
            valid_answers = sum(1 for r in validation_results if r['validation']['valid'])
            validation_accuracy = (valid_answers / len(validation_results)) * 100
            print(f"\n✅ DATA VALIDATION:")
            print(f"  • Accuracy: {validation_accuracy:.1f}% ({valid_answers}/{len(validation_results)})")
            
            # Show failed validations
            failed_validations = [r for r in validation_results if not r['validation']['valid']]
            if failed_validations:
                print(f"\n❌ FAILED VALIDATIONS:")
                for fv in failed_validations:
                    print(f"  • {fv['query'][:50]}...")
                    print(f"    → {fv['validation']['message']}")
        
        print(f"\n📈 OVERALL RESULTS:")
        print(f"  • Total Tests: {total_tests}")
        print(f"  • Passed: {successful_tests} ✅")
        print(f"  • Failed: {failed_tests} ❌")
        print(f"  • Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        print("\n" + "="*70)
        
        # Performance recommendations
        if chat_results:
            avg_time = sum(r['response_time_ms'] for r in chat_results) / len(chat_results)
            if avg_time > 3000:
                print("\n⚡ PERFORMANCE RECOMMENDATIONS:")
                print("  • Response times are high (>3 seconds)")
                print("  • Consider optimizing:")
                print("    - Vector store indexing")
                print("    - LLM temperature settings")
                print("    - Chunk size and overlap")
                print("    - Retriever top_k parameter")
                print("    - Caching frequently asked queries")
                print("="*70)


def main():
    """Main test execution"""
    import sys
    
    # Configuration
    base_url = "http://localhost:8000"
    product_file = "/home/labuser/RAG_assessment/product_info.txt"
    
    # Check if server is running
    print("🔍 Checking if server is running...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print("✅ Server is running!")
    except Exception as e:
        print(f"❌ Server is not running: {e}")
        print("\nPlease start the server first:")
        print("  bash run.sh")
        sys.exit(1)
    
    # Run tests
    tester = ChatbotTester(base_url, product_file)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
