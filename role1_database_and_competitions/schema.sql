-- =============================================================================
-- Game Analytics: Unlocking Tennis Data with SportRadar API
-- Role 1: Master Relational Database Schema (MySQL DDL)
-- File: role1_database_and_competitions/schema.sql
-- =============================================================================

CREATE DATABASE IF NOT EXISTS tennis_analytics;
USE tennis_analytics;

-- Temporarily disable foreign key checks during schema initialization
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS competitor_rankings;
DROP TABLE IF EXISTS competitors;
DROP TABLE IF EXISTS venues;
DROP TABLE IF EXISTS complexes;
DROP TABLE IF EXISTS competitions;
DROP TABLE IF EXISTS categories;

SET FOREIGN_KEY_CHECKS = 1;

-- -----------------------------------------------------------------------------
-- 1. categories table
-- Stores distinct tennis competition categories (e.g., ATP, WTA, ITF Men, ITF Women)
-- -----------------------------------------------------------------------------
CREATE TABLE categories (
    category_id VARCHAR(50) NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 2. competitions table
-- Stores tennis tournaments and sub-tournaments with self-referencing hierarchy
-- -----------------------------------------------------------------------------
CREATE TABLE competitions (
    competition_id VARCHAR(50) NOT NULL,
    competition_name VARCHAR(100) NOT NULL,
    parent_id VARCHAR(50) NULL,
    type VARCHAR(20) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    category_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (competition_id),
    CONSTRAINT fk_competitions_category
        FOREIGN KEY (category_id) REFERENCES categories(category_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_competitions_parent
        FOREIGN KEY (parent_id) REFERENCES competitions(competition_id)
        ON UPDATE CASCADE ON DELETE SET NULL,
    INDEX idx_competitions_category (category_id),
    INDEX idx_competitions_parent (parent_id),
    INDEX idx_competitions_type (type),
    INDEX idx_competitions_gender (gender)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 3. complexes table
-- Stores sports/tennis complexes hosting tennis venues
-- -----------------------------------------------------------------------------
CREATE TABLE complexes (
    complex_id VARCHAR(50) NOT NULL,
    complex_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (complex_id),
    INDEX idx_complexes_name (complex_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 4. venues table
-- Stores individual tennis courts / stadiums within complexes
-- -----------------------------------------------------------------------------
CREATE TABLE venues (
    venue_id VARCHAR(50) NOT NULL,
    venue_name VARCHAR(100) NOT NULL,
    city_name VARCHAR(100) NOT NULL,
    country_name VARCHAR(100) NOT NULL,
    country_code CHAR(3) NOT NULL,
    timezone VARCHAR(100) NOT NULL,
    complex_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (venue_id),
    CONSTRAINT fk_venues_complex
        FOREIGN KEY (complex_id) REFERENCES complexes(complex_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    INDEX idx_venues_complex (complex_id),
    INDEX idx_venues_country (country_name),
    INDEX idx_venues_city (city_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 5. competitors table
-- Stores tennis athletes / players
-- -----------------------------------------------------------------------------
CREATE TABLE competitors (
    competitor_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    country_code CHAR(3) NOT NULL,
    abbreviation VARCHAR(10) NOT NULL,
    PRIMARY KEY (competitor_id),
    INDEX idx_competitors_country (country),
    INDEX idx_competitors_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 6. competitor_rankings table
-- Stores ranking points, movement, and tournament counts for competitors
-- -----------------------------------------------------------------------------
CREATE TABLE competitor_rankings (
    rank_id INT NOT NULL AUTO_INCREMENT,
    `rank` INT NOT NULL,
    movement INT NOT NULL,
    points INT NOT NULL,
    competitions_played INT NOT NULL,
    competitor_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (rank_id),
    UNIQUE KEY uq_competitor_ranking (competitor_id),
    CONSTRAINT fk_rankings_competitor
        FOREIGN KEY (competitor_id) REFERENCES competitors(competitor_id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    INDEX idx_rankings_competitor (competitor_id),
    INDEX idx_rankings_rank (`rank`),
    INDEX idx_rankings_points (points)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
