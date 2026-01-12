"""Pydantic models for the Braze Code Generator.

This module defines type-safe data models used throughout the workflow.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, HttpUrl, Field


# ============================================================================
# LLM Configuration
# ============================================================================

class ModelProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class ModelTier(str, Enum):
    """Model usage tiers."""
    PRIMARY = "primary"        # High-quality code generation
    RESEARCH = "research"      # Documentation search, lightweight
    VALIDATION = "validation"  # Code validation, lightweight


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    provider: ModelProvider = Field(
        default=ModelProvider.OPENAI,
        description="LLM provider to use"
    )

    # Provider-specific API keys
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key"
    )
    google_api_key: Optional[str] = Field(
        default=None,
        description="Google API key"
    )

    # Model mappings per provider
    model_mappings: Dict[str, Dict[str, str]] = Field(
        default_factory=lambda: {
            "openai": {
                "primary": "gpt-4o",
                "research": "gpt-4o-mini",
                "validation": "gpt-4o-mini"
            },
            "anthropic": {
                "primary": "claude-opus-4-5-20251101",
                "research": "claude-sonnet-4-5-20250929",
                "validation": "claude-sonnet-4-5-20250929"
            },
            "google": {
                "primary": "gemini-2.0-flash-exp",
                "research": "gemini-2.0-flash-exp",
                "validation": "gemini-2.0-flash-exp"
            }
        },
        description="Model name mappings for each provider and tier"
    )

    def validate_api_key(self) -> bool:
        """Validate that appropriate API key is set for the current provider."""
        if self.provider == ModelProvider.OPENAI:
            return bool(self.openai_api_key)
        elif self.provider == ModelProvider.ANTHROPIC:
            return bool(self.anthropic_api_key)
        elif self.provider == ModelProvider.GOOGLE:
            return bool(self.google_api_key)
        return False

    def get_model_name(self, tier: ModelTier) -> str:
        """Get model name for given tier and current provider."""
        return self.model_mappings[self.provider.value][tier.value]

    class Config:
        json_schema_extra = {
            "example": {
                "provider": "openai",
                "openai_api_key": "sk-...",
                "model_mappings": {
                    "openai": {
                        "primary": "gpt-4o",
                        "research": "gpt-4o-mini",
                        "validation": "gpt-4o-mini"
                    }
                }
            }
        }


# ============================================================================
# Branding Data Models
# ============================================================================

class ColorScheme(BaseModel):
    """Color palette extracted from customer website."""

    primary: str = Field(
        description="Primary brand color (hex)",
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )
    secondary: str = Field(
        description="Secondary color (hex)",
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )
    accent: str = Field(
        description="Accent color for CTAs (hex)",
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )
    background: str = Field(
        description="Background color (hex)",
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )
    text: str = Field(
        description="Text color (hex)",
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "primary": "#3accdd",
                "secondary": "#2196F3",
                "accent": "#f64060",
                "background": "#ffffff",
                "text": "#333333"
            }
        }


class TypographyData(BaseModel):
    """Typography settings extracted from customer website."""

    primary_font: str = Field(
        description="Primary font family",
        examples=["'Inter', sans-serif", "'Roboto', sans-serif"]
    )
    heading_font: str = Field(
        description="Heading font family",
        examples=["'Poppins', sans-serif", "'Montserrat', sans-serif"]
    )
    base_size: str = Field(
        default="16px",
        description="Base font size"
    )
    heading_scale: List[str] = Field(
        default=["32px", "28px", "24px", "20px", "18px", "16px"],
        description="H1-H6 font sizes"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "primary_font": "'Inter', sans-serif",
                "heading_font": "'Poppins', sans-serif",
                "base_size": "16px",
                "heading_scale": ["32px", "28px", "24px", "20px", "18px", "16px"]
            }
        }


class BrandingData(BaseModel):
    """Complete branding information extracted from customer website."""

    website_url: HttpUrl = Field(
        description="Customer website URL"
    )
    colors: ColorScheme = Field(
        description="Color palette"
    )
    typography: TypographyData = Field(
        description="Typography settings"
    )
    extraction_success: bool = Field(
        description="Whether extraction was successful"
    )
    fallback_used: bool = Field(
        default=False,
        description="Whether default Braze branding was used as fallback"
    )
    extraction_notes: Optional[str] = Field(
        default=None,
        description="Notes about extraction process or issues"
    )


# ============================================================================
# Braze API Configuration
# ============================================================================

class BrazeAPIConfig(BaseModel):
    """Braze API configuration for SDK initialization."""

    api_key: str = Field(
        description="Braze API key (UUID format)",
        min_length=32
    )
    sdk_endpoint: str = Field(
        description="Braze SDK endpoint for Web SDK initialization (e.g., 'sdk.iad-01.braze.com')"
    )
    validated: bool = Field(
        default=False,
        description="Whether configuration has been validated"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "api_key": "18f10b29-2070-4638-bf4a-833207ce841a",
                "sdk_endpoint": "sdk.iad-01.braze.com",
                "validated": True
            }
        }


# ============================================================================
# SDK Feature Planning
# ============================================================================

class SDKFeature(BaseModel):
    """A specific Braze SDK feature to implement."""

    name: str = Field(
        description="Feature name"
    )
    description: str = Field(
        description="Feature description"
    )
    sdk_methods: List[str] = Field(
        default_factory=list,
        description="Braze SDK methods to use"
    )
    implementation_notes: Optional[str] = Field(
        default=None,
        description="Implementation guidance"
    )
    priority: int = Field(
        default=1,
        ge=1,
        le=3,
        description="Priority: 1=high, 2=medium, 3=low"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Push Notification Subscription",
                "description": "Allow users to opt-in to push notifications",
                "sdk_methods": ["braze.requestPushPermission()", "braze.subscribeUser()"],
                "implementation_notes": "Show modal on page load, store preference",
                "priority": 1
            }
        }


class SDKFeaturePlan(BaseModel):
    """Complete feature plan for the landing page."""

    features: List[SDKFeature] = Field(
        description="List of features to implement"
    )
    page_title: str = Field(
        description="Landing page title"
    )
    page_description: str = Field(
        description="Landing page description"
    )
    branding_constraints: Optional[str] = Field(
        default=None,
        description="Branding constraints from extracted data"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "features": [
                    {
                        "name": "User Tracking",
                        "description": "Track user interactions",
                        "sdk_methods": ["braze.logCustomEvent()"],
                        "priority": 1
                    }
                ],
                "page_title": "Braze SDK Demo - Nike",
                "page_description": "Interactive demo showcasing Braze SDK capabilities",
                "branding_constraints": "Use Nike colors: #111, #fff, #ff6b35"
            }
        }


# ============================================================================
# Code Generation
# ============================================================================

class GeneratedCode(BaseModel):
    """Generated HTML/CSS/JS code."""

    html: str = Field(
        description="Complete HTML code"
    )
    inline_css: str = Field(
        default="",
        description="Inline CSS (if any)"
    )
    inline_js: str = Field(
        default="",
        description="Inline JavaScript (if any)"
    )
    braze_sdk_initialized: bool = Field(
        default=False,
        description="Whether Braze SDK is properly initialized"
    )
    features_implemented: List[str] = Field(
        default_factory=list,
        description="List of implemented feature names"
    )


# ============================================================================
# Validation & Testing
# ============================================================================

class ValidationIssue(BaseModel):
    """A single validation issue found during testing."""

    severity: str = Field(
        description="Issue severity",
        pattern=r"^(error|warning|info)$"
    )
    category: str = Field(
        description="Issue category",
        examples=["html", "css", "javascript", "braze_sdk", "accessibility"]
    )
    message: str = Field(
        description="Issue description"
    )
    line_number: Optional[int] = Field(
        default=None,
        description="Line number where issue occurs"
    )
    fix_suggestion: Optional[str] = Field(
        default=None,
        description="Suggested fix"
    )


class ValidationReport(BaseModel):
    """Complete validation report from browser testing."""

    passed: bool = Field(
        description="Whether validation passed"
    )
    issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="List of validation issues"
    )
    braze_sdk_loaded: bool = Field(
        description="Whether Braze SDK loaded successfully"
    )
    console_errors: List[str] = Field(
        default_factory=list,
        description="JavaScript console errors"
    )
    screenshots: List[str] = Field(
        default_factory=list,
        description="Paths to screenshot files"
    )
    test_timestamp: Optional[str] = Field(
        default=None,
        description="When validation was performed"
    )


# ============================================================================
# Research & Documentation
# ============================================================================

class BrazeDocumentation(BaseModel):
    """Braze documentation retrieved from MCP server."""

    page_title: str = Field(
        description="Documentation page title"
    )
    page_url: str = Field(
        description="Documentation page URL"
    )
    content: str = Field(
        description="Page content"
    )
    code_examples: List[str] = Field(
        default_factory=list,
        description="Code examples from page"
    )
    relevance_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Relevance to user query (0-1)"
    )


class ResearchResult(BaseModel):
    """Research results from Braze documentation."""

    query: str = Field(
        description="Research query"
    )
    documentation_pages: List[BrazeDocumentation] = Field(
        description="Retrieved documentation pages"
    )
    summary: Optional[str] = Field(
        default=None,
        description="Summary of research findings"
    )
    implementation_guidance: Optional[str] = Field(
        default=None,
        description="Implementation guidance from docs"
    )


# ============================================================================
# Export Metadata
# ============================================================================

class ExportMetadata(BaseModel):
    """Metadata for exported landing page."""

    export_timestamp: str = Field(
        description="When page was exported"
    )
    customer_website: str = Field(
        description="Customer website URL"
    )
    features: List[str] = Field(
        description="Implemented features"
    )
    colors: ColorScheme = Field(
        description="Applied color scheme"
    )
    fonts: str = Field(
        description="Applied fonts"
    )
    generator_version: str = Field(
        default="1.0.0",
        description="Generator version"
    )


# ============================================================================
# Default Values
# ============================================================================

# Default Braze branding (fallback when website analysis fails)
DEFAULT_BRAZE_COLORS = ColorScheme(
    primary="#3accdd",    # Braze teal
    secondary="#2196F3",  # Blue
    accent="#f64060",     # Braze coral
    background="#ffffff",
    text="#333333"
)

DEFAULT_BRAZE_TYPOGRAPHY = TypographyData(
    primary_font="'Inter', sans-serif",
    heading_font="'Poppins', sans-serif",
    base_size="16px",
    heading_scale=["32px", "28px", "24px", "20px", "18px", "16px"]
)
