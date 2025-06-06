from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from typing import Optional, List
from pydantic import BaseModel
import logging
import io
import os
import sys
from pathlib import Path

# Configure logging
try:
    # Create logs directory in the same directory as this file
    current_dir = Path(__file__).parent
    log_dir = current_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging to both file and console
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "parlogic.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_dir / 'parlogic.log'}")
except Exception as e:
    print(f"Error setting up logging: {str(e)}")
    sys.exit(1)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data storage (in production, this would be a database)
inventory_data = {}
extended_data = {}  # For storing additional HCO data fields

class HCODataMapping:
    REQUIRED_MAPPINGS = {
        'item_id': ['HCO Item Number', 'item_id'],
        'date': ['HCO Transaction Date', 'date'],
        'quantity': ['HCO Quantity', 'quantity']
    }
    
    EXTENDED_FIELDS = [
        'Facility Type',
        'HCO UOM',
        'Department Code',
        'Contract Type Flag',
        'Contract ID',
        'PSC',
        'UNSPSC Class'
    ]

    @staticmethod
    def is_hco_format(columns):
        logger.debug(f"[FORMAT CHECK] Checking columns for HCO format: {columns}")
        # Check if any of the HCO columns are present for each required field
        for target_col, source_cols in HCODataMapping.REQUIRED_MAPPINGS.items():
            if not any(col in columns for col in source_cols):
                logger.debug(f"[FORMAT CHECK] Missing mapping for {target_col}. Looking for any of: {source_cols}")
                return False
            logger.debug(f"[FORMAT CHECK] Found mapping for {target_col}")
        return True

class UsagePattern(BaseModel):
    item_id: str
    average_daily_usage: float
    peak_usage: float
    seasonality_factor: Optional[float] = None
    trend: str
    confidence_level: float

class PARLevels(BaseModel):
    item_id: str
    min_par: float
    max_par: float
    reorder_point: float
    safety_stock: float

class StockRecommendation(BaseModel):
    item_id: str
    current_stock: int
    recommended_order: int
    urgency: str
    next_review_date: str

