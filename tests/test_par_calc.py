"""Tests for the PAR level calculator module."""

import pytest
import pandas as pd
from pathlib import Path
from analysis.par_calc import PARCalculator

@pytest.fixture
def sample_usage_path():
    """Return the path to the sample usage history CSV file."""
    return Path(__file__).parent / 'data' / 'sample_usage_history.csv'

@pytest.fixture
def calculator(sample_usage_path):
    """Return a PARCalculator instance with sample data loaded."""
    df = pd.read_csv(sample_usage_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Set up calculator with known lead times
    lead_times = {
        'SUP001': 10,  # N95 Masks: 10 days
        'SUP002': 7,   # Surgical Gloves: 7 days
        'SUP003': 14   # IV Solution: 14 days
    }
    
    calculator = PARCalculator(
        usage_data=df,
        lead_time_days=lead_times,
        service_level=0.95,  # 95% service level
        review_period_days=7  # Weekly review
    )
    return calculator

def test_safety_stock_calculation(calculator):
    """Test safety stock calculation."""
    # Get usage stats and seasonality for N95 masks
    usage_ranges = calculator.usage_analyzer.calculate_usage_range('SUP001')
    seasonality = calculator.usage_analyzer.detect_seasonality('SUP001')
    
    safety_stock = calculator.calculate_safety_stock(
        'SUP001',
        usage_ranges['SUP001'],
        seasonality['SUP001']
    )
    
    # Safety stock should be positive
    assert safety_stock > 0
    
    # Safety stock should be higher for seasonal items
    assert seasonality['SUP001']['seasonal_pattern']
    
    # Calculate safety stock for non-seasonal item (Surgical Gloves)
    gloves_ranges = calculator.usage_analyzer.calculate_usage_range('SUP002')
    gloves_seasonality = calculator.usage_analyzer.detect_seasonality('SUP002')
    
    gloves_safety = calculator.calculate_safety_stock(
        'SUP002',
        gloves_ranges['SUP002'],
        gloves_seasonality['SUP002']
    )
    
    # Non-seasonal item should have lower safety stock relative to average usage
    assert (safety_stock / usage_ranges['SUP001']['avg_monthly']) > \
           (gloves_safety / gloves_ranges['SUP002']['avg_monthly'])

def test_par_level_calculation(calculator):
    """Test PAR level calculation."""
    par_levels = calculator.calculate_par_levels('SUP001')
    
    assert 'SUP001' in par_levels
    item_levels = par_levels['SUP001']
    
    # Check all required fields are present
    required_fields = {
        'min_par', 'max_par', 'reorder_point', 'safety_stock',
        'avg_daily_usage', 'lead_time_days', 'review_period_days'
    }
    assert all(field in item_levels for field in required_fields)
    
    # Verify relationships between levels
    assert item_levels['min_par'] == item_levels['reorder_point']
    assert item_levels['max_par'] > item_levels['min_par']
    assert item_levels['reorder_point'] > item_levels['safety_stock']
    
    # Verify lead time is correct
    assert item_levels['lead_time_days'] == 10  # Set in fixture
    
    # Calculate for all items
    all_levels = calculator.calculate_par_levels()
    assert len(all_levels) == 3  # Three items in sample data

def test_recommendations(calculator):
    """Test PAR level recommendations."""
    # First get PAR levels to determine appropriate test values
    par_levels = calculator.calculate_par_levels()
    
    # Set test stock levels based on calculated PARs
    current_stock = {
        'SUP001': int(par_levels['SUP001']['min_par'] * 0.5),  # Below min
        'SUP002': int((par_levels['SUP002']['min_par'] + par_levels['SUP002']['max_par']) / 2),  # Optimal
        'SUP003': int(par_levels['SUP003']['max_par'] * 1.5)  # Above max
    }
    
    recommendations = calculator.get_recommendations(current_stock=current_stock)
    
    # Check N95 masks (low stock)
    sup001_rec = recommendations['SUP001']
    assert sup001_rec['needs_reorder']
    assert sup001_rec['status'] == 'BELOW_MIN'
    assert sup001_rec['reorder_amount'] > 0
    assert "Place order" in sup001_rec['recommendation']
    
    # Check surgical gloves (optimal)
    sup002_rec = recommendations['SUP002']
    assert not sup002_rec['needs_reorder']
    assert sup002_rec['status'] == 'OPTIMAL'
    assert sup002_rec['reorder_amount'] == 0
    assert "optimal range" in sup002_rec['recommendation']
    
    # Check IV solution (overstocked)
    sup003_rec = recommendations['SUP003']
    assert not sup003_rec['needs_reorder']
    assert sup003_rec['status'] == 'ABOVE_MAX'
    assert "above maximum" in sup003_rec['recommendation']

def test_service_level_impact(sample_usage_path):
    """Test impact of different service levels on safety stock."""
    df = pd.read_csv(sample_usage_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Create calculators with different service levels
    calc_90 = PARCalculator(df, service_level=0.90)
    calc_99 = PARCalculator(df, service_level=0.99)
    
    # Get PAR levels for both
    levels_90 = calc_90.calculate_par_levels('SUP001')
    levels_99 = calc_99.calculate_par_levels('SUP001')
    
    # Higher service level should require more safety stock
    assert levels_99['SUP001']['safety_stock'] > levels_90['SUP001']['safety_stock']
    
    # And consequently higher PAR levels
    assert levels_99['SUP001']['min_par'] > levels_90['SUP001']['min_par']
    assert levels_99['SUP001']['max_par'] > levels_90['SUP001']['max_par']

def test_lead_time_updates(calculator):
    """Test updating lead times."""
    # Get initial PAR levels
    initial_levels = calculator.calculate_par_levels('SUP001')
    
    # Update lead time
    calculator.set_lead_time('SUP001', 20)  # Double the lead time
    
    # Get new PAR levels
    new_levels = calculator.calculate_par_levels('SUP001')
    
    # Longer lead time should increase safety stock and PAR levels
    assert new_levels['SUP001']['safety_stock'] > initial_levels['SUP001']['safety_stock']
    assert new_levels['SUP001']['min_par'] > initial_levels['SUP001']['min_par']
    assert new_levels['SUP001']['max_par'] > initial_levels['SUP001']['max_par'] 