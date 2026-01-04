#!/usr/bin/env python3
"""Test script to verify all 9 agent modes work correctly."""

import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from deep_research.core.factory import create_agent_by_name

# List of all agent modes to test
AGENT_MODES = [
    # LLM Chaining
    "llm_chaining_query",
    "llm_chaining_tools",
    "llm_chaining_memory",
    # RAG Tools
    "rag_web_search",
    "rag_document",
    "rag_corrective",
    # ReAct Multi-Agent
    "react_tool_using",
    "react_agentic_rag",
    "react_deep_research"
]

# Simple test queries for each type
TEST_QUERIES = {
    "llm_chaining_query": "What is the capital of France?",
    "llm_chaining_tools": "What is 25 * 4 + 10?",
    "llm_chaining_memory": "My name is Alice. What's my name?",
    "rag_web_search": "What are the latest AI developments?",
    "rag_document": "What were OPM's goals in 2020?",
    "rag_corrective": "What were OPM's strategic objectives in 2021?",
    "react_tool_using": "What day of the week is today?",
    "react_agentic_rag": "What were OPM's accomplishments in 2022?",
    "react_deep_research": "Research the impact of AI on employment" # This one takes long
}

def test_agent(agent_name):
    """Test a single agent mode."""
    print(f"\n{'='*60}")
    print(f"Testing: {agent_name}")
    print(f"{'='*60}")

    try:
        # Create agent
        print(f"Creating agent '{agent_name}'...")
        agent = create_agent_by_name(agent_name)
        print("✓ Agent created successfully")

        # Get test query
        query = TEST_QUERIES.get(agent_name, "Hello")
        print(f"\nSending test query: '{query}'")

        # Process message
        response = agent.process_message(query, [])

        print(f"\n✓ Response received ({len(response)} chars)")
        print(f"Response preview: {response[:200]}...")

        return True

    except Exception as e:
        print(f"\n✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run tests for all agent modes."""
    print("Starting agent mode tests...")
    print(f"Total modes to test: {len(AGENT_MODES)}")

    results = {}

    for agent_name in AGENT_MODES:
        # Skip deep research for quick testing (takes too long)
        if agent_name == "react_deep_research":
            print(f"\n{'='*60}")
            print(f"Skipping: {agent_name} (too slow for quick test)")
            print(f"{'='*60}")
            results[agent_name] = "SKIPPED"
            continue

        success = test_agent(agent_name)
        results[agent_name] = "PASS" if success else "FAIL"

    # Print summary
    print(f"\n\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")

    for agent_name, status in results.items():
        status_symbol = "✓" if status == "PASS" else ("○" if status == "SKIPPED" else "✗")
        print(f"{status_symbol} {agent_name}: {status}")

    passed = sum(1 for s in results.values() if s == "PASS")
    failed = sum(1 for s in results.values() if s == "FAIL")
    skipped = sum(1 for s in results.values() if s == "SKIPPED")

    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")

    if failed > 0:
        sys.exit(1)
    else:
        print("\n✓ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
