"""
Data analysis utilities for sprint data processing.
Provides functions for loading, analyzing, and transforming sprint CSV data.
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SprintDataAnalyzer:
    """Handles all data analysis operations on sprint data."""
    
    def __init__(self, csv_path: str):
        """Initialize with CSV file path."""
        self.csv_path = csv_path
        self.df: Optional[pd.DataFrame] = None
        self._load_data()
    
    def _load_data(self):
        """Load and preprocess the CSV data."""
        try:
            self.df = pd.read_csv(self.csv_path)
            
            # Convert date columns to datetime
            date_columns = ['Created_Date', 'Started_Date', 'Completed_Date']
            for col in date_columns:
                if col in self.df.columns:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
            
            # Convert Story_Points to numeric
            if 'Story_Points' in self.df.columns:
                self.df['Story_Points'] = pd.to_numeric(self.df['Story_Points'], errors='coerce')
            
            logger.info(f"Successfully loaded {len(self.df)} records from {self.csv_path}")
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the dataset."""
        if self.df is None:
            return {}
        
        return {
            "total_tickets": len(self.df),
            "columns": list(self.df.columns),
            "sprints": self.df['Sprint_ID'].unique().tolist() if 'Sprint_ID' in self.df.columns else [],
            "ticket_types": self.df['Type'].value_counts().to_dict() if 'Type' in self.df.columns else {},
            "status_distribution": self.df['Status'].value_counts().to_dict() if 'Status' in self.df.columns else {},
            "total_story_points": int(self.df['Story_Points'].sum()) if 'Story_Points' in self.df.columns else 0,
            "date_range": {
                "start": self.df['Created_Date'].min().strftime('%Y-%m-%d') if 'Created_Date' in self.df.columns and not self.df['Created_Date'].isna().all() else None,
                "end": self.df['Created_Date'].max().strftime('%Y-%m-%d') if 'Created_Date' in self.df.columns and not self.df['Created_Date'].isna().all() else None
            }
        }
    
    def get_sprint_summary(self, sprint_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary for a specific sprint or all sprints."""
        if self.df is None:
            return {}
        
        if sprint_id:
            sprint_df = self.df[self.df['Sprint_ID'] == sprint_id]
        else:
            sprint_df = self.df
        
        return {
            "sprint_id": sprint_id or "All Sprints",
            "total_tickets": len(sprint_df),
            "status_breakdown": sprint_df['Status'].value_counts().to_dict(),
            "type_breakdown": sprint_df['Type'].value_counts().to_dict(),
            "total_story_points": int(sprint_df['Story_Points'].sum()),
            "completed_story_points": int(sprint_df[sprint_df['Status'] == 'Done']['Story_Points'].sum()),
            "in_progress_tickets": len(sprint_df[sprint_df['Status'] == 'In Progress']),
            "team_members": sprint_df['Assignee'].unique().tolist(),
            "high_priority_tickets": len(sprint_df[sprint_df['Priority'] == 'High'])
        }
    
    def get_team_performance(self) -> List[Dict[str, Any]]:
        """Get performance metrics by team member."""
        if self.df is None:
            return []
        
        performance = []
        for assignee in self.df['Assignee'].unique():
            assignee_df = self.df[self.df['Assignee'] == assignee]
            performance.append({
                "assignee": assignee,
                "role": assignee_df['Assignee_Role'].iloc[0] if 'Assignee_Role' in assignee_df.columns else None,
                "total_tickets": len(assignee_df),
                "completed_tickets": len(assignee_df[assignee_df['Status'] == 'Done']),
                "in_progress_tickets": len(assignee_df[assignee_df['Status'] == 'In Progress']),
                "total_story_points": int(assignee_df['Story_Points'].sum()),
                "completed_story_points": int(assignee_df[assignee_df['Status'] == 'Done']['Story_Points'].sum())
            })
        
        return sorted(performance, key=lambda x: x['completed_story_points'], reverse=True)
    
    def get_bug_analysis(self) -> Dict[str, Any]:
        """Analyze bug tickets."""
        if self.df is None:
            return {}
        
        bugs = self.df[self.df['Type'] == 'Bug']
        
        return {
            "total_bugs": len(bugs),
            "open_bugs": len(bugs[bugs['Status'].isin(['To Do', 'In Progress', 'In Testing'])]),
            "closed_bugs": len(bugs[bugs['Status'] == 'Done']),
            "critical_bugs": len(bugs[bugs['Priority'] == 'Critical']),
            "high_priority_bugs": len(bugs[bugs['Priority'] == 'High']),
            "bugs_by_sprint": bugs.groupby('Sprint_ID').size().to_dict(),
            "bugs_by_assignee": bugs['Assignee'].value_counts().to_dict()
        }
    
    def query_data(self, query: str) -> pd.DataFrame:
        """Execute a pandas query on the dataframe."""
        if self.df is None:
            return pd.DataFrame()
        
        try:
            return self.df.query(query)
        except Exception as e:
            logger.error(f"Query error: {str(e)}")
            return pd.DataFrame()
    
    def get_filtered_data(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """Filter data based on provided criteria."""
        if self.df is None:
            return pd.DataFrame()
        
        filtered_df = self.df.copy()
        
        for key, value in filters.items():
            if key in filtered_df.columns:
                if isinstance(value, list):
                    filtered_df = filtered_df[filtered_df[key].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[key] == value]
        
        return filtered_df
    
    def get_dataframe(self) -> pd.DataFrame:
        """Return the raw dataframe."""
        return self.df if self.df is not None else pd.DataFrame()
