"""
LangChain Tools for Sprint Data Analysis
Provides tools that enable LLMs to perform real data analysis using pandas.
"""

from langchain_core.tools import Tool, StructuredTool, tool
from typing import Dict, Any, List, Optional, Union
import json
import pandas as pd
import logging

from dataframe_query_executor import DataFrameQueryExecutor

logger = logging.getLogger(__name__)


class DataAnalysisTools:
    """
    Factory class for creating LangChain tools that perform data analysis.
    """
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with a DataFrame."""
        self.executor = DataFrameQueryExecutor(df)
        self.df = df
    
    def get_all_tools(self) -> List[Tool]:
        """Get all available analysis tools."""
        return [
            self.create_filter_tool(),
            self.create_calculate_metric_tool(),
            self.create_compare_sprints_tool(),
            self.create_team_analysis_tool(),
            self.create_trend_analysis_tool(),
            self.create_quality_metrics_tool(),
            self.create_aggregation_tool(),
            self.create_sprint_health_tool(),
            self.create_work_distribution_tool(),
            self.create_get_raw_data_tool(),
            self.create_statistical_summary_tool()
        ]
    
    def create_filter_tool(self) -> Tool:
        """Create a tool for filtering data."""
        def filter_data(query: str) -> str:
            """
            Filter sprint data based on conditions.
            
            Input should be a JSON string with conditions, e.g.:
            '{"Sprint_ID": "SPR-001"}' or
            '{"Status": "Done", "Type": "Bug"}' or
            '{"Priority": ["High", "Critical"]}'
            
            Returns filtered data as JSON.
            """
            try:
                conditions = json.loads(query)
                result_df = self.executor.execute_query('filter', conditions=conditions)
                
                # Return summary stats rather than full data
                return json.dumps({
                    'total_records': len(result_df),
                    'story_points_sum': float(result_df['Story_Points'].sum()) if 'Story_Points' in result_df.columns else 0,
                    'status_distribution': result_df['Status'].value_counts().to_dict() if 'Status' in result_df.columns else {},
                    'type_distribution': result_df['Type'].value_counts().to_dict() if 'Type' in result_df.columns else {},
                    'sample_tickets': result_df[['Ticket_ID', 'Title', 'Status', 'Story_Points']].head(5).to_dict('records') if 'Ticket_ID' in result_df.columns else []
                }, indent=2)
            except Exception as e:
                logger.error(f"Filter error: {e}")
                return json.dumps({'error': str(e)})
        
        return Tool(
            name="filter_sprint_data",
            func=filter_data,
            description=(
                "Filter sprint data based on conditions like Sprint_ID, Status, Type, Priority, Assignee, etc. "
                "Input must be a JSON string with column:value pairs. "
                "Example: '{\"Sprint_ID\": \"SPR-001\"}' or '{\"Status\": \"Done\", \"Type\": \"Story\"}'. "
                "Returns summary statistics of filtered data."
            )
        )
    
    def create_calculate_metric_tool(self) -> Tool:
        """Create a tool for calculating specific metrics."""
        def calculate_metric(query: str) -> str:
            """
            Calculate specific metrics from sprint data.
            
            Input should be JSON with 'metric_name' and optional parameters, e.g.:
            '{"metric_name": "completion_rate", "sprint_id": "SPR-001", "by": "tickets"}' or
            '{"metric_name": "velocity", "sprint_id": "SPR-002"}' or
            '{"metric_name": "bug_resolution_rate"}'
            
            Available metrics:
            - completion_rate: Calculate completion rate (params: sprint_id, by='tickets' or 'points')
            - velocity: Calculate velocity (params: sprint_id)
            - capacity_utilization: Calculate capacity usage (params: sprint_id)
            - cycle_time_avg: Calculate average cycle time (params: status, ticket_type)
            - bug_resolution_rate: Calculate bug resolution rate
            - team_productivity: Calculate team productivity metrics (params: sprint_id)
            
            Returns calculated metric value(s).
            """
            try:
                params = json.loads(query)
                metric_name = params.pop('metric_name')
                
                result = self.executor.execute_query('calculate_metric', metric_name=metric_name, **params)
                
                if isinstance(result, dict):
                    return json.dumps(result, indent=2)
                else:
                    return json.dumps({'value': result, 'metric': metric_name}, indent=2)
            except Exception as e:
                logger.error(f"Metric calculation error: {e}")
                return json.dumps({'error': str(e)})
        
        return Tool(
            name="calculate_sprint_metric",
            func=calculate_metric,
            description=(
                "Calculate specific sprint metrics like completion_rate, velocity, capacity_utilization, "
                "cycle_time_avg, bug_resolution_rate, or team_productivity. "
                "Input must be JSON with 'metric_name' and any required parameters. "
                "Example: '{\"metric_name\": \"velocity\", \"sprint_id\": \"SPR-001\"}'"
            )
        )
    
    def create_compare_sprints_tool(self) -> Tool:
        """Create a tool for comparing multiple sprints."""
        def compare_sprints(query: str) -> str:
            """
            Compare multiple sprints across metrics.
            
            Input should be JSON with 'sprint_ids' list and 'metrics' list, e.g.:
            '{"sprint_ids": ["SPR-001", "SPR-002", "SPR-003"], "metrics": ["velocity", "completion_rate", "bug_count"]}'
            
            Available metrics: velocity, completion_rate, bug_count, team_size, avg_cycle_time
            
            Returns comparison data as JSON.
            """
            try:
                params = json.loads(query)
                sprint_ids = params.get('sprint_ids', [])
                metrics = params.get('metrics', ['velocity', 'completion_rate'])
                
                result_df = self.executor.execute_query('compare_sprints', sprint_ids=sprint_ids, metrics=metrics)
                
                return json.dumps({
                    'comparison': result_df.to_dict('records'),
                    'summary': {
                        'total_sprints_compared': len(result_df),
                        'metrics_analyzed': metrics
                    }
                }, indent=2)
            except Exception as e:
                logger.error(f"Sprint comparison error: {e}")
                return json.dumps({'error': str(e)})
        
        return Tool(
            name="compare_sprints",
            func=compare_sprints,
            description=(
                "Compare multiple sprints across various metrics like velocity, completion_rate, bug_count, etc. "
                "Input must be JSON with 'sprint_ids' (list) and 'metrics' (list). "
                "Example: '{\"sprint_ids\": [\"SPR-001\", \"SPR-002\"], \"metrics\": [\"velocity\", \"completion_rate\"]}'"
            )
        )
    
    def create_team_analysis_tool(self) -> Tool:
        """Create a tool for team member analysis."""
        def team_analysis(query: str) -> str:
            """
            Analyze and compare team member performance.
            
            Input should be JSON with 'metric' to compare, e.g.:
            '{"metric": "velocity"}' or
            '{"metric": "completion_rate"}' or
            '{"metric": "avg_cycle_time"}'
            
            Available metrics: velocity, completion_rate, avg_cycle_time, ticket_count
            
            Returns team member comparison data.
            """
            try:
                params = json.loads(query)
                metric = params.get('metric', 'velocity')
                
                result_df = self.executor.execute_query('team_comparison', metric=metric)
                
                return json.dumps({
                    'team_comparison': result_df.to_dict('records'),
                    'metric': metric,
                    'team_size': len(result_df)
                }, indent=2)
            except Exception as e:
                logger.error(f"Team analysis error: {e}")
                return json.dumps({'error': str(e)})
        
        return Tool(
            name="analyze_team_performance",
            func=team_analysis,
            description=(
                "Analyze and compare team member performance across metrics like velocity, completion_rate, "
                "avg_cycle_time, or ticket_count. "
                "Input must be JSON with 'metric' key. "
                "Example: '{\"metric\": \"velocity\"}'"
            )
        )
    
    def create_trend_analysis_tool(self) -> Tool:
        """Create a tool for trend analysis."""
        def trend_analysis(query: str) -> str:
            """
            Analyze trends over time or across groups.
            
            Input should be JSON with 'metric' and optional 'group_by', e.g.:
            '{"metric": "velocity", "group_by": "Sprint_ID"}' or
            '{"metric": "bug_count", "group_by": "Sprint_ID"}'
            
            Available metrics: velocity, completion_rate, bug_count, avg_cycle_time
            Default group_by is 'Sprint_ID'
            
            Returns trend data over time/groups.
            """
            try:
                params = json.loads(query)
                metric = params.get('metric', 'velocity')
                group_by = params.get('group_by', 'Sprint_ID')
                
                result_df = self.executor.execute_query('trend_analysis', metric=metric, group_by=group_by)
                
                return json.dumps({
                    'trend_data': result_df.to_dict('records'),
                    'metric': metric,
                    'grouped_by': group_by
                }, indent=2)
            except Exception as e:
                logger.error(f"Trend analysis error: {e}")
                return json.dumps({'error': str(e)})
        
        return Tool(
            name="analyze_trends",
            func=trend_analysis,
            description=(
                "Analyze trends of metrics over time or across groups. "
                "Input must be JSON with 'metric' and optional 'group_by'. "
                "Example: '{\"metric\": \"velocity\", \"group_by\": \"Sprint_ID\"}'"
            )
        )
    
    def create_quality_metrics_tool(self) -> Tool:
        """Create a tool for quality metrics analysis."""
        def quality_metrics(query: str) -> str:
            """
            Calculate comprehensive quality metrics.
            
            Input should be JSON with optional 'sprint_id', e.g.:
            '{"sprint_id": "SPR-001"}' or '{}' for all data
            
            Returns quality metrics including bug ratios, resolution rates, severity distribution, etc.
            """
            try:
                params = json.loads(query) if query and query.strip() else {}
                sprint_id = params.get('sprint_id')
                
                result = self.executor.execute_query('calculate_metric', metric_name='quality_metrics', sprint_id=sprint_id)
                
                return json.dumps(result, indent=2)
            except Exception as e:
                logger.error(f"Quality metrics error: {e}")
                return json.dumps({'error': str(e)})
        
        return Tool(
            name="calculate_quality_metrics",
            func=quality_metrics,
            description=(
                "Calculate comprehensive quality metrics including bug counts, bug-to-story ratio, "
                "resolution rates, severity distribution, and average fix times. "
                "Input can be empty '{}' for all data or JSON with 'sprint_id' for specific sprint. "
                "Example: '{\"sprint_id\": \"SPR-001\"}'"
            )
        )
    
    def create_aggregation_tool(self) -> Tool:
        """Create a tool for data aggregation."""
        def aggregate_data(query: str) -> str:
            """
            Perform aggregation operations on data.
            
            Input should be JSON with optional 'group_by' and 'aggregations', e.g.:
            '{"group_by": ["Sprint_ID"], "aggregations": {"Story_Points": ["sum", "mean"]}}' or
            '{"group_by": ["Assignee", "Status"], "aggregations": {"Story_Points": "sum"}}'
            
            Returns aggregated data.
            """
            try:
                params = json.loads(query)
                group_by = params.get('group_by')
                aggregations = params.get('aggregations')
                
                result_df = self.executor.execute_query('aggregate', group_by=group_by, aggregations=aggregations)
                
                return json.dumps({
                    'aggregated_data': result_df.to_dict('records'),
                    'row_count': len(result_df)
                }, indent=2)
            except Exception as e:
                logger.error(f"Aggregation error: {e}")
                return json.dumps({'error': str(e)})
        
        return Tool(
            name="aggregate_data",
            func=aggregate_data,
            description=(
                "Perform aggregation operations like sum, mean, count, etc. on sprint data. "
                "Input must be JSON with optional 'group_by' (list of columns) and 'aggregations' (dict). "
                "Example: '{\"group_by\": [\"Sprint_ID\"], \"aggregations\": {\"Story_Points\": \"sum\"}}'"
            )
        )
    
    def create_sprint_health_tool(self) -> Tool:
        """Create a tool for comprehensive sprint health analysis."""
        def sprint_health(query: str) -> str:
            """
            Calculate comprehensive sprint health metrics and score.
            
            Input should be JSON with 'sprint_id', e.g.:
            '{"sprint_id": "SPR-001"}'
            
            Returns detailed health metrics including completion rates, velocity, bugs, priorities, and health score.
            """
            try:
                params = json.loads(query)
                sprint_id = params.get('sprint_id')
                
                if not sprint_id:
                    return json.dumps({'error': 'sprint_id is required'})
                
                result = self.executor.execute_query('calculate_metric', metric_name='sprint_health', sprint_id=sprint_id)
                
                return json.dumps(result, indent=2)
            except Exception as e:
                logger.error(f"Sprint health error: {e}")
                return json.dumps({'error': str(e)})
        
        return Tool(
            name="calculate_sprint_health",
            func=sprint_health,
            description=(
                "Calculate comprehensive sprint health metrics including completion rates, velocity, "
                "bug counts, priority distribution, and an overall health score (0-100). "
                "Input must be JSON with 'sprint_id'. "
                "Example: '{\"sprint_id\": \"SPR-001\"}'"
            )
        )
    
    def create_work_distribution_tool(self) -> Tool:
        """Create a tool for work distribution analysis."""
        def work_distribution(query: str) -> str:
            """
            Analyze work distribution across team members.
            
            Input should be JSON with optional 'sprint_id', e.g.:
            '{"sprint_id": "SPR-001"}' or '{}' for all data
            
            Returns work distribution metrics including balance score and standard deviation.
            """
            try:
                params = json.loads(query) if query and query.strip() else {}
                sprint_id = params.get('sprint_id')
                
                result = self.executor.execute_query('calculate_metric', metric_name='work_distribution', sprint_id=sprint_id)
                
                return json.dumps(result, indent=2)
            except Exception as e:
                logger.error(f"Work distribution error: {e}")
                return json.dumps({'error': str(e)})
        
        return Tool(
            name="analyze_work_distribution",
            func=work_distribution,
            description=(
                "Analyze how work (story points) is distributed across team members. "
                "Returns distribution percentages, balance score, and standard deviation. "
                "Input can be empty '{}' for all data or JSON with 'sprint_id' for specific sprint. "
                "Example: '{\"sprint_id\": \"SPR-001\"}'"
            )
        )
    
    def create_get_raw_data_tool(self) -> Tool:
        """Create a tool to get raw data overview."""
        def get_raw_data(query: str) -> str:
            """
            Get overview of available data.
            
            Input can be empty or JSON with optional filters.
            
            Returns information about available sprints, team members, data ranges, etc.
            """
            try:
                sprints = self.df['Sprint_ID'].unique().tolist() if 'Sprint_ID' in self.df.columns else []
                team_members = self.df['Assignee'].unique().tolist() if 'Assignee' in self.df.columns else []
                
                return json.dumps({
                    'total_tickets': len(self.df),
                    'available_sprints': sprints,
                    'sprint_count': len(sprints),
                    'team_members': team_members,
                    'team_size': len(team_members),
                    'ticket_types': self.df['Type'].value_counts().to_dict() if 'Type' in self.df.columns else {},
                    'status_distribution': self.df['Status'].value_counts().to_dict() if 'Status' in self.df.columns else {},
                    'total_story_points': float(self.df['Story_Points'].sum()) if 'Story_Points' in self.df.columns else 0,
                    'date_range': {
                        'earliest': self.df['Created_Date'].min().strftime('%Y-%m-%d') if 'Created_Date' in self.df.columns and not self.df['Created_Date'].isna().all() else None,
                        'latest': self.df['Created_Date'].max().strftime('%Y-%m-%d') if 'Created_Date' in self.df.columns and not self.df['Created_Date'].isna().all() else None
                    }
                }, indent=2)
            except Exception as e:
                logger.error(f"Get raw data error: {e}")
                return json.dumps({'error': str(e)})
        
        return Tool(
            name="get_data_overview",
            func=get_raw_data,
            description=(
                "Get an overview of available sprint data including available sprints, team members, "
                "ticket counts, types, and date ranges. Use this first to understand what data is available. "
                "Input can be empty string or '{}'."
            )
        )
    
    def create_statistical_summary_tool(self) -> Tool:
        """Create a tool for statistical summaries."""
        def statistical_summary(query: str) -> str:
            """
            Get statistical summary of numeric columns.
            
            Input should be JSON with optional 'columns' list, e.g.:
            '{"columns": ["Story_Points", "Cycle_Time_Days"]}' or '{}' for all numeric columns
            
            Returns statistical measures like mean, median, std, min, max, quartiles.
            """
            try:
                params = json.loads(query) if query and query.strip() else {}
                columns = params.get('columns')
                
                result = self.executor.execute_query('statistical_summary', columns=columns)
                
                return json.dumps(result, indent=2)
            except Exception as e:
                logger.error(f"Statistical summary error: {e}")
                return json.dumps({'error': str(e)})
        
        return Tool(
            name="get_statistical_summary",
            func=statistical_summary,
            description=(
                "Get statistical summary (mean, median, std, min, max, quartiles) of numeric columns. "
                "Input can be empty '{}' for all numeric columns or JSON with 'columns' list. "
                "Example: '{\"columns\": [\"Story_Points\", \"Cycle_Time_Days\"]}'"
            )
        )