@app.post("/upload")
async def upload_file(file: UploadFile):
    logger.info(f"[UPLOAD START] Received file upload request: {file.filename}")
    
    if not file.filename.endswith('.csv'):
        logger.error(f"Invalid file type: {file.filename}")
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        # Read the file content
        contents = await file.read()
        logger.info(f"[FILE READ] File size: {len(contents)} bytes")
        
        # Convert to StringIO for pandas
        csv_file = io.StringIO(contents.decode('utf-8'))
        
        # Read CSV content
        df = pd.read_csv(csv_file)
        logger.info(f"[CSV READ] Columns: {df.columns.tolist()}")
        logger.info(f"[CSV READ] Shape: {df.shape}")
        
        # First check for HCO format
        has_hco_format = HCODataMapping.is_hco_format(df.columns)
        logger.info(f"[FORMAT CHECK] HCO format detected: {has_hco_format}")
        
        if has_hco_format:
            logger.info("[PROCESSING] Using HCO format")
            # Create mapped dataframe with required columns
            mapped_df = pd.DataFrame()
            
            # Map required columns
            for target_col, source_cols in HCODataMapping.REQUIRED_MAPPINGS.items():
                for source_col in source_cols:
                    if source_col in df.columns:
                        mapped_df[target_col] = df[source_col]
                        logger.info(f"[MAPPING] Mapped {source_col} to {target_col}")
                        break
            
            # Store extended data if available
            extended_cols = [col for col in HCODataMapping.EXTENDED_FIELDS if col in df.columns]
            if extended_cols:
                extended_df = df[extended_cols].copy()
                extended_df['item_id'] = mapped_df['item_id']  # Add item_id for reference
                logger.info(f"[EXTENDED DATA] Found fields: {extended_cols}")
            
            # Use mapped dataframe for further processing
            df = mapped_df
            
        else:
            logger.info("[PROCESSING] Using simple format")
            # For simple format, verify required columns exist
            required_columns = ['item_id', 'date', 'quantity']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                error_msg = f"Missing required columns: {missing_columns}"
                logger.error(f"[FORMAT ERROR] {error_msg}")
                raise HTTPException(status_code=400, detail=error_msg)

        # Verify we have all required columns after mapping
        required_columns = ['item_id', 'date', 'quantity']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Missing required columns after mapping: {missing_columns}"
            logger.error(f"[MAPPING ERROR] {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        # Validate data types
        try:
            logger.info("[VALIDATION] Starting data type validation")
            df['date'] = pd.to_datetime(df['date'])
            df['quantity'] = pd.to_numeric(df['quantity'])
            logger.info("[VALIDATION] Data type validation successful")
        except Exception as e:
            logger.error(f"[VALIDATION ERROR] {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data types. Date should be in YYYY-MM-DD format and quantity should be numeric. Error: {str(e)}"
            )

        # Store data
        stored_items = []
        for item_id in df['item_id'].unique():
            item_data = df[df['item_id'] == item_id]
            inventory_data[item_id] = item_data.to_dict('records')
            stored_items.append(item_id)
            
            # Store extended data if available
            if has_hco_format and extended_cols:
                item_extended = extended_df[extended_df['item_id'] == item_id]
                if not item_extended.empty:
                    extended_data[item_id] = item_extended.to_dict('records')
                    logger.info(f"[STORAGE] Stored extended data for item_id: {item_id}")
            
            logger.info(f"[STORAGE] Stored data for item_id: {item_id}, records: {len(item_data)}")
        
        return {
            "message": "File uploaded successfully",
            "rows": len(df),
            "items": len(df['item_id'].unique()),
            "date_range": f"{df['date'].min()} to {df['date'].max()}",
            "format": "HCO" if has_hco_format else "simple",
            "extended_fields": extended_cols if has_hco_format else []
        }
        
    except pd.errors.EmptyDataError:
        logger.error("[ERROR] Empty CSV file")
        raise HTTPException(status_code=400, detail="The CSV file is empty")
        
    except pd.errors.ParserError as e:
        logger.error(f"[ERROR] CSV parsing error: {str(e)}")
        raise HTTPException(status_code=400, detail="Error parsing CSV file. Please check the file format.")
        
    except Exception as e:
        logger.error(f"[ERROR] Unexpected error during file upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    finally:
        await file.close()

@app.get("/analyze/usage/")
async def analyze_usage(start_date: str, end_date: str, item_id: Optional[str] = None) -> UsagePattern:
    if not inventory_data:
        raise HTTPException(status_code=404, detail="No data available. Please upload data first.")
    
    if item_id and item_id not in inventory_data:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    
    # Sample analysis (replace with actual analysis in production)
    sample_item = item_id or list(inventory_data.keys())[0]
    return UsagePattern(
        item_id=sample_item,
        average_daily_usage=15.5,
        peak_usage=25.0,
        seasonality_factor=1.2,
        trend="increasing",
        confidence_level=0.95
    )

@app.get("/par/{item_id}")
async def get_par_levels(item_id: str) -> PARLevels:
    if not inventory_data:
        raise HTTPException(status_code=404, detail="No data available. Please upload data first.")
    
    if item_id not in inventory_data:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    
    # Get basic inventory data
    item_records = inventory_data[item_id]
    df = pd.DataFrame(item_records)
    
    # Calculate base metrics
    daily_usage = df.groupby(df['date'].dt.date)['quantity'].sum()
    avg_daily_usage = daily_usage.mean()
    std_daily_usage = daily_usage.std()
    
    # Enhanced calculations using extended data if available
    if item_id in extended_data:
        ext_data = pd.DataFrame(extended_data[item_id])
        
        # Adjust for facility type if available
        if 'Facility Type' in ext_data.columns:
            facility_factor = 1.2 if ext_data['Facility Type'].iloc[0] == 'Hospital' else 1.0
            avg_daily_usage *= facility_factor
        
        # Adjust for contract requirements if available
        if 'Contract Type Flag' in ext_data.columns and 'Contract ID' in ext_data.columns:
            has_contract = not ext_data['Contract ID'].iloc[0].isna()
            contract_factor = 1.1 if has_contract else 1.0
            avg_daily_usage *= contract_factor
    
    # Calculate PAR levels
    safety_stock = std_daily_usage * 2  # 2 sigma for 95% service level
    min_par = avg_daily_usage * 3  # 3 days minimum stock
    max_par = avg_daily_usage * 7  # 7 days maximum stock
    reorder_point = min_par + safety_stock
    
    return PARLevels(
        item_id=item_id,
        min_par=float(min_par),
        max_par=float(max_par),
        reorder_point=float(reorder_point),
        safety_stock=float(safety_stock)
    )

@app.get("/recommendations")
async def get_recommendations() -> List[StockRecommendation]:
    if not inventory_data:
        raise HTTPException(status_code=404, detail="No data available. Please upload data first.")
    
    # Sample recommendations (replace with actual calculations in production)
    recommendations = []
    for item_id in inventory_data:
        recommendations.append(
            StockRecommendation(
                item_id=item_id,
                current_stock=50,
                recommended_order=25,
                urgency="medium",
                next_review_date=(datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            )
        )
    return recommendations

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
