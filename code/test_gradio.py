#!/usr/bin/env python3
"""Test Gradio setup to diagnose blank UI issue."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import gradio as gr

def simple_respond(message, history):
    """Simple echo response."""
    return f"Echo: {message}"

print("Testing Gradio ChatInterface...")
print(f"Gradio version: {gr.__version__}")

try:
    demo = gr.ChatInterface(
        fn=simple_respond,
        title="Test Chat Interface",
        description="Simple test to verify Gradio works",
        examples=[
            ["Hello"],
            ["How are you?"]
        ]
    )

    print("✓ ChatInterface created successfully")
    print("Launching on http://127.0.0.1:7860")
    print("Press Ctrl+C to stop")

    demo.launch(server_name="127.0.0.1", server_port=7860)

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
