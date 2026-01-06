"""HTML template generator for Braze SDK landing pages.

This module provides base HTML templates with proper Braze SDK integration.
"""

from typing import Optional
from braze_code_gen.core.models import BrandingData, BrazeAPIConfig


def generate_base_template(
    branding: BrandingData,
    braze_config: BrazeAPIConfig,
    page_title: str = "Braze SDK Demo",
    page_description: str = "Interactive Braze SDK Demo Landing Page"
) -> str:
    """Generate base HTML template with Braze SDK integration.

    Args:
        branding: Branding data (colors, typography)
        braze_config: Braze API configuration
        page_title: Page title
        page_description: Page description

    Returns:
        str: Complete HTML template

    Example:
        >>> template = generate_base_template(branding, braze_config)
    """
    # Extract branding values
    primary_color = branding.colors.primary
    accent_color = branding.colors.accent
    background_color = branding.colors.background
    text_color = branding.colors.text
    primary_font = branding.typography.primary_font
    heading_font = branding.typography.heading_font

    # Braze configuration
    api_key = braze_config.api_key
    sdk_endpoint = str(braze_config.rest_endpoint).replace('https://', '')

    template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <meta name="description" content="{page_description}">

    <!-- Google Fonts -->
    {_generate_google_fonts_link(primary_font, heading_font)}

    <!-- Braze SDK -->
    <script src="https://js.appboycdn.com/web-sdk/4.9/braze.min.js"></script>

    <!-- Custom Styles -->
    <style>
        /* CSS Variables for easy theming */
        :root {{
            --primary-color: {primary_color};
            --accent-color: {accent_color};
            --background-color: {background_color};
            --text-color: {text_color};
            --font-primary: {primary_font};
            --font-heading: {heading_font};
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: var(--font-primary);
            color: var(--text-color);
            background-color: var(--background-color);
            line-height: 1.6;
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-family: var(--font-heading);
            color: var(--primary-color);
            margin-bottom: 1rem;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .btn {{
            display: inline-block;
            padding: 0.75rem 1.5rem;
            background-color: var(--accent-color);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            font-family: var(--font-primary);
            text-decoration: none;
            transition: opacity 0.3s ease;
        }}

        .btn:hover {{
            opacity: 0.9;
        }}

        .btn-secondary {{
            background-color: var(--primary-color);
        }}

        input, textarea {{
            width: 100%;
            padding: 0.75rem;
            margin-bottom: 1rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: var(--font-primary);
            font-size: 1rem;
        }}

        label {{
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
        }}

        .form-group {{
            margin-bottom: 1.5rem;
        }}

        .header {{
            text-align: center;
            padding: 3rem 2rem;
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            color: white;
        }}

        .header h1 {{
            color: white;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}

        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}

        .section {{
            padding: 3rem 0;
        }}

        .section-title {{
            font-size: 2rem;
            margin-bottom: 2rem;
            text-align: center;
        }}

        .card {{
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}

        /* Braze-specific styles */
        #braze-status {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 1rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            font-size: 0.9rem;
            max-width: 300px;
        }}

        .status-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }}

        .status-connected {{
            background-color: #4CAF50;
        }}

        .status-disconnected {{
            background-color: #f44336;
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <h1>{page_title}</h1>
        <p>{page_description}</p>
    </div>

    <!-- Main Content -->
    <div class="container">
        <div class="section">
            <h2 class="section-title">Braze SDK Features</h2>

            <!-- Content will be added by code generation agent -->
            <div id="features-container">
                <p style="text-align: center; color: #999;">Features will be added here...</p>
            </div>
        </div>
    </div>

    <!-- Braze Status Indicator -->
    <div id="braze-status">
        <div>
            <span class="status-indicator status-disconnected" id="status-dot"></span>
            <strong id="status-text">Initializing Braze SDK...</strong>
        </div>
        <div id="status-details" style="margin-top: 0.5rem; font-size: 0.85rem; color: #666;"></div>
    </div>

    <!-- Braze SDK Initialization -->
    <script>
        // Initialize Braze SDK
        (function() {{
            try {{
                // Initialize with your API key and SDK endpoint
                braze.initialize('{api_key}', {{
                    baseUrl: '{sdk_endpoint}',
                    enableLogging: true
                }});

                // Open session
                braze.openSession();

                // Update status
                updateBrazeStatus('connected', 'Braze SDK Connected', 'Session opened successfully');

                console.log('Braze SDK initialized successfully');
            }} catch (error) {{
                console.error('Error initializing Braze SDK:', error);
                updateBrazeStatus('disconnected', 'Braze SDK Error', error.message);
            }}
        }})();

        // Helper function to update status indicator
        function updateBrazeStatus(status, text, details) {{
            const dot = document.getElementById('status-dot');
            const statusText = document.getElementById('status-text');
            const statusDetails = document.getElementById('status-details');

            dot.className = 'status-indicator status-' + status;
            statusText.textContent = text;
            if (details) {{
                statusDetails.textContent = details;
            }}
        }}

        // Helper function to track custom event
        function trackBrazeEvent(eventName, properties) {{
            try {{
                braze.logCustomEvent(eventName, properties);
                console.log('Tracked event:', eventName, properties);
                return true;
            }} catch (error) {{
                console.error('Error tracking event:', error);
                return false;
            }}
        }}

        // Helper function to set user attribute
        function setBrazeUserAttribute(key, value) {{
            try {{
                braze.getUser().setCustomUserAttribute(key, value);
                console.log('Set user attribute:', key, value);
                return true;
            }} catch (error) {{
                console.error('Error setting user attribute:', error);
                return false;
            }}
        }}
    </script>
</body>
</html>'''

    return template


def _generate_google_fonts_link(primary_font: str, heading_font: str) -> str:
    """Generate Google Fonts link tag.

    Args:
        primary_font: Primary font family
        heading_font: Heading font family

    Returns:
        str: Google Fonts link tag or empty string
    """
    # Extract font names
    fonts = set()

    for font in [primary_font, heading_font]:
        # Remove quotes and fallbacks
        font_name = font.strip("'\"").split(',')[0].strip()
        # Skip generic families
        if font_name.lower() not in ['sans-serif', 'serif', 'monospace', 'cursive', 'fantasy']:
            fonts.add(font_name.replace(' ', '+'))

    if not fonts:
        return ""

    # Generate Google Fonts URL
    fonts_param = '|'.join(fonts)
    return f'<link href="https://fonts.googleapis.com/css2?family={fonts_param}&display=swap" rel="stylesheet">'


def generate_feature_section_html(
    feature_name: str,
    feature_description: str,
    feature_html: str
) -> str:
    """Generate HTML for a single feature section.

    Args:
        feature_name: Feature name
        feature_description: Feature description
        feature_html: Feature implementation HTML

    Returns:
        str: Feature section HTML

    Example:
        >>> section = generate_feature_section_html(
        ...     "Push Notifications",
        ...     "Request push notification permission",
        ...     "<button onclick='requestPush()'>Enable Push</button>"
        ... )
    """
    return f'''
    <div class="card">
        <h3>{feature_name}</h3>
        <p>{feature_description}</p>
        <div class="feature-content">
            {feature_html}
        </div>
    </div>
    '''


def wrap_feature_sections(feature_sections: list[str]) -> str:
    """Wrap multiple feature sections.

    Args:
        feature_sections: List of feature section HTML strings

    Returns:
        str: Combined feature sections
    """
    return '\n'.join(feature_sections)
