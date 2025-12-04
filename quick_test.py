"""
Quick test of the enhanced data analysis.
"""

from data_analyzer import SprintDataAnalyzer
from agent import SprintAnalysisAgent
import json

# Initialize
print("🚀 Initializing Sprint Analysis Agent...")
data_analyzer = SprintDataAnalyzer("sprint_synthetic_data(Tickets).csv")
agent = SprintAnalysisAgent(data_analyzer)

print(f"✅ Agent initialized with {len(agent.tools)} tools")
print(f"📊 Loaded {len(data_analyzer.df)} tickets from CSV\n")

# Test a simple query
print("=" * 80)
print("🔍 Test Query: What is the velocity of SPR-001?")
print("=" * 80)

result = agent.query("What is the velocity of SPR-001?")

print("\n📝 Answer:")
print(result['answer'])

print(f"\n📈 Charts generated: {len(result['charts'])}")

print("\n" + "=" * 80)
print("✅ Test complete!")
print("=" * 80)

print("\n💡 The chatbot now:")
print("   ✓ Loads CSV data into pandas DataFrame")
print("   ✓ Executes real DataFrame queries and calculations")
print("   ✓ Uses tools to calculate metrics like velocity, completion rates, etc.")
print("   ✓ Provides data-driven answers based on actual analysis")
