-- =============================================================================
-- Game Analytics: Unlocking Tennis Data with SportRadar API
-- Role 1: Analytical SQL Queries - Competitions & Categories
-- File: role1_database_and_competitions/queries_competitions.sql
-- =============================================================================

USE tennis_analytics;

-- -----------------------------------------------------------------------------
-- Query 1: List all competitions along with their category name
-- Demonstrates INNER JOIN between competitions and categories
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 2: Count the number of competitions in each category
-- Aggregation with LEFT JOIN to include categories with 0 competitions
-- -----------------------------------------------------------------------------
SELECT 
    cat.category_id,
    cat.category_name,
    COUNT(c.competition_id) AS total_competitions
FROM categories cat
LEFT JOIN competitions c ON cat.category_id = c.category_id
GROUP BY cat.category_id, cat.category_name
ORDER BY total_competitions DESC, cat.category_name ASC;

-- -----------------------------------------------------------------------------
-- Query 3: Find all competitions of type 'doubles'
-- Filtering by competition format
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 4: Get competitions that belong to a specific category (e.g., 'ITF Men')
-- Parameterized category lookup
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 5: Identify parent competitions and their sub-competitions (self-join)
-- Uses self-referencing relationship via parent_id
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 6: Analyze the distribution of competition types by category
-- Multi-column GROUP BY analysis
-- -----------------------------------------------------------------------------
SELECT 
    cat.category_name,
    c.type AS competition_type,
    COUNT(c.competition_id) AS competition_count
FROM categories cat
INNER JOIN competitions c ON cat.category_id = c.category_id
GROUP BY cat.category_name, c.type
ORDER BY cat.category_name ASC, competition_count DESC;

-- -----------------------------------------------------------------------------
-- Query 7: List all competitions with no parent (top-level competitions)
-- Filtering top of hierarchy where parent_id IS NULL
-- -----------------------------------------------------------------------------
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
