"""SDK feature suggestions for quick access in Gradio UI.

This module provides predefined feature templates that users can click
to quickly generate common Braze SDK landing pages.
"""

from typing import List, Dict

# Feature suggestion templates
FEATURE_SUGGESTIONS = [
    {
        "id": "push_notifications",
        "label": "Push Notifications",
        "description": "Web push notification subscription",
        "prompt": "Create a landing page with push notification subscription. Include a button to request push permission and show subscription status.",
        "features": ["requestPushPermission()", "subscribeUser()"],
        "icon": "🔔"
    },
    {
        "id": "user_tracking",
        "label": "User Tracking",
        "description": "Track user events and attributes",
        "prompt": "Create a landing page with user tracking features. Include event logging and custom user attributes.",
        "features": ["logCustomEvent()", "setCustomUserAttribute()"],
        "icon": "📊"
    },
    {
        "id": "in_app_messages",
        "label": "In-App Messages",
        "description": "Display in-app messages",
        "prompt": "Create a landing page that displays in-app messages from Braze. Include message triggers and display controls.",
        "features": ["subscribeToInAppMessage()", "display()"],
        "icon": "💬"
    },
    {
        "id": "content_cards",
        "label": "Content Cards",
        "description": "Display content cards feed",
        "prompt": "Create a landing page with a content cards feed. Include card display, click tracking, and dismissal.",
        "features": ["subscribeToContentCardsUpdates()", "logContentCardClick()"],
        "icon": "🗂️"
    },
    {
        "id": "user_identification",
        "label": "User Identification",
        "description": "Identify and manage users",
        "prompt": "Create a landing page with user identification. Include forms to change user ID and set user properties like name and email.",
        "features": ["changeUser()", "setEmail()", "setFirstName()", "setLastName()"],
        "icon": "👤"
    },
    {
        "id": "email_subscription",
        "label": "Email Subscription",
        "description": "Manage email preferences",
        "prompt": "Create a landing page for email subscription management. Include email capture, subscription preferences, and opt-in/opt-out controls.",
        "features": ["setEmail()", "addAlias()", "setEmailNotificationSubscriptionType()"],
        "icon": "📧"
    },
    {
        "id": "user_properties",
        "label": "User Properties",
        "description": "Set comprehensive user attributes",
        "prompt": "Create a landing page to collect user properties. Include forms for demographics (age, gender, location) and custom attributes.",
        "features": ["setGender()", "setDateOfBirth()", "setCountry()", "setCity()"],
        "icon": "📝"
    },
    {
        "id": "full_demo",
        "label": "Full SDK Demo",
        "description": "Comprehensive SDK showcase",
        "prompt": "Create a comprehensive landing page showcasing all major Braze SDK features: push notifications, user tracking, in-app messages, content cards, and user identification.",
        "features": ["All major SDK methods"],
        "icon": "🎯"
    }
]


def get_feature_suggestions() -> List[Dict]:
    """Get all feature suggestions.

    Returns:
        List[Dict]: List of feature suggestion dictionaries
    """
    return FEATURE_SUGGESTIONS


def get_suggestion_by_id(suggestion_id: str) -> Dict:
    """Get a specific feature suggestion by ID.

    Args:
        suggestion_id: Suggestion ID (e.g., "push_notifications")

    Returns:
        Dict: Feature suggestion or empty dict if not found
    """
    for suggestion in FEATURE_SUGGESTIONS:
        if suggestion["id"] == suggestion_id:
            return suggestion
    return {}


def get_suggestion_prompt(suggestion_id: str) -> str:
    """Get the prompt text for a feature suggestion.

    Args:
        suggestion_id: Suggestion ID

    Returns:
        str: Prompt text or empty string if not found
    """
    suggestion = get_suggestion_by_id(suggestion_id)
    return suggestion.get("prompt", "")


def format_suggestion_label(suggestion: Dict) -> str:
    """Format suggestion label with icon.

    Args:
        suggestion: Suggestion dictionary

    Returns:
        str: Formatted label (e.g., "🔔 Push Notifications")
    """
    icon = suggestion.get("icon", "")
    label = suggestion.get("label", "")
    return f"{icon} {label}" if icon else label
