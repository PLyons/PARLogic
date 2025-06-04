"""
Usage Analysis Module for PARLogic.
Calculates key metrics from inventory data including:
- Monthly usage patterns
- Min/Max ranges
- Seasonal trends
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
import logging
from datetime import datetime
import calendar

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UsageAnalyzer:
    """Analyzes inventory usage patterns and calculates key metrics."""
    
    def __init__(self, df: Optional[pd.DataFrame] = None):
        """
        Initialize the analyzer with optional DataFrame.
        
        Args:
            df: Optional pandas DataFrame with inventory data
        """
        self.df = df
        self._validate_df() if df is not None else None
        
    def set_data(self, df: pd.DataFrame) -> None:
        """
        Set the data to analyze.
        
        Args:
            df: pandas DataFrame with inventory data
        """
        self.df = df
        self._validate_df()
        
    def _validate_df(self) -> None:
        """Validate that DataFrame has required columns."""
        required_cols = {'item_id', 'date', 'quantity'}
        if not all(col in self.df.columns for col in required_cols):
            raise ValueError(f"DataFrame missing required columns. Must have: {required_cols}")
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(self.df['date']):
            try:
                self.df['date'] = pd.to_datetime(self.df['date'])
            except Exception as e:
                raise ValueError(f"Could not convert date column to datetime: {str(e)}")
    
    def calculate_monthly_usage(self, item_id: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate monthly usage statistics for all items or a specific item.
        
        Args:
            item_id: Optional item ID to filter by
            
        Returns:
            DataFrame with monthly usage statistics:
            - Month
            - Total Usage
            - Average Daily Usage
            - Min Usage
            - Max Usage
            - Standard Deviation
        """
        if self.df is None:
            raise ValueError("No data has been set. Call set_data() first.")
            
        if len(self.df) == 0:
            return pd.DataFrame(columns=[
                'month', 'item_id', 'total_usage', 'avg_daily_usage',
                'min_usage', 'max_usage', 'std_dev'
            ])
            
        # Filter by item_id if provided
        df = self.df[self.df['item_id'] == item_id] if item_id else self.df
        
        # Group by month and calculate metrics
        monthly_stats = (
            df.groupby([
                pd.Grouper(key='date', freq='M'),
                'item_id'
            ])['quantity']
            .agg([
                ('total_usage', 'sum'),
                ('min_usage', 'min'),
                ('max_usage', 'max'),
                ('std_dev', 'std')
            ])
            .reset_index()
        )
        
        # Calculate average daily usage based on days in month
        monthly_stats['avg_daily_usage'] = monthly_stats.apply(
            lambda row: row['total_usage'] / calendar.monthrange(
                row['date'].year, row['date'].month
            )[1],
            axis=1
        )
        
        # Rename date column to month for clarity
        monthly_stats = monthly_stats.rename(columns={'date': 'month'})
        
        # Ensure columns are in the expected order
        column_order = [
            'month', 'item_id', 'total_usage', 'avg_daily_usage',
            'min_usage', 'max_usage', 'std_dev'
        ]
        monthly_stats = monthly_stats[column_order]
        
        return monthly_stats
    
    def calculate_usage_range(self, item_id: Optional[str] = None) -> Dict[str, Dict[str, float]]:
        """
        Calculate min/max usage ranges for all items or a specific item.
        
        Args:
            item_id: Optional item ID to filter by
            
        Returns:
            Dictionary with usage ranges per item:
            {
                'item_id': {
                    'min_monthly': float,
                    'max_monthly': float,
                    'avg_monthly': float,
                    'std_dev': float
                }
            }
        """
        if self.df is None:
            raise ValueError("No data has been set. Call set_data() first.")
            
        # Filter by item_id if provided
        df = self.df[self.df['item_id'] == item_id] if item_id else self.df
        
        # Group by item and month to get monthly totals
        monthly_totals = (
            df.groupby([
                'item_id',
                df['date'].dt.to_period('M')
            ])['quantity']
            .sum()
            .reset_index()
        )
        
        # Calculate ranges per item
        ranges = {}
        for item in monthly_totals['item_id'].unique():
            item_data = monthly_totals[monthly_totals['item_id'] == item]['quantity']
            ranges[item] = {
                'min_monthly': float(item_data.min()),
                'max_monthly': float(item_data.max()),
                'avg_monthly': float(item_data.mean()),
                'std_dev': float(item_data.std())
            }
            
        return ranges
    
    def detect_seasonality(self, item_id: Optional[str] = None) -> Dict[str, Dict[str, Union[bool, int, float]]]:
        """
        Detect seasonal patterns in usage data.
        
        Args:
            item_id: Optional item ID to filter by
            
        Returns:
            Dictionary with seasonality metrics per item:
            {
                'item_id': {
                    'seasonal_pattern': bool,
                    'peak_month': int,
                    'trough_month': int,
                    'seasonality_strength': float
                }
            }
        """
        if self.df is None:
            raise ValueError("No data has been set. Call set_data() first.")
            
        # Filter by item_id if provided
        df = self.df[self.df['item_id'] == item_id] if item_id else self.df
        
        # Group by item and month to get monthly averages
        monthly_avg = (
            df.groupby([
                'item_id',
                df['date'].dt.month
            ])['quantity']
            .mean()
            .reset_index()
        )
        
        seasonality = {}
        for item in monthly_avg['item_id'].unique():
            item_data = monthly_avg[monthly_avg['item_id'] == item]
            
            # Calculate metrics
            max_month = int(item_data.loc[item_data['quantity'].idxmax(), 'date'])
            min_month = int(item_data.loc[item_data['quantity'].idxmin(), 'date'])
            
            # Calculate seasonality strength (ratio of max to min)
            max_val = item_data['quantity'].max()
            min_val = item_data['quantity'].min()
            strength = (max_val - min_val) / (max_val + min_val) if (max_val + min_val) > 0 else 0
            
            # A seasonal pattern exists if the strength is above 0.2 (20% variation)
            seasonality[item] = {
                'seasonal_pattern': strength > 0.2,
                'peak_month': max_month,
                'trough_month': min_month,
                'seasonality_strength': float(strength)
            }
            
        return seasonality 