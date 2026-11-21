"""Game Analytics: Unlocking Tennis Data with SportRadar API.

Role 3: Interactive Streamlit Web Application
File: role3_sql_and_core_app/app.py

This application features:
1. Multi-tab, responsive UI with tennis-themed aesthetics and custom styling.
2. Sidebar filters: Gender, Rank Range, Country, Points Threshold, Competition Type, Category.
3. Tab 1: Homepage KPI Dashboard & distribution analytics.
4. Tab 2: Search & Filter Competitors with Player Spotlight Details Viewer (st.metric delta).
5. Tab 3: Country-Wise Analysis & Leaderboards (Top-Ranked & Highest Points).
6. Tab 4: Competitions & Venues Explorer + Live SQL Query Runner (executes all 20 project queries).
"""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("Streamlit-App")

# Ensure repository root is on sys.path
CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent if CURRENT_DIR.name.startswith("role") else CURRENT_DIR

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from role3_sql_and_core_app.db_connection import (
    execute_cached_query,
    execute_query,
    get_all_20_queries,
    test_connection,
)
from role4_analytics_and_docs.analytics_leaderboards import (
    get_competition_hierarchy,
    get_competitor_directory,
    get_country_analytics,
    get_kpi_metrics,
    get_venues_by_complex,
    plot_competition_type_distribution,
    plot_competitions_by_category,
    plot_competitors_by_country,
    plot_points_distribution,
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Tennis Game Analytics | Sportradar v3",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Global Page Styling */
    .main {
        background-color: #0E1117;
    }
    .stMetric {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .metric-card-header {
        font-size: 0.9rem;
        color: #94A3B8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .player-card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .query-box {
        background-color: #1E293B;
        border-left: 4px solid #10B981;
        padding: 12px 16px;
        border-radius: 4px;
        font-family: monospace;
        margin: 10px 0;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 10px;
        font-size: 0.8rem;
        font-weight: 700;
        border-radius: 9999px;
        background-color: #10B981;
        color: #FFFFFF;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS & DATABASE STATUS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1595435934249-5df7ed86e1c0?auto=format&fit=crop&w=400&q=80",
        caption="Game Analytics: Sportradar Tennis v3",
        use_container_width=True,
    )

    st.markdown("### 🔌 Database Connectivity")
    db_connected, db_message = test_connection()
    if db_connected:
        st.success("● Connected to MySQL (Active)", icon="✅")
    else:
        st.error(f"● Database Disconnected\n\n{db_message}", icon="❌")

    st.markdown("---")
    st.markdown("### 🎛️ Global Analytics Filters")

    # Fetch dynamic options from database
    try:
        df_countries_list = execute_query("SELECT DISTINCT country FROM competitors ORDER BY country ASC;")
        country_options = ["All Countries"] + df_countries_list["country"].dropna().tolist()
    except Exception:
        country_options = ["All Countries"]

    try:
        df_types_list = execute_query("SELECT DISTINCT type FROM competitions ORDER BY type ASC;")
        type_options = ["All Types"] + df_types_list["type"].dropna().tolist()
    except Exception:
        type_options = ["All Types", "singles", "doubles", "mixed"]

    try:
        df_categories_list = execute_query("SELECT DISTINCT category_name FROM categories ORDER BY category_name ASC;")
        category_options = ["All Categories"] + df_categories_list["category_name"].dropna().tolist()
    except Exception:
        category_options = ["All Categories", "ATP", "WTA", "ITF Men", "ITF Women"]

    selected_gender = st.selectbox("Player / Tour Gender", ["All Genders", "Men", "Women", "Mixed"])
    rank_range = st.slider("Rank Range", min_value=1, max_value=50, value=(1, 20), step=1)
    selected_country = st.selectbox("Competitor Country", country_options)
    points_threshold = st.slider("Minimum Points Threshold", min_value=0, max_value=8000, value=0, step=250)
    selected_comp_type = st.selectbox("Competition Format", type_options)
    selected_category = st.selectbox("Tournament Circuit", category_options)

    st.markdown("---")
    st.markdown("### ⚡ ETL Maintenance")
    if st.button("🔄 Trigger Master ETL Sync", help="Run the full 3-stage Sportradar ETL pipeline"):
        with st.spinner("Executing Master ETL Pipeline..."):
            try:
                from role2_complexes_and_rankings.run_all_etl import run_pipeline
                etl_res = run_pipeline()
                if etl_res["status"] == "SUCCESS":
                    st.success(f"ETL Completed in {etl_res.get('duration_seconds', 0)}s!")
                    st.cache_data.clear()
                else:
                    st.warning(f"ETL completed with notices: {etl_res.get('status')}")
            except Exception as e:
                st.error(f"ETL execution failed: {e}")

    st.markdown(
        "<div style='font-size: 0.75rem; color: #64748B; text-align: center; margin-top: 20px;'>"
        "Sportradar Tennis Trial v3 API<br>MySQL 8.0 & SQLAlchemy Engine"
        "</div>",
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# HEADER SECTION
# -----------------------------------------------------------------------------
st.title("🎾 Game Analytics: Unlocking Tennis Data")
st.markdown(
    "**End-to-End Analytics Platform powered by Sportradar Tennis v3 API, MySQL, and SQLAlchemy.** "
    "Explore tournament hierarchies, infrastructure venues, and live doubles competitor rankings."
)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Homepage KPI Dashboard",
    "🔍 Competitors & Details Viewer",
    "🌍 Country Analytics & Leaderboards",
    "🏟️ Competitions, Venues & SQL Runner",
])

# =============================================================================
# TAB 1: HOMEPAGE KPI DASHBOARD
# =============================================================================
with tab1:
    st.subheader("Executive KPI Overview")
    kpi = get_kpi_metrics()

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Total Competitors", f"{kpi['total_competitors']}", help="Distinct tennis athletes in database")
    with col2:
        st.metric("Nations Represented", f"{kpi['total_countries']}", help="Unique player origin countries")
    with col3:
        st.metric("World #1 Points", f"{kpi['highest_points']:,}", help="Maximum doubles ranking points")
    with col4:
        st.metric("Competitions", f"{kpi['total_competitions']}", help="Tournaments across ATP, WTA, and ITF")
    with col5:
        st.metric("Stadium Venues", f"{kpi['total_venues']}", help="Individual courts and arena venues")
    with col6:
        st.metric("Complexes", f"{kpi['total_complexes']}", help="Tennis grounds and sporting complexes")

    st.markdown("---")

    col_chart_left, col_chart_right = st.columns(2)
    with col_chart_left:
        df_rankings_all = get_competitor_directory(min_rank=1, max_rank=100)
        st.plotly_chart(plot_points_distribution(df_rankings_all), use_container_width=True)

    with col_chart_right:
        st.plotly_chart(plot_competitions_by_category(), use_container_width=True)

    col_chart_full = st.container()
    with col_chart_full:
        st.plotly_chart(plot_competition_type_distribution(), use_container_width=True)


# =============================================================================
# TAB 2: SEARCH & FILTER COMPETITORS + DETAILS VIEWER
# =============================================================================
with tab2:
    st.subheader("Competitor Directory & Profile Inspector")

    search_col, count_col = st.columns([3, 1])
    with search_col:
        player_search = st.text_input("🔎 Search Competitor by Name", placeholder="e.g. Granollers, Pavic, Bopanna...")

    # Query filtered competitors using sidebar criteria + local search
    df_filtered_competitors = get_competitor_directory(
        country=selected_country,
        min_rank=rank_range[0],
        max_rank=rank_range[1],
        min_points=points_threshold,
        search_query=player_search,
    )

    with count_col:
        st.metric("Matching Athletes", f"{len(df_filtered_competitors)}")

    # Main Grid: Left side interactive table, Right side Player Spotlight Viewer
    col_table, col_details = st.columns([3, 2])

    with col_table:
        st.markdown("##### Athlete Leaderboard Grid")
        if df_filtered_competitors.empty:
            st.info("No competitors found matching your active filter criteria.")
        else:
            display_df = df_filtered_competitors.copy()
            # Stylize display columns
            display_df["Rank"] = display_df["rank"].apply(lambda r: f"#{r}")
            display_df["Weekly Shift"] = display_df["movement"].apply(
                lambda m: f"🔼 +{m}" if m > 0 else (f"🔽 {m}" if m < 0 else "⏺ 0")
            )
            st.dataframe(
                display_df[[
                    "Rank",
                    "competitor_name",
                    "country",
                    "points",
                    "Weekly Shift",
                    "competitions_played",
                ]].rename(columns={
                    "competitor_name": "Player Name",
                    "country": "Country",
                    "points": "Ranking Points",
                    "competitions_played": "Tournaments Played",
                }),
                use_container_width=True,
                height=450,
            )

    with col_details:
        st.markdown("##### 👤 Competitor Spotlight Details")
        if not df_filtered_competitors.empty:
            competitor_names = df_filtered_competitors["competitor_name"].tolist()
            selected_player_name = st.selectbox("Select Athlete to Inspect", competitor_names)

            player_row = df_filtered_competitors[
                df_filtered_competitors["competitor_name"] == selected_player_name
            ].iloc[0]

            # Player Card Presentation
            st.markdown(
                f"""
                <div class="player-card">
                    <h3 style="margin-top:0; color:#F8FAFC;">🎾 {player_row['competitor_name']}</h3>
                    <p style="color:#94A3B8; margin-bottom: 12px;">
                        <strong>Country:</strong> {player_row['country']} ({player_row['country_code']}) &nbsp;|&nbsp;
                        <strong>Abbrev:</strong> {player_row['abbreviation']}
                    </p>
                    <p style="color:#64748B; font-size:0.8rem; font-family: monospace;">ID: {player_row['competitor_id']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            p_col1, p_col2 = st.columns(2)
            with p_col1:
                movement = int(player_row["movement"])
                delta_str = f"{movement:+d} positions" if movement != 0 else "No change"
                st.metric(
                    label="Current World Rank",
                    value=f"#{player_row['rank']}",
                    delta=delta_str,
                    delta_color="normal",
                )
            with p_col2:
                st.metric(
                    label="Official Ranking Points",
                    value=f"{player_row['points']:,} pts",
                )

            p_col3, p_col4 = st.columns(2)
            with p_col3:
                st.metric(
                    label="Competitions Played",
                    value=f"{player_row['competitions_played']} events",
                )
            with p_col4:
                avg_points = (
                    player_row["points"] / player_row["competitions_played"]
                    if player_row["competitions_played"] > 0 else 0
                )
                st.metric(
                    label="Points Per Event",
                    value=f"{avg_points:.1f} pts/event",
                )
        else:
            st.info("Select or adjust filters to inspect player profiles.")


# =============================================================================
# TAB 3: COUNTRY-WISE ANALYSIS & LEADERBOARDS
# =============================================================================
with tab3:
    st.subheader("Global Country-Wise Performance & Dual Leaderboards")

    df_countries = get_country_analytics()

    chart_col, table_col = st.columns([3, 2])
    with chart_col:
        st.plotly_chart(plot_competitors_by_country(df_countries), use_container_width=True)

    with table_col:
        st.markdown("##### Country Aggregation Summary")
        st.dataframe(
            df_countries.rename(columns={
                "country": "Nation",
                "country_code": "Code",
                "total_competitors": "Athletes",
                "total_points": "Total Points",
                "average_points": "Avg Points",
                "highest_rank": "Best Rank",
            }),
            use_container_width=True,
            height=380,
        )

    st.markdown("---")
    st.subheader("Dual Analytical Leaderboards")

    board_col1, board_col2 = st.columns(2)

    with board_col1:
        st.markdown("##### 🏆 Top-Ranked Competitors Leaderboard")
        df_top_ranked = execute_query("""
            SELECT 
                r.`rank` AS `Rank`,
                c.name AS `Competitor`,
                c.country AS `Country`,
                r.points AS `Points`,
                r.movement AS `Weekly Shift`
            FROM competitor_rankings r
            INNER JOIN competitors c ON r.competitor_id = c.competitor_id
            ORDER BY r.`rank` ASC
            LIMIT 10;
        """)
        df_top_ranked["Rank"] = df_top_ranked["Rank"].apply(lambda r: f"#{r}")
        df_top_ranked["Weekly Shift"] = df_top_ranked["Weekly Shift"].apply(
            lambda m: f"🔼 +{m}" if m > 0 else (f"🔽 {m}" if m < 0 else "⏺ 0")
        )
        st.dataframe(df_top_ranked, use_container_width=True, height=350)

    with board_col2:
        st.markdown("##### ⚡ Highest Points Scoring Leaderboard")
        df_points_leader = execute_query("""
            SELECT 
                c.name AS `Competitor`,
                c.country AS `Country`,
                r.points AS `Total Points`,
                r.competitions_played AS `Events`,
                r.`rank` AS `World Rank`
            FROM competitor_rankings r
            INNER JOIN competitors c ON r.competitor_id = c.competitor_id
            ORDER BY r.points DESC, r.`rank` ASC
            LIMIT 10;
        """)
        df_points_leader["World Rank"] = df_points_leader["World Rank"].apply(lambda r: f"#{r}")
        st.dataframe(df_points_leader, use_container_width=True, height=350)


# =============================================================================
# TAB 4: COMPETITIONS & VENUES EXPLORER + LIVE SQL RUNNER
# =============================================================================
with tab4:
    st.subheader("Tournament Structures & Infrastructure Venues")

    exp_col1, exp_col2 = st.columns(2)

    with exp_col1:
        st.markdown("##### 🌲 Tournament Hierarchy (Parent -> Sub-Competitions)")
        df_hierarchy = get_competition_hierarchy()
        if not df_hierarchy.empty:
            st.dataframe(
                df_hierarchy.rename(columns={
                    "parent_competition": "Parent Tournament",
                    "sub_competition": "Sub-Event / Category",
                    "sub_competition_type": "Format",
                    "sub_competition_gender": "Gender",
                    "category_name": "Circuit",
                }),
                use_container_width=True,
                height=300,
            )
        else:
            st.info("No hierarchy relationships found.")

    with exp_col2:
        st.markdown("##### 🏟️ Venues by Complex & City")
        df_venues = get_venues_by_complex()
        if not df_venues.empty:
            st.dataframe(
                df_venues.rename(columns={
                    "complex_name": "Complex Ground",
                    "venue_name": "Stadium / Court",
                    "city_name": "City",
                    "country_name": "Country",
                    "country_code": "Code",
                    "timezone": "Timezone",
                }),
                use_container_width=True,
                height=300,
            )
        else:
            st.info("No venues found.")

    st.markdown("---")
    st.subheader("⚡ Live Analytical SQL Query Runner (All 20 Queries)")
    st.markdown(
        "Execute any of the 20 official project queries directly against the live MySQL database. "
        "Inspect execution times, underlying SQL logic, and full result sets."
    )

    all_queries = get_all_20_queries()
    query_titles = [f"Q{q['id']}: {q['title']}" for q in all_queries]

    selected_query_title = st.selectbox("Select SQL Query to Inspect & Execute", query_titles)
    selected_query_index = query_titles.index(selected_query_title)
    selected_query_obj = all_queries[selected_query_index]

    st.markdown(f"**Section:** `{selected_query_obj['section']}`")
    st.markdown(f"**Description:** {selected_query_obj['description']}")

    # SQL Editor / Viewer
    sql_to_run = st.text_area(
        "SQL Query Expression (Editable):",
        value=selected_query_obj["sql"],
        height=140,
    )

    col_btn_run, col_export = st.columns([1, 4])
    with col_btn_run:
        run_btn = st.button("🚀 Run Query", type="primary")

    if run_btn:
        start_q_time = time.time()
        try:
            with st.spinner("Executing query against MySQL..."):
                query_result_df = execute_query(sql_to_run)
                duration = time.time() - start_q_time

            st.success(f"Query returned {len(query_result_df)} rows in {duration:.4f} seconds.")
            st.dataframe(query_result_df, use_container_width=True)

            # Download CSV button
            csv_data = query_result_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export Query Result as CSV",
                data=csv_data,
                file_name=f"query_{selected_query_obj['id']}_result.csv",
                mime="text/csv",
            )
        except Exception as q_err:
            st.error(f"SQL Execution Error: {q_err}")


# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #64748B; font-size: 0.85rem; padding: 20px 0;">
        Game Analytics: Unlocking Tennis Data with SportRadar API | Built with Python, Streamlit, SQLAlchemy & MySQL<br>
        Structured across 4 specialized role directories for modular collaboration.
    </div>
    """,
    unsafe_allow_html=True,
)
