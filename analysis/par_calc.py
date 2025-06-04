"""
PAR Level Calculator Module for PARLogic.

This module calculates optimal PAR levels and reorder points based on:
- Historical usage patterns
- Seasonality factors
- Safety stock requirements
- Lead time variability
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Union, List
import logging
from datetime import datetime
from .usage_analysis import UsageAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PARCalculator:
    """Calculates optimal PAR levels and reorder points for inventory items."""
    
    def __init__(
        self,
        usage_data: Optional[pd.DataFrame] = None,
        lead_time_days: Optional[Dict[str, int]] = None,
        service_level: float = 0.95,
        review_period_days: int = 7
    ):
        """
        Initialize the PAR calculator.
        
        Args:
            usage_data: Optional DataFrame with historical usage data
            lead_time_days: Dict mapping item_id to lead time in days
            service_level: Desired service level (default: 95%)
            review_period_days: Review period in days (default: 7 days)
        """
        self.usage_analyzer = UsageAnalyzer(usage_data)
        self.lead_time_days = lead_time_days or {}
        self.service_level = service_level
        self.review_period_days = review_period_days
        
        # Service level to Z-score mapping for safety stock
        self.z_score = {
            0.90: 1.28,
            0.95: 1.645,
            0.98: 2.054,
            0.99: 2.326,
            0.999: 3.090
        }.get(service_level, 1.645)  # Default to 95% if not found
        
    def set_data(self, usage_data: pd.DataFrame) -> None:
        """Set the usage data for analysis."""
        self.usage_analyzer.set_data(usage_data)
        
    def set_lead_time(self, item_id: str, days: int) -> None:
        """Set the lead time for a specific item."""
        self.lead_time_days[item_id] = days
        
    def calculate_safety_stock(
        self,
        item_id: str,
        usage_stats: Dict[str, float],
        seasonality: Dict[str, Union[bool, int, float]]
    ) -> float:
        """
        Calculate safety stock level based on usage variability and lead time.
        
        Args:
            item_id: Item identifier
            usage_stats: Dictionary with usage statistics
            seasonality: Dictionary with seasonality information
            
        Returns:
            Recommended safety stock level
        """
        lead_time = self.lead_time_days.get(item_id, 14)  # Default to 14 days if not specified
        
        # Calculate daily standard deviation from monthly
        daily_std = usage_stats['std_dev'] / np.sqrt(30)
        
        # Adjust for seasonality if present
        if seasonality['seasonal_pattern']:
            # Increase safety stock during peak months
            current_month = datetime.now().month
            if current_month == seasonality['peak_month']:
                daily_std *= (1 + seasonality['seasonality_strength'])
        
        # Safety stock = Z × σ × √(L + R)
        # Where: Z = service level factor
        #        σ = daily standard deviation
        #        L = lead time
        #        R = review period
        safety_stock = self.z_score * daily_std * np.sqrt(lead_time + self.review_period_days)
        
        return float(safety_stock)
    
    def calculate_par_levels(
        self,
        item_id: Optional[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate PAR levels for one or all items.
        
        Args:
            item_id: Optional item ID to calculate for
            
        Returns:
            Dictionary with PAR levels and related metrics:
            {
                'item_id': {
                    'min_par': float,
                    'max_par': float,
                    'reorder_point': float,
                    'safety_stock': float,
                    'avg_daily_usage': float,
                    'lead_time_days': int,
                    'review_period_days': int
                }
            }
        """
        # Get usage statistics
        usage_ranges = self.usage_analyzer.calculate_usage_range(item_id)
        seasonality = self.usage_analyzer.detect_seasonality(item_id)
        
        par_levels = {}
        for item, stats in usage_ranges.items():
            if item_id and item != item_id:
                continue
                
            # Get lead time for item
            lead_time = self.lead_time_days.get(item, 14)  # Default to 14 days
            
            # Calculate average daily usage
            avg_daily_usage = stats['avg_monthly'] / 30
            
            # Calculate safety stock
            safety_stock = self.calculate_safety_stock(
                item,
                stats,
                seasonality[item]
            )
            
            # Calculate reorder point
            # ROP = (Average daily usage × Lead time) + Safety stock
            reorder_point = (avg_daily_usage * lead_time) + safety_stock
            
            # Calculate min and max PAR levels
            # Min PAR = Reorder point
            # Max PAR = ROP + (Average daily usage × Review period)
            min_par = reorder_point
            max_par = reorder_point + (avg_daily_usage * self.review_period_days)
            
            # Store results
            par_levels[item] = {
                'min_par': float(min_par),
                'max_par': float(max_par),
                'reorder_point': float(reorder_point),
                'safety_stock': float(safety_stock),
                'avg_daily_usage': float(avg_daily_usage),
                'lead_time_days': lead_time,
                'review_period_days': self.review_period_days
            }
            
        return par_levels
    
    def get_recommendations(
        self,
        item_id: Optional[str] = None,
        current_stock: Optional[Dict[str, int]] = None
    ) -> Dict[str, Dict[str, Union[float, str, bool]]]:
        """
        Get PAR level recommendations and reorder suggestions.
        
        Args:
            item_id: Optional item ID to get recommendations for
            current_stock: Optional dict of current stock levels
            
        Returns:
            Dictionary with recommendations:
            {
                'item_id': {
                    'min_par': float,
                    'max_par': float,
                    'reorder_point': float,
                    'current_stock': float,
                    'needs_reorder': bool,
                    'reorder_amount': float,
                    'status': str,
                    'recommendation': str
                }
            }
        """
        # Calculate PAR levels
        par_levels = self.calculate_par_levels(item_id)
        
        # Get current stock levels or use empty dict
        current_stock = current_stock or {}
        
        recommendations = {}
        for item, levels in par_levels.items():
            stock = current_stock.get(item, 0)
            
            # Determine if reorder is needed
            needs_reorder = stock <= levels['reorder_point']
            
            # Calculate reorder amount if needed
            reorder_amount = levels['max_par'] - stock if needs_reorder else 0
            
            # Determine status
            if stock < levels['min_par']:
                status = 'BELOW_MIN'
            elif stock > levels['max_par']:
                status = 'ABOVE_MAX'
            else:
                status = 'OPTIMAL'
                
            # Generate recommendation text
            if needs_reorder:
                recommendation = (
                    f"Place order for {int(reorder_amount)} units to reach optimal stock level. "
                    f"Current stock ({int(stock)}) is below reorder point ({int(levels['reorder_point'])})."
                )
            elif status == 'ABOVE_MAX':
                recommendation = (
                    f"Stock level ({int(stock)}) is above maximum PAR ({int(levels['max_par'])}). "
                    f"Consider reducing order quantities."
                )
            else:
                recommendation = "Stock levels are within optimal range. No action needed."
            
            recommendations[item] = {
                'min_par': levels['min_par'],
                'max_par': levels['max_par'],
                'reorder_point': levels['reorder_point'],
                'current_stock': float(stock),
                'needs_reorder': needs_reorder,
                'reorder_amount': float(reorder_amount),
                'status': status,
                'recommendation': recommendation
            }
            
        return recommendations 