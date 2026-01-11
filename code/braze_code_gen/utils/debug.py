"""Debugging and logging utilities for Braze Code Generator.

This module provides enhanced logging, state inspection, and debugging tools
for troubleshooting the multi-agent workflow.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path

from braze_code_gen.core.state import CodeGenerationState


# Configure logging format
DETAILED_FORMAT = (
    '%(asctime)s - %(name)s - %(levelname)s - '
    '[%(filename)s:%(lineno)d] - %(message)s'
)

SIMPLE_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    detailed: bool = False
) -> logging.Logger:
    """Setup logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path
        detailed: Whether to use detailed format with file/line numbers

    Returns:
        logging.Logger: Configured root logger
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    log_format = DETAILED_FORMAT if detailed else SIMPLE_FORMAT

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[]
    )

    root_logger = logging.getLogger()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(logging.Formatter(DETAILED_FORMAT))
        root_logger.addHandler(file_handler)
        root_logger.info(f"Logging to file: {log_file}")

    return root_logger


class StateDebugger:
    """Debug utility for inspecting workflow state."""

    def __init__(self, output_dir: str = "/tmp/braze_debug"):
        """Initialize state debugger.

        Args:
            output_dir: Directory for debug output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def dump_state(
        self,
        state: CodeGenerationState,
        node_name: str,
        iteration: Optional[int] = None
    ) -> str:
        """Dump state to JSON file for debugging.

        Args:
            state: Current workflow state
            node_name: Name of the node that produced this state
            iteration: Optional iteration number (for refinement loops)

        Returns:
            str: Path to dumped file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        iteration_str = f"_iter{iteration}" if iteration is not None else ""
        filename = f"state_{node_name}{iteration_str}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)

        # Convert state to serializable format
        state_dict = self._serialize_state(state)

        with open(filepath, 'w') as f:
            json.dump(state_dict, f, indent=2, default=str)

        logging.info(f"State dumped to: {filepath}")
        return filepath

    def _serialize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Convert state to JSON-serializable format.

        Args:
            state: State dictionary

        Returns:
            Dict: Serializable state
        """
        serialized = {}

        for key, value in state.items():
            try:
                # Handle Pydantic models
                if hasattr(value, 'model_dump'):
                    serialized[key] = value.model_dump()
                # Handle lists of Pydantic models
                elif isinstance(value, list) and value and hasattr(value[0], 'model_dump'):
                    serialized[key] = [item.model_dump() for item in value]
                # Handle messages
                elif hasattr(value, 'content'):
                    serialized[key] = {
                        'type': type(value).__name__,
                        'content': value.content
                    }
                # Handle other types
                else:
                    serialized[key] = value
            except Exception as e:
                serialized[key] = f"<serialization error: {str(e)}>"

        return serialized

    def print_state_summary(self, state: CodeGenerationState):
        """Print concise state summary to console.

        Args:
            state: Current workflow state
        """
        print("\n" + "="*60)
        print("WORKFLOW STATE SUMMARY")
        print("="*60)

        # Key fields
        print(f"User Request: {state.get('user_request', 'N/A')[:80]}...")
        print(f"Website URL: {state.get('customer_website_url', 'N/A')}")
        print(f"Refinement Iteration: {state.get('refinement_iteration', 0)}/{state.get('max_refinement_iterations', 3)}")
        print(f"Validation Passed: {state.get('validation_passed', False)}")

        # Feature plan
        feature_plan = state.get('feature_plan')
        if feature_plan:
            print(f"\nFeatures: {len(feature_plan.features) if hasattr(feature_plan, 'features') else 'N/A'}")

        # Branding
        branding = state.get('branding_data')
        if branding:
            print(f"Branding: Extracted from {branding.website_url if hasattr(branding, 'website_url') else 'N/A'}")

        # Generated code
        generated_code = state.get('generated_code')
        if generated_code:
            print(f"Generated Code: {len(str(generated_code)) if generated_code else 0} chars")

        # Errors
        errors = state.get('validation_errors', [])
        if errors:
            print(f"\nValidation Errors ({len(errors)}):")
            for i, error in enumerate(errors[:3], 1):
                print(f"  {i}. {error[:100]}...")

        error = state.get('error')
        if error:
            print(f"\nWorkflow Error: {error}")

        print("="*60 + "\n")


class PerformanceTracker:
    """Track performance metrics for workflow execution."""

    def __init__(self):
        """Initialize performance tracker."""
        self.timings: Dict[str, float] = {}
        self.start_times: Dict[str, float] = {}

    def start(self, node_name: str):
        """Start timing a node.

        Args:
            node_name: Name of the node
        """
        import time
        self.start_times[node_name] = time.time()

    def end(self, node_name: str):
        """End timing a node and record duration.

        Args:
            node_name: Name of the node
        """
        import time
        if node_name in self.start_times:
            duration = time.time() - self.start_times[node_name]
            self.timings[node_name] = duration
            del self.start_times[node_name]
            logging.debug(f"Node {node_name} completed in {duration:.2f}s")

    def print_summary(self):
        """Print performance summary."""
        if not self.timings:
            print("No performance data collected")
            return

        print("\n" + "="*60)
        print("PERFORMANCE SUMMARY")
        print("="*60)

        total_time = sum(self.timings.values())
        print(f"Total Time: {total_time:.2f}s\n")

        print("Node Timings:")
        for node, duration in sorted(self.timings.items(), key=lambda x: x[1], reverse=True):
            percentage = (duration / total_time) * 100
            print(f"  {node:20s}: {duration:6.2f}s ({percentage:5.1f}%)")

        print("="*60 + "\n")

    def get_metrics(self) -> Dict[str, float]:
        """Get performance metrics.

        Returns:
            Dict[str, float]: Node timings in seconds
        """
        return self.timings.copy()


def format_error_message(error: Exception, context: Optional[str] = None) -> str:
    """Format error message with context.

    Args:
        error: Exception that occurred
        context: Optional context description

    Returns:
        str: Formatted error message
    """
    error_type = type(error).__name__
    error_msg = str(error)

    formatted = f"{error_type}: {error_msg}"

    if context:
        formatted = f"[{context}] {formatted}"

    return formatted


def create_debug_archive(
    output_dir: str,
    export_dir: str,
    log_file: Optional[str] = None
) -> str:
    """Create a debug archive with logs and generated files.

    Args:
        output_dir: Debug output directory
        export_dir: Export directory with generated HTML
        log_file: Optional log file to include

    Returns:
        str: Path to created archive
    """
    import tarfile
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"braze_debug_{timestamp}.tar.gz"
    archive_path = os.path.join("/tmp", archive_name)

    with tarfile.open(archive_path, "w:gz") as tar:
        # Add debug files
        if os.path.exists(output_dir):
            tar.add(output_dir, arcname="debug")

        # Add generated files
        if os.path.exists(export_dir):
            tar.add(export_dir, arcname="exports")

        # Add log file
        if log_file and os.path.exists(log_file):
            tar.add(log_file, arcname="logs/app.log")

    logging.info(f"Debug archive created: {archive_path}")
    return archive_path


# Global instances for easy access
_state_debugger: Optional[StateDebugger] = None
_performance_tracker: Optional[PerformanceTracker] = None


def get_state_debugger() -> StateDebugger:
    """Get global state debugger instance.

    Returns:
        StateDebugger: Global debugger instance
    """
    global _state_debugger
    if _state_debugger is None:
        _state_debugger = StateDebugger()
    return _state_debugger


def get_performance_tracker() -> PerformanceTracker:
    """Get global performance tracker instance.

    Returns:
        PerformanceTracker: Global tracker instance
    """
    global _performance_tracker
    if _performance_tracker is None:
        _performance_tracker = PerformanceTracker()
    return _performance_tracker
