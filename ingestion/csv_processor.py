import pandas as pd
from fastapi import UploadFile, HTTPException
import os
from typing import Optional
from datetime import datetime
import aiofiles
from config.api_config import settings

class CSVProcessor:
    """Handles CSV file processing and validation"""
    
    REQUIRED_COLUMNS = [
        "item_id",
        "timestamp",
        "quantity",
        "transaction_type"
    ]
    
    async def process_upload(self, file: UploadFile) -> pd.DataFrame:
        """Process and validate uploaded CSV file"""
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are allowed"
            )
            
        # Create temp file path
        temp_path = os.path.join(settings.UPLOAD_DIR, f"temp_{datetime.now().timestamp()}.csv")
        
        try:
            # Save uploaded file
            async with aiofiles.open(temp_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            
            # Read and validate CSV
            df = pd.read_csv(temp_path)
            self._validate_dataframe(df)
            
            return df
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def _validate_dataframe(self, df: pd.DataFrame) -> None:
        """Validate DataFrame structure and content"""
        # Check required columns
        missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required columns: {', '.join(missing_cols)}"
            )
        
        # Validate data types
        try:
            df['item_id'] = df['item_id'].astype(str)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['quantity'] = pd.to_numeric(df['quantity'])
            df['transaction_type'] = df['transaction_type'].astype(str)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid data format: {str(e)}"
            )
        
        # Validate transaction types
        valid_types = {'issue', 'receipt', 'adjustment'}
        invalid_types = set(df['transaction_type'].unique()) - valid_types
        if invalid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid transaction types: {', '.join(invalid_types)}"
            )
        
        # Validate quantities
        if (df['quantity'] == 0).any():
            raise HTTPException(
                status_code=400,
                detail="Quantity cannot be zero"
            ) 