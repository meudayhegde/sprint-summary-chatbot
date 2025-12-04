"""
Advanced DataFrame Query Executor for Sprint Data Analysis
Provides complex data analysis capabilities using pandas operations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class DataFrameQueryExecutor:
    """
    Executes complex data analysis queries on pandas DataFrame.
    Provides methods for aggregations, calculations, filtering, and metric computation.
    """
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with a DataFrame."""
        self.df = df.copy()
        self._ensure_data_types()
    
    def _ensure_data_types(self):
        """Ensure proper data types for analysis."""
        date_columns = ['Created_Date', 'Started_Date', 'Completed_Date', 'Sprint_Start', 'Sprint_End']
        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
        
        if 'Story_Points' in self.df.columns:
            self.df['Story_Points'] = pd.to_numeric(self.df['Story_Points'], errors='coerce')
        
        numeric_cols = ['Cycle_Time_Days', 'Dev_Time_Hours', 'QA_Time_Hours', 'Estimated_Hours', 'Team_Capacity_Hours']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
    
    def execute_query(self, query_type: str, **kwargs) -> Union[Dict, List, pd.DataFrame, float, int]:
        """
        Execute a query based on type.
        
        Args:
            query_type: Type of query to execute
            **kwargs: Query parameters
            
        Returns:
            Query results in appropriate format
        """
        query_methods = {
            'filter': self._filter_data,
            'aggregate': self._aggregate_data,
            'group_by': self._group_by_analysis,
            'calculate_metric': self._calculate_metric,
            'compare_sprints': self._compare_sprints,
            'trend_analysis': self._trend_analysis,
            'team_comparison': self._team_comparison,
            'time_series': self._time_series_analysis,
            'pivot': self._pivot_analysis,
            'statistical_summary': self._statistical_summary
        }
        
        method = query_methods.get(query_type)
        if not method:
            raise ValueError(f"Unknown query type: {query_type}")
        
        return method(**kwargs)
    
    def _filter_data(self, conditions: Dict[str, Any]) -> pd.DataFrame:
        """
        Filter DataFrame based on conditions.
        
        Args:
            conditions: Dict of column: value(s) pairs
            
        Returns:
            Filtered DataFrame
        """
        result_df = self.df.copy()
        
        for column, value in conditions.items():
            if column not in result_df.columns:
                continue
            
            if isinstance(value, list):
                result_df = result_df[result_df[column].isin(value)]
            elif isinstance(value, dict):
                # Handle operators like >, <, >=, <=
                op = value.get('operator', '==')
                val = value.get('value')
                
                if op == '>':
                    result_df = result_df[result_df[column] > val]
                elif op == '<':
                    result_df = result_df[result_df[column] < val]
                elif op == '>=':
                    result_df = result_df[result_df[column] >= val]
                elif op == '<=':
                    result_df = result_df[result_df[column] <= val]
                elif op == '!=':
                    result_df = result_df[result_df[column] != val]
                else:
                    result_df = result_df[result_df[column] == val]
            else:
                result_df = result_df[result_df[column] == value]
        
        return result_df
    
    def _aggregate_data(self, 
                       group_by: Optional[List[str]] = None,
                       aggregations: Dict[str, Union[str, List[str]]] = None) -> pd.DataFrame:
        """
        Perform aggregation operations.
        
        Args:
            group_by: Columns to group by
            aggregations: Dict of column: aggregation_function(s)
            
        Returns:
            Aggregated DataFrame
        """
        if group_by:
            grouped = self.df.groupby(group_by)
            
            if aggregations:
                result = grouped.agg(aggregations)
            else:
                result = grouped.size().reset_index(name='count')
            
            return result.reset_index() if not isinstance(result, pd.DataFrame) else result
        else:
            # No grouping, just aggregate entire DataFrame
            if aggregations:
                result = {}
                for col, funcs in aggregations.items():
                    if col not in self.df.columns:
                        continue
                    
                    if isinstance(funcs, str):
                        funcs = [funcs]
                    
                    for func in funcs:
                        key = f"{col}_{func}"
                        if func == 'count':
                            result[key] = self.df[col].count()
                        elif func == 'sum':
                            result[key] = self.df[col].sum()
                        elif func == 'mean':
                            result[key] = self.df[col].mean()
                        elif func == 'median':
                            result[key] = self.df[col].median()
                        elif func == 'min':
                            result[key] = self.df[col].min()
                        elif func == 'max':
                            result[key] = self.df[col].max()
                        elif func == 'std':
                            result[key] = self.df[col].std()
                
                return pd.DataFrame([result])
            
            return pd.DataFrame([{'count': len(self.df)}])
    
    def _group_by_analysis(self, 
                          group_columns: List[str],
                          value_column: str,
                          aggregation: str = 'sum') -> pd.DataFrame:
        """
        Group by analysis with single aggregation.
        
        Args:
            group_columns: Columns to group by
            value_column: Column to aggregate
            aggregation: Aggregation function (sum, mean, count, etc.)
            
        Returns:
            Grouped DataFrame
        """
        if value_column not in self.df.columns:
            return pd.DataFrame()
        
        grouped = self.df.groupby(group_columns)[value_column]
        
        agg_map = {
            'sum': grouped.sum,
            'mean': grouped.mean,
            'median': grouped.median,
            'count': grouped.count,
            'min': grouped.min,
            'max': grouped.max,
            'std': grouped.std
        }
        
        agg_func = agg_map.get(aggregation, grouped.sum)
        result = agg_func().reset_index()
        
        return result
    
    def _calculate_metric(self, metric_name: str, **params) -> Union[float, Dict[str, Any]]:
        """
        Calculate specific metrics.
        
        Args:
            metric_name: Name of metric to calculate
            **params: Metric-specific parameters
            
        Returns:
            Calculated metric value or dict of values
        """
        metric_calculators = {
            'completion_rate': self._calc_completion_rate,
            'velocity': self._calc_velocity,
            'capacity_utilization': self._calc_capacity_utilization,
            'cycle_time_avg': self._calc_avg_cycle_time,
            'bug_resolution_rate': self._calc_bug_resolution_rate,
            'team_productivity': self._calc_team_productivity,
            'sprint_health': self._calc_sprint_health,
            'work_distribution': self._calc_work_distribution,
            'quality_metrics': self._calc_quality_metrics,
            'burndown_data': self._calc_burndown_data
        }
        
        calculator = metric_calculators.get(metric_name)
        if not calculator:
            raise ValueError(f"Unknown metric: {metric_name}")
        
        return calculator(**params)
    
    def _calc_completion_rate(self, sprint_id: Optional[str] = None, by: str = 'tickets') -> float:
        """Calculate completion rate."""
        df = self._filter_data({'Sprint_ID': sprint_id}) if sprint_id else self.df
        
        if by == 'tickets':
            total = len(df)
            completed = len(df[df['Status'] == 'Done'])
        else:  # by story points
            total = df['Story_Points'].sum()
            completed = df[df['Status'] == 'Done']['Story_Points'].sum()
        
        return round((completed / total * 100) if total > 0 else 0, 2)
    
    def _calc_velocity(self, sprint_id: Optional[str] = None) -> float:
        """Calculate velocity (completed story points)."""
        df = self._filter_data({'Sprint_ID': sprint_id}) if sprint_id else self.df
        completed_points = df[df['Status'] == 'Done']['Story_Points'].sum()
        return round(float(completed_points), 2)
    
    def _calc_capacity_utilization(self, sprint_id: str) -> Optional[float]:
        """Calculate capacity utilization for a sprint."""
        df = self._filter_data({'Sprint_ID': sprint_id})
        
        if 'Team_Capacity_Hours' not in df.columns or df.empty:
            return None
        
        capacity = df['Team_Capacity_Hours'].iloc[0]
        if pd.isna(capacity) or capacity == 0:
            return None
        
        actual_hours = df['Dev_Time_Hours'].sum() + df.get('QA_Time_Hours', pd.Series([0])).sum()
        
        return round((actual_hours / capacity * 100), 2)
    
    def _calc_avg_cycle_time(self, status: Optional[str] = 'Done', ticket_type: Optional[str] = None) -> float:
        """Calculate average cycle time."""
        df = self.df[self.df['Status'] == status] if status else self.df
        
        if ticket_type:
            df = df[df['Type'] == ticket_type]
        
        if 'Cycle_Time_Days' not in df.columns or df.empty:
            return 0.0
        
        avg_time = df['Cycle_Time_Days'].mean()
        return round(float(avg_time), 2) if not pd.isna(avg_time) else 0.0
    
    def _calc_bug_resolution_rate(self) -> float:
        """Calculate bug resolution rate."""
        bugs = self.df[self.df['Type'] == 'Bug']
        if len(bugs) == 0:
            return 0.0
        
        resolved = len(bugs[bugs['Status'] == 'Done'])
        return round((resolved / len(bugs) * 100), 2)
    
    def _calc_team_productivity(self, sprint_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate team productivity metrics."""
        df = self._filter_data({'Sprint_ID': sprint_id}) if sprint_id else self.df
        
        team_metrics = []
        for assignee in df['Assignee'].unique():
            assignee_df = df[df['Assignee'] == assignee]
            
            completed_points = assignee_df[assignee_df['Status'] == 'Done']['Story_Points'].sum()
            total_tickets = len(assignee_df)
            completed_tickets = len(assignee_df[assignee_df['Status'] == 'Done'])
            
            team_metrics.append({
                'assignee': assignee,
                'completed_points': float(completed_points),
                'total_tickets': int(total_tickets),
                'completed_tickets': int(completed_tickets),
                'completion_rate': round((completed_tickets / total_tickets * 100), 2) if total_tickets > 0 else 0
            })
        
        return {
            'team_members': team_metrics,
            'total_team_points': float(sum(m['completed_points'] for m in team_metrics)),
            'avg_points_per_person': round(sum(m['completed_points'] for m in team_metrics) / len(team_metrics), 2) if team_metrics else 0
        }
    
    def _calc_sprint_health(self, sprint_id: str) -> Dict[str, Any]:
        """Calculate comprehensive sprint health metrics."""
        df = self._filter_data({'Sprint_ID': sprint_id})
        
        total_points = df['Story_Points'].sum()
        completed_points = df[df['Status'] == 'Done']['Story_Points'].sum()
        in_progress_points = df[df['Status'] == 'In Progress']['Story_Points'].sum()
        todo_points = df[df['Status'] == 'To Do']['Story_Points'].sum()
        
        total_tickets = len(df)
        completed_tickets = len(df[df['Status'] == 'Done'])
        
        bugs_count = len(df[df['Type'] == 'Bug'])
        critical_bugs = len(df[(df['Type'] == 'Bug') & (df['Priority'] == 'Critical')])
        high_priority_incomplete = len(df[(df['Priority'] == 'High') & (df['Status'] != 'Done')])
        
        return {
            'sprint_id': sprint_id,
            'completion_rate_points': round((completed_points / total_points * 100), 2) if total_points > 0 else 0,
            'completion_rate_tickets': round((completed_tickets / total_tickets * 100), 2) if total_tickets > 0 else 0,
            'velocity': float(completed_points),
            'work_in_progress_points': float(in_progress_points),
            'todo_points': float(todo_points),
            'bugs_count': int(bugs_count),
            'critical_bugs': int(critical_bugs),
            'high_priority_incomplete': int(high_priority_incomplete),
            'health_score': self._calculate_health_score(df)
        }
    
    def _calculate_health_score(self, df: pd.DataFrame) -> float:
        """Calculate a health score (0-100) based on various factors."""
        score = 100.0
        
        # Deduct for low completion rate
        total = df['Story_Points'].sum()
        completed = df[df['Status'] == 'Done']['Story_Points'].sum()
        completion_rate = (completed / total * 100) if total > 0 else 0
        score -= max(0, (70 - completion_rate) * 0.5)  # Deduct if below 70%
        
        # Deduct for critical bugs
        critical_bugs = len(df[(df['Type'] == 'Bug') & (df['Priority'] == 'Critical')])
        score -= critical_bugs * 10
        
        # Deduct for high priority incomplete items
        high_priority_incomplete = len(df[(df['Priority'] == 'High') & (df['Status'] != 'Done')])
        score -= high_priority_incomplete * 5
        
        # Deduct for many items in To Do status (not started)
        todo_count = len(df[df['Status'] == 'To Do'])
        total_count = len(df)
        todo_ratio = (todo_count / total_count * 100) if total_count > 0 else 0
        if todo_ratio > 30:
            score -= (todo_ratio - 30) * 0.5
        
        return max(0, min(100, round(score, 2)))
    
    def _calc_work_distribution(self, sprint_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate work distribution across team."""
        df = self._filter_data({'Sprint_ID': sprint_id}) if sprint_id else self.df
        
        by_assignee = df.groupby('Assignee')['Story_Points'].sum().to_dict()
        
        total_points = sum(by_assignee.values())
        distribution = {
            assignee: {
                'story_points': float(points),
                'percentage': round((points / total_points * 100), 2) if total_points > 0 else 0
            }
            for assignee, points in by_assignee.items()
        }
        
        # Calculate standard deviation to check balance
        points_list = [points for points in by_assignee.values()]
        std_dev = np.std(points_list) if len(points_list) > 1 else 0
        mean_points = np.mean(points_list) if len(points_list) > 0 else 0
        
        return {
            'distribution': distribution,
            'balance_score': round(100 - min(100, (std_dev / mean_points * 100 if mean_points > 0 else 0)), 2),
            'std_deviation': round(float(std_dev), 2),
            'mean_points_per_person': round(float(mean_points), 2)
        }
    
    def _calc_quality_metrics(self, sprint_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate quality-related metrics."""
        df = self._filter_data({'Sprint_ID': sprint_id}) if sprint_id else self.df
        
        bugs = df[df['Type'] == 'Bug']
        stories = df[df['Type'] == 'Story']
        
        total_bugs = len(bugs)
        total_stories = len(stories)
        
        bug_ratio = (total_bugs / total_stories * 100) if total_stories > 0 else 0
        
        resolved_bugs = len(bugs[bugs['Status'] == 'Done'])
        bug_resolution_rate = (resolved_bugs / total_bugs * 100) if total_bugs > 0 else 0
        
        # Severity distribution
        severity_dist = {}
        if 'Severity' in bugs.columns:
            severity_dist = bugs['Severity'].value_counts().to_dict()
        
        # Average bug fix time
        closed_bugs = bugs[bugs['Status'] == 'Done']
        avg_bug_fix_time = closed_bugs['Cycle_Time_Days'].mean() if 'Cycle_Time_Days' in closed_bugs.columns and not closed_bugs.empty else 0
        
        return {
            'total_bugs': int(total_bugs),
            'bug_to_story_ratio': round(bug_ratio, 2),
            'bug_resolution_rate': round(bug_resolution_rate, 2),
            'severity_distribution': {k: int(v) for k, v in severity_dist.items()},
            'avg_bug_fix_time_days': round(float(avg_bug_fix_time), 2) if not pd.isna(avg_bug_fix_time) else 0
        }
    
    def _calc_burndown_data(self, sprint_id: str) -> List[Dict[str, Any]]:
        """Calculate burndown chart data."""
        df = self._filter_data({'Sprint_ID': sprint_id})
        
        if 'Completed_Date' not in df.columns or df.empty:
            return []
        
        # Get sprint date range
        sprint_start = df['Sprint_Start'].iloc[0]
        sprint_end = df['Sprint_End'].iloc[0]
        
        if pd.isna(sprint_start) or pd.isna(sprint_end):
            return []
        
        total_points = df['Story_Points'].sum()
        
        # Create daily burndown
        completed_df = df[df['Status'] == 'Done'].copy()
        completed_df = completed_df.sort_values('Completed_Date')
        
        burndown = []
        remaining = total_points
        
        for _, row in completed_df.iterrows():
            if not pd.isna(row['Completed_Date']):
                remaining -= row['Story_Points']
                burndown.append({
                    'date': row['Completed_Date'].strftime('%Y-%m-%d'),
                    'remaining_points': float(remaining),
                    'completed_points': float(total_points - remaining)
                })
        
        return burndown
    
    def _compare_sprints(self, sprint_ids: List[str], metrics: List[str]) -> pd.DataFrame:
        """Compare multiple sprints across specified metrics."""
        comparison_data = []
        
        for sprint_id in sprint_ids:
            sprint_df = self._filter_data({'Sprint_ID': sprint_id})
            
            if sprint_df.empty:
                continue
            
            sprint_metrics = {'Sprint_ID': sprint_id}
            
            for metric in metrics:
                if metric == 'velocity':
                    sprint_metrics['Velocity'] = float(sprint_df[sprint_df['Status'] == 'Done']['Story_Points'].sum())
                elif metric == 'completion_rate':
                    total = sprint_df['Story_Points'].sum()
                    completed = sprint_df[sprint_df['Status'] == 'Done']['Story_Points'].sum()
                    sprint_metrics['Completion_Rate'] = round((completed / total * 100), 2) if total > 0 else 0
                elif metric == 'bug_count':
                    sprint_metrics['Bugs'] = int(len(sprint_df[sprint_df['Type'] == 'Bug']))
                elif metric == 'team_size':
                    sprint_metrics['Team_Size'] = int(sprint_df['Assignee'].nunique())
                elif metric == 'avg_cycle_time':
                    done_df = sprint_df[sprint_df['Status'] == 'Done']
                    if 'Cycle_Time_Days' in done_df.columns and not done_df.empty:
                        sprint_metrics['Avg_Cycle_Time'] = round(float(done_df['Cycle_Time_Days'].mean()), 2)
                    else:
                        sprint_metrics['Avg_Cycle_Time'] = 0
            
            comparison_data.append(sprint_metrics)
        
        return pd.DataFrame(comparison_data)
    
    def _trend_analysis(self, metric: str, group_by: str = 'Sprint_ID') -> pd.DataFrame:
        """Analyze trends over time or across groups."""
        if group_by not in self.df.columns:
            return pd.DataFrame()
        
        grouped = self.df.groupby(group_by)
        
        trend_data = []
        for name, group in grouped:
            data_point = {group_by: name}
            
            if metric == 'velocity':
                data_point['value'] = float(group[group['Status'] == 'Done']['Story_Points'].sum())
            elif metric == 'completion_rate':
                total = group['Story_Points'].sum()
                completed = group[group['Status'] == 'Done']['Story_Points'].sum()
                data_point['value'] = round((completed / total * 100), 2) if total > 0 else 0
            elif metric == 'bug_count':
                data_point['value'] = int(len(group[group['Type'] == 'Bug']))
            elif metric == 'avg_cycle_time':
                done = group[group['Status'] == 'Done']
                if 'Cycle_Time_Days' in done.columns and not done.empty:
                    data_point['value'] = round(float(done['Cycle_Time_Days'].mean()), 2)
                else:
                    data_point['value'] = 0
            
            trend_data.append(data_point)
        
        return pd.DataFrame(trend_data)
    
    def _team_comparison(self, metric: str) -> pd.DataFrame:
        """Compare team members across a specific metric."""
        grouped = self.df.groupby('Assignee')
        
        comparison_data = []
        for assignee, group in grouped:
            member_data = {'Assignee': assignee}
            
            if metric == 'velocity':
                member_data['value'] = float(group[group['Status'] == 'Done']['Story_Points'].sum())
            elif metric == 'completion_rate':
                total = len(group)
                completed = len(group[group['Status'] == 'Done'])
                member_data['value'] = round((completed / total * 100), 2) if total > 0 else 0
            elif metric == 'avg_cycle_time':
                done = group[group['Status'] == 'Done']
                if 'Cycle_Time_Days' in done.columns and not done.empty:
                    member_data['value'] = round(float(done['Cycle_Time_Days'].mean()), 2)
                else:
                    member_data['value'] = 0
            elif metric == 'ticket_count':
                member_data['value'] = int(len(group))
            
            comparison_data.append(member_data)
        
        return pd.DataFrame(comparison_data).sort_values('value', ascending=False)
    
    def _time_series_analysis(self, date_column: str, value_column: str, aggregation: str = 'sum') -> pd.DataFrame:
        """Perform time series analysis."""
        if date_column not in self.df.columns or value_column not in self.df.columns:
            return pd.DataFrame()
        
        df = self.df.copy()
        df = df.dropna(subset=[date_column])
        
        df['date_only'] = df[date_column].dt.date
        
        grouped = df.groupby('date_only')[value_column]
        
        if aggregation == 'sum':
            result = grouped.sum()
        elif aggregation == 'mean':
            result = grouped.mean()
        elif aggregation == 'count':
            result = grouped.count()
        else:
            result = grouped.sum()
        
        return result.reset_index()
    
    def _pivot_analysis(self, index: str, columns: str, values: str, aggfunc: str = 'sum') -> pd.DataFrame:
        """Create pivot table analysis."""
        try:
            pivot = pd.pivot_table(
                self.df,
                index=index,
                columns=columns,
                values=values,
                aggfunc=aggfunc,
                fill_value=0
            )
            return pivot.reset_index()
        except Exception as e:
            logger.error(f"Pivot error: {e}")
            return pd.DataFrame()
    
    def _statistical_summary(self, columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get statistical summary of numeric columns."""
        if columns:
            df = self.df[columns]
        else:
            df = self.df.select_dtypes(include=[np.number])
        
        summary = {}
        for col in df.columns:
            summary[col] = {
                'count': int(df[col].count()),
                'mean': round(float(df[col].mean()), 2) if not pd.isna(df[col].mean()) else 0,
                'median': round(float(df[col].median()), 2) if not pd.isna(df[col].median()) else 0,
                'std': round(float(df[col].std()), 2) if not pd.isna(df[col].std()) else 0,
                'min': round(float(df[col].min()), 2) if not pd.isna(df[col].min()) else 0,
                'max': round(float(df[col].max()), 2) if not pd.isna(df[col].max()) else 0,
                'q25': round(float(df[col].quantile(0.25)), 2) if not pd.isna(df[col].quantile(0.25)) else 0,
                'q75': round(float(df[col].quantile(0.75)), 2) if not pd.isna(df[col].quantile(0.75)) else 0
            }
        
        return summary
    
    def get_dataframe(self) -> pd.DataFrame:
        """Return the DataFrame for direct access."""
        return self.df
