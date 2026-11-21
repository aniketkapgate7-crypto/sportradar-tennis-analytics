-- =============================================================================
-- Game Analytics: Unlocking Tennis Data with SportRadar API
-- Role 3: Analytical SQL Queries - Complexes & Venues
-- File: role3_sql_and_core_app/queries_complexes.sql
-- =============================================================================

USE tennis_analytics;

-- -----------------------------------------------------------------------------
-- Query 8: List all venues along with their associated complex name
-- Relational join between venues and complexes
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 9: Count the number of venues in each complex
-- Aggregate venue count per complex with LEFT JOIN
-- -----------------------------------------------------------------------------
SELECT 
    c.complex_id,
    c.complex_name,
    COUNT(v.venue_id) AS total_venues
FROM complexes c
LEFT JOIN venues v ON c.complex_id = v.complex_id
GROUP BY c.complex_id, c.complex_name
ORDER BY total_venues DESC, c.complex_name ASC;

-- -----------------------------------------------------------------------------
-- Query 10: Get details of venues in a specific country (e.g., 'Chile')
-- Geographical filtering
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Query 11: Identify all venues and their timezones
-- Timezone mapping for international scheduling
-- -----------------------------------------------------------------------------
SELECT 
    v.venue_id,
    v.venue_name,
    v.city_name,
    v.country_name,
    v.timezone
FROM venues v
ORDER BY v.timezone ASC, v.venue_name ASC;

-- -----------------------------------------------------------------------------
-- Query 12: Find complexes that have more than one venue (HAVING COUNT(*) > 1)
-- Multi-court complex identification
-- -----------------------------------------------------------------------------
SELECT 
    c.complex_id,
    c.complex_name,
    COUNT(v.venue_id) AS venue_count
FROM complexes c
INNER JOIN venues v ON c.complex_id = v.complex_id
GROUP BY c.complex_id, c.complex_name
HAVING COUNT(v.venue_id) > 1
ORDER BY venue_count DESC, c.complex_name ASC;

-- -----------------------------------------------------------------------------
-- Query 13: List venues grouped by country
-- Summary of tennis infrastructure per country
-- -----------------------------------------------------------------------------
SELECT 
    v.country_name,
    v.country_code,
    COUNT(v.venue_id) AS venue_count,
    GROUP_CONCAT(v.venue_name ORDER BY v.venue_name SEPARATOR ', ') AS venue_list
FROM venues v
GROUP BY v.country_name, v.country_code
ORDER BY venue_count DESC, v.country_name ASC;

-- -----------------------------------------------------------------------------
-- Query 14: Find all venues for a specific complex (e.g., 'Nacional')
-- Pattern matching on complex name
-- -----------------------------------------------------------------------------
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
