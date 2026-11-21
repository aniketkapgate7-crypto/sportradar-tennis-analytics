-- =============================================================================
-- Game Analytics: Unlocking Tennis Data with SportRadar API
-- Role 3: Analytical SQL Queries - Competitor Rankings
-- File: role3_sql_and_core_app/queries_rankings.sql
-- =============================================================================

USE tennis_analytics;

-- -----------------------------------------------------------------------------
-- Query 15: Get all competitors with their rank and points
-- Complete doubles leaderboard overview
-- -----------------------------------------------------------------------------
SELECT 
    r.rank,
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
ORDER BY r.rank ASC;

-- -----------------------------------------------------------------------------
-- Query 16: Find competitors ranked in the top 5
-- Elite tier filter
-- -----------------------------------------------------------------------------
SELECT 
    r.rank,
    c.name AS competitor_name,
    c.country,
    c.abbreviation,
    r.points,
    r.movement,
    r.competitions_played
FROM competitor_rankings r
INNER JOIN competitors c ON r.competitor_id = c.competitor_id
WHERE r.rank <= 5
ORDER BY r.rank ASC;

-- -----------------------------------------------------------------------------
-- Query 17: List competitors with no rank movement (movement = 0)
-- Identify stable rankings without weekly movement
-- -----------------------------------------------------------------------------
SELECT 
    r.rank,
    c.name AS competitor_name,
    c.country,
    r.points,
    r.movement,
    r.competitions_played
FROM competitor_rankings r
INNER JOIN competitors c ON r.competitor_id = c.competitor_id
WHERE r.movement = 0
ORDER BY r.rank ASC;

-- -----------------------------------------------------------------------------
-- Query 18: Get the total points of competitors from a specific country (e.g., 'Croatia')
-- Country point aggregation
-- -----------------------------------------------------------------------------
SELECT 
    c.country,
    c.country_code,
    COUNT(c.competitor_id) AS total_players,
    SUM(r.points) AS total_points,
    ROUND(AVG(r.points), 2) AS average_points,
    MIN(r.rank) AS best_rank
FROM competitors c
INNER JOIN competitor_rankings r ON c.competitor_id = r.competitor_id
WHERE c.country = 'Croatia'
GROUP BY c.country, c.country_code;

-- -----------------------------------------------------------------------------
-- Query 19: Count the number of competitors per country
-- Global talent distribution
-- -----------------------------------------------------------------------------
SELECT 
    c.country,
    c.country_code,
    COUNT(c.competitor_id) AS total_competitors,
    SUM(r.points) AS aggregate_points,
    ROUND(AVG(r.points), 2) AS average_points,
    MIN(r.rank) AS highest_rank
FROM competitors c
INNER JOIN competitor_rankings r ON c.competitor_id = r.competitor_id
GROUP BY c.country, c.country_code
ORDER BY total_competitors DESC, aggregate_points DESC;

-- -----------------------------------------------------------------------------
-- Query 20: Find competitors with the highest points in the current week
-- Dynamic subquery identifying current tournament/points leader(s)
-- -----------------------------------------------------------------------------
SELECT 
    r.rank,
    c.name AS competitor_name,
    c.country,
    c.country_code,
    r.points,
    r.movement,
    r.competitions_played
FROM competitor_rankings r
INNER JOIN competitors c ON r.competitor_id = c.competitor_id
WHERE r.points = (SELECT MAX(points) FROM competitor_rankings)
ORDER BY r.rank ASC;
