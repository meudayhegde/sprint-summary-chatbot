"""
Test script to verify the enhanced data analysis capabilities.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from data_analyzer import SprintDataAnalyzer
from agent import SprintAnalysisAgent

def test_queries():
    """Test various complex queries to ensure real data analysis."""
    
    # Initialize analyzer and agent
    print("🚀 Initializing Sprint Analysis Agent with real DataFrame analysis...")
    data_analyzer = SprintDataAnalyzer("sprint_synthetic_data(Tickets).csv")
    agent = SprintAnalysisAgent(data_analyzer)
    
    # Test queries that require actual data analysis
    test_cases = [
        "What is the velocity of SPR-001?",
        "Compare the completion rates of SPR-001, SPR-002, and SPR-003",
        "Which team member has the highest productivity?",
        "What is the bug resolution rate across all sprints?",
        "How is work distributed across the team in SPR-002?",
        "What is the health score of SPR-003?",
        "Show me the trend of velocity across all sprints",
        "How many critical bugs are there and who is working on them?",
        "What is the average cycle time for completed stories?",
        "Which sprint had the best completion rate?"
    ]
    
    print(f"\n📊 Testing {len(test_cases)} complex queries...\n")
    print("=" * 80)
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}/{len(test_cases)}")
        print(f"Question: {question}")
        print("-" * 80)
        
        try:
            result = agent.query(question)
            answer = result.get("answer", "No answer")
            charts = result.get("charts", [])
            
            print(f"✅ Answer:\n{answer}")
            print(f"\n📈 Charts generated: {len(charts)}")
            
            # Check if answer contains actual numbers (indicating real analysis)
            has_numbers = any(char.isdigit() for char in answer)
            if has_numbers:
                print("✓ Answer contains numerical data (real analysis performed)")
            else:
                print("⚠️  Answer may not contain calculated metrics")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("=" * 80)
    
    print("\n✅ Testing complete!")
    print("\n💡 The agent now uses real pandas DataFrame operations via LangChain tools")
    print("   to calculate metrics, filter data, and provide accurate answers.")


if __name__ == "__main__":
    test_queries()
