"""
Header Component - Professional and Aesthetic Header for Engagement Prediction App

This module provides a unified, formal header component that can be used across all pages.
Features:
- Corporate gradient design
- Animated subtle effects
- Responsive layout
- Consistent branding with TEC and Globant logos

Author: ITESM
Date: 2025-11-24
"""

import streamlit as st
import base64
from pathlib import Path
from datetime import datetime


def get_img_base64(path: str) -> str:
    """Convert image to base64 string for embedding in HTML."""
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""


def get_global_css() -> str:
    """Return the global CSS styles for the application."""
    return """
    <style>
        /* ============================================
           GLOBAL RESET & BASE STYLES
           ============================================ */

        .block-container {
            padding-top: 0 !important;
        }

        /* Hide default Streamlit header */
        header[data-testid="stHeader"] {
            background: transparent;
        }

        /* ============================================
           PROFESSIONAL HEADER STYLES
           ============================================ */

        .professional-header {
            background: #ffffff !important;
            padding: 2rem 3rem;
            margin: -1rem -1rem 2rem -1rem;
            border-bottom: 3px solid #2E86AB;
            position: relative;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
        }

        .header-content {
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1.5rem;
        }

        .header-title-section {
            flex: 1;
            min-width: 300px;
        }

        .header-title {
            color: #1a1f2e;
            font-size: 2.2rem;
            font-weight: 600;
            margin: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            letter-spacing: 0.5px;
            line-height: 1.2;
        }

        .header-subtitle {
            color: #2E86AB;
            font-size: 1rem;
            font-weight: 500;
            margin: 0.5rem 0 0 0;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        .header-divider {
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, #2E86AB, #1a5f7a);
            margin: 1rem 0;
            border-radius: 2px;
        }

        .header-description {
            color: #5a6270;
            font-size: 0.95rem;
            margin: 0;
            max-width: 600px;
            line-height: 1.5;
        }

        .header-meta {
            display: flex;
            align-items: center;
            gap: 1.5rem;
            flex-wrap: wrap;
        }

        .header-badge {
            background: rgba(46, 134, 171, 0.1);
            border: 1px solid rgba(46, 134, 171, 0.3);
            padding: 0.4rem 1rem;
            border-radius: 20px;
            color: #2E86AB;
            font-size: 0.8rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        /* ============================================
           SIDEBAR STYLES
           ============================================ */

        [data-testid="stSidebarNav"] {
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 1rem;
            margin-bottom: 1rem;
        }

        .sidebar-logos {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            padding: 0.5rem 0;
        }

        .sidebar-logos img {
            height: 45px;
            width: auto;
            transition: transform 0.3s ease;
        }

        .sidebar-logos img:hover {
            transform: scale(1.05);
        }

        .sidebar-logos .divider {
            color: #ccc;
            font-size: 1.8rem;
            font-weight: 200;
        }

        /* ============================================
           SECTION STYLES
           ============================================ */

        .sub-header {
            font-size: 1.4rem;
            font-weight: 600;
            color: #1a1f2e;
            margin-top: 2rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #2E86AB;
            display: inline-block;
        }

        .section-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2d3548;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
        }

        /* ============================================
           CARD STYLES
           ============================================ */

        .metric-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            padding: 1.25rem;
            border-radius: 8px;
            border-left: 4px solid #2E86AB;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .feature-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #2E86AB;
            margin: 0.5rem 0;
            height: 100%;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .feature-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .feature-card h4 {
            color: #1a1f2e;
            margin: 0 0 0.5rem 0;
            font-size: 1.1rem;
            font-weight: 600;
        }

        .feature-card p {
            color: #5a6270;
            margin: 0;
            font-size: 0.95rem;
            line-height: 1.5;
        }

        .info-box {
            background: linear-gradient(135deg, #f0f4f8 0%, #e8eef4 100%);
            padding: 1.25rem;
            border-radius: 8px;
            border-left: 4px solid #2E86AB;
            margin: 1rem 0;
        }

        .step-box {
            background: linear-gradient(135deg, #f8f9fa 0%, #f0f2f5 100%);
            padding: 1.25rem;
            border-radius: 8px;
            border-left: 4px solid #2E86AB;
            margin: 0.5rem 0;
        }

        .action-card {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            margin: 0.5rem 0;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .action-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .action-card h4 {
            color: #1a1f2e;
            margin: 0.5rem 0;
            font-size: 1rem;
            font-weight: 600;
        }

        .action-card p {
            color: #666;
            font-size: 0.85rem;
            margin: 0;
        }

        /* ============================================
           QUALITY INDICATORS
           ============================================ */

        .quality-good {
            color: #06A77D;
            font-weight: 600;
        }

        .quality-warning {
            color: #F77F00;
            font-weight: 600;
        }

        .quality-error {
            color: #D62828;
            font-weight: 600;
        }

        /* ============================================
           RESPONSIVE ADJUSTMENTS
           ============================================ */

        @media (max-width: 768px) {
            .professional-header {
                padding: 1.5rem;
            }

            .header-title {
                font-size: 1.6rem;
            }

            .header-content {
                flex-direction: column;
                align-items: flex-start;
            }

            .header-meta {
                width: 100%;
            }
        }
    </style>
    """


def render_sidebar_logos():
    """Render the TEC and Globant logos in the sidebar."""
    try:
        # Get the path relative to app directory
        app_dir = Path(__file__).parent.parent
        tec_path = app_dir / "public" / "img" / "tec.png"
        globant_path = app_dir / "public" / "img" / "globant.png"

        # Try alternative path if first doesn't work
        if not tec_path.exists():
            tec_path = Path("public/img/tec.png")
            globant_path = Path("public/img/globant.png")

        tec_b64 = get_img_base64(str(tec_path))
        globant_b64 = get_img_base64(str(globant_path))

        if tec_b64 and globant_b64:
            st.markdown(f"""
            <div class="sidebar-logos">
                <img src="data:image/png;base64,{tec_b64}" alt="TEC Logo">
                <span class="divider">|</span>
                <img src="data:image/png;base64,{globant_b64}" alt="Globant Logo">
            </div>
            """, unsafe_allow_html=True)
            st.markdown("---")
    except Exception:
        pass


def render_header(
    title: str,
    subtitle: str,
    description: str = "",
    show_date: bool = True
):
    """
    Render a professional header for the page.

    Args:
        title: Main title of the page
        subtitle: Subtitle/section identifier
        description: Optional description text
        show_date: Whether to show current date badge
    """
    # Apply global CSS
    st.markdown(get_global_css(), unsafe_allow_html=True)

    # Build the header HTML
    current_date = datetime.now().strftime("%d %b %Y")
    date_badge = f'<div class="header-badge"><span>{current_date}</span></div>' if show_date else ""
    description_html = f'<p class="header-description">{description}</p>' if description else ""

    header_html = f'''<div class="professional-header"><div class="header-content"><div class="header-title-section"><h1 class="header-title">{title}</h1><p class="header-subtitle">{subtitle}</p><div class="header-divider"></div>{description_html}</div><div class="header-meta">{date_badge}<div class="header-badge"><span>Markov Analysis</span></div></div></div></div>'''

    st.markdown(header_html, unsafe_allow_html=True)
