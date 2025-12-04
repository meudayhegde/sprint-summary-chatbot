"""
Visualization utilities for creating charts and graphs.
Uses Plotly for interactive visualizations.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Any, Optional
import json


class ChartGenerator:
    """Generate various charts and visualizations for sprint data."""
    
    @staticmethod
    def create_status_pie_chart(df: pd.DataFrame) -> str:
        """Create a pie chart showing status distribution."""
        if df.empty or 'Status' not in df.columns:
            return ""
        
        status_counts = df['Status'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=status_counts.index,
            values=status_counts.values,
            hole=0.3,
            marker=dict(colors=['#10b981', '#f59e0b', '#3b82f6', '#8b5cf6', '#ef4444'])
        )])
        
        fig.update_layout(
            title="Ticket Status Distribution",
            height=400,
            showlegend=True,
            template="plotly_white"
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_sprint_velocity_chart(df: pd.DataFrame) -> str:
        """Create a bar chart showing story points by sprint."""
        if df.empty or 'Sprint_ID' not in df.columns or 'Story_Points' not in df.columns:
            return ""
        
        sprint_data = df.groupby(['Sprint_ID', 'Status'])['Story_Points'].sum().reset_index()
        
        fig = px.bar(
            sprint_data,
            x='Sprint_ID',
            y='Story_Points',
            color='Status',
            title='Sprint Velocity - Story Points by Status',
            labels={'Story_Points': 'Story Points', 'Sprint_ID': 'Sprint'},
            color_discrete_map={
                'Done': '#10b981',
                'In Progress': '#f59e0b',
                'In Testing': '#3b82f6',
                'To Do': '#6b7280'
            }
        )
        
        fig.update_layout(
            height=450,
            template="plotly_white",
            xaxis_title="Sprint",
            yaxis_title="Story Points",
            legend_title="Status"
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_team_performance_chart(df: pd.DataFrame) -> str:
        """Create a bar chart showing team member performance."""
        if df.empty or 'Assignee' not in df.columns or 'Story_Points' not in df.columns:
            return ""
        
        # Group by assignee and status
        team_data = df.groupby(['Assignee', 'Status'])['Story_Points'].sum().reset_index()
        
        fig = px.bar(
            team_data,
            x='Assignee',
            y='Story_Points',
            color='Status',
            title='Team Performance - Story Points by Member',
            labels={'Story_Points': 'Story Points', 'Assignee': 'Team Member'},
            color_discrete_map={
                'Done': '#10b981',
                'In Progress': '#f59e0b',
                'In Testing': '#3b82f6',
                'To Do': '#6b7280'
            }
        )
        
        fig.update_layout(
            height=450,
            template="plotly_white",
            xaxis_title="Team Member",
            yaxis_title="Story Points",
            legend_title="Status"
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_ticket_type_chart(df: pd.DataFrame) -> str:
        """Create a bar chart showing ticket type distribution."""
        if df.empty or 'Type' not in df.columns:
            return ""
        
        type_counts = df['Type'].value_counts().reset_index()
        type_counts.columns = ['Type', 'Count']
        
        fig = px.bar(
            type_counts,
            x='Type',
            y='Count',
            title='Ticket Type Distribution',
            labels={'Count': 'Number of Tickets', 'Type': 'Ticket Type'},
            color='Type',
            color_discrete_sequence=['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']
        )
        
        fig.update_layout(
            height=400,
            template="plotly_white",
            showlegend=False
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_priority_distribution_chart(df: pd.DataFrame) -> str:
        """Create a pie chart showing priority distribution."""
        if df.empty or 'Priority' not in df.columns:
            return ""
        
        priority_counts = df['Priority'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=priority_counts.index,
            values=priority_counts.values,
            marker=dict(colors=['#ef4444', '#f59e0b', '#3b82f6', '#6b7280'])
        )])
        
        fig.update_layout(
            title="Priority Distribution",
            height=400,
            showlegend=True,
            template="plotly_white"
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_timeline_chart(df: pd.DataFrame) -> str:
        """Create a timeline chart showing ticket creation over time."""
        if df.empty or 'Created_Date' not in df.columns:
            return ""
        
        # Filter out null dates
        timeline_df = df[df['Created_Date'].notna()].copy()
        if timeline_df.empty:
            return ""
        
        timeline_df['Date'] = pd.to_datetime(timeline_df['Created_Date']).dt.date
        daily_counts = timeline_df.groupby('Date').size().reset_index(name='Count')
        
        fig = px.line(
            daily_counts,
            x='Date',
            y='Count',
            title='Tickets Created Over Time',
            labels={'Count': 'Number of Tickets', 'Date': 'Date'},
            markers=True
        )
        
        fig.update_layout(
            height=400,
            template="plotly_white",
            xaxis_title="Date",
            yaxis_title="Tickets Created"
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_bug_severity_chart(df: pd.DataFrame) -> str:
        """Create a chart showing bug distribution by severity."""
        if df.empty or 'Type' not in df.columns or 'Priority' not in df.columns:
            return ""
        
        bugs = df[df['Type'] == 'Bug']
        if bugs.empty:
            return ""
        
        bug_priority = bugs.groupby(['Priority', 'Status']).size().reset_index(name='Count')
        
        fig = px.bar(
            bug_priority,
            x='Priority',
            y='Count',
            color='Status',
            title='Bug Distribution by Priority and Status',
            labels={'Count': 'Number of Bugs', 'Priority': 'Priority'},
            color_discrete_map={
                'Done': '#10b981',
                'In Progress': '#f59e0b',
                'In Testing': '#3b82f6',
                'To Do': '#ef4444'
            }
        )
        
        fig.update_layout(
            height=400,
            template="plotly_white"
        )
        
        return fig.to_json()
    
    @staticmethod
    def create_completion_rate_chart(df: pd.DataFrame) -> str:
        """Create a gauge chart showing completion rate."""
        if df.empty or 'Status' not in df.columns or 'Story_Points' not in df.columns:
            return ""
        
        total_points = df['Story_Points'].sum()
        completed_points = df[df['Status'] == 'Done']['Story_Points'].sum()
        
        if total_points == 0:
            completion_rate = 0
        else:
            completion_rate = (completed_points / total_points) * 100
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=completion_rate,
            title={'text': "Sprint Completion Rate (%)"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#10b981"},
                'steps': [
                    {'range': [0, 50], 'color': "#fee2e2"},
                    {'range': [50, 80], 'color': "#fef3c7"},
                    {'range': [80, 100], 'color': "#d1fae5"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=400,
            template="plotly_white"
        )
        
        return fig.to_json()
