"""
Quick test script for search functionality and analytics
Run this to test search without opening the browser
"""
import requests
import json
import time

API_BASE = "http://127.0.0.1:8000/api"

def test_search(query, types=None):
    """Test a search query"""
    print(f"\n{'='*60}")
    print(f"Testing Search: '{query}'")
    print(f"{'='*60}")
    
    start = time.time()
    params = {"q": query}
    if types:
        params["types"] = types
    
    try:
        response = requests.get(f"{API_BASE}/search", params=params)
        elapsed = (time.time() - start) * 1000
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"⏱️  Response Time: {elapsed:.0f}ms (backend: {data.get('response_time_ms', 0)}ms)")
            print(f"📊 Total Results: {data.get('total_results', 0)}")
            
            if data['results']:
                print(f"\n📋 Results:")
                for i, result in enumerate(data['results'][:5], 1):
                    print(f"  {i}. [{result['type']}] {result['title']}")
                    print(f"     {result['description']}")
                    print(f"     Relevance: {result['relevance']:.2f}")
            else:
                print("❌ No results found")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

def test_analytics():
    """Test analytics endpoint"""
    print(f"\n{'='*60}")
    print(f"Search Analytics Dashboard")
    print(f"{'='*60}")
    
    try:
        response = requests.get(f"{API_BASE}/search/analytics")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📈 Overview:")
            print(f"  Total Searches: {data['total_searches']}")
            print(f"  Last 24 Hours: {data['searches_last_24h']}")
            
            perf = data['performance']
            print(f"\n⚡ Performance:")
            print(f"  Average: {perf['avg_response_ms']:.1f}ms")
            print(f"  Min: {perf['min_response_ms']}ms")
            print(f"  Max: {perf['max_response_ms']}ms")
            
            if data['popular_searches']:
                print(f"\n🔥 Popular Searches:")
                for i, search in enumerate(data['popular_searches'][:10], 1):
                    print(f"  {i}. '{search['query']}' - {search['search_count']} searches, "
                          f"avg {search['avg_results']} results")
            
            if data['no_result_searches']:
                print(f"\n❌ Searches with No Results (Opportunities to Add Data):")
                for i, search in enumerate(data['no_result_searches'][:10], 1):
                    print(f"  {i}. '{search['query']}' - {search['attempt_count']} attempts")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

def run_test_suite():
    """Run comprehensive test suite"""
    print("\n🚀 Project RawHorse - Search Testing Suite")
    print("="*60)
    
    # Test 1: Entity search
    test_search("Peraton")
    time.sleep(0.5)
    
    # Test 2: Acronym search
    test_search("NGA")
    time.sleep(0.5)
    
    # Test 3: Partial match
    test_search("pera")
    time.sleep(0.5)
    
    # Test 4: Amount search
    test_search("223")
    time.sleep(0.5)
    
    # Test 5: Multi-word search
    test_search("National Geospatial")
    time.sleep(0.5)
    
    # Test 6: Investment firm
    test_search("Veritas")
    time.sleep(0.5)
    
    # Test 7: Fuzzy matching (typo)
    test_search("Pereton")
    time.sleep(0.5)
    
    # Test 8: No results (should track)
    test_search("xyz123abc")
    time.sleep(0.5)
    
    # Show analytics
    test_analytics()
    
    print(f"\n{'='*60}")
    print("✅ Test Suite Complete!")
    print("="*60)
    print("\n💡 Tips:")
    print("  - Open http://127.0.0.1:8000 to test in the browser")
    print("  - Press '/' to focus the search bar")
    print("  - Use ↑↓ arrows to navigate results")
    print("  - View analytics at http://127.0.0.1:8000/api/search/analytics")

if __name__ == "__main__":
    try:
        run_test_suite()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        print("Make sure the server is running at http://127.0.0.1:8000")

