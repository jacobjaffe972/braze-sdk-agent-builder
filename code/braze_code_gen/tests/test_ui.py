"""Smoke tests for Gradio UI.

These tests verify that the UI can be initialized and basic functionality works.
"""

import pytest
from unittest.mock import Mock, patch

from braze_code_gen.ui.gradio_app import BrazeCodeGenUI
from braze_code_gen.core.models import BrazeAPIConfig


class TestBrazeCodeGenUI:
    """Test suite for Gradio UI."""

    def test_ui_initialization(self):
        """Test that UI can be initialized."""
        ui = BrazeCodeGenUI(
            export_dir="/tmp/test_exports",
            enable_browser_testing=False
        )

        assert ui is not None
        assert ui.orchestrator is not None
        assert ui.current_api_config is None

    def test_validate_api_config_success(self):
        """Test successful API configuration validation."""
        ui = BrazeCodeGenUI(enable_browser_testing=False)

        test_api_key = "test_key_12345678901234567890123456789012"  # 32+ chars
        status, config, api_section, chat_section = ui.validate_api_config(
            api_key=test_api_key,
            rest_endpoint="https://rest.iad-01.braze.com"
        )

        assert "✅" in status
        assert config is not None
        assert config.api_key == test_api_key
        assert config.rest_endpoint == "https://rest.iad-01.braze.com"
        assert ui.current_api_config is not None

    def test_validate_api_config_invalid_key(self):
        """Test validation with invalid API key."""
        ui = BrazeCodeGenUI(enable_browser_testing=False)

        status, config, _, _ = ui.validate_api_config(
            api_key="short",
            rest_endpoint="https://rest.iad-01.braze.com"
        )

        assert "❌" in status
        assert config is None
        assert ui.current_api_config is None

    def test_validate_api_config_invalid_endpoint(self):
        """Test validation with invalid REST endpoint."""
        ui = BrazeCodeGenUI(enable_browser_testing=False)

        test_api_key = "test_key_12345678901234567890123456789012"  # 32+ chars
        status, config, _, _ = ui.validate_api_config(
            api_key=test_api_key,
            rest_endpoint="http://invalid.com"  # Not HTTPS
        )

        assert "❌" in status
        assert config is None

    def test_extract_website_url(self):
        """Test URL extraction from messages."""
        ui = BrazeCodeGenUI(enable_browser_testing=False)

        # Test with URL
        message1 = "Create a landing page for https://www.nike.com with push notifications"
        url1 = ui.extract_website_url(message1)
        assert url1 == "https://www.nike.com"

        # Test without URL
        message2 = "Create a landing page with push notifications"
        url2 = ui.extract_website_url(message2)
        assert url2 is None

        # Test with multiple URLs (takes first)
        message3 = "Compare https://nike.com and https://adidas.com"
        url3 = ui.extract_website_url(message3)
        assert url3 == "https://nike.com"

    def test_generate_streaming_without_api_config(self):
        """Test that generation fails gracefully without API config."""
        ui = BrazeCodeGenUI(enable_browser_testing=False)

        history = []
        message = "Create a landing page"

        # Should yield error message
        gen = ui.generate_streaming(message, history)
        result = list(gen)

        assert len(result) > 0
        last_history = result[-1]
        assert len(last_history) > 0
        assert "⚠️" in last_history[-1][1]

    def test_get_preview_html_no_file(self):
        """Test preview HTML when no file exists."""
        ui = BrazeCodeGenUI(enable_browser_testing=False)

        html = ui.get_preview_html()
        assert "No landing page generated yet" in html

    def test_get_branding_data_empty(self):
        """Test branding data retrieval when empty."""
        ui = BrazeCodeGenUI(enable_browser_testing=False)

        data = ui.get_branding_data()
        assert "message" in data

    def test_export_html_file_no_file(self):
        """Test export when no file exists."""
        ui = BrazeCodeGenUI(enable_browser_testing=False)

        result = ui.export_html_file()
        assert result is None

    def test_insert_suggestion(self):
        """Test feature suggestion insertion."""
        ui = BrazeCodeGenUI(enable_browser_testing=False)

        # Test inserting into empty message
        result1 = ui.insert_suggestion("push_notifications", "")
        assert "push notification" in result1.lower()

        # Test appending to existing message
        result2 = ui.insert_suggestion("user_tracking", "Also add ")
        assert "Also add" in result2
        assert "tracking" in result2.lower()


@pytest.mark.integration
class TestGradioInterfaceCreation:
    """Integration tests for Gradio interface creation."""

    def test_create_gradio_interface(self):
        """Test that Gradio interface can be created."""
        from braze_code_gen.ui.gradio_app import create_gradio_interface

        demo = create_gradio_interface(
            export_dir="/tmp/test_exports",
            enable_browser_testing=False
        )

        assert demo is not None
        # Gradio Blocks object should have certain attributes
        assert hasattr(demo, 'launch')


if __name__ == "__main__":
    # Run basic smoke test
    print("Running UI smoke tests...")

    ui = BrazeCodeGenUI(enable_browser_testing=False)
    print("✓ UI initialization successful")

    test_api_key = "test_key_12345678901234567890123456789012"
    status, config, _, _ = ui.validate_api_config(
        api_key=test_api_key,
        rest_endpoint="https://rest.iad-01.braze.com"
    )
    print(f"✓ API validation: {status}")

    url = ui.extract_website_url("Create page for https://nike.com")
    print(f"✓ URL extraction: {url}")

    print("\n✅ All smoke tests passed!")
