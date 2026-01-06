"""State management for the Braze Code Generator workflow.

This module defines the TypedDict state schema used by the LangGraph StateGraph.
"""

from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from braze_code_gen.core.models import (
    BrandingData,
    BrazeAPIConfig,
    SDKFeaturePlan,
    GeneratedCode,
    ValidationReport,
    ResearchResult,
)


class CodeGenerationState(TypedDict):
    """State for the Braze Code Generator workflow.

    This state is passed through all nodes in the StateGraph workflow.
    Messages are automatically accumulated using the add_messages annotation.
    """

    # ========================================================================
    # Message History
    # ========================================================================

    messages: Annotated[Sequence[BaseMessage], add_messages]
    """Conversation messages (user input + agent responses).

    The add_messages annotation ensures messages are appended, not replaced.
    """

    # ========================================================================
    # User Input
    # ========================================================================

    user_features: Optional[list[str]]
    """List of SDK features requested by user."""

    customer_website_url: Optional[str]
    """Customer website URL for branding extraction."""

    # ========================================================================
    # API Configuration
    # ========================================================================

    braze_api_config: Optional[BrazeAPIConfig]
    """Braze API configuration (key + REST endpoint)."""

    # ========================================================================
    # Branding & Planning
    # ========================================================================

    branding_data: Optional[BrandingData]
    """Extracted website branding (colors, typography)."""

    feature_plan: Optional[SDKFeaturePlan]
    """Complete feature plan with SDK methods."""

    # ========================================================================
    # Research
    # ========================================================================

    research_results: Optional[ResearchResult]
    """Braze documentation research results."""

    # ========================================================================
    # Code Generation
    # ========================================================================

    generated_code: Optional[GeneratedCode]
    """Generated HTML/CSS/JS code."""

    # ========================================================================
    # Validation
    # ========================================================================

    validation_report: Optional[ValidationReport]
    """Browser testing validation report."""

    validation_passed: Optional[bool]
    """Whether validation passed (shortcut field)."""

    refinement_iteration: int
    """Number of refinement iterations (starts at 0)."""

    max_refinement_iterations: int
    """Maximum refinement iterations before giving up."""

    # ========================================================================
    # Export
    # ========================================================================

    export_file_path: Optional[str]
    """Path to exported HTML file."""

    is_complete: bool
    """Whether workflow is complete."""

    # ========================================================================
    # Workflow Control
    # ========================================================================

    next_step: str
    """Next workflow step (for conditional routing)."""

    error: Optional[str]
    """Error message (if any)."""


# ============================================================================
# Initial State Factory
# ============================================================================

def create_initial_state(
    user_message: str,
    braze_api_config: BrazeAPIConfig,
    customer_website_url: Optional[str] = None,
    max_refinement_iterations: int = 3,
) -> CodeGenerationState:
    """Create initial state for the workflow.

    Args:
        user_message: User's initial message with feature requests
        braze_api_config: Validated Braze API configuration
        customer_website_url: Optional customer website URL
        max_refinement_iterations: Max refinement attempts (default: 3)

    Returns:
        CodeGenerationState: Initial state for workflow
    """
    from langchain_core.messages import HumanMessage

    return {
        # Messages
        "messages": [HumanMessage(content=user_message)],

        # User Input
        "user_features": None,
        "customer_website_url": customer_website_url,

        # API Configuration
        "braze_api_config": braze_api_config,

        # Branding & Planning
        "branding_data": None,
        "feature_plan": None,

        # Research
        "research_results": None,

        # Code Generation
        "generated_code": None,

        # Validation
        "validation_report": None,
        "validation_passed": None,
        "refinement_iteration": 0,
        "max_refinement_iterations": max_refinement_iterations,

        # Export
        "export_file_path": None,
        "is_complete": False,

        # Workflow Control
        "next_step": "lead",
        "error": None,
    }


# ============================================================================
# State Update Helpers
# ============================================================================

def update_state(
    state: CodeGenerationState,
    **updates
) -> dict:
    """Helper to create partial state updates.

    Args:
        state: Current state
        **updates: Fields to update

    Returns:
        dict: Partial state update

    Example:
        >>> return update_state(state, validation_passed=True, next_step="finalize")
    """
    return {k: v for k, v in updates.items()}


def mark_error(error_message: str) -> dict:
    """Create state update for error condition.

    Args:
        error_message: Error description

    Returns:
        dict: State update with error

    Example:
        >>> return mark_error("Website analysis failed: timeout")
    """
    return {
        "error": error_message,
        "next_step": "error_handler",
        "is_complete": True,
    }


def mark_complete(export_path: str) -> dict:
    """Create state update for successful completion.

    Args:
        export_path: Path to exported HTML file

    Returns:
        dict: State update marking completion

    Example:
        >>> return mark_complete("/tmp/braze_landing_nike_20260106.html")
    """
    return {
        "export_file_path": export_path,
        "is_complete": True,
        "next_step": "end",
    }
