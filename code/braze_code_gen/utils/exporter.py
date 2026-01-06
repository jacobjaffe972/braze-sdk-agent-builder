"""HTML export system for generated landing pages.

This module handles exporting generated landing pages to HTML files with metadata.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from braze_code_gen.core.models import (
    BrandingData,
    SDKFeaturePlan,
    ExportMetadata,
)

logger = logging.getLogger(__name__)


class HTMLExporter:
    """Exporter for landing page HTML files."""

    def __init__(self, export_dir: str = "/tmp/braze_exports"):
        """Initialize the HTML exporter.

        Args:
            export_dir: Directory for exported files
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"HTML exporter initialized: {self.export_dir}")

    def export_landing_page(
        self,
        html_content: str,
        branding_data: BrandingData,
        feature_plan: SDKFeaturePlan,
        generator_version: str = "1.0.0"
    ) -> Path:
        """Export landing page to HTML file with metadata.

        Args:
            html_content: Complete HTML content
            branding_data: Branding data used
            feature_plan: Feature plan implemented
            generator_version: Version of code generator

        Returns:
            Path: Path to exported HTML file

        Example:
            >>> exporter = HTMLExporter()
            >>> path = exporter.export_landing_page(
            ...     html_content="<html>...</html>",
            ...     branding_data=branding_data,
            ...     feature_plan=feature_plan
            ... )
            >>> print(path)
            /tmp/braze_exports/braze_landing_nike_20260106_143022.html
        """
        # Generate filename
        filename = self._generate_filename(branding_data.website_url)
        filepath = self.export_dir / filename

        # Create metadata
        metadata = self._create_metadata(
            branding_data,
            feature_plan,
            generator_version
        )

        # Add metadata comment to HTML
        html_with_metadata = self._add_metadata_comment(html_content, metadata)

        # Write HTML file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_with_metadata)

        logger.info(f"Exported landing page to: {filepath}")

        # Write metadata sidecar JSON
        self._write_metadata_sidecar(filepath, metadata)

        return filepath

    def _generate_filename(self, website_url: str) -> str:
        """Generate filename from website URL and timestamp.

        Args:
            website_url: Customer website URL

        Returns:
            str: Generated filename

        Example:
            >>> exporter._generate_filename("https://nike.com")
            'braze_landing_nike_20260106_143022.html'
        """
        # Extract domain from URL
        from urllib.parse import urlparse
        parsed = urlparse(str(website_url))
        domain = parsed.netloc or parsed.path
        domain = domain.replace('www.', '').replace('.com', '').replace('.', '_')

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return f"braze_landing_{domain}_{timestamp}.html"

    def _create_metadata(
        self,
        branding_data: BrandingData,
        feature_plan: SDKFeaturePlan,
        generator_version: str
    ) -> ExportMetadata:
        """Create export metadata.

        Args:
            branding_data: Branding data
            feature_plan: Feature plan
            generator_version: Generator version

        Returns:
            ExportMetadata: Metadata object
        """
        return ExportMetadata(
            export_timestamp=datetime.now().isoformat(),
            customer_website=str(branding_data.website_url),
            features=[f.name for f in feature_plan.features],
            colors=branding_data.colors,
            fonts=branding_data.typography.primary_font,
            generator_version=generator_version
        )

    def _add_metadata_comment(
        self,
        html_content: str,
        metadata: ExportMetadata
    ) -> str:
        """Add metadata comment to HTML.

        Args:
            html_content: Original HTML
            metadata: Metadata to add

        Returns:
            str: HTML with metadata comment

        Example:
            <!--
            Braze SDK Landing Page
            Generated: 2026-01-06T14:30:22
            Customer Website: https://nike.com
            Features: Push Notifications, User Tracking
            Colors: Primary=#111, Accent=#ff6b35
            Fonts: 'Helvetica Neue', sans-serif
            Generator: v1.0.0
            -->
        """
        comment = f"""<!--
Braze SDK Landing Page
Generated: {metadata.export_timestamp}
Customer Website: {metadata.customer_website}
Features: {', '.join(metadata.features)}
Colors: Primary={metadata.colors.primary}, Accent={metadata.colors.accent}
Fonts: {metadata.fonts}
Generator: v{metadata.generator_version}
-->
"""
        # Insert after <!DOCTYPE html> or at the beginning
        if '<!DOCTYPE html>' in html_content or '<!doctype html>' in html_content:
            # Insert after doctype
            import re
            html_content = re.sub(
                r'(<!DOCTYPE html>)',
                r'\1\n' + comment,
                html_content,
                flags=re.IGNORECASE
            )
        else:
            # Insert at beginning
            html_content = comment + '\n' + html_content

        return html_content

    def _write_metadata_sidecar(self, html_filepath: Path, metadata: ExportMetadata):
        """Write metadata as JSON sidecar file.

        Args:
            html_filepath: Path to HTML file
            metadata: Metadata to write

        Creates a file like: braze_landing_nike_20260106.html.meta.json
        """
        meta_filepath = html_filepath.with_suffix('.html.meta.json')

        with open(meta_filepath, 'w', encoding='utf-8') as f:
            json.dump(metadata.model_dump(), f, indent=2)

        logger.debug(f"Wrote metadata sidecar: {meta_filepath}")

    def get_export_path(self, filename: str) -> Path:
        """Get full path for exported file.

        Args:
            filename: Filename

        Returns:
            Path: Full path
        """
        return self.export_dir / filename

    def list_exports(self) -> list[Path]:
        """List all exported HTML files.

        Returns:
            list[Path]: List of exported file paths
        """
        return sorted(
            self.export_dir.glob("braze_landing_*.html"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

    def cleanup_old_exports(self, keep_count: int = 10):
        """Remove old exports, keeping only most recent N files.

        Args:
            keep_count: Number of recent exports to keep
        """
        exports = self.list_exports()

        if len(exports) > keep_count:
            for old_export in exports[keep_count:]:
                old_export.unlink()
                # Also remove metadata sidecar
                meta_file = old_export.with_suffix('.html.meta.json')
                if meta_file.exists():
                    meta_file.unlink()

                logger.info(f"Removed old export: {old_export.name}")
