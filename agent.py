"""
LangChain agent for analyzing sprint data with multi-LLM support.
Supports OpenAI, Google Gemini, and Anthropic Claude models.
"""

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Optional, Dict, Any, List
import pandas as pd
import json
import logging
import re

from data_analyzer import SprintDataAnalyzer
from chart_generator import ChartGenerator
from config import settings

logger = logging.getLogger(__name__)


class SprintAnalysisAgent:
    """Simplified agent for sprint data analysis with chart generation."""
    
    def __init__(self, data_analyzer: SprintDataAnalyzer):
        self.data_analyzer = data_analyzer
        self.chart_generator = ChartGenerator()
        self.llm = self._initialize_llm()
        logger.info("Sprint Analysis Agent initialized with direct LLM approach")
    
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on configuration."""
        provider = settings.llm_provider.lower()
        
        try:
            if provider == "openai":
                if not settings.openai_api_key:
                    raise ValueError("OpenAI API key not configured")
                return ChatOpenAI(
                    model=settings.openai_model,
                    api_key=settings.openai_api_key,
                    temperature=0.1
                )
            elif provider == "gemini":
                if not settings.google_api_key:
                    raise ValueError("Google API key not configured")
                return ChatGoogleGenerativeAI(
                    model=settings.gemini_model,
                    google_api_key=settings.google_api_key,
                    temperature=0.1
                )
            elif provider == "anthropic":
                if not settings.anthropic_api_key:
                    raise ValueError("Anthropic API key not configured")
                return ChatAnthropic(
                    model=settings.anthropic_model,
                    api_key=settings.anthropic_api_key,
                    temperature=0.1
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            raise
    

    
    def _get_data_summary(self, input_str: str = "") -> str:
        """Tool function to get data summary."""
        summary = self.data_analyzer.get_data_summary()
        return json.dumps(summary, indent=2)
    
    def _get_sprint_summary(self, sprint_id: str = "") -> str:
        """Tool function to get sprint summary."""
        sprint_id = sprint_id.strip() if sprint_id else None
        summary = self.data_analyzer.get_sprint_summary(sprint_id)
        return json.dumps(summary, indent=2)
    
    def _get_team_performance(self, input_str: str = "") -> str:
        """Tool function to get team performance."""
        performance = self.data_analyzer.get_team_performance()
        return json.dumps(performance, indent=2)
    
    def _get_bug_analysis(self, input_str: str = "") -> str:
        """Tool function to get bug analysis."""
        analysis = self.data_analyzer.get_bug_analysis()
        return json.dumps(analysis, indent=2)
    
    def _query_tickets(self, query: str) -> str:
        """Tool function to query tickets."""
        try:
            result_df = self.data_analyzer.query_data(query)
            if result_df.empty:
                return "No tickets match the query."
            return result_df.to_json(orient='records', date_format='iso')
        except Exception as e:
            return f"Error executing query: {str(e)}"
    
    def _get_tickets_by_status(self, status: str) -> str:
        """Tool function to get tickets by status."""
        filters = {"Status": status.strip()}
        result_df = self.data_analyzer.get_filtered_data(filters)
        if result_df.empty:
            return f"No tickets with status '{status}'."
        return result_df[['Ticket_ID', 'Title', 'Type', 'Priority', 'Assignee', 'Story_Points']].to_json(orient='records')
    
    def _get_tickets_by_assignee(self, assignee: str) -> str:
        """Tool function to get tickets by assignee."""
        filters = {"Assignee": assignee.strip()}
        result_df = self.data_analyzer.get_filtered_data(filters)
        if result_df.empty:
            return f"No tickets assigned to '{assignee}'."
        return result_df[['Ticket_ID', 'Title', 'Type', 'Status', 'Priority', 'Story_Points']].to_json(orient='records')
    
    def _create_status_chart(self, input_str: str = "") -> str:
        """Tool function to create status chart."""
        df = self.data_analyzer.get_dataframe()
        chart_json = self.chart_generator.create_status_pie_chart(df)
        return chart_json if chart_json else "Unable to create chart"
    
    def _create_velocity_chart(self, input_str: str = "") -> str:
        """Tool function to create velocity chart."""
        df = self.data_analyzer.get_dataframe()
        chart_json = self.chart_generator.create_sprint_velocity_chart(df)
        return chart_json if chart_json else "Unable to create chart"
    
    def _create_team_chart(self, input_str: str = "") -> str:
        """Tool function to create team performance chart."""
        df = self.data_analyzer.get_dataframe()
        chart_json = self.chart_generator.create_team_performance_chart(df)
        return chart_json if chart_json else "Unable to create chart"
    
    def _create_priority_chart(self, input_str: str = "") -> str:
        """Tool function to create priority distribution chart."""
        df = self.data_analyzer.get_dataframe()
        chart_json = self.chart_generator.create_priority_distribution_chart(df)
        return chart_json if chart_json else "Unable to create chart"
    
    def _create_bug_chart(self, input_str: str = "") -> str:
        """Tool function to create bug analysis chart."""
        df = self.data_analyzer.get_dataframe()
        chart_json = self.chart_generator.create_bug_severity_chart(df)
        return chart_json if chart_json else "Unable to create chart"
    

    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a user question and return the answer with any charts.
        
        Returns:
            Dict with 'answer' (str) and 'charts' (list of chart JSONs)
        """
        try:
            return self._process_query_with_llm(question)
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": f"I encountered an error processing your question. Please try rephrasing it.",
                "charts": []
            }
    
    def _process_query_with_llm(self, question: str) -> Dict[str, Any]:
        """
        Process query using LLM with intelligent tool selection.
        """
        question_lower = question.lower()
        charts = []
        
        # First, analyze the data and determine what to show
        data_context = self._get_relevant_data(question_lower)
        
        # Check if charts are needed
        chart_needed = any(word in question_lower for word in ['chart', 'graph', 'visualize', 'visualization', 'plot', 'show me'])
        
        # Generate charts if appropriate
        if chart_needed or 'velocity' in question_lower or 'trend' in question_lower:
            charts = self._generate_appropriate_charts(question_lower)
        
        # Use LLM to generate natural language response
        system_prompt = """You are an expert sprint data analyst with deep knowledge of agile metrics and KPIs.

**Your Capabilities:**
1. Analyze sprint data and provide precise, data-driven insights
2. Calculate derived metrics when not directly available in the data
3. Compare performance across sprints, teams, and time periods
4. Identify trends, patterns, and anomalies

**Key Metrics You Can Calculate:**
- **Completion Rate**: (Completed tickets or story points / Total tickets or story points) × 100%
- **Velocity**: Story points completed per sprint
- **Capacity Utilization**: (Story points completed / Team capacity) × 100%
- **Bug Resolution Rate**: (Closed bugs / Total bugs) × 100%
- **Cycle Time**: Average time from start to completion
- **Team Productivity**: Story points per team member
- **Work Distribution**: Balance of work across team members
- **Sprint Progress**: % of work completed vs in-progress vs to-do
- **Quality Metrics**: Bug ratio, defect density

**Instructions:**
- When asked about metrics not directly provided, calculate them from available data
- Always show your calculations clearly (e.g., "Completion rate: 15 done / 20 total = 75%")
- Provide context and insights, not just numbers
- Compare current performance to averages or previous sprints when relevant
- Identify red flags (overallocation, blocked tickets, high bug counts)
- Be concise but thorough, using bullet points for clarity
- Format percentages, ratios, and trends clearly"""
        
        user_prompt = f"""Question: {question}

Available Data Context:
{data_context}

**Analysis Instructions:**
1. Examine the data carefully for both direct values and values that need calculation
2. If the question asks about a metric not directly provided (like completion rate, velocity, productivity), calculate it from the available data
3. Show your calculations clearly in the answer
4. Provide context and insights beyond just numbers
5. Compare against benchmarks or averages when relevant
6. Highlight any concerning patterns (low completion rates, many blocked tickets, etc.)

Please provide a clear, data-driven answer with calculated metrics where needed."""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            answer = response.content if hasattr(response, 'content') else str(response)
            
            # Mention charts if generated
            if charts:
                answer += "\n\nI've generated visual charts to help illustrate this data."
            
            return {
                "answer": answer,
                "charts": charts
            }
        except Exception as e:
            logger.error(f"LLM error: {e}")
            # Fallback to direct answer
            return self._direct_query(question)
    
    def _get_relevant_data(self, question_lower: str) -> str:
        """Get relevant data based on the question."""
        try:
            if 'bug' in question_lower:
                return self._get_bug_analysis("")
            elif 'team' in question_lower or 'performance' in question_lower or 'member' in question_lower:
                return self._get_team_performance("")
            elif any(spr in question_lower for spr in ['spr-', 'sprint']):
                # Try to extract sprint ID
                match = re.search(r'spr-\d+', question_lower)
                if match:
                    return self._get_sprint_summary(match.group().upper())
                return self._get_sprint_summary("")
            else:
                return self._get_data_summary("")
        except Exception as e:
            logger.error(f"Error getting data: {e}")
            return self._get_data_summary("")
    
    def _generate_appropriate_charts(self, question_lower: str) -> List[Dict]:
        """Generate appropriate charts based on question keywords."""
        charts = []
        
        try:
            if 'velocity' in question_lower:
                chart_json = self._create_velocity_chart("")
                if chart_json:
                    charts.append(json.loads(chart_json))
            
            if 'team' in question_lower or 'performance' in question_lower:
                chart_json = self._create_team_chart("")
                if chart_json:
                    charts.append(json.loads(chart_json))
            
            if 'status' in question_lower and 'chart' in question_lower:
                chart_json = self._create_status_chart("")
                if chart_json:
                    charts.append(json.loads(chart_json))
            
            if 'priority' in question_lower and 'chart' in question_lower:
                chart_json = self._create_priority_chart("")
                if chart_json:
                    charts.append(json.loads(chart_json))
            
            if 'bug' in question_lower and any(w in question_lower for w in ['chart', 'visualize', 'graph']):
                chart_json = self._create_bug_chart("")
                if chart_json:
                    charts.append(json.loads(chart_json))
            
            # Default charts for general queries
            if not charts and any(word in question_lower for word in ['overview', 'summary', 'show me']):
                chart_json = self._create_status_chart("")
                if chart_json:
                    charts.append(json.loads(chart_json))
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
        
        return charts
    
    def _direct_query(self, question: str) -> Dict[str, Any]:
        """
        Fallback method to handle queries directly without agent executor.
        Uses simple keyword matching and direct tool calls.
        """
        question_lower = question.lower()
        charts = []
        answer = ""
        
        try:
            # Check for chart requests
            if any(word in question_lower for word in ['chart', 'graph', 'visualize', 'visualization', 'plot']):
                if 'velocity' in question_lower or 'sprint' in question_lower:
                    chart_json = self._create_velocity_chart("")
                    if chart_json:
                        charts.append(json.loads(chart_json))
                        answer = "I've created a sprint velocity chart showing story points by sprint and status."
                elif 'team' in question_lower or 'performance' in question_lower:
                    chart_json = self._create_team_chart("")
                    if chart_json:
                        charts.append(json.loads(chart_json))
                        answer = "I've created a team performance chart showing story points by team member."
                elif 'status' in question_lower:
                    chart_json = self._create_status_chart("")
                    if chart_json:
                        charts.append(json.loads(chart_json))
                        answer = "I've created a status distribution chart."
                elif 'priority' in question_lower:
                    chart_json = self._create_priority_chart("")
                    if chart_json:
                        charts.append(json.loads(chart_json))
                        answer = "I've created a priority distribution chart."
                elif 'bug' in question_lower:
                    chart_json = self._create_bug_chart("")
                    if chart_json:
                        charts.append(json.loads(chart_json))
                        answer = "I've created a bug distribution chart by priority and status."
            
            # Check for data requests
            if any(word in question_lower for word in ['summary', 'overview', 'overall']):
                if 'sprint' in question_lower and any(spr in question.upper() for spr in ['SPR-', 'SPRINT']):
                    # Extract sprint ID
                    import re
                    match = re.search(r'SPR-\d+', question.upper())
                    if match:
                        summary = self._get_sprint_summary(match.group())
                        answer = f"Sprint Summary:\n{summary}"
                else:
                    summary = self._get_data_summary("")
                    answer = f"Overall Data Summary:\n{summary}"
            elif 'team' in question_lower and 'performance' in question_lower:
                performance = self._get_team_performance("")
                answer = f"Team Performance:\n{performance}"
            elif 'bug' in question_lower:
                bugs = self._get_bug_analysis("")
                answer = f"Bug Analysis:\n{bugs}"
            elif not answer:
                # Default response
                summary = self._get_data_summary("")
                answer = f"Here's a summary of the sprint data:\n{summary}"
            
            return {
                "answer": answer,
                "charts": charts
            }
        except Exception as e:
            logger.error(f"Error in direct query: {str(e)}")
            return {
                "answer": f"I can see your question but encountered an error processing it. Please try rephrasing or ask about: sprint summary, team performance, bug analysis, or request specific charts.",
                "charts": []
            }
