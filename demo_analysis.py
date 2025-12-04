"""
Demonstration of enhanced data analysis capabilities.
Tests various complex queries to show real DataFrame analysis.
"""

from data_analyzer import SprintDataAnalyzer
from agent import SprintAnalysisAgent
import json

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_result(result):
    """Print query result."""
    print(f"\n📝 Answer:\n{result['answer']}")
    if result['charts']:
        print(f"\n📈 Generated {len(result['charts'])} chart(s)")

# Initialize
print_header("🚀 Sprint Analysis Chatbot - Enhanced with Real DataFrame Analysis")
print("\nInitializing...")
data_analyzer = SprintDataAnalyzer("sprint_synthetic_data(Tickets).csv")
agent = SprintAnalysisAgent(data_analyzer)

print(f"✅ Agent initialized with {len(agent.tools)} data analysis tools")
print(f"📊 Loaded {len(data_analyzer.df)} tickets")

# Demonstrate various capabilities
demos = [
    {
        "category": "Simple Metric Calculation",
        "query": "What is the velocity of SPR-001?"
    },
    {
        "category": "Sprint Comparison",
        "query": "Compare the completion rates of SPR-001 and SPR-002"
    },
    {
        "category": "Team Analysis",
        "query": "Which team member completed the most story points?"
    },
    {
        "category": "Bug Analysis",
        "query": "What is the bug resolution rate and how many critical bugs are there?"
    },
    {
        "category": "Sprint Health",
        "query": "What is the health score of SPR-003?"
    }
]

for demo in demos:
    print_header(f"🔍 {demo['category']}")
    print(f"Query: {demo['query']}")
    
    try:
        result = agent.query(demo['query'])
        print_result(result)
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# Summary
print_header("✅ Demonstration Complete")
print("""
The chatbot now performs REAL data analysis:
  
  ✓ Loads CSV data into pandas DataFrame
  ✓ Executes actual DataFrame queries (filtering, aggregation, grouping)
  ✓ Calculates metrics using pandas operations (sum, mean, count, etc.)
  ✓ Compares data across sprints, teams, and time periods
  ✓ Provides accurate, data-driven answers based on calculations
  
Available Analysis Tools:
  • get_data_overview - Understand available data
  • filter_sprint_data - Filter by any criteria
  • calculate_sprint_metric - Calculate velocity, completion rates, etc.
  • compare_sprints - Multi-sprint comparison
  • analyze_team_performance - Team member analysis
  • analyze_trends - Trends over time
  • calculate_quality_metrics - Bug metrics
  • calculate_sprint_health - Health scoring
  • analyze_work_distribution - Work balance
  • aggregate_data - Custom aggregations
  • get_statistical_summary - Statistical analysis

Try the web interface at http://localhost:8000 to interact with the chatbot!
""")
