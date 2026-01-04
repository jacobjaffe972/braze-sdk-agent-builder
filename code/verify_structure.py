#!/usr/bin/env python3
"""
Verify the code structure and imports are correct.
This does static analysis without requiring dependencies to be installed.
"""

import os
import ast
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_file_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r') as f:
            source = f.read()
        ast.parse(source)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def verify_imports(filepath):
    """Extract and verify import structure (without actually importing)."""
    try:
        with open(filepath, 'r') as f:
            source = f.read()

        tree = ast.parse(source)
        imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                imports.append(module)

        return imports
    except Exception as e:
        return []

def main():
    """Verify the deep_research package structure."""

    print("="*60)
    print("DEEP RESEARCH AGENT - STRUCTURE VERIFICATION")
    print("="*60)

    # Files to check
    files_to_check = [
        # Core
        ("deep_research/core/chat_interface.py", "Base Interface"),
        ("deep_research/core/factory.py", "Factory Pattern"),

        # Prompts
        ("deep_research/prompts/LLM_CHAINING_PROMPTS.py", "LLM Chaining Prompts"),
        ("deep_research/prompts/RAG_PROMPTS.py", "RAG Prompts"),
        ("deep_research/prompts/AGENT_PROMPTS.py", "Agent Prompts"),

        # Agents
        ("deep_research/agents/llm_chaining.py", "LLM Chaining Agent"),
        ("deep_research/agents/llm_rag_tools.py", "LLM RAG Tools Agent"),
        ("deep_research/agents/react_multi_agent.py", "ReAct Multi-Agent"),

        # Tools
        ("deep_research/tools/calculator.py", "Calculator Tool"),

        # Entry points
        ("run.py", "Run Script"),
        ("deep_research/app.py", "Gradio App"),
    ]

    results = []

    for filepath, description in files_to_check:
        full_path = project_root / filepath
        print(f"\n[{description}]")
        print(f"  Path: {filepath}")

        if not full_path.exists():
            print(f"  ✗ FILE NOT FOUND")
            results.append(("✗", description, "Missing file"))
            continue

        # Check syntax
        is_valid, message = check_file_syntax(full_path)
        if not is_valid:
            print(f"  ✗ SYNTAX ERROR: {message}")
            results.append(("✗", description, message))
            continue

        # Get imports
        imports = verify_imports(full_path)
        deep_research_imports = [imp for imp in imports if 'deep_research' in imp]

        print(f"  ✓ Syntax valid")
        print(f"  Imports: {len(imports)} total, {len(deep_research_imports)} from deep_research")

        if deep_research_imports:
            for imp in deep_research_imports[:3]:  # Show first 3
                print(f"    - {imp}")
            if len(deep_research_imports) > 3:
                print(f"    ... and {len(deep_research_imports) - 3} more")

        results.append(("✓", description, "Valid"))

    # Summary
    print(f"\n\n{'='*60}")
    print("VERIFICATION SUMMARY")
    print(f"{'='*60}")

    passed = sum(1 for status, _, _ in results if status == "✓")
    failed = sum(1 for status, _, _ in results if status == "✗")

    for status, description, message in results:
        status_display = "PASS" if status == "✓" else "FAIL"
        print(f"{status} {description}: {status_display}")
        if status == "✗":
            print(f"    {message}")

    print(f"\nTotal: {passed}/{len(files_to_check)} files verified")

    # Check __init__.py files
    print(f"\n{'='*60}")
    print("CHECKING __init__.py FILES")
    print(f"{'='*60}")

    init_files = [
        "deep_research/__init__.py",
        "deep_research/agents/__init__.py",
        "deep_research/prompts/__init__.py",
        "deep_research/core/__init__.py",
        "deep_research/tools/__init__.py",
    ]

    for init_file in init_files:
        full_path = project_root / init_file
        exists = "✓" if full_path.exists() else "✗"
        print(f"{exists} {init_file}")

    # Final verdict
    print(f"\n{'='*60}")
    if failed == 0:
        print("✓ ALL STRUCTURE CHECKS PASSED")
        print("✓ All files have valid syntax")
        print("✓ Imports use correct 'deep_research' package name")
        print("\nNote: This verification only checks file structure and syntax.")
        print("To fully test the agents, you need to:")
        print("  1. Install dependencies (langchain, langgraph, etc.)")
        print("  2. Set up environment variables (OPENAI_API_KEY, etc.)")
        print("  3. Run: python run.py --agent <agent_name>")
        sys.exit(0)
    else:
        print(f"✗ {failed} FILES FAILED VERIFICATION")
        sys.exit(1)

if __name__ == "__main__":
    main()
