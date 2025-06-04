import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import json
import os
import pandas as pd
from unittest.mock import patch, MagicMock

# Add project root to Python path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app
from api.security import API_KEYS

client = TestClient(app)
VALID_API_KEY = "test-key"

# Mock data for tests
MOCK_USAGE_DATA = {
    "item_id": "TEST001",
    "average_daily_usage": 5.5,
    "peak_usage": 10.0,
    "seasonality_factor": 1.2,
    "trend": "increasing",
    "confidence_level": 0.95
}

MOCK_PAR_DATA = {
    "item_id": "TEST001",
    "min_par": 50,
    "max_par": 100,
    "reorder_point": 30,
    "safety_stock": 20,
    "service_level": 0.95,
    "lead_time_days": 3
}

MOCK_RECOMMENDATIONS = {
    "recommendations": [
        {
            "item_id": "TEST001",
            "current_stock": 25,
            "recommended_action": "reorder",
            "urgency": "high",
            "details": "Stock below reorder point"
        }
    ],
    "timestamp": datetime.now().isoformat()
}

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/", headers={"X-API-Key": VALID_API_KEY})
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "PARLogic API"
    }

def test_upload_csv():
    """Test CSV upload endpoint"""
    # Create test CSV file
    test_data = pd.DataFrame({
        "item_id": ["TEST001", "TEST001"],
        "timestamp": ["2024-01-01 10:00:00", "2024-01-01 11:00:00"],
        "quantity": [-1, 2],
        "transaction_type": ["issue", "receipt"]
    })
    test_file = "test_upload.csv"
    test_data.to_csv(test_file, index=False)
    
    try:
        with open(test_file, "rb") as f:
            response = client.post(
                "/upload/",
                files={"file": ("test.csv", f, "text/csv")},
                headers={"X-API-Key": VALID_API_KEY}
            )
        
        assert response.status_code == 200
        assert response.json()["rows"] == 2
        assert response.json()["message"] == "File processed successfully"
    
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

@patch('analysis.usage_analysis.UsageAnalyzer.calculate_monthly_usage')
@patch('analysis.usage_analysis.UsageAnalyzer.detect_seasonality')
def test_analyze_usage(mock_seasonality, mock_monthly):
    """Test usage analysis endpoint"""
    # Mock monthly usage data
    dates = pd.date_range('2024-01-01', '2024-02-01', freq='M')
    mock_monthly.return_value = pd.DataFrame({
        'month': dates,
        'item_id': ['TEST001'] * len(dates),
        'total_usage': [100] * len(dates),
        'avg_daily_usage': [3.33] * len(dates),
        'min_usage': [2] * len(dates),
        'max_usage': [5] * len(dates),
        'std_dev': [1.0] * len(dates)
    })
    
    # Mock seasonality data
    mock_seasonality.return_value = {
        'TEST001': {
            'seasonal_pattern': True,
            'peak_month': 12,
            'trough_month': 7,
            'seasonality_strength': 0.3
        }
    }
    
    response = client.get(
        "/analyze/usage/",
        params={
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "item_id": "TEST001"
        },
        headers={"X-API-Key": VALID_API_KEY}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["item_id"] == "TEST001"
    assert data["average_daily_usage"] > 0
    assert data["peak_usage"] > 0
    assert data["seasonality_factor"] == 0.3
    assert data["trend"] == "stable"  # Since all values are the same
    assert data["confidence_level"] == 0.95

@patch('analysis.par_calc.PARCalculator.calculate_par_levels')
def test_calculate_par(mock_calculate):
    """Test PAR level calculation endpoint"""
    mock_calculate.return_value = MOCK_PAR_DATA
    
    response = client.get(
        "/calculate/par/",
        params={
            "item_id": "TEST001",
            "service_level": 0.95,
            "lead_time_days": 3
        },
        headers={"X-API-Key": VALID_API_KEY}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data == MOCK_PAR_DATA

@patch('analysis.par_calc.PARCalculator.get_recommendations')
def test_get_recommendations(mock_recommendations):
    """Test recommendations endpoint"""
    mock_recommendations.return_value = MOCK_RECOMMENDATIONS["recommendations"]
    
    response = client.get(
        "/recommendations/",
        params={"item_id": "TEST001"},
        headers={"X-API-Key": VALID_API_KEY}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "timestamp" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["item_id"] == "TEST001"

def test_invalid_api_key():
    """Test authentication with invalid API key"""
    response = client.get(
        "/analyze/usage/",
        params={
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        },
        headers={"X-API-Key": "invalid-key"}
    )
    
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]

def test_rate_limit():
    """Test rate limiting"""
    # Reset rate limit storage
    from api.security import RATE_LIMITS
    RATE_LIMITS.clear()
    
    # Find rate limit for test key
    rate_limit = API_KEYS[VALID_API_KEY]["rate_limit"]
    
    # Make requests up to rate limit
    for _ in range(rate_limit):
        response = client.get(
            "/",
            headers={"X-API-Key": VALID_API_KEY}
        )
        assert response.status_code == 200
    
    # Next request should fail
    response = client.get(
        "/",
        headers={"X-API-Key": VALID_API_KEY}
    )
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["detail"] 