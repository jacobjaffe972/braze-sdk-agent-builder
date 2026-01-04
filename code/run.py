import os
import sys
import argparse

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Run Deep Research AI Assistant')
parser.add_argument(
    '--agent',
    type=str,
    default='LLM_Chaining',
    help='Agent to run. Options: LLM_Chaining, LLM_RAG_Tools, ReaAct_Multi_Agent, '
         'or specific modes like llm_chaining_query, rag_web_search, react_deep_research'
)
args = parser.parse_args()

# Import and run the app
from deep_research.app import create_demo

if __name__ == "__main__":
    demo = create_demo(agent_name=args.agent)
    demo.launch()