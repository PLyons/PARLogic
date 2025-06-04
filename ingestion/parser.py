"""
CSV Parser for hospital supply chain data.
Handles purchase order history and inventory data.
"""

import pandas as pd
from typing import Dict, List, Optional, Union
from pathlib import Path
import logging
from io import StringIO
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CSVParser:
    """Parser for hospital supply chain CSV data."""
    
    REQUIRED_COLUMNS = {
        'item_id': str,
        'item_name': str,
        'quantity': int,
        'date': str,
        'unit_price': float
    }
    
    OPTIONAL_COLUMNS = {
        'category': str,
        'supplier': str,
        'department': str,
        'location': str,
        'min_stock': int,
        'max_stock': int
    }

    def __init__(self):
        """Initialize the CSV parser."""
        self.df = None

    def parse_csv(self, source: Union[str, Path, StringIO], **kwargs) -> pd.DataFrame:
        """
        Parse a CSV file containing hospital supply chain data.
        
        Args:
            source: Path to the CSV file or StringIO object
            **kwargs: Additional arguments to pass to pd.read_csv
        
        Returns:
            pd.DataFrame: Parsed and validated DataFrame
            
        Raises:
            ValueError: If required columns are missing or data types are incorrect
            FileNotFoundError: If the CSV file doesn't exist
        """
        try:
            # Read CSV file
            logger.info(f"Reading CSV data")
            self.df = pd.read_csv(source, **kwargs)
            
            # Convert column names to lowercase and remove whitespace
            self.df.columns = self.df.columns.str.lower().str.strip()
            
            # Validate required columns
            missing_cols = set(self.REQUIRED_COLUMNS.keys()) - set(self.df.columns)
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Convert data types and handle errors
            for col, dtype in self.REQUIRED_COLUMNS.items():
                try:
                    if dtype == str:
                        self.df[col] = self.df[col].astype(str).str.strip()
                    else:
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                except Exception as e:
                    raise ValueError(f"Error converting column {col} to {dtype}: {str(e)}")
            
            # Handle optional columns if present
            for col, dtype in self.OPTIONAL_COLUMNS.items():
                if col in self.df.columns:
                    try:
                        if dtype == str:
                            self.df[col] = self.df[col].astype(str).str.strip()
                        else:
                            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                    except Exception as e:
                        logger.warning(f"Error converting optional column {col}: {str(e)}")
            
            # Convert date column to datetime
            try:
                self.df['date'] = pd.to_datetime(self.df['date'])
            except Exception as e:
                raise ValueError(f"Error parsing date column: {str(e)}")
            
            # Remove rows with missing values in required columns
            self.df = self.df.dropna(subset=list(self.REQUIRED_COLUMNS.keys()))
            
            logger.info(f"Successfully parsed CSV with {len(self.df)} rows")
            return self.df
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {source}")
            raise
        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}")
            raise

    def get_summary(self) -> Dict[str, Union[int, List[str]]]:
        """
        Get a summary of the parsed data.
        
        Returns:
            Dict containing:
                - row_count: Total number of rows
                - columns: List of available columns
                - missing_optional: List of missing optional columns
        """
        if self.df is None:
            raise ValueError("No data has been parsed yet")
            
        return {
            'row_count': len(self.df),
            'columns': list(self.df.columns),
            'missing_optional': list(set(self.OPTIONAL_COLUMNS.keys()) - set(self.df.columns))
        }

    def validate_values(self, reference_date: Optional[datetime] = None) -> List[Dict[str, Union[str, int]]]:
        """
        Perform basic validation on the parsed data.
        
        Args:
            reference_date: Optional reference date for validation (useful for testing)
        
        Returns:
            List of validation issues found
        """
        if self.df is None:
            raise ValueError("No data has been parsed yet")
            
        issues = []
        
        # Check for negative quantities
        neg_qty = self.df[self.df['quantity'] < 0]
        if not neg_qty.empty:
            issues.append({
                'type': 'negative_quantity',
                'count': len(neg_qty),
                'message': f"Found {len(neg_qty)} rows with negative quantities"
            })
        
        # Check for future dates
        today = pd.Timestamp(reference_date) if reference_date else pd.Timestamp.now()
        logger.info(f"Reference date for validation: {today}")
        future_dates = self.df[self.df['date'] > today]
        if not future_dates.empty:
            logger.info(f"Found future dates: {future_dates['date'].tolist()}")
            issues.append({
                'type': 'future_date',
                'count': len(future_dates),
                'message': f"Found {len(future_dates)} rows with future dates"
            })
        
        # Check for zero or negative prices
        invalid_prices = self.df[self.df['unit_price'] <= 0]
        if not invalid_prices.empty:
            issues.append({
                'type': 'invalid_price',
                'count': len(invalid_prices),
                'message': f"Found {len(invalid_prices)} rows with zero or negative prices"
            })
        
        return issues
