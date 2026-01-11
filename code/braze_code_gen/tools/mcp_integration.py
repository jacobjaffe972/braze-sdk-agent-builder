"""MCP integration for Braze documentation access.

This module wraps the Braze Docs MCP server and provides LangChain tool interfaces.
"""

import json
import logging
import subprocess
from typing import List, Optional, Annotated

from langchain_core.tools import tool

from braze_code_gen.core.models import BrazeDocumentation

logger = logging.getLogger(__name__)


class BrazeDocsMCP:
    """Wrapper for Braze Documentation MCP server."""

    def __init__(
        self,
        server_path: str = "/Users/Jacob.Jaffe/code-gen-agent/braze-docs-mcp",
        cache_file: str = "braze_docs_cache.json"
    ):
        """Initialize Braze Docs MCP wrapper.

        Args:
            server_path: Path to MCP server directory
            cache_file: Name of cache file
        """
        self.server_path = server_path
        self.cache_file = f"{server_path}/{cache_file}"
        self.docs_cache = self._load_cache()
        logger.info(f"Loaded {len(self.docs_cache)} Braze documentation pages")

    def _load_cache(self) -> dict:
        """Load documentation cache from JSON file.

        Returns:
            dict: Documentation cache
        """
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Cache file not found: {self.cache_file}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing cache file: {e}")
            return {}

    def search_documentation(
        self,
        query: str,
        max_results: int = 5
    ) -> List[BrazeDocumentation]:
        """Search Braze documentation for relevant pages.

        Args:
            query: Search query
            max_results: Maximum number of results

        Returns:
            List[BrazeDocumentation]: Relevant documentation pages

        Example:
            >>> mcp = BrazeDocsMCP()
            >>> results = mcp.search_documentation("Web SDK initialization")
            >>> for doc in results:
            ...     print(doc.page_title)
        """
        query_lower = query.lower()
        results = []

        for page_path, page_data in self.docs_cache.items():
            title = page_data.get('title', '').lower()
            content = page_data.get('content', '').lower()

            # Calculate relevance score
            relevance = 0.0
            if query_lower in title:
                relevance += 0.5
            if query_lower in content:
                relevance += 0.3
            # Boost by occurrence count
            relevance += min(content.count(query_lower) * 0.1, 0.2)

            if relevance > 0:
                doc = BrazeDocumentation(
                    page_title=page_data.get('title', ''),
                    page_url=page_data.get('url', ''),
                    content=page_data.get('content', '')[:3000],  # Limit content
                    code_examples=page_data.get('code_examples', [])[:5],
                    relevance_score=min(relevance, 1.0)
                )
                results.append((relevance, doc))

        # Sort by relevance and return top results
        results.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in results[:max_results]]

    def get_page(self, page_path: str) -> Optional[BrazeDocumentation]:
        """Get specific documentation page by path.

        Args:
            page_path: Page path (e.g., "developer_guide/platform_integration_guides/web/initial_sdk_setup")

        Returns:
            Optional[BrazeDocumentation]: Documentation page or None
        """
        # Try exact match
        page_data = self.docs_cache.get(page_path)

        # Try with/without trailing slash
        if not page_data:
            page_data = self.docs_cache.get(page_path.rstrip('/'))
        if not page_data:
            page_data = self.docs_cache.get(page_path + '/')

        if not page_data:
            logger.warning(f"Page not found: {page_path}")
            return None

        return BrazeDocumentation(
            page_title=page_data.get('title', ''),
            page_url=page_data.get('url', ''),
            content=page_data.get('content', ''),
            code_examples=page_data.get('code_examples', []),
            relevance_score=1.0
        )

    def list_pages(self, limit: int = 50) -> List[str]:
        """List available documentation pages.

        Args:
            limit: Maximum number of pages to return

        Returns:
            List[str]: List of page paths
        """
        return list(self.docs_cache.keys())[:limit]

    def get_code_examples(self, topic: str) -> List[str]:
        """Get code examples related to a topic.

        Args:
            topic: Topic to search for

        Returns:
            List[str]: Code examples
        """
        docs = self.search_documentation(topic, max_results=3)
        examples = []
        for doc in docs:
            examples.extend(doc.code_examples)
        return examples[:10]  # Return up to 10 examples


