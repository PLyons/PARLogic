"""Tests for the CSV parser module."""

import pytest
import pandas as pd
from pathlib import Path
from io import StringIO
from datetime import datetime
from ingestion.parser import CSVParser

@pytest.fixture
def sample_csv_path():
    """Return the path to the sample CSV file."""
    return Path(__file__).parent / 'data' / 'sample_inventory.csv'

@pytest.fixture
def parser():
    """Return a CSVParser instance."""
    return CSVParser()

def test_parse_csv_basic(parser, sample_csv_path):
    """Test basic CSV parsing functionality."""
    df = parser.parse_csv(sample_csv_path)
    
    # Check if all required columns are present
    assert all(col in df.columns for col in parser.REQUIRED_COLUMNS)
    
    # Check if data types are correct
    assert df['item_id'].dtype == 'object'  # string
    assert df['quantity'].dtype in ['int64', 'float64']
    assert df['unit_price'].dtype == 'float64'
    assert pd.api.types.is_datetime64_any_dtype(df['date'])

def test_parse_csv_validation(parser, sample_csv_path):
    """Test CSV validation functionality."""
    parser.parse_csv(sample_csv_path)
    # Use a fixed date for testing (2024-06-01)
    reference_date = datetime(2024, 6, 1)
    issues = parser.validate_values(reference_date=reference_date)
    
    # We should find several issues in our sample data
    assert len(issues) > 0
    
    # Check for specific issues we know exist in the sample data
    issue_types = [issue['type'] for issue in issues]
    assert 'negative_quantity' in issue_types  # SUP006 has negative quantity
    assert 'future_date' in issue_types       # SUP004 has future date
    assert 'invalid_price' in issue_types     # SUP003 has negative price

def test_get_summary(parser, sample_csv_path):
    """Test summary generation."""
    parser.parse_csv(sample_csv_path)
    summary = parser.get_summary()
    
    assert summary['row_count'] == 6
    assert len(summary['columns']) >= len(parser.REQUIRED_COLUMNS)
    assert isinstance(summary['missing_optional'], list)

def test_missing_required_columns():
    """Test handling of missing required columns."""
    parser = CSVParser()
    csv_data = StringIO("item_name,quantity\na,1\nb,2\n")
    
    with pytest.raises(ValueError) as exc_info:
        parser.parse_csv(csv_data)
    assert "Missing required columns" in str(exc_info.value)

def test_invalid_date_format():
    """Test handling of invalid date formats."""
    parser = CSVParser()
    csv_data = StringIO(
        "item_id,item_name,quantity,date,unit_price\n"
        "1,test,1,invalid_date,1.0\n"
    )
    
    with pytest.raises(ValueError) as exc_info:
        parser.parse_csv(csv_data)
    assert "Error parsing date column" in str(exc_info.value) 