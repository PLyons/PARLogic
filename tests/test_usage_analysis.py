"""Tests for the usage analysis module."""

import pytest
import pandas as pd
from pathlib import Path
from analysis.usage_analysis import UsageAnalyzer

@pytest.fixture
def sample_usage_path():
    """Return the path to the sample usage history CSV file."""
    return Path(__file__).parent / 'data' / 'sample_usage_history.csv'

@pytest.fixture
def analyzer(sample_usage_path):
    """Return a UsageAnalyzer instance with sample data loaded."""
    df = pd.read_csv(sample_usage_path)
    df['date'] = pd.to_datetime(df['date'])
    analyzer = UsageAnalyzer(df)
    return analyzer

def test_monthly_usage_calculation(analyzer):
    """Test calculation of monthly usage statistics."""
    # Test for a specific item
    stats = analyzer.calculate_monthly_usage('SUP001')
    
    assert len(stats) == 12  # One year of data
    assert all(col in stats.columns for col in [
        'month', 'item_id', 'total_usage', 'avg_daily_usage',
        'min_usage', 'max_usage', 'std_dev'
    ])
    
    # Verify winter months have higher usage for N95 masks
    winter_months = [12, 1, 2]
    summer_months = [6, 7, 8]
    
    winter_usage = stats[stats['month'].dt.month.isin(winter_months)]['total_usage'].mean()
    summer_usage = stats[stats['month'].dt.month.isin(summer_months)]['total_usage'].mean()
    assert winter_usage > summer_usage

def test_usage_range_calculation(analyzer):
    """Test calculation of usage ranges."""
    # Test for all items
    ranges = analyzer.calculate_usage_range()
    
    assert len(ranges) == 3  # Three items in sample data
    assert all(item_id in ranges for item_id in ['SUP001', 'SUP002', 'SUP003'])
    
    # Check specific item ranges
    sup001_range = ranges['SUP001']
    assert sup001_range['min_monthly'] == 400  # July usage
    assert sup001_range['max_monthly'] == 1600  # December usage
    assert 800 < sup001_range['avg_monthly'] < 1000  # Approximate average

def test_seasonality_detection(analyzer):
    """Test detection of seasonal patterns."""
    seasonality = analyzer.detect_seasonality()
    
    # N95 masks should show seasonal pattern (winter peaks)
    sup001_season = seasonality['SUP001']
    assert sup001_season['seasonal_pattern']
    assert sup001_season['peak_month'] == 12  # December peak
    assert sup001_season['trough_month'] == 7  # July trough
    
    # Surgical gloves should not show strong seasonality
    sup002_season = seasonality['SUP002']
    assert not sup002_season['seasonal_pattern']
    
    # IV Solution shows moderate summer peak
    sup003_season = seasonality['SUP003']
    assert sup003_season['peak_month'] == 7  # July peak

def test_data_validation(sample_usage_path):
    """Test data validation on initialization."""
    # Test with missing required column
    bad_df = pd.DataFrame({
        'item_id': ['SUP001'],
        'quantity': [100]  # Missing date column
    })
    
    with pytest.raises(ValueError) as exc_info:
        UsageAnalyzer(bad_df)
    assert "missing required columns" in str(exc_info.value).lower()
    
    # Test with invalid date format
    bad_dates_df = pd.DataFrame({
        'item_id': ['SUP001'],
        'date': ['invalid_date'],
        'quantity': [100]
    })
    
    with pytest.raises(ValueError) as exc_info:
        UsageAnalyzer(bad_dates_df)
    assert "convert date column" in str(exc_info.value).lower()

def test_empty_data_handling():
    """Test handling of empty or unset data."""
    analyzer = UsageAnalyzer()
    
    with pytest.raises(ValueError) as exc_info:
        analyzer.calculate_monthly_usage()
    assert "no data has been set" in str(exc_info.value).lower()
    
    # Test with empty DataFrame
    empty_df = pd.DataFrame(columns=['item_id', 'date', 'quantity'])
    analyzer.set_data(empty_df)
    
    monthly_stats = analyzer.calculate_monthly_usage()
    assert len(monthly_stats) == 0 