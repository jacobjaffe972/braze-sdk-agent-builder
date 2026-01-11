#!/bin/bash
# Test runner for Braze Code Generator

echo "=== Braze Code Generator Test Suite ==="
echo ""

# Set environment
export PYTHONPATH=/Users/Jacob.Jaffe/code-gen-agent/code
export OPENAI_API_KEY=dummy_key_for_testing

# Python binary
PYTHON=/Users/Jacob.Jaffe/code-gen-agent/braze-docs-mcp/venv/bin/python

# Run different test suites
echo "1. Running UI tests..."
$PYTHON -m pytest braze_code_gen/tests/test_ui.py -v --tb=short

echo ""
echo "2. Running workflow tests..."
$PYTHON -m pytest braze_code_gen/tests/test_workflow.py -v --tb=short

echo ""
echo "3. Running E2E tests..."
$PYTHON -m pytest braze_code_gen/tests/test_e2e.py -v --tb=short

echo ""
echo "=== Test Summary ==="
$PYTHON -m pytest braze_code_gen/tests/ --tb=no -q
