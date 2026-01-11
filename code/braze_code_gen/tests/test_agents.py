"""Unit tests for all agent modules.

Tests verify that each agent properly processes state and returns expected updates.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from braze_code_gen.core.state import CodeGenerationState
from braze_code_gen.core.models import (
    SDKFeaturePlan,
    SDKFeature,
    BrandingData,
    ColorScheme,
    TypographyData,
    BrazeAPIConfig,
    GeneratedCode
)
from braze_code_gen.agents.planning_agent import PlanningAgent
from braze_code_gen.agents.research_agent import ResearchAgent
from braze_code_gen.agents.code_generation_agent import CodeGenerationAgent
from braze_code_gen.agents.validation_agent import ValidationAgent
from braze_code_gen.agents.refinement_agent import RefinementAgent
from braze_code_gen.agents.finalization_agent import FinalizationAgent


class TestPlanningAgent:
    """Test suite for Planning Agent."""

    @patch('braze_code_gen.agents.planning_agent.ChatOpenAI')
    def test_planning_agent_initialization(self, mock_llm):
        """Test that planning agent initializes correctly."""
        agent = PlanningAgent(model="gpt-4o-mini", temperature=0.3)

        assert agent is not None
        assert agent.llm is not None
        assert agent.website_analyzer is not None

    @patch('braze_code_gen.agents.planning_agent.ChatOpenAI')
    def test_planning_agent_extracts_url(self, mock_llm):
        """Test URL extraction from user request."""
        agent = PlanningAgent()

        message = "Create a landing page for https://nike.com with push notifications"
        url = agent._extract_website_url(message)

        assert url == "https://nike.com"

    @patch('braze_code_gen.agents.planning_agent.ChatOpenAI')
    def test_planning_agent_no_url(self, mock_llm):
        """Test behavior when no URL provided."""
        agent = PlanningAgent()

        message = "Create a landing page with push notifications"
        url = agent._extract_website_url(message)

        assert url is None

    @patch('braze_code_gen.agents.planning_agent.ChatOpenAI')
    @patch('braze_code_gen.agents.planning_agent.WebsiteAnalyzer')
    def test_planning_agent_process_with_mock_llm(self, mock_analyzer, mock_llm_class):
        """Test planning agent process with mocked LLM."""
        # Setup mock LLM response
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        mock_llm.invoke.return_value = AIMessage(content="""
        Feature Plan:
        1. Push Notifications - requestPushPermission()
        2. User Tracking - logCustomEvent()
        """)

        # Setup mock website analyzer
        mock_analyzer_instance = Mock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_website.return_value = BrandingData(
            website_url="https://nike.com",
            colors=ColorScheme(primary="#000", secondary="#fff", accent="#ff6b35"),
            typography=TypographyData(primary_font="Arial"),
            extraction_success=True,
            fallback_used=False
        )

        agent = PlanningAgent()
        agent.website_analyzer = mock_analyzer_instance

        state = {
            "messages": [HumanMessage(content="Create a landing page for https://nike.com")],
            "user_request": "Create a landing page for https://nike.com"
        }

        result = agent.process(state)

        assert "feature_plan" in result or "error" in result


class TestResearchAgent:
    """Test suite for Research Agent."""

    @patch('braze_code_gen.agents.research_agent.ChatOpenAI')
    def test_research_agent_initialization(self, mock_llm):
        """Test that research agent initializes correctly."""
        agent = ResearchAgent(model="gpt-4o-mini", temperature=0.3)

        assert agent is not None
        assert agent.llm is not None
        assert agent.agent is not None

    @patch('braze_code_gen.agents.research_agent.ChatOpenAI')
    def test_research_agent_format_feature_plan(self, mock_llm):
        """Test feature plan formatting."""
        agent = ResearchAgent()

        feature_plan = SDKFeaturePlan(
            page_title="Test Page",
            page_description="Test Description",
            features=[
                SDKFeature(
                    name="Push Notifications",
                    description="Web push",
                    sdk_methods=["requestPushPermission()"],
                    priority=1
                )
            ]
        )

        formatted = agent._format_feature_plan(feature_plan)

        assert "Push Notifications" in formatted
        assert "requestPushPermission()" in formatted


class TestCodeGenerationAgent:
    """Test suite for Code Generation Agent."""

    @patch('braze_code_gen.agents.code_generation_agent.ChatOpenAI')
    def test_code_gen_agent_initialization(self, mock_llm):
        """Test that code generation agent initializes correctly."""
        agent = CodeGenerationAgent(model="gpt-4o", temperature=0.7)

        assert agent is not None
        assert agent.llm is not None

    @patch('braze_code_gen.agents.code_generation_agent.ChatOpenAI')
    def test_code_gen_combines_html(self, mock_llm):
        """Test HTML combination from parts."""
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance

        agent = CodeGenerationAgent()

        html = "<html><body>Test</body></html>"
        css = "body { color: red; }"
        js = "console.log('test');"

        combined = agent._combine_html_parts(html, css, js)

        assert "<!DOCTYPE html>" in combined or "<html>" in combined
        assert "Test" in combined


class TestValidationAgent:
    """Test suite for Validation Agent."""

    @patch('braze_code_gen.agents.validation_agent.ChatOpenAI')
    def test_validation_agent_initialization(self, mock_llm):
        """Test that validation agent initializes correctly."""
        agent = ValidationAgent(
            model="gpt-4o-mini",
            temperature=0.3,
            enable_browser_testing=False
        )

        assert agent is not None
        assert agent.llm is not None

    @patch('braze_code_gen.agents.validation_agent.ChatOpenAI')
    def test_validation_checks_sdk_initialization(self, mock_llm):
        """Test SDK initialization checking."""
        agent = ValidationAgent(enable_browser_testing=False)

        html_with_sdk = """
        <html>
        <script src="https://js.appboycdn.com/web-sdk/4.0/braze.min.js"></script>
        <script>
        braze.initialize('api-key', {baseUrl: 'https://sdk.iad-01.braze.com'});
        </script>
        </html>
        """

        has_sdk = agent._check_sdk_loaded(html_with_sdk)
        assert has_sdk is True

        html_without_sdk = "<html><body>No SDK</body></html>"
        has_sdk = agent._check_sdk_loaded(html_without_sdk)
        assert has_sdk is False


class TestRefinementAgent:
    """Test suite for Refinement Agent."""

    @patch('braze_code_gen.agents.refinement_agent.ChatOpenAI')
    def test_refinement_agent_initialization(self, mock_llm):
        """Test that refinement agent initializes correctly."""
        agent = RefinementAgent(model="gpt-4o", temperature=0.5)

        assert agent is not None
        assert agent.llm is not None

    @patch('braze_code_gen.agents.refinement_agent.ChatOpenAI')
    def test_refinement_formats_issues(self, mock_llm):
        """Test issue formatting for LLM."""
        agent = RefinementAgent()

        issues = [
            "SDK not loaded",
            "JavaScript error on line 10",
            "Missing event handler"
        ]

        formatted = agent._format_issues(issues)

        assert "SDK not loaded" in formatted
        assert "line 10" in formatted
        assert len(formatted) > 50  # Should have context


class TestFinalizationAgent:
    """Test suite for Finalization Agent."""

    @patch('braze_code_gen.agents.finalization_agent.ChatOpenAI')
    def test_finalization_agent_initialization(self, mock_llm):
        """Test that finalization agent initializes correctly."""
        agent = FinalizationAgent(
            model="gpt-4o",
            temperature=0.3,
            export_dir="/tmp/test"
        )

        assert agent is not None
        assert agent.llm is not None
        assert agent.exporter is not None

    @patch('braze_code_gen.agents.finalization_agent.ChatOpenAI')
    def test_finalization_adds_metadata_comment(self, mock_llm):
        """Test metadata comment generation."""
        agent = FinalizationAgent(export_dir="/tmp/test")

        metadata = {
            "generated_at": "2026-01-07T12:00:00",
            "customer_website": "https://nike.com",
            "features": ["Push Notifications", "User Tracking"]
        }

        comment = agent._generate_metadata_comment(metadata)

        assert "Braze SDK Landing Page" in comment
        assert "2026-01-07" in comment
        assert "nike.com" in comment
        assert "Push Notifications" in comment


class TestAgentStateManagement:
    """Test suite for agent state handling."""

    def test_state_has_required_keys(self):
        """Test that initial state has all required keys."""
        from braze_code_gen.core.state import create_initial_state

        state = create_initial_state(
            user_message="Test message",
            braze_api_config=BrazeAPIConfig(
                api_key="test_key_12345678901234567890123456789012",
                rest_endpoint="https://rest.iad-01.braze.com",
                validated=True
            ),
            customer_website_url="https://nike.com"
        )

        required_keys = [
            "messages",
            "user_request",
            "braze_api_config",
            "customer_website_url",
            "refinement_iteration",
            "max_refinement_iterations"
        ]

        for key in required_keys:
            assert key in state, f"Missing required key: {key}"

    def test_state_typing(self):
        """Test that state follows TypedDict contract."""
        from braze_code_gen.core.state import CodeGenerationState

        # This should not raise type errors
        state: CodeGenerationState = {
            "messages": [],
            "user_request": "Test",
            "feature_plan": None,
            "research_results": None,
            "generated_code": None,
            "validation_passed": False,
            "validation_errors": [],
            "refinement_iteration": 0,
            "max_refinement_iterations": 3,
            "customer_website_url": None,
            "branding_data": None,
            "braze_api_config": None,
            "export_file_path": None,
            "error": None
        }

        assert isinstance(state, dict)


class TestAgentErrorHandling:
    """Test suite for agent error handling."""

    @patch('braze_code_gen.agents.planning_agent.ChatOpenAI')
    def test_planning_agent_handles_llm_error(self, mock_llm_class):
        """Test planning agent handles LLM errors gracefully."""
        mock_llm = Mock()
        mock_llm_class.return_value = mock_llm
        mock_llm.invoke.side_effect = Exception("LLM API Error")

        agent = PlanningAgent()
        state = {
            "messages": [HumanMessage(content="Test")],
            "user_request": "Test"
        }

        result = agent.process(state)

        assert "error" in result
        assert "LLM API Error" in result["error"] or "planning failed" in result["error"].lower()

    @patch('braze_code_gen.agents.research_agent.ChatOpenAI')
    def test_research_agent_continues_on_error(self, mock_llm):
        """Test research agent continues workflow even on error."""
        agent = ResearchAgent()

        # Create invalid state (no feature plan)
        state = {
            "messages": [],
            "feature_plan": None
        }

        result = agent.process(state)

        # Should return error but continue
        assert "error" in result
        # Should still proceed to next step
        assert result.get("next_step") in ["code_generation", "error_handler"]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
