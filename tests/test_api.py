"""
API Test Script
Quick test for all backend endpoints using requests library.

Usage:
    1. Start the server: python run.py
    2. In another terminal: python tests/test_api.py
"""
import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"


def test_health():
    """Test health check endpoint."""
    print("\n--- Test: Health Check ---")
    resp = requests.get(f"{BASE_URL}/health")
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.json()}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    print("  PASSED")


def test_analyze_genuine():
    """Test analyzing a likely genuine review."""
    print("\n--- Test: Analyze Genuine Review ---")
    resp = requests.post(f"{BASE_URL}/reviews/analyze", json={
        "review_text": "I bought this coffee maker three months ago. The brewing process takes about 5 minutes, and the coffee tastes good. The carafe keeps coffee warm for about an hour. One downside is that the water reservoir is a bit small for our family of four. Overall, it's a decent machine for the price."
    })
    data = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Classification: {data.get('classification')}")
    print(f"  Credibility Score: {data.get('credibility_score')}")
    print(f"  Fake Probability: {data.get('fake_probability')}")
    print(f"  Flags: {len(data.get('flags', []))}")
    assert resp.status_code == 200
    assert data["success"] is True
    print("  PASSED")


def test_analyze_fake():
    """Test analyzing a likely fake review."""
    print("\n--- Test: Analyze Fake Review ---")
    resp = requests.post(f"{BASE_URL}/reviews/analyze", json={
        "review_text": "AMAZING!!! BEST PRODUCT EVER!!! Must buy this incredible life changing product!!! HIGHLY RECOMMEND!!! Perfect perfect perfect!!! Five stars!!!"
    })
    data = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Classification: {data.get('classification')}")
    print(f"  Credibility Score: {data.get('credibility_score')}")
    print(f"  Flags: {len(data.get('flags', []))}")
    for flag in data.get("flags", []):
        print(f"    - [{flag['severity']}] {flag['message']}")
    assert resp.status_code == 200
    assert data["success"] is True
    print("  PASSED")


def test_empty_input():
    """Test empty input validation."""
    print("\n--- Test: Empty Input ---")
    resp = requests.post(f"{BASE_URL}/reviews/analyze", json={
        "review_text": ""
    })
    data = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Error: {data.get('error')}")
    assert resp.status_code == 400
    assert data["success"] is False
    print("  PASSED")


def test_short_input():
    """Test too-short input validation."""
    print("\n--- Test: Too Short Input ---")
    resp = requests.post(f"{BASE_URL}/reviews/analyze", json={
        "review_text": "good"
    })
    data = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Error: {data.get('error')}")
    assert resp.status_code == 400
    assert data["success"] is False
    print("  PASSED")


def test_history():
    """Test history endpoint."""
    print("\n--- Test: History ---")
    resp = requests.get(f"{BASE_URL}/history")
    data = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Total records: {data.get('total')}")
    assert resp.status_code == 200
    print("  PASSED")


def test_dashboard():
    """Test dashboard endpoint."""
    print("\n--- Test: Dashboard ---")
    resp = requests.get(f"{BASE_URL}/admin/dashboard")
    data = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Total analyzed: {data.get('total_analyzed')}")
    print(f"  Total genuine: {data.get('total_genuine')}")
    print(f"  Total fake: {data.get('total_fake')}")
    print(f"  Avg credibility: {data.get('avg_credibility_score')}")
    assert resp.status_code == 200
    print("  PASSED")


def test_rules():
    """Test detection rules endpoint."""
    print("\n--- Test: Detection Rules ---")
    resp = requests.get(f"{BASE_URL}/admin/rules")
    data = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Total rules: {len(data.get('rules', []))}")
    for rule in data.get("rules", []):
        print(f"    - {rule['rule_name']} (active: {rule['is_active']})")
    assert resp.status_code == 200
    print("  PASSED")


def test_model_status():
    """Test model status endpoint."""
    print("\n--- Test: Model Status ---")
    resp = requests.get(f"{BASE_URL}/reviews/model-status")
    data = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Model loaded: {data.get('is_loaded')}")
    assert resp.status_code == 200
    print("  PASSED")


def test_batch_analyze():
    """Test batch analysis endpoint."""
    print("\n--- Test: Batch Analyze ---")
    resp = requests.post(f"{BASE_URL}/reviews/batch-analyze", json={
        "reviews": [
            "This product works as expected. Decent quality for the price.",
            "BEST EVER!!! AMAZING INCREDIBLE MUST BUY!!!",
            "I've been using this for 2 weeks. The battery lasts about 8 hours. Build quality is okay."
        ]
    })
    data = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Total results: {data.get('total')}")
    for i, result in enumerate(data.get("results", [])):
        print(f"    Review {i + 1}: {result.get('classification')} (score: {result.get('credibility_score')})")
    assert resp.status_code == 200
    print("  PASSED")


def main():
    print("=" * 60)
    print("  Fake Review Detection API - Test Suite")
    print("=" * 60)

    tests = [
        test_health,
        test_analyze_genuine,
        test_analyze_fake,
        test_empty_input,
        test_short_input,
        test_history,
        test_dashboard,
        test_rules,
        test_model_status,
        test_batch_analyze,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"  Results: {passed} passed, {failed} failed, {len(tests)} total")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
