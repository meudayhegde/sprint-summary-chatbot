"""
LangChain agent for analyzing sprint data with multi-LLM support.
Supports OpenAI, Google Gemini, and Anthropic Claude models.
Uses real pandas DataFrame analysis with tool calling for accurate data-driven responses.
"""

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from typing import Optional, Dict, Any, List
import pandas as pd
import json
import logging
import re

from data_analyzer import SprintDataAnalyzer
from chart_generator import ChartGenerator
from data_analysis_tools import DataAnalysisTools
from dataframe_query_executor import DataFrameQueryExecutor
from config import settings

logger = logging.getLogger(__name__)


class SprintAnalysisAgent:
    """
    Advanced agent for sprint data analysis with real pandas DataFrame operations.
    Uses tools to execute actual data queries and calculations.
    """
    
    def __init__(self, data_analyzer: SprintDataAnalyzer):
        self.data_analyzer = data_analyzer
        self.chart_generator = ChartGenerator()
        self.llm = self._initialize_llm()
        
        # Initialize data analysis components
        self.query_executor = DataFrameQueryExecutor(data_analyzer.df)
        self.analysis_tools_factory = DataAnalysisTools(data_analyzer.df)
        self.tools = self.analysis_tools_factory.get_all_tools()
        
        # Create tool map for easy access
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        logger.info(f"Sprint Analysis Agent initialized with {len(self.tools)} data analysis tools")
    
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
                    temperature=0.0  # Use 0 for deterministic analysis
                )
            elif provider == "gemini":
                if not settings.google_api_key:
                    raise ValueError("Google API key not configured")
                return ChatGoogleGenerativeAI(
                    model=settings.gemini_model,
                    google_api_key=settings.google_api_key,
                    temperature=0.0
                )
            elif provider == "anthropic":
                if not settings.anthropic_api_key:
                    raise ValueError("Anthropic API key not configured")
                return ChatAnthropic(
                    model=settings.anthropic_model,
                    api_key=settings.anthropic_api_key,
                    temperature=0.0
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            raise
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Process a user question using tool-based data analysis.
        
        Args:
            question: User's question about sprint data
            
        Returns:
            Dict with 'answer' (str) and 'charts' (list of chart JSONs)
        """
        try:
            logger.info(f"Processing query: {question}")
            
            # Analyze the question and decide which tools to use
            tool_calls = self._determine_tool_calls(question)
            
            # Execute tool calls and collect results
            tool_results = []
            for tool_name, tool_input in tool_calls:
                if tool_name in self.tool_map:
                    try:
                        result = self.tool_map[tool_name].func(tool_input)
                        tool_results.append({
                            'tool': tool_name,
                            'input': tool_input,
                            'output': result
                        })
                    except Exception as e:
                        logger.error(f"Tool {tool_name} error: {e}")
            
            # Use LLM to synthesize results into a natural language answer
            answer = self._synthesize_answer(question, tool_results)
            
            # Generate appropriate charts based on the question
            charts = self._generate_charts_for_question(question)
            
            # Add chart mention if charts were generated
            if charts and "chart" not in answer.lower() and "visual" not in answer.lower():
                answer += "\n\n📊 I've generated visual charts to help illustrate this data."
            
            return {
                "answer": answer,
                "charts": charts
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return {
                "answer": f"I encountered an error analyzing the data. Please try rephrasing your question or ask about specific sprints, teams, or metrics.",
                "charts": []
            }
    
    def _determine_tool_calls(self, question: str) -> List[tuple]:
        """
        Determine which tools to call based on the question.
        
        Args:
            question: User's question
            
        Returns:
            List of (tool_name, tool_input) tuples
        """
        question_lower = question.lower()
        tool_calls = []
        
        # Extract sprint ID if mentioned
        sprint_match = re.search(r'spr-\d+', question_lower)
        sprint_id = sprint_match.group().upper() if sprint_match else None
        
        # Always start with overview if asking general questions
        if any(word in question_lower for word in ['overview', 'summary', 'all', 'general']):
            tool_calls.append(('get_data_overview', '{}'))
        
        # Velocity queries
        if 'velocity' in question_lower:
            if sprint_id:
                tool_calls.append(('calculate_sprint_metric', json.dumps({'metric_name': 'velocity', 'sprint_id': sprint_id})))
            else:
                tool_calls.append(('analyze_trends', json.dumps({'metric': 'velocity', 'group_by': 'Sprint_ID'})))
        
        # Completion rate queries
        if any(word in question_lower for word in ['completion', 'complete', 'done', 'finished']):
            if sprint_id:
                tool_calls.append(('calculate_sprint_metric', json.dumps({'metric_name': 'completion_rate', 'sprint_id': sprint_id, 'by': 'points'})))
            else:
                tool_calls.append(('analyze_trends', json.dumps({'metric': 'completion_rate', 'group_by': 'Sprint_ID'})))
        
        # Team/member queries
        if any(word in question_lower for word in ['team', 'member', 'assignee', 'who', 'performance']):
            tool_calls.append(('analyze_team_performance', json.dumps({'metric': 'velocity'})))
        
        # Bug queries
        if 'bug' in question_lower:
            tool_calls.append(('calculate_quality_metrics', json.dumps({'sprint_id': sprint_id} if sprint_id else {})))
        
        # Sprint comparison
        if 'compare' in question_lower:
            # Extract multiple sprint IDs
            sprint_matches = re.findall(r'spr-\d+', question_lower)
            if len(sprint_matches) >= 2:
                sprint_ids = [m.upper() for m in sprint_matches]
                tool_calls.append(('compare_sprints', json.dumps({
                    'sprint_ids': sprint_ids,
                    'metrics': ['velocity', 'completion_rate', 'bug_count']
                })))
        
        # Sprint health
        if 'health' in question_lower and sprint_id:
            tool_calls.append(('calculate_sprint_health', json.dumps({'sprint_id': sprint_id})))
        
        # Work distribution
        if 'distribution' in question_lower or 'balance' in question_lower:
            tool_calls.append(('analyze_work_distribution', json.dumps({'sprint_id': sprint_id} if sprint_id else {})))
        
        # Cycle time
        if 'cycle' in question_lower or 'time' in question_lower:
            tool_calls.append(('calculate_sprint_metric', json.dumps({'metric_name': 'cycle_time_avg', 'status': 'Done'})))
        
        # If no specific tool was identified, use get_data_overview
        if not tool_calls:
            tool_calls.append(('get_data_overview', '{}'))
        
        logger.info(f"Determined tool calls: {[t[0] for t in tool_calls]}")
        return tool_calls
    
    def _synthesize_answer(self, question: str, tool_results: List[Dict]) -> str:
        """
        Use LLM to synthesize tool results into a natural language answer.
        
        Args:
            question: Original user question
            tool_results: List of tool execution results
            
        Returns:
            Natural language answer
        """
        if not tool_results:
            return "I couldn't find relevant data to answer your question. Please try rephrasing or ask about specific sprints, teams, or metrics."
        
        # Build context from tool results
        context_parts = []
        for result in tool_results:
            context_parts.append(f"Tool: {result['tool']}\nInput: {result['input']}\nOutput:\n{result['output']}\n")
        
        context = "\n---\n".join(context_parts)
        
        system_prompt = """You are an expert sprint data analyst. You have just executed data analysis tools and received real results from the sprint database.

Your task is to synthesize these tool results into a clear, insightful answer to the user's question.

**Guidelines:**
1. Use ONLY the data from the tool results - do not make up numbers
2. Present the key findings clearly with bullet points
3. Show calculations when relevant (e.g., "Velocity: 45 points completed")
4. Provide context and comparisons
5. Highlight any concerns (critical bugs, low completion rates, etc.)
6. Be concise but thorough
7. Use emojis sparingly for emphasis (⚠️ ✅ 📊)

**Format:**
- Start with a direct answer to the question
- Follow with supporting details
- End with any recommendations or observations"""

        user_prompt = f"""Question: {question}

Tool Execution Results:
{context}

Please provide a clear, data-driven answer based on the tool results above."""
        
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            answer = response.content if hasattr(response, 'content') else str(response)
            return answer
            
        except Exception as e:
            logger.error(f"LLM synthesis error: {e}")
            # Fallback to simple formatting of results
            return self._format_results_simple(question, tool_results)
    
    def _format_results_simple(self, question: str, tool_results: List[Dict]) -> str:
        """Fallback method to format results without LLM."""
        answer_parts = [f"Based on the analysis:"]
        
        for result in tool_results:
            try:
                result_data = json.loads(result['output'])
                answer_parts.append(f"\n{json.dumps(result_data, indent=2)}")
            except:
                answer_parts.append(f"\n{result['output']}")
        
        return "\n".join(answer_parts)
    
    def _generate_charts_for_question(self, question: str) -> List[Dict]:
        """
        Generate appropriate charts based on the question content.
        
        Args:
            question: User's question
            
        Returns:
            List of chart JSON objects
        """
        question_lower = question.lower()
        charts = []
        df = self.data_analyzer.get_dataframe()
        
        try:
            # Velocity/sprint trends
            if any(word in question_lower for word in ['velocity', 'trend', 'progress', 'sprint']):
                chart_json = self.chart_generator.create_sprint_velocity_chart(df)
                if chart_json:
                    charts.append(json.loads(chart_json))
            
            # Team performance
            if any(word in question_lower for word in ['team', 'member', 'assignee', 'who', 'performance']):
                chart_json = self.chart_generator.create_team_performance_chart(df)
                if chart_json:
                    charts.append(json.loads(chart_json))
            
            # Bug analysis
            if 'bug' in question_lower:
                chart_json = self.chart_generator.create_bug_severity_chart(df)
                if chart_json:
                    charts.append(json.loads(chart_json))
            
            # Status distribution
            if any(word in question_lower for word in ['status', 'done', 'complete', 'progress', 'distribution']):
                chart_json = self.chart_generator.create_status_pie_chart(df)
                if chart_json:
                    charts.append(json.loads(chart_json))
            
            # Priority distribution
            if 'priority' in question_lower or 'high' in question_lower or 'critical' in question_lower:
                chart_json = self.chart_generator.create_priority_distribution_chart(df)
                if chart_json:
                    charts.append(json.loads(chart_json))
            
            # Overview/dashboard
            if any(word in question_lower for word in ['overview', 'summary', 'dashboard', 'show me']) and not charts:
                # Add status chart for overview
                chart_json = self.chart_generator.create_status_pie_chart(df)
                if chart_json:
                    charts.append(json.loads(chart_json))
                # Add velocity chart
                chart_json = self.chart_generator.create_sprint_velocity_chart(df)
                if chart_json:
                    charts.append(json.loads(chart_json))
        
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
        
        return charts
