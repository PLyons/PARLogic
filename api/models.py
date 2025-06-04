from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class HealthCheck(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service health status")
    service: str = Field(..., description="Service name")

class UploadResponse(BaseModel):
    """File upload response model"""
    message: str = Field(..., description="Status message")
    rows: int = Field(..., description="Number of rows processed")

class UsagePattern(BaseModel):
    """Usage pattern analysis response model"""
    item_id: str = Field(..., description="Item identifier")
    average_daily_usage: float = Field(..., description="Average daily usage")
    peak_usage: float = Field(..., description="Peak usage")
    seasonality_factor: Optional[float] = Field(None, description="Seasonality factor if detected")
    trend: str = Field(..., description="Usage trend (increasing/decreasing/stable)")
    confidence_level: float = Field(..., description="Statistical confidence level")

class PARLevels(BaseModel):
    """PAR level calculation response model"""
    item_id: str = Field(..., description="Item identifier")
    min_par: int = Field(..., description="Minimum PAR level")
    max_par: int = Field(..., description="Maximum PAR level")
    reorder_point: int = Field(..., description="Reorder point")
    safety_stock: int = Field(..., description="Safety stock level")
    service_level: float = Field(..., description="Service level used in calculation")
    lead_time_days: int = Field(..., description="Lead time in days")

class StockRecommendation(BaseModel):
    """Stock recommendation response model"""
    item_id: str = Field(..., description="Item identifier")
    current_stock: int = Field(..., description="Current stock level")
    recommended_action: str = Field(..., description="Recommended action (reorder/adjust PAR/no action)")
    urgency: str = Field(..., description="Action urgency (high/medium/low)")
    details: str = Field(..., description="Detailed recommendation")

class RecommendationResponse(BaseModel):
    """Recommendations response model"""
    recommendations: List[StockRecommendation] = Field(..., description="List of stock recommendations")
    timestamp: datetime = Field(..., description="Timestamp of recommendations")

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error details")
