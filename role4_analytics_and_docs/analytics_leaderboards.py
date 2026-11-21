"""Game Analytics: Unlocking Tennis Data with SportRadar API.

Role 4: Analytics, Leaderboards & Visualization Engine
File: role4_analytics_and_docs/analytics_leaderboards.py

This module provides:
1. Analytical computation routines for competitor leaderboards, country aggregates, and KPIs.
2. Production-ready Plotly chart generators for Streamlit dashboards:
   - Country-wise competitor counts & aggregate points charts
   - Points distribution histograms
   - Competition category and type distribution sunburst / bar charts
3. Standalone CLI execution providing formatted summary reports for Role 4 team deliverables.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy.engine import Engine

# Ensure repository root is on sys.path
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name.startswith("role") else CURRENT_DIR

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from role3_sql_and_core_app.db_connection import execute_query, get_db_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("Analytics-Leaderboards")


def get_kpi_metrics() -> Dict[str, Any]:
    """Calculate key performance indicators (KPIs) across the tennis database.

    Returns:
        Dictionary containing counts and high-water mark metrics:
        - total_competitors
        - total_countries
        - highest_points
        - total_competitions
        - total_venues
        - total_complexes
    """
    kpis = {
        "total_competitors": 0,
        "total_countries": 0,
        "highest_points": 0,
        "total_competitions": 0,
        "total_venues": 0,
        "total_complexes": 0,
    }

    try:
        df_comp = execute_query("SELECT COUNT(DISTINCT competitor_id) AS cnt, COUNT(DISTINCT country) AS countries FROM competitors;")
        if not df_comp.empty:
            kpis["total_competitors"] = int(df_comp["cnt"].iloc[0] or 0)
            kpis["total_countries"] = int(df_comp["countries"].iloc[0] or 0)

        df_rank = execute_query("SELECT MAX(points) AS max_pts FROM competitor_rankings;")
        if not df_rank.empty:
            kpis["highest_points"] = int(df_rank["max_pts"].iloc[0] or 0)

        df_tourneys = execute_query("SELECT COUNT(*) AS total_comp FROM competitions;")
        if not df_tourneys.empty:
            kpis["total_competitions"] = int(df_tourneys["total_comp"].iloc[0] or 0)

        df_ven = execute_query("SELECT COUNT(*) AS total_ven FROM venues;")
        if not df_ven.empty:
            kpis["total_venues"] = int(df_ven["total_ven"].iloc[0] or 0)

        df_cplx = execute_query("SELECT COUNT(*) AS total_cplx FROM complexes;")
        if not df_cplx.empty:
            kpis["total_complexes"] = int(df_cplx["total_cplx"].iloc[0] or 0)

    except Exception as exc:
        logger.error("Error computing KPI metrics: %s", exc)

    return kpis


def get_competitor_directory(
    country: Optional[str] = None,
    min_rank: int = 1,
    max_rank: int = 100,
    min_points: int = 0,
    search_query: Optional[str] = None,
) -> pd.DataFrame:
    """Fetch competitor directory with ranking metrics and search/filter predicates.

    Args:
        country: Optional filter for player country.
        min_rank: Lower bound for ranking filter.
        max_rank: Upper bound for ranking filter.
        min_points: Minimum ranking points threshold.
        search_query: Substring filter for competitor name.

    Returns:
        Filtered pandas DataFrame sorted by rank ascending.
    """
    sql = """
        SELECT 
            r.`rank`,
            c.competitor_id,
            c.name AS competitor_name,
            c.country,
            c.country_code,
            c.abbreviation,
            r.points,
            r.movement,
            r.competitions_played
        FROM competitor_rankings r
        INNER JOIN competitors c ON r.competitor_id = c.competitor_id
        WHERE r.`rank` BETWEEN :min_rank AND :max_rank
          AND r.points >= :min_points
    """
    params: Dict[str, Any] = {
        "min_rank": min_rank,
        "max_rank": max_rank,
        "min_points": min_points,
    }

    if country and country != "All Countries":
        sql += " AND c.country = :country"
        params["country"] = country

    if search_query and search_query.strip():
        sql += " AND LOWER(c.name) LIKE :search"
        params["search"] = f"%{search_query.strip().lower()}%"

    sql += " ORDER BY r.`rank` ASC, r.points DESC;"

    return execute_query(sql, params)


def get_country_analytics() -> pd.DataFrame:
    """Aggregate competitors and points by country.

    Returns:
        DataFrame with country, competitor count, total points, avg points, and best rank.
    """
    sql = """
        SELECT 
            c.country,
            c.country_code,
            COUNT(c.competitor_id) AS total_competitors,
            SUM(r.points) AS total_points,
            ROUND(AVG(r.points), 1) AS average_points,
            MIN(r.`rank`) AS highest_rank
        FROM competitors c
        INNER JOIN competitor_rankings r ON c.competitor_id = r.competitor_id
        GROUP BY c.country, c.country_code
        ORDER BY total_competitors DESC, total_points DESC;
    """
    return execute_query(sql)


def get_competition_hierarchy() -> pd.DataFrame:
    """Fetch parent competitions and their associated sub-competitions."""
    sql = """
        SELECT 
            p.competition_name AS parent_competition,
            s.competition_name AS sub_competition,
            s.type AS sub_competition_type,
            s.gender AS sub_competition_gender,
            cat.category_name
        FROM competitions s
        INNER JOIN competitions p ON s.parent_id = p.competition_id
        INNER JOIN categories cat ON s.category_id = cat.category_id
        ORDER BY p.competition_name ASC, s.competition_name ASC;
    """
    return execute_query(sql)


def get_venues_by_complex() -> pd.DataFrame:
    """Fetch all venues with complex information."""
    sql = """
        SELECT 
            c.complex_name,
            v.venue_name,
            v.city_name,
            v.country_name,
            v.country_code,
            v.timezone
        FROM venues v
        INNER JOIN complexes c ON v.complex_id = c.complex_id
        ORDER BY c.complex_name ASC, v.venue_name ASC;
    """
    return execute_query(sql)


# -----------------------------------------------------------------------------
# PLOTLY CHART GENERATORS
# -----------------------------------------------------------------------------

def plot_competitors_by_country(df_country: pd.DataFrame) -> go.Figure:
    """Create a styled horizontal bar chart of competitors per country."""
    if df_country.empty:
        return go.Figure()

    fig = px.bar(
        df_country.head(15),
        x="total_competitors",
        y="country",
        orientation="h",
        color="total_points",
        color_continuous_scale="Viridis",
        labels={
            "total_competitors": "Number of Players",
            "country": "Country",
            "total_points": "Total Points",
        },
        title="Top Nations by Represented Competitors & Points",
        text="total_competitors",
    )
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        template="plotly_dark",
        margin=dict(l=20, r=20, t=50, b=20),
        height=400,
    )
    fig.update_traces(textposition="outside")
    return fig


def plot_points_distribution(df_rankings: pd.DataFrame) -> go.Figure:
    """Create a histogram showing ranking points distribution across competitors."""
    if df_rankings.empty:
        return go.Figure()

    fig = px.histogram(
        df_rankings,
        x="points",
        nbins=12,
        marginal="box",
        title="Competitor Points Distribution & Spread",
        labels={"points": "Ranking Points", "count": "Player Count"},
        color_discrete_sequence=["#10B981"],
        template="plotly_dark",
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=380,
    )
    return fig


def plot_competitions_by_category(df_comp: Optional[pd.DataFrame] = None) -> go.Figure:
    """Create a donut chart of competitions by tour category."""
    if df_comp is None or df_comp.empty:
        df_comp = execute_query("""
            SELECT cat.category_name, COUNT(c.competition_id) AS total_competitions
            FROM categories cat
            LEFT JOIN competitions c ON cat.category_id = c.category_id
            GROUP BY cat.category_name
            ORDER BY total_competitions DESC;
        """)

    if df_comp.empty:
        return go.Figure()

    fig = px.pie(
        df_comp,
        names="category_name",
        values="total_competitions",
        hole=0.45,
        title="Competitions by Category Breakdown",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        template="plotly_dark",
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=380,
    )
    return fig


def plot_competition_type_distribution() -> go.Figure:
    """Create a grouped bar chart of competition type distribution across categories."""
    df_types = execute_query("""
        SELECT cat.category_name, c.type AS competition_type, COUNT(c.competition_id) AS count
        FROM categories cat
        INNER JOIN competitions c ON cat.category_id = c.category_id
        GROUP BY cat.category_name, c.type
        ORDER BY cat.category_name ASC;
    """)

    if df_types.empty:
        return go.Figure()

    fig = px.bar(
        df_types,
        x="category_name",
        y="count",
        color="competition_type",
        barmode="group",
        title="Competition Formats (Singles / Doubles / Mixed) by Category",
        labels={"category_name": "Tour Category", "count": "Count", "competition_type": "Format"},
        template="plotly_dark",
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=380,
    )
    return fig


if __name__ == "__main__":
    logger.info("Executing Role 4 Analytics Module CLI demonstration...")
    kpi = get_kpi_metrics()
    print("\n--- KPI METRICS SUMMARY ---")
    for k, v in kpi.items():
        print(f"  {k}: {v}")

    print("\n--- COUNTRY PERFORMANCE BREAKDOWN ---")
    df_cnt = get_country_analytics()
    print(df_cnt.to_string(index=False))

    print("\n--- TOP 5 COMPETITORS ---")
    df_top5 = get_competitor_directory(min_rank=1, max_rank=5)
    print(df_top5[["rank", "competitor_name", "country", "points", "movement"]].to_string(index=False))
