import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from typing import List, Dict, Optional, Tuple
import os
from dotenv import load_dotenv
import logging
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class GoogleSheetsHandler:
    def __init__(self):
        self.sheet_url = os.getenv("GOOGLE_SHEET_URL")
        self.credentials_file = os.getenv("GOOGLE_CREDENTIALS_FILE")
        self.scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
        self.worksheet_name = "QueryDatabase"
        self.sheet = None
        self._initialize_sheet()

    def _initialize_sheet(self):
        """Initialize connection to Google Sheets"""
        try:
            if not self.sheet_url or not self.credentials_file:
                logger.error("Missing Google Sheets configuration")
                return

            creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, self.scope)
            client = gspread.authorize(creds)
            
            # Open the spreadsheet
            try:
                spreadsheet = client.open_by_url(self.sheet_url)
                logger.info(f"Successfully opened spreadsheet: {self.sheet_url}")
            except gspread.SpreadsheetNotFound:
                logger.error(f"Could not find spreadsheet at URL: {self.sheet_url}")
                return
            
            # Try to get the worksheet, create it if it doesn't exist
            try:
                self.sheet = spreadsheet.worksheet(self.worksheet_name)
                logger.info(f"Successfully accessed worksheet: {self.worksheet_name}")
            except gspread.WorksheetNotFound:
                # Create the worksheet with headers
                self.sheet = spreadsheet.add_worksheet(self.worksheet_name, 1000, 2)
                self.sheet.append_row(["question", "sql"])
                logger.info(f"Created new worksheet: {self.worksheet_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Google Sheets: {str(e)}")
            self.sheet = None

    def save_query(self, question: str, sql_query: str) -> Tuple[bool, str]:
        """
        Save a new question and SQL query to the sheet
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self.sheet:
                logger.warning("Sheet not initialized, attempting to initialize...")
                self._initialize_sheet()  # Try to initialize again
                if not self.sheet:
                    logger.error("Failed to initialize sheet")
                    return False, "Failed to connect to Google Sheets"
            
            logger.info(f"Attempting to save query - Question: {question[:50]}...")
            
            # Ensure we have valid data
            if not question or not sql_query:
                logger.error("Invalid data: question or sql_query is empty")
                return False, "Question or SQL query is empty"
            
            # Check if this exact question already exists
            records = self.sheet.get_all_records()
            for record in records:
                if record['question'].lower().strip() == question.lower().strip():
                    logger.info(f"Question already exists: {question[:50]}...")
                    return False, "This question already exists in the database"
            
            # Append new row
            try:
                self.sheet.append_row([question, sql_query])
                logger.info("Successfully appended row to sheet")
                
                # Verify the row was added
                new_records = self.sheet.get_all_records()
                if new_records and new_records[-1]['question'] == question and new_records[-1]['sql'] == sql_query:
                    logger.info("Verified row was added successfully")
                    return True, "Query saved successfully to database!"
                else:
                    logger.error("Failed to verify row was added")
                    return False, "Failed to verify the query was saved"
            except Exception as e:
                logger.error(f"Error appending row: {str(e)}")
                return False, f"Error saving query: {str(e)}"
                
        except Exception as e:
            logger.error(f"Error saving to Google Sheets: {str(e)}")
            return False, f"Error: {str(e)}"

    def get_all_queries(self) -> List[Dict[str, str]]:
        """Retrieve all saved queries from the sheet"""
        try:
            if not self.sheet:
                self._initialize_sheet()  # Try to initialize again
                if not self.sheet:
                    return []
            
            # Get all records
            records = self.sheet.get_all_records()
            return records
        except Exception as e:
            logger.error(f"Error retrieving from Google Sheets: {str(e)}")
            return []
    
    def get_query_count(self) -> int:
        """Get the total number of saved queries"""
        try:
            records = self.get_all_queries()
            return len(records)
        except Exception as e:
            logger.error(f"Error getting query count: {str(e)}")
            return 0

    def find_exact_match(self, question: str) -> Optional[Dict[str, str]]:
        """Find exact match for a question in the sheet"""
        try:
            if not self.sheet:
                self._initialize_sheet()
                if not self.sheet:
                    return None
            
            records = self.get_all_queries()
            
            # First try exact match (case-insensitive)
            for record in records:
                if record['question'].lower().strip() == question.lower().strip():
                    logger.info(f"Found exact match for question: {question}")
                    return record
            
            # If no exact match, try fuzzy matching with high threshold
            best_match = process.extractOne(
                question,
                [record['question'] for record in records],
                scorer=fuzz.token_sort_ratio,
                score_cutoff=95  # Very high threshold for near-exact matches
            )
            
            if best_match:
                match_text, score = best_match
                logger.info(f"Found fuzzy match with score {score} for question: {question}")
                # Find the record with the matching question
                for record in records:
                    if record['question'] == match_text:
                        return record
            
            logger.info(f"No match found for question: {question}")
            return None
        except Exception as e:
            logger.error(f"Error finding exact match: {str(e)}")
            return None

    def find_similar_queries(self, question: str, threshold: float = 60) -> List[Dict[str, str]]:
        """Find similar questions in the sheet using fuzzy string matching"""
        try:
            if not self.sheet:
                self._initialize_sheet()
                if not self.sheet:
                    return []
            
            records = self.get_all_queries()
            similar_queries = []
            
            # Use multiple fuzzy matching strategies
            matches = []
            for record in records:
                # Try different fuzzy matching methods
                ratio = fuzz.ratio(question.lower(), record['question'].lower())
                partial_ratio = fuzz.partial_ratio(question.lower(), record['question'].lower())
                token_sort_ratio = fuzz.token_sort_ratio(question.lower(), record['question'].lower())
                token_set_ratio = fuzz.token_set_ratio(question.lower(), record['question'].lower())
                
                # Calculate weighted average of different matching methods
                # Give more weight to token-based methods as they handle word order better
                weighted_score = (
                    ratio * 0.2 +  # Basic ratio
                    partial_ratio * 0.2 +  # Partial string matching
                    token_sort_ratio * 0.3 +  # Token-based matching (word order independent)
                    token_set_ratio * 0.3  # Token-based matching (word order and duplicates independent)
                )
                
                if weighted_score >= threshold:
                    matches.append({
                        'question': record['question'],
                        'sql': record['sql'],
                        'score': weighted_score
                    })
            
            # Sort by score in descending order
            matches.sort(key=lambda x: x['score'], reverse=True)
            
            # Take top 5 matches
            similar_queries = matches[:5]
            
            # Log the matches for debugging
            if similar_queries:
                logger.info(f"Found {len(similar_queries)} similar queries:")
                for query in similar_queries:
                    logger.info(f"Similarity: {query['score']:.2f} - Question: {query['question']}")
            
            return similar_queries
        except Exception as e:
            logger.error(f"Error finding similar queries: {str(e)}")
            return [] 