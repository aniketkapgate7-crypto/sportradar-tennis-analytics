-- =============================================================================
-- Game Analytics: Unlocking Tennis Data with SportRadar API
-- Role 4: Complete Master Catalog of All 20 Analytical SQL Queries
-- File: role4_analytics_and_docs/All_SQL_Queries.sql
-- =============================================================================

USE tennis_analytics;

-- =============================================================================
-- SECTION 1: COMPETITIONS & CATEGORIES ANALYTICS (Queries 1 - 7)
-- =============================================================================

-- Query 1: List all competitions along with their category name
-- Purpose: Join tournaments with their governing categories (ATP, WTA, ITF, etc.)
SELECT 
    c.competition_id,
    c.competition_name,
    c.type,
    c.gender,
    cat.category_id,
    cat.category_name
FROM competitions c
INNER JOIN categories cat ON c.category_id = cat.category_id
ORDER BY cat.category_name ASC, c.competition_name ASC;

-- Query 2: Count the number of competitions in each category
-- Purpose: Aggregated distribution of competitions across tennis tour categories
SELECT 
    cat.category_id,
    cat.category_name,
    COUNT(c.competition_id) AS total_competitions
FROM categories cat
LEFT JOIN competitions c ON cat.category_id = c.category_id
GROUP BY cat.category_id, cat.category_name
ORDER BY total_competitions DESC, cat.category_name ASC;

-- Query 3: Find all competitions of type 'doubles'
-- Purpose: Filter competitions formatted specifically for doubles play
SELECT 
    c.competition_id,
    c.competition_name,
    c.type,
    c.gender,
    cat.category_name
FROM competitions c
INNER JOIN categories cat ON c.category_id = cat.category_id
WHERE LOWER(c.type) = 'doubles'
ORDER BY c.competition_name ASC;

-- Query 4: Get competitions that belong to a specific category (e.g., 'ITF Men')
-- Purpose: Targeted lookup of competitions in an exact circuit category
SELECT 
    c.competition_id,
    c.competition_name,
    c.type,
    c.gender,
    cat.category_name
FROM competitions c
INNER JOIN categories cat ON c.category_id = cat.category_id
WHERE cat.category_name = 'ITF Men'
ORDER BY c.competition_name ASC;

-- Query 5: Identify parent competitions and their sub-competitions (self-join)
-- Purpose: Unpack the hierarchical tournament structure (e.g., Grand Slam -> Singles/Doubles)
SELECT 
    p.competition_id AS parent_competition_id,
    p.competition_name AS parent_competition_name,
    s.competition_id AS sub_competition_id,
    s.competition_name AS sub_competition_name,
    s.type AS sub_competition_type,
    s.gender AS sub_competition_gender
FROM competitions s
INNER JOIN competitions p ON s.parent_id = p.competition_id
ORDER BY p.competition_name ASC, s.competition_name ASC;

-- Query 6: Analyze the distribution of competition types by category
-- Purpose: Cross-tabulation of competition format (singles/doubles/mixed) per category
SELECT 
    cat.category_name,
    c.type AS competition_type,
    COUNT(c.competition_id) AS competition_count
FROM categories cat
INNER JOIN competitions c ON cat.category_id = c.category_id
GROUP BY cat.category_name, c.type
ORDER BY cat.category_name ASC, competition_count DESC;

-- Query 7: List all competitions with no parent (top-level competitions)
-- Purpose: Retrieve master/flagship tournaments that sit at the top of the hierarchy
SELECT 
    c.competition_id,
    c.competition_name,
    c.type,
    c.gender,
    cat.category_name
FROM competitions c
INNER JOIN categories cat ON c.category_id = cat.category_id
WHERE c.parent_id IS NULL
ORDER BY cat.category_name ASC, c.competition_name ASC;


-- =============================================================================
-- SECTION 2: COMPLEXES & VENUES INFRASTRUCTURE ANALYTICS (Queries 8 - 14)
-- =============================================================================