# ============================================================================
# LangChain Tool Wrappers
# ============================================================================

# Global MCP instance (initialized on first use)
_mcp_instance: Optional[BrazeDocsMCP] = None


def get_mcp_instance() -> BrazeDocsMCP:
    """Get or create global MCP instance.

    Returns:
        BrazeDocsMCP: MCP instance
    """
    global _mcp_instance
    if _mcp_instance is None:
        _mcp_instance = BrazeDocsMCP()
    return _mcp_instance


@tool
def search_braze_docs(
    query: Annotated[str, "Search query for Braze documentation"]
) -> str:
    """Search Braze documentation for relevant information.

    Use this tool to find Braze SDK documentation, API references,
    integration guides, and code examples.

    Examples:
    - "Web SDK initialization"
    - "track custom events JavaScript"
    - "user attributes API"
    - "push notifications Web SDK"

    Args:
        query: What to search for in Braze docs

    Returns:
        str: Relevant documentation pages and code examples
    """
    mcp = get_mcp_instance()
    results = mcp.search_documentation(query, max_results=3)

    if not results:
        return f"No Braze documentation found for query: '{query}'"

    # Format results
    output = [f"Found {len(results)} relevant Braze documentation pages:\n"]

    for i, doc in enumerate(results, 1):
        output.append(f"\n## {i}. {doc.page_title}")
        output.append(f"**URL**: {doc.page_url}")
        output.append(f"**Relevance**: {doc.relevance_score:.2f}\n")

        # Add content snippet
        content_preview = doc.content[:500] + "..." if len(doc.content) > 500 else doc.content
        output.append(f"**Content**:\n{content_preview}\n")

        # Add code examples
        if doc.code_examples:
            output.append(f"**Code Examples** ({len(doc.code_examples)} found):")
            for j, example in enumerate(doc.code_examples[:2], 1):
                output.append(f"\n### Example {j}:")
                output.append(f"```javascript\n{example}\n```")

    return "\n".join(output)


@tool
def get_braze_code_examples(
    topic: Annotated[str, "Topic to get code examples for"]
) -> str:
    """Get Braze SDK code examples for a specific topic.

    Use this tool when you need specific code examples for implementing
    Braze SDK features.

    Examples:
    - "initialize Web SDK"
    - "log custom event"
    - "set user attributes"
    - "request push permission"

    Args:
        topic: Topic to get code examples for

    Returns:
        str: Code examples from Braze documentation
    """
    mcp = get_mcp_instance()
    examples = mcp.get_code_examples(topic)

    if not examples:
        return f"No code examples found for topic: '{topic}'"

    output = [f"Found {len(examples)} code examples for '{topic}':\n"]

    for i, example in enumerate(examples, 1):
        output.append(f"\n### Example {i}:")
        output.append(f"```javascript\n{example}\n```\n")

    return "\n".join(output)


@tool
def list_braze_doc_pages() -> str:
    """List available Braze documentation pages.

    Use this tool to see what documentation is available in the cache.

    Returns:
        str: List of available documentation pages
    """
    mcp = get_mcp_instance()
    pages = mcp.list_pages(limit=30)

    if not pages:
        return "No documentation pages available"

    output = [f"Available Braze documentation pages ({len(pages)} shown):\n"]
    for i, page in enumerate(pages, 1):
        output.append(f"{i}. {page}")

    return "\n".join(output)


# Export tools for agent use
BRAZE_DOCS_TOOLS = [
    search_braze_docs,
    get_braze_code_examples,
    list_braze_doc_pages,
]
