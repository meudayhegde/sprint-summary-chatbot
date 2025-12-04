"""
Dashboard data analyzer for sprint metrics and visualizations.
Provides data for all dashboard charts and KPIs.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
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
    elif pd.isna(obj):
        return None
    return obj


class DashboardAnalyzer:
    """Handles all dashboard data calculations and transformations."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with DataFrame."""
        self.df = df.copy()
        self._preprocess_data()
    
    def _preprocess_data(self):
        """Preprocess data for dashboard calculations."""
        # Convert date columns
        date_columns = ['Created_Date', 'Started_Date', 'Completed_Date', 'Sprint_Start', 'Sprint_End']
        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = ['Story_Points', 'Cycle_Time_Days', 'Dev_Time_Hours', 
                          'QA_Time_Hours', 'Estimated_Hours', 'Team_Capacity_Hours']
        for col in numeric_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
    
    def get_kpis(self) -> Dict[str, Any]:
        """
        Calculate all KPIs for Sheet 1.
        Returns: Sprint Velocity, Delivery %, Bug Count, Spillover %, Avg Cycle Time
        """
        # Get all sprints
        sprints = self.df['Sprint_ID'].unique()
        
        # Calculate per-sprint metrics
        sprint_metrics = []
        for sprint in sprints:
            sprint_data = self.df[self.df['Sprint_ID'] == sprint]
            
            # Planned vs completed story points
            planned_points = sprint_data['Story_Points'].sum()
            completed_points = sprint_data[sprint_data['Status'] == 'Done']['Story_Points'].sum()
            
            # Bug count
            bugs = len(sprint_data[sprint_data['Type'] == 'Bug'])
            
            # Spillover items
            spillover = len(sprint_data[sprint_data['State'] == 'Spillover'])
            total_items = len(sprint_data)
            spillover_pct = (spillover / total_items * 100) if total_items > 0 else 0
            
            # Cycle time
            completed = sprint_data[(sprint_data['Status'] == 'Done') & 
                                   (sprint_data['Cycle_Time_Days'].notna())]
            avg_cycle_time = completed['Cycle_Time_Days'].mean() if len(completed) > 0 else 0
            
            sprint_metrics.append({
                'sprint_id': sprint,
                'velocity': completed_points,
                'planned_points': planned_points,
                'delivery_pct': (completed_points / planned_points * 100) if planned_points > 0 else 0,
                'bugs': bugs,
                'spillover_pct': spillover_pct,
                'avg_cycle_time': avg_cycle_time
            })
        
        # Overall metrics
        total_completed = sum(m['velocity'] for m in sprint_metrics)
        total_planned = sum(m['planned_points'] for m in sprint_metrics)
        avg_velocity = total_completed / len(sprint_metrics) if len(sprint_metrics) > 0 else 0
        overall_delivery = (total_completed / total_planned * 100) if total_planned > 0 else 0
        total_bugs = self.df[self.df['Type'] == 'Bug'].shape[0]
        
        # Overall spillover
        spillover_items = self.df[self.df['State'] == 'Spillover']
        spillover_count = len(spillover_items)
        total_items = len(self.df)
        overall_spillover_pct = (spillover_count / total_items * 100) if total_items > 0 else 0
        
        # Overall avg cycle time
        all_completed = self.df[(self.df['Status'] == 'Done') & 
                                (self.df['Cycle_Time_Days'].notna())]
        overall_avg_cycle_time = all_completed['Cycle_Time_Days'].mean() if len(all_completed) > 0 else 0
        
        return _convert_to_python_types({
            'sprint_velocity': {
                'value': round(avg_velocity, 1),
                'indicator': 'green' if avg_velocity >= 15 else 'red',
                'label': 'Sprint Velocity (Avg Points)'
            },
            'delivery_percentage': {
                'value': round(overall_delivery, 1),
                'indicator': 'green' if overall_delivery >= 70 else 'red',
                'label': 'Delivery %'
            },
            'bug_count': {
                'value': total_bugs,
                'indicator': 'red' if total_bugs > 5 else 'green',
                'label': 'Total Bugs'
            },
            'spillover_percentage': {
                'value': round(overall_spillover_pct, 1),
                'indicator': 'red' if overall_spillover_pct > 15 else 'green',
                'label': 'Spillover %'
            },
            'avg_cycle_time': {
                'value': round(overall_avg_cycle_time, 1),
                'indicator': 'green' if overall_avg_cycle_time <= 3 else 'red',
                'label': 'Avg Cycle Time (Days)'
            },
            'sprint_details': sprint_metrics
        })
    
    def get_state_distribution(self) -> Dict[str, Any]:
        """
        Get state distribution data for Sheet 2.
        Returns: Bar chart data with percentage labels.
        """
        state_counts = self.df['State'].value_counts()
        total = state_counts.sum()
        
        states = state_counts.index.tolist()
        counts = state_counts.values.tolist()
        percentages = [(count / total * 100) for count in counts]
        
        return _convert_to_python_types({
            'states': states,
            'counts': counts,
            'percentages': [round(p, 1) for p in percentages],
            'total': total
        })
    
    def get_velocity_chart(self) -> Dict[str, Any]:
        """
        Get velocity chart data for Sheet 3.
        Returns: Line chart data with planned vs completed story points.
        """
        sprints = sorted(self.df['Sprint_ID'].unique())
        
        planned = []
        completed = []
        
        for sprint in sprints:
            sprint_data = self.df[self.df['Sprint_ID'] == sprint]
            planned_points = sprint_data['Story_Points'].sum()
            completed_points = sprint_data[sprint_data['Status'] == 'Done']['Story_Points'].sum()
            
            planned.append(planned_points)
            completed.append(completed_points)
        
        return _convert_to_python_types({
            'sprints': sprints,
            'planned': planned,
            'completed': completed
        })
    
    def get_cycle_time_analysis(self) -> Dict[str, Any]:
        """
        Get cycle time analysis for Sheet 4.
        Returns: Data for box plot and scatter plot (Story Points vs Cycle Time).
        """
        # Filter completed items with cycle time data
        completed = self.df[(self.df['Status'] == 'Done') & 
                           (self.df['Cycle_Time_Days'].notna()) &
                           (self.df['Story_Points'].notna())]
        
        if len(completed) == 0:
            return {
                'box_plot': {'states': [], 'cycle_times': []},
                'scatter': {'story_points': [], 'cycle_times': [], 'titles': []}
            }
        
        # Box plot data by state
        box_data = []
        states = completed['State'].unique()
        for state in states:
            state_data = completed[completed['State'] == state]
            box_data.append({
                'state': state,
                'cycle_times': state_data['Cycle_Time_Days'].tolist()
            })
        
        # Scatter plot data
        scatter = {
            'story_points': completed['Story_Points'].tolist(),
            'cycle_times': completed['Cycle_Time_Days'].tolist(),
            'titles': completed['Title'].tolist(),
            'ticket_ids': completed['Ticket_ID'].tolist()
        }
        
        # Calculate correlation
        if len(completed) > 1:
            correlation = completed['Story_Points'].corr(completed['Cycle_Time_Days'])
        else:
            correlation = 0
        
        return _convert_to_python_types({
            'box_plot': box_data,
            'scatter': scatter,
            'correlation': round(correlation, 3)
        })
    
    def get_bugs_breakdown(self) -> Dict[str, Any]:
        """
        Get bugs breakdown for Sheet 5.
        Returns: Severity pie chart and bugs per area bar chart.
        """
        bugs = self.df[self.df['Type'] == 'Bug'].copy()
        
        if len(bugs) == 0:
            return {
                'severity': {'labels': [], 'values': []},
                'by_area': {'areas': [], 'counts': []}
            }
        
        # Severity breakdown
        severity_counts = bugs['Severity'].value_counts()
        severity_data = {
            'labels': severity_counts.index.tolist(),
            'values': severity_counts.values.tolist()
        }
        
        # Bugs by area
        area_counts = bugs['Area_Module'].value_counts()
        area_data = {
            'areas': area_counts.index.tolist(),
            'counts': area_counts.values.tolist()
        }
        
        return _convert_to_python_types({
            'severity': severity_data,
            'by_area': area_data,
            'total_bugs': len(bugs)
        })
    
    def get_workload_distribution(self) -> Dict[str, Any]:
        """
        Get workload distribution for Sheet 6.
        Returns: Stacked bar (hours per assignee), pie (% distribution), 
                 heatmap (assignee x area matrix).
        """
        # Calculate total hours per assignee
        self.df['Total_Hours'] = (self.df['Dev_Time_Hours'].fillna(0) + 
                                  self.df['QA_Time_Hours'].fillna(0))
        
        # Hours per assignee with breakdown
        assignee_work = self.df.groupby('Assignee').agg({
            'Dev_Time_Hours': 'sum',
            'QA_Time_Hours': 'sum',
            'Total_Hours': 'sum'
        }).reset_index()
        
        assignee_work = assignee_work.sort_values('Total_Hours', ascending=False)
        
        # Workload percentage
        total_hours = assignee_work['Total_Hours'].sum()
        workload_pct = []
        for _, row in assignee_work.iterrows():
            pct = (row['Total_Hours'] / total_hours * 100) if total_hours > 0 else 0
            workload_pct.append({
                'assignee': row['Assignee'],
                'percentage': round(pct, 1)
            })
        
        # Heatmap: assignee x area
        heatmap_data = self.df.groupby(['Assignee', 'Area_Module']).size().reset_index(name='count')
        
        # Pivot for heatmap
        heatmap_pivot = heatmap_data.pivot(index='Assignee', 
                                           columns='Area_Module', 
                                           values='count').fillna(0)
        
        return _convert_to_python_types({
            'stacked_bar': {
                'assignees': assignee_work['Assignee'].tolist(),
                'dev_hours': assignee_work['Dev_Time_Hours'].tolist(),
                'qa_hours': assignee_work['QA_Time_Hours'].tolist()
            },
            'pie_data': workload_pct,
            'heatmap': {
                'assignees': heatmap_pivot.index.tolist(),
                'areas': heatmap_pivot.columns.tolist(),
                'values': heatmap_pivot.values.tolist()
            }
        })
    
    def get_spillover_overview(self) -> Dict[str, Any]:
        """
        Get spillover overview for Sheet 7.
        Returns: Table and chart data for spilled items.
        """
        spillover = self.df[self.df['State'] == 'Spillover'].copy()
        
        if len(spillover) == 0:
            return {
                'table': [],
                'chart': {'areas': [], 'story_points': []},
                'total_spilled': 0,
                'total_points_spilled': 0
            }
        
        # Table data
        table_data = []
        for _, row in spillover.iterrows():
            table_data.append({
                'ticket_id': row['Ticket_ID'],
                'title': row['Title'],
                'area': row['Area_Module'],
                'story_points': row['Story_Points'],
                'assignee': row['Assignee'],
                'carried_over_from': row.get('Carried_Over_From', '')
            })
        
        # Chart: story points by area
        area_points = spillover.groupby('Area_Module')['Story_Points'].sum().sort_values(ascending=False)
        
        return _convert_to_python_types({
            'table': table_data,
            'chart': {
                'areas': area_points.index.tolist(),
                'story_points': area_points.values.tolist()
            },
            'total_spilled': len(spillover),
            'total_points_spilled': spillover['Story_Points'].sum()
        })
    
    def get_raw_data(self) -> Dict[str, Any]:
        """
        Get structured raw data for Sheet 8.
        Returns: Formatted tables for transparency.
        """
        # Summary by sprint
        sprint_summary = []
        for sprint in sorted(self.df['Sprint_ID'].unique()):
            sprint_data = self.df[self.df['Sprint_ID'] == sprint]
            sprint_summary.append({
                'sprint_id': sprint,
                'total_items': len(sprint_data),
                'stories': len(sprint_data[sprint_data['Type'] == 'Story']),
                'bugs': len(sprint_data[sprint_data['Type'] == 'Bug']),
                'tasks': len(sprint_data[sprint_data['Type'] == 'Task']),
                'completed': len(sprint_data[sprint_data['Status'] == 'Done']),
                'in_progress': len(sprint_data[sprint_data['Status'] == 'In Progress']),
                'todo': len(sprint_data[sprint_data['Status'] == 'To Do']),
                'total_points': sprint_data['Story_Points'].sum(),
                'completed_points': sprint_data[sprint_data['Status'] == 'Done']['Story_Points'].sum()
            })
        
        # Summary by type
        type_summary = []
        for item_type in self.df['Type'].unique():
            type_data = self.df[self.df['Type'] == item_type]
            type_summary.append({
                'type': item_type,
                'count': len(type_data),
                'completed': len(type_data[type_data['Status'] == 'Done']),
                'in_progress': len(type_data[type_data['Status'] == 'In Progress']),
                'todo': len(type_data[type_data['Status'] == 'To Do']),
                'total_points': type_data['Story_Points'].sum()
            })
        
        # Team summary
        team_summary = []
        for assignee in self.df['Assignee'].unique():
            assignee_data = self.df[self.df['Assignee'] == assignee]
            team_summary.append({
                'assignee': assignee,
                'role': assignee_data['Assignee_Role'].iloc[0],
                'total_items': len(assignee_data),
                'completed': len(assignee_data[assignee_data['Status'] == 'Done']),
                'total_points': assignee_data['Story_Points'].sum(),
                'completed_points': assignee_data[assignee_data['Status'] == 'Done']['Story_Points'].sum(),
                'total_hours': (assignee_data['Dev_Time_Hours'].fillna(0) + 
                               assignee_data['QA_Time_Hours'].fillna(0)).sum()
            })
        
        return _convert_to_python_types({
            'sprint_summary': sprint_summary,
            'type_summary': type_summary,
            'team_summary': team_summary
        })
