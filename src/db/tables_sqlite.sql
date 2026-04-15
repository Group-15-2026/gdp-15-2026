-- SQLite-compatible schema for Geopolitical Intelligence Assistant
-- Note: Run PRAGMA foreign_keys = ON; before using this schema

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS articles (
    article_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    publication_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    text_body TEXT,
    article_type TEXT,  -- conflict, politics, tragedy, etc.
    url TEXT
);

CREATE TABLE IF NOT EXISTS themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS actors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    actor_type TEXT NOT NULL,  -- country, company, politician, celebrity, other
    impact_score INTEGER DEFAULT 0 CHECK (impact_score >= -10 AND impact_score <= 10),
    public_opinion REAL CHECK (public_opinion >= 0 AND public_opinion <= 10),
    controversy REAL CHECK (controversy >= 0 AND controversy <= 10),
    mentions_weight REAL CHECK (mentions_weight >= 0 AND mentions_weight <= 100),
    UNIQUE(name, actor_type)
);

CREATE TABLE IF NOT EXISTS article_to_actors (
    article_id TEXT REFERENCES articles(article_id),
    actor_id INTEGER REFERENCES actors(id),
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (article_id, actor_id)
);

CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT REFERENCES articles(article_id),
    claim_text TEXT NOT NULL,
    opinion_score REAL CHECK (opinion_score >= 0 AND opinion_score <= 10)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    controversy REAL CHECK (controversy >= 0 AND controversy <= 10),
    economic_impact TEXT,        -- JSON: {severity: "low|medium|high", justification: "..."}
    financial_market_impact TEXT,
    security_impact TEXT,
    diplomatic_impact TEXT,
    event_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS article_to_event (
    article_id TEXT REFERENCES articles(article_id),
    event_id INTEGER REFERENCES events(id),
    relevance_score REAL,
    PRIMARY KEY (article_id, event_id)
);

CREATE TABLE IF NOT EXISTS actors_to_themes (
    actor_id INTEGER REFERENCES actors(id),
    theme_id INTEGER REFERENCES themes(id),
    PRIMARY KEY (actor_id, theme_id)
);

CREATE TABLE IF NOT EXISTS events_to_themes (
    event_id INTEGER REFERENCES events(id),
    theme_id INTEGER REFERENCES themes(id),
    PRIMARY KEY (event_id, theme_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_articles_publication_time ON articles(publication_time);
CREATE INDEX IF NOT EXISTS idx_actors_name ON actors(name);
CREATE INDEX IF NOT EXISTS idx_actors_type ON actors(actor_type);
CREATE INDEX IF NOT EXISTS idx_claims_article ON claims(article_id);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date);
CREATE INDEX IF NOT EXISTS idx_article_to_actors_article ON article_to_actors(article_id);
CREATE INDEX IF NOT EXISTS idx_article_to_actors_actor ON article_to_actors(actor_id);
CREATE INDEX IF NOT EXISTS idx_article_to_event_article ON article_to_event(article_id);
CREATE INDEX IF NOT EXISTS idx_article_to_event_event ON article_to_event(event_id);