-- Query 8: List all venues along with their associated complex name
-- Purpose: Associate courts and stadiums with their parent tennis complex facility
SELECT 
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    v.country_code,
    v.timezone,
    c.complex_id,
    c.complex_name
FROM venues v
INNER JOIN complexes c ON v.complex_id = c.complex_id
ORDER BY c.complex_name ASC, v.venue_name ASC;

-- Query 9: Count the number of venues in each complex
-- Purpose: Evaluate infrastructure capacity of complexes hosting multiple courts
SELECT 
    c.complex_id,
    c.complex_name,
    COUNT(v.venue_id) AS total_venues
FROM complexes c
LEFT JOIN venues v ON c.complex_id = v.complex_id
GROUP BY c.complex_id, c.complex_name
ORDER BY total_venues DESC, c.complex_name ASC;

-- Query 10: Get details of venues in a specific country (e.g., 'Chile')
-- Purpose: Geographic query returning tennis courts and host cities in a specified nation
SELECT 
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    v.country_code,
    v.timezone,
    c.complex_name
FROM venues v
INNER JOIN complexes c ON v.complex_id = c.complex_id
WHERE v.country_name = 'Chile'
ORDER BY v.city_name ASC, v.venue_name ASC;

-- Query 11: Identify all venues and their timezones
-- Purpose: Map timezone boundaries across international venues for broadcast/match timing
SELECT 
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    v.timezone
FROM venues v
ORDER BY v.timezone ASC, v.venue_name ASC;

-- Query 12: Find complexes that have more than one venue (HAVING COUNT(*) > 1)
-- Purpose: Identify major multi-venue tournament facilities using group filtering
SELECT 
    c.complex_id,
    c.complex_name,
    COUNT(v.venue_id) AS venue_count
FROM complexes c
INNER JOIN venues v ON c.complex_id = v.complex_id
GROUP BY c.complex_id, c.complex_name
HAVING COUNT(v.venue_id) > 1
ORDER BY venue_count DESC, c.complex_name ASC;

-- Query 13: List venues grouped by country
-- Purpose: Aggregate venue counts and names formatted as comma-separated lists per country
SELECT 
    v.country_name,
    v.country_code,
    COUNT(v.venue_id) AS venue_count,
    GROUP_CONCAT(v.venue_name ORDER BY v.venue_name SEPARATOR ', ') AS venue_list
FROM venues v
GROUP BY v.country_name, v.country_code
ORDER BY venue_count DESC, v.country_name ASC;

-- Query 14: Find all venues for a specific complex (e.g., 'Nacional')
-- Purpose: Substring search to locate venues under complexes matching a keyword
SELECT 
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    v.timezone,
    c.complex_name
FROM venues v
INNER JOIN complexes c ON v.complex_id = c.complex_id
WHERE c.complex_name LIKE '%Nacional%'
ORDER BY v.venue_name ASC;


-- =============================================================================
-- SECTION 3: COMPETITORS & RANKINGS PERFORMANCE ANALYTICS (Queries 15 - 20)
-- =============================================================================

-- Query 15: Get all competitors with their rank and points
-- Purpose: Complete doubles leaderboard sorted by official ATP/WTA ranking
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

-- Query 16: Find competitors ranked in the top 5
-- Purpose: Isolate the world elite tier of doubles tennis competitors
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

-- Query 17: List competitors with no rank movement (movement = 0)
-- Purpose: Track players maintaining rating stability without week-over-week rank shifts
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

-- Query 18: Get the total points of competitors from a specific country (e.g., 'Croatia')
-- Purpose: Compute total and average ranking points for a given tennis federation
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

-- Query 19: Count the number of competitors per country
-- Purpose: Comprehensive ranking of nations by player count and cumulative point strength
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

-- Query 20: Find competitors with the highest points in the current week
-- Purpose: Dynamic subquery identifying the current world #1 points leader(s)
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
