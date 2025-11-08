-- Initial Schema for Pixel Pirates D1 Database
-- Migration: 0001_init_schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    is_superuser INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Posts table (for content to analyze)
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    image_url TEXT,
    source_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Analysis results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    credibility_score REAL NOT NULL,
    bias_score REAL,
    sentiment_score REAL,
    is_misinformation INTEGER DEFAULT 0,
    confidence REAL,
    analysis_type TEXT,
    details TEXT, -- JSON string
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User reports table
CREATE TABLE IF NOT EXISTS user_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    report_type TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Saved posts table (user bookmarks)
CREATE TABLE IF NOT EXISTS saved_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_posts_user_id ON posts(user_id);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at);
CREATE INDEX IF NOT EXISTS idx_analysis_post_id ON analysis_results(post_id);
CREATE INDEX IF NOT EXISTS idx_analysis_user_id ON analysis_results(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_post_id ON user_reports(post_id);
CREATE INDEX IF NOT EXISTS idx_reports_status ON user_reports(status);
CREATE INDEX IF NOT EXISTS idx_saved_user_id ON saved_posts(user_id);

-- Insert a test user (password: testpass123)
-- Note: This is a bcrypt hash of "testpass123"
INSERT OR IGNORE INTO users (id, username, email, hashed_password, is_superuser)
VALUES (
    1,
    'admin',
    'admin@pixelpirates.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7jFu.N9iu6',
    1
);
