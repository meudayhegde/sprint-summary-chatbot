"""
Quick verification that the new modules can be imported and initialized.
"""

import sys
import traceback

def test_imports():
    """Test that all new modules can be imported."""
    print("🔍 Testing module imports...\n")
    
    try:
        print("1. Importing dataframe_query_executor...")
        from dataframe_query_executor import DataFrameQueryExecutor
        print("   ✅ DataFrameQueryExecutor imported successfully")
        
        print("\n2. Importing data_analysis_tools...")
        from data_analysis_tools import DataAnalysisTools
        print("   ✅ DataAnalysisTools imported successfully")
        
        print("\n3. Importing updated agent...")
        from agent import SprintAnalysisAgent
        print("   ✅ SprintAnalysisAgent imported successfully")
        
        print("\n4. Testing DataFrameQueryExecutor initialization...")
        import pandas as pd
        test_df = pd.DataFrame({
            'Sprint_ID': ['SPR-001', 'SPR-001', 'SPR-002'],
            'Story_Points': [5, 3, 8],
            'Status': ['Done', 'Done', 'In Progress'],
            'Type': ['Story', 'Bug', 'Story'],
            'Assignee': ['Alice', 'Bob', 'Alice']
        })
        executor = DataFrameQueryExecutor(test_df)
        print("   ✅ DataFrameQueryExecutor initialized successfully")
        
        print("\n5. Testing a simple query...")
        result = executor.execute_query('calculate_metric', metric_name='velocity')
        print(f"   ✅ Query executed successfully. Result: {result}")
        
        print("\n6. Testing DataAnalysisTools initialization...")
        tools_factory = DataAnalysisTools(test_df)
        tools = tools_factory.get_all_tools()
        print(f"   ✅ Created {len(tools)} analysis tools")
        
        print("\n7. Listing available tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description[:60]}...")
        
        print("\n" + "="*80)
        print("✅ All verifications passed!")
        print("="*80)
        print("\n📊 The chatbot now has real DataFrame analysis capabilities:")
        print("   • Executes actual pandas queries and calculations")
        print("   • Uses LangChain tool calling for data-driven answers")
        print("   • Provides accurate metrics from real data operations")
        print("\n🚀 Ready to start the application!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        print("\nTraceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
