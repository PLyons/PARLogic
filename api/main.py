from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import pandas as pd
from datetime import datetime
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.usage_analysis import UsageAnalyzer
from analysis.par_calc import PARCalculator
from ingestion.csv_processor import CSVProcessor
from api.models import (
    HealthCheck, UploadResponse, UsagePattern,
    PARLevels, RecommendationResponse, ErrorResponse
)
from api.security import verify_api_key

app = FastAPI(
    title="PARLogic API",
    description="""
    Hospital Supply Chain Management System API
    
    This API provides endpoints for:
    * Uploading and validating usage history data
    * Analyzing usage patterns and seasonality
    * Calculating optimal PAR levels
    * Getting inventory recommendations
    
    Authentication:
    * All endpoints require an API key
    * Include the API key in the X-API-Key header
    * Rate limits apply based on your API key tier
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthCheck, tags=["System"])
async def root(client: dict = Depends(verify_api_key)):
    """
    Health check endpoint
    
    Returns:
        HealthCheck: Service health status
    """
    return {"status": "healthy", "service": "PARLogic API"}

@app.post("/upload/", response_model=UploadResponse, tags=["Data Ingestion"])
async def upload_csv(
    file: UploadFile = File(...),
    client: dict = Depends(verify_api_key)
):
    """
    Upload and process usage history CSV file
    
    The CSV file should contain the following columns:
    * item_id: Unique identifier for the item
    * timestamp: Date and time of the transaction
    * quantity: Transaction quantity (positive for receipts, negative for issues)
    * transaction_type: Type of transaction (issue/receipt/adjustment)
    
    Args:
        file (UploadFile): CSV file containing usage history data
        
    Returns:
        UploadResponse: Processing status and number of rows processed
        
    Raises:
        HTTPException: If file validation fails
    """
    try:
        processor = CSVProcessor()
        df = await processor.process_upload(file)
        return {"message": "File processed successfully", "rows": len(df)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analyze/usage/", response_model=UsagePattern, tags=["Analysis"])
async def analyze_usage(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    item_id: Optional[str] = Query(None, description="Specific item ID to analyze"),
    client: dict = Depends(verify_api_key)
):
    """
    Analyze usage patterns for specified period
    
    This endpoint analyzes historical usage data to identify:
    * Average daily usage
    * Peak usage periods
    * Seasonality patterns
    * Usage trends
    
    Args:
        start_date (str): Analysis period start date
        end_date (str): Analysis period end date
        item_id (Optional[str]): Specific item to analyze
        
    Returns:
        UsagePattern: Usage analysis results
        
    Raises:
        HTTPException: If analysis fails or date format is invalid
    """
    try:
        analyzer = UsageAnalyzer()
        
        # Get monthly usage statistics
        monthly_stats = analyzer.calculate_monthly_usage(item_id)
        
        # Get seasonality information
        seasonality = analyzer.detect_seasonality(item_id)
        
        # Calculate trend
        if len(monthly_stats) >= 2:
            first_month = monthly_stats.iloc[0]['total_usage']
            last_month = monthly_stats.iloc[-1]['total_usage']
            trend = "increasing" if last_month > first_month else "decreasing" if last_month < first_month else "stable"
        else:
            trend = "stable"
        
        # Prepare response
        item_seasonality = seasonality[item_id] if item_id in seasonality else next(iter(seasonality.values()))
        monthly_avg = monthly_stats['avg_daily_usage'].mean()
        monthly_max = monthly_stats['max_usage'].max()
        
        return {
            "item_id": item_id or next(iter(seasonality.keys())),
            "average_daily_usage": float(monthly_avg),
            "peak_usage": float(monthly_max),
            "seasonality_factor": float(item_seasonality['seasonality_strength']),
            "trend": trend,
            "confidence_level": 0.95  # Default confidence level
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/calculate/par/", response_model=PARLevels, tags=["PAR Levels"])
async def calculate_par(
    item_id: str = Query(..., description="Item ID to calculate PAR levels for"),
    service_level: float = Query(0.95, description="Desired service level (0-1)"),
    lead_time_days: int = Query(..., description="Lead time in days"),
    client: dict = Depends(verify_api_key)
):
    """
    Calculate PAR levels for specified item
    
    This endpoint calculates:
    * Minimum PAR level
    * Maximum PAR level
    * Reorder point
    * Safety stock level
    
    The calculation takes into account:
    * Historical usage patterns
    * Seasonality
    * Service level requirements
    * Lead time
    
    Args:
        item_id (str): Item to calculate PAR levels for
        service_level (float): Desired service level (default: 0.95)
        lead_time_days (int): Lead time for replenishment
        
    Returns:
        PARLevels: Calculated PAR levels and related metrics
        
    Raises:
        HTTPException: If calculation fails or parameters are invalid
    """
    try:
        calculator = PARCalculator()
        results = calculator.calculate_par_levels(
            item_id=item_id,
            service_level=service_level,
            lead_time_days=lead_time_days
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/recommendations/", response_model=RecommendationResponse, tags=["Recommendations"])
async def get_recommendations(
    item_id: Optional[str] = Query(None, description="Specific item ID for recommendations"),
    client: dict = Depends(verify_api_key)
):
    """
    Get inventory recommendations
    
    This endpoint provides recommendations for:
    * Stock replenishment
    * PAR level adjustments
    * Urgent actions needed
    
    Args:
        item_id (Optional[str]): Specific item to get recommendations for
        
    Returns:
        RecommendationResponse: List of recommendations and timestamp
        
    Raises:
        HTTPException: If recommendation generation fails
    """
    try:
        calculator = PARCalculator()
        recommendations = calculator.get_recommendations(item_id=item_id)
        return {
            "recommendations": recommendations,
            "timestamp": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom exception handler to ensure consistent error responses"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=str(exc.detail)).model_dump()
    )
