-- Vadis Media Product Placement Database Schema

-- Scripts table
CREATE TABLE IF NOT EXISTS scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    genre TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product placements table
CREATE TABLE IF NOT EXISTS product_placements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    script_id INTEGER,
    product_name TEXT NOT NULL,
    brand TEXT NOT NULL,
    placement_type TEXT,
    scene_description TEXT,
    estimated_cost REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (script_id) REFERENCES scripts(id)
);

-- Actors table
CREATE TABLE IF NOT EXISTS actors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tmdb_id INTEGER UNIQUE,
    name TEXT NOT NULL,
    country TEXT,
    popularity REAL,
    profile_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Script casting table
CREATE TABLE IF NOT EXISTS script_casting (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    script_id INTEGER,
    actor_id INTEGER,
    role_name TEXT,
    match_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (script_id) REFERENCES scripts(id),
    FOREIGN KEY (actor_id) REFERENCES actors(id)
);

-- Revenue forecasts table
CREATE TABLE IF NOT EXISTS revenue_forecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    script_id INTEGER,
    genre TEXT NOT NULL,
    product_category TEXT,
    estimated_revenue REAL,
    estimated_roi REAL,
    market_reach TEXT,
    forecast_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (script_id) REFERENCES scripts(id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_scripts_genre ON scripts(genre);
CREATE INDEX IF NOT EXISTS idx_product_placements_script ON product_placements(script_id);
CREATE INDEX IF NOT EXISTS idx_actors_tmdb ON actors(tmdb_id);
CREATE INDEX IF NOT EXISTS idx_script_casting_script ON script_casting(script_id);
CREATE INDEX IF NOT EXISTS idx_revenue_forecasts_script ON revenue_forecasts(script_id);
