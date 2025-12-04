"""
Data analysis utilities for sprint data processing.
Provides functions for loading, analyzing, and transforming sprint CSV data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def _convert_to_python_types(obj):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: _convert_to_python_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_to_python_types(item) for item in obj]
    return obj


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
        """Get a comprehensive summary of the dataset with calculated metrics."""
        if self.df is None:
            return {}
        
        total_tickets = len(self.df)
        done_tickets = len(self.df[self.df['Status'] == 'Done'])
        total_points = int(self.df['Story_Points'].sum()) if 'Story_Points' in self.df.columns else 0
        completed_points = int(self.df[self.df['Status'] == 'Done']['Story_Points'].sum()) if 'Story_Points' in self.df.columns else 0
        
        # Calculate overall completion rates
        overall_completion_rate = (done_tickets / total_tickets * 100) if total_tickets > 0 else 0
        points_completion_rate = (completed_points / total_points * 100) if total_points > 0 else 0
        
        # Get sprint count and velocity
        sprints = self.df['Sprint_ID'].unique().tolist() if 'Sprint_ID' in self.df.columns else []
        num_sprints = len(sprints)
        avg_velocity = completed_points / num_sprints if num_sprints > 0 else 0
        
        # Team metrics
        team_size = self.df['Assignee'].nunique() if 'Assignee' in self.df.columns else 0
        avg_points_per_person = completed_points / team_size if team_size > 0 else 0
        
        return _convert_to_python_types({
            "total_tickets": total_tickets,
            "done_tickets": done_tickets,
            "in_progress_tickets": len(self.df[self.df['Status'] == 'In Progress']),
            "todo_tickets": len(self.df[self.df['Status'] == 'To Do']),
            "overall_completion_rate": round(overall_completion_rate, 1),
            "sprints": sprints,
            "total_sprints": num_sprints,
            "ticket_types": self.df['Type'].value_counts().to_dict() if 'Type' in self.df.columns else {},
            "status_distribution": self.df['Status'].value_counts().to_dict() if 'Status' in self.df.columns else {},
            "total_story_points": total_points,
            "completed_story_points": completed_points,
            "points_completion_rate": round(points_completion_rate, 1),
            "average_velocity_per_sprint": round(avg_velocity, 1),
            "team_size": team_size,
            "avg_points_per_person": round(avg_points_per_person, 1),
            "total_bugs": len(self.df[self.df['Type'] == 'Bug']),
            "total_stories": len(self.df[self.df['Type'] == 'Story']),
            "total_tasks": len(self.df[self.df['Type'] == 'Task']),
            "date_range": {
                "start": self.df['Created_Date'].min().strftime('%Y-%m-%d') if 'Created_Date' in self.df.columns and not self.df['Created_Date'].isna().all() else None,
                "end": self.df['Created_Date'].max().strftime('%Y-%m-%d') if 'Created_Date' in self.df.columns and not self.df['Created_Date'].isna().all() else None
            }
        })
    
    def get_sprint_summary(self, sprint_id: Optional[str] = None) -> Dict[str, Any]:
        """Get summary for a specific sprint or all sprints with calculated metrics."""
        if self.df is None:
            return {}
        
        if sprint_id:
            sprint_df = self.df[self.df['Sprint_ID'] == sprint_id]
        else:
            sprint_df = self.df
        
        total_tickets = len(sprint_df)
        done_tickets = len(sprint_df[sprint_df['Status'] == 'Done'])
        total_points = int(sprint_df['Story_Points'].sum())
        completed_points = int(sprint_df[sprint_df['Status'] == 'Done']['Story_Points'].sum())
        in_progress_points = int(sprint_df[sprint_df['Status'] == 'In Progress']['Story_Points'].sum())
        
        # Calculate metrics
        completion_rate = (done_tickets / total_tickets * 100) if total_tickets > 0 else 0
        points_completion_rate = (completed_points / total_points * 100) if total_points > 0 else 0
        
        # Get capacity if available for specific sprint
        capacity = None
        capacity_utilization = None
        if sprint_id and 'Team_Capacity_Hours' in sprint_df.columns:
            capacity = sprint_df['Team_Capacity_Hours'].iloc[0] if len(sprint_df) > 0 else None
            if capacity and 'Dev_Time_Hours' in sprint_df.columns:
                actual_hours = sprint_df['Dev_Time_Hours'].sum() + sprint_df.get('QA_Time_Hours', 0).sum()
                capacity_utilization = (actual_hours / capacity * 100) if capacity > 0 else None
        
        return _convert_to_python_types({
            "sprint_id": sprint_id or "All Sprints",
            "total_tickets": total_tickets,
            "done_tickets": done_tickets,
            "in_progress_tickets": len(sprint_df[sprint_df['Status'] == 'In Progress']),
            "todo_tickets": len(sprint_df[sprint_df['Status'] == 'To Do']),
            "completion_rate_by_count": round(completion_rate, 1),
            "status_breakdown": sprint_df['Status'].value_counts().to_dict(),
            "type_breakdown": sprint_df['Type'].value_counts().to_dict(),
            "total_story_points": total_points,
            "completed_story_points": completed_points,
            "in_progress_story_points": in_progress_points,
            "points_completion_rate": round(points_completion_rate, 1),
            "velocity": completed_points,  # Story points completed
            "team_members": sprint_df['Assignee'].unique().tolist(),
            "team_size": sprint_df['Assignee'].nunique(),
            "high_priority_tickets": len(sprint_df[sprint_df['Priority'] == 'High']),
            "blocked_tickets": len(sprint_df[sprint_df['State'] == 'Blocked']) if 'State' in sprint_df.columns else 0,
            "team_capacity_hours": capacity,
            "capacity_utilization_percent": round(capacity_utilization, 1) if capacity_utilization else None
        })
    
    def get_team_performance(self) -> List[Dict[str, Any]]:
        """Get performance metrics by team member with calculated KPIs."""
        if self.df is None:
            return []
        
        performance = []
        for assignee in self.df['Assignee'].unique():
            assignee_df = self.df[self.df['Assignee'] == assignee]
            total_tickets = len(assignee_df)
            completed_tickets = len(assignee_df[assignee_df['Status'] == 'Done'])
            total_points = int(assignee_df['Story_Points'].sum())
            completed_points = int(assignee_df[assignee_df['Status'] == 'Done']['Story_Points'].sum())
            
            # Calculate completion rates
            ticket_completion_rate = (completed_tickets / total_tickets * 100) if total_tickets > 0 else 0
            points_completion_rate = (completed_points / total_points * 100) if total_points > 0 else 0
            
            # Calculate average cycle time if available
            done_df = assignee_df[assignee_df['Status'] == 'Done']
            avg_cycle_time = done_df['Cycle_Time_Days'].mean() if 'Cycle_Time_Days' in done_df.columns and not done_df.empty else None
            
            performance.append({
                "assignee": assignee,
                "role": assignee_df['Assignee_Role'].iloc[0] if 'Assignee_Role' in assignee_df.columns else None,
                "total_tickets": total_tickets,
                "completed_tickets": completed_tickets,
                "in_progress_tickets": len(assignee_df[assignee_df['Status'] == 'In Progress']),
                "todo_tickets": len(assignee_df[assignee_df['Status'] == 'To Do']),
                "ticket_completion_rate": round(ticket_completion_rate, 1),
                "total_story_points": total_points,
                "completed_story_points": completed_points,
                "points_completion_rate": round(points_completion_rate, 1),
                "average_cycle_time_days": round(avg_cycle_time, 1) if avg_cycle_time else None,
                "bugs_assigned": len(assignee_df[assignee_df['Type'] == 'Bug']),
                "stories_assigned": len(assignee_df[assignee_df['Type'] == 'Story']),
                "tasks_assigned": len(assignee_df[assignee_df['Type'] == 'Task'])
            })
        
        return _convert_to_python_types(sorted(performance, key=lambda x: x['completed_story_points'], reverse=True))
    
    def get_bug_analysis(self) -> Dict[str, Any]:
        """Analyze bug tickets with calculated metrics."""
        if self.df is None:
            return {}
        
        bugs = self.df[self.df['Type'] == 'Bug']
        total_bugs = len(bugs)
        closed_bugs = len(bugs[bugs['Status'] == 'Done'])
        open_bugs = len(bugs[bugs['Status'].isin(['To Do', 'In Progress', 'In Testing'])])
        
        # Calculate bug metrics
        resolution_rate = (closed_bugs / total_bugs * 100) if total_bugs > 0 else 0
        
        # Bug to story ratio
        total_stories = len(self.df[self.df['Type'] == 'Story'])
        bug_ratio = (total_bugs / total_stories * 100) if total_stories > 0 else 0
        
        # Average bug cycle time
        closed_bugs_df = bugs[bugs['Status'] == 'Done']
        avg_resolution_time = closed_bugs_df['Cycle_Time_Days'].mean() if 'Cycle_Time_Days' in closed_bugs_df.columns and not closed_bugs_df.empty else None
        
        return _convert_to_python_types({
            "total_bugs": total_bugs,
            "open_bugs": open_bugs,
            "closed_bugs": closed_bugs,
            "in_testing_bugs": len(bugs[bugs['Status'] == 'In Testing']),
            "resolution_rate": round(resolution_rate, 1),
            "bug_to_story_ratio": round(bug_ratio, 1),
            "average_resolution_time_days": round(avg_resolution_time, 1) if avg_resolution_time else None,
            "critical_bugs": len(bugs[bugs['Priority'] == 'Critical']),
            "high_priority_bugs": len(bugs[bugs['Priority'] == 'High']),
            "medium_priority_bugs": len(bugs[bugs['Priority'] == 'Medium']),
            "low_priority_bugs": len(bugs[bugs['Priority'] == 'Low']),
            "high_severity_bugs": len(bugs[bugs['Severity'] == 'High']) if 'Severity' in bugs.columns else 0,
            "bugs_by_sprint": bugs.groupby('Sprint_ID').size().to_dict(),
            "bugs_by_assignee": bugs['Assignee'].value_counts().to_dict(),
            "bugs_by_status": bugs['Status'].value_counts().to_dict()
        })
    
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
