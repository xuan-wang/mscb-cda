from pathlib import Path
import pandas as pd
from typing import Union, Optional
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def read_csv(file_path: Union[str, Path], 
             date_column: str = 'Date',
             parse_dates: bool = True) -> pd.DataFrame:
    """
    Read CSV file with error handling and date parsing
    
    Args:
        file_path: Path to CSV file
        date_column: Name of date column
        parse_dates: Whether to parse dates
        
    Returns:
        DataFrame from CSV file
    """
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        df = pd.read_csv(file_path)
        
        if parse_dates and date_column in df.columns:
            df = process_dates(df, date_column)
            
        return df
        
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path}: {str(e)}")
        raise

def process_dates(df: pd.DataFrame, 
                 date_column: str = 'Date') -> pd.DataFrame:
    """
    Process date column in DataFrame
    
    Args:
        df: Input DataFrame
        date_column: Name of date column
        
    Returns:
        DataFrame with processed dates
    """
    try:
        df[date_column] = pd.to_datetime(df[date_column])
        return df.sort_values(by=date_column).reset_index(drop=True)
    except Exception as e:
        logger.error(f"Error processing dates: {str(e)}")
        raise

def save_to_csv(df: pd.DataFrame, 
                file_path: Union[str, Path], 
                index: bool = False) -> None:
    """
    Save DataFrame to CSV with error handling
    
    Args:
        df: DataFrame to save
        file_path: Path to save CSV
        index: Whether to save index
    """
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(file_path, index=index)
        logger.info(f"Successfully saved CSV to {file_path}")
    except Exception as e:
        logger.error(f"Error saving CSV to {file_path}: {str(e)}")
        raise

def validate_data(df: pd.DataFrame, 
                 required_columns: list,
                 date_column: str = 'Date') -> bool:
    """
    Validate DataFrame structure and content
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        date_column: Name of date column
        
    Returns:
        bool: True if validation passes
    """
    try:
        # Check required columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Validate date column
        if date_column in df.columns:
            invalid_dates = df[~pd.to_datetime(df[date_column], errors='coerce').notna()]
            if not invalid_dates.empty:
                raise ValueError(f"Invalid dates found in rows: {invalid_dates.index.tolist()}")
                
        return True
        
    except Exception as e:
        logger.error(f"Data validation failed: {str(e)}")
        raise