-- Database Schema for Polymarket Whale Tracker
-- This schema supports persistent data storage for enhanced features
-- Database: PostgreSQL (recommended) or MySQL

-- ============================================================================
-- TRADERS TABLE
-- ============================================================================
CREATE TABLE traders (
    id SERIAL PRIMARY KEY,
    wallet_address VARCHAR(42) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    pseudonym VARCHAR(100),
    profile_image_url TEXT,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Cached Statistics (updated periodically)
    total_volume DECIMAL(20, 2) DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    total_positions INTEGER DEFAULT 0,
    win_count INTEGER DEFAULT 0,
    loss_count INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2) DEFAULT 0,
    total_pnl DECIMAL(20, 2) DEFAULT 0,
    roi_percentage DECIMAL(10, 2) DEFAULT 0,
    trader_tier VARCHAR(50),
    risk_score DECIMAL(5, 2) DEFAULT 0,
    
    -- Activity Metrics
    unique_markets_traded INTEGER DEFAULT 0,
    avg_trade_size DECIMAL(20, 2) DEFAULT 0,
    trades_per_day DECIMAL(10, 2) DEFAULT 0,
    best_trade DECIMAL(20, 2) DEFAULT 0,
    worst_trade DECIMAL(20, 2) DEFAULT 0,
    
    -- Time Period
    last_stats_update TIMESTAMP,
    stats_period_days INTEGER DEFAULT 30,
    
    INDEX idx_wallet (wallet_address),
    INDEX idx_volume (total_volume DESC),
    INDEX idx_win_rate (win_rate DESC),
    INDEX idx_tier (trader_tier)
);

-- ============================================================================
-- TRADES TABLE
-- ============================================================================
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    transaction_hash VARCHAR(66) UNIQUE NOT NULL,
    trader_id INTEGER REFERENCES traders(id),
    wallet_address VARCHAR(42) NOT NULL,
    
    -- Trade Details
    market_condition_id VARCHAR(66),
    market_slug VARCHAR(200),
    market_title TEXT,
    event_slug VARCHAR(200),
    
    -- Trade Data
    side VARCHAR(10) NOT NULL, -- BUY or SELL
    outcome VARCHAR(50),
    outcome_index INTEGER,
    size DECIMAL(20, 8) NOT NULL,
    price DECIMAL(10, 8) NOT NULL,
    value DECIMAL(20, 2) NOT NULL,
    
    -- Metadata
    asset_id VARCHAR(66),
    icon_url TEXT,
    timestamp BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Classification
    is_whale_trade BOOLEAN DEFAULT FALSE,
    whale_threshold DECIMAL(20, 2),
    
    INDEX idx_trader (trader_id),
    INDEX idx_wallet (wallet_address),
    INDEX idx_market (market_condition_id),
    INDEX idx_timestamp (timestamp DESC),
    INDEX idx_value (value DESC),
    INDEX idx_whale (is_whale_trade, timestamp DESC)
);

-- ============================================================================
-- POSITIONS TABLE
-- ============================================================================
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    trader_id INTEGER REFERENCES traders(id),
    wallet_address VARCHAR(42) NOT NULL,
    
    -- Position Details
    market_condition_id VARCHAR(66) NOT NULL,
    market_slug VARCHAR(200),
    market_title TEXT,
    asset_id VARCHAR(66),
    outcome VARCHAR(50),
    
    -- Position Data
    size DECIMAL(20, 8) NOT NULL,
    avg_price DECIMAL(10, 8) NOT NULL,
    current_price DECIMAL(10, 8),
    initial_value DECIMAL(20, 2) NOT NULL,
    current_value DECIMAL(20, 2),
    
    -- P&L
    cash_pnl DECIMAL(20, 2),
    percent_pnl DECIMAL(10, 2),
    realized_pnl DECIMAL(20, 2),
    
    -- Status
    is_open BOOLEAN DEFAULT TRUE,
    is_closed BOOLEAN DEFAULT FALSE,
    is_redeemable BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    opened_at TIMESTAMP,
    closed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_trader (trader_id),
    INDEX idx_wallet (wallet_address),
    INDEX idx_market (market_condition_id),
    INDEX idx_open (is_open, wallet_address),
    INDEX idx_pnl (cash_pnl DESC)
);

-- ============================================================================
-- MARKETS TABLE
-- ============================================================================
CREATE TABLE markets (
    id SERIAL PRIMARY KEY,
    condition_id VARCHAR(66) UNIQUE NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    
    -- Market Data
    question TEXT,
    category VARCHAR(100),
    description TEXT,
    icon_url TEXT,
    
    -- Financial Metrics
    volume DECIMAL(20, 2) DEFAULT 0,
    liquidity DECIMAL(20, 2) DEFAULT 0,
    volume_24h DECIMAL(20, 2) DEFAULT 0,
    
    -- Calculated Metrics
    vol_liq_ratio DECIMAL(10, 4),
    activity_score DECIMAL(5, 2),
    health_score DECIMAL(5, 2),
    popularity_tier VARCHAR(50),
    
    -- Sentiment (cached)
    sentiment_label VARCHAR(50),
    sentiment_score DECIMAL(5, 2),
    sentiment_confidence DECIMAL(5, 2),
    sentiment_updated_at TIMESTAMP,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_closed BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_condition (condition_id),
    INDEX idx_slug (slug),
    INDEX idx_volume (volume DESC),
    INDEX idx_active (is_active, volume DESC)
);

-- ============================================================================
-- COPY_TRADING_FOLLOWS TABLE
-- ============================================================================
CREATE TABLE copy_trading_follows (
    id SERIAL PRIMARY KEY,
    follower_wallet VARCHAR(42) NOT NULL,
    following_trader_id INTEGER REFERENCES traders(id),
    following_wallet VARCHAR(42) NOT NULL,
    
    -- Copy Settings
    max_position_size DECIMAL(20, 2) NOT NULL,
    copy_percentage DECIMAL(5, 2) NOT NULL,
    max_total_exposure DECIMAL(20, 2) NOT NULL,
    min_trader_confidence DECIMAL(20, 2) DEFAULT 10,
    auto_exit BOOLEAN DEFAULT TRUE,
    
    -- Market Filters (JSON)
    markets_to_copy TEXT, -- JSON array
    markets_to_exclude TEXT, -- JSON array
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Statistics
    total_copied_trades INTEGER DEFAULT 0,
    total_volume_copied DECIMAL(20, 2) DEFAULT 0,
    total_pnl DECIMAL(20, 2) DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    stopped_at TIMESTAMP,
    last_copy_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_follower (follower_wallet),
    INDEX idx_following (following_trader_id),
    INDEX idx_active (is_active, follower_wallet),
    UNIQUE (follower_wallet, following_wallet)
);

-- ============================================================================
-- COPIED_TRADES TABLE
-- ============================================================================
CREATE TABLE copied_trades (
    id SERIAL PRIMARY KEY,
    follow_id INTEGER REFERENCES copy_trading_follows(id),
    original_trade_id INTEGER REFERENCES trades(id),
    
    -- Follower Info
    follower_wallet VARCHAR(42) NOT NULL,
    
    -- Original Trade
    original_wallet VARCHAR(42) NOT NULL,
    original_size DECIMAL(20, 8) NOT NULL,
    original_value DECIMAL(20, 2) NOT NULL,
    
    -- Copied Trade
    copied_size DECIMAL(20, 8) NOT NULL,
    copied_value DECIMAL(20, 2) NOT NULL,
    copied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Trade Details (duplicated for convenience)
    market_condition_id VARCHAR(66),
    market_title TEXT,
    side VARCHAR(10),
    price DECIMAL(10, 8),
    
    -- Result
    copy_successful BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    -- P&L (if closed)
    realized_pnl DECIMAL(20, 2),
    
    INDEX idx_follow (follow_id),
    INDEX idx_follower (follower_wallet),
    INDEX idx_original_trade (original_trade_id),
    INDEX idx_timestamp (copied_at DESC)
);

-- ============================================================================
-- MARKET_SENTIMENT_HISTORY TABLE
-- ============================================================================
CREATE TABLE market_sentiment_history (
    id SERIAL PRIMARY KEY,
    market_id INTEGER REFERENCES markets(id),
    condition_id VARCHAR(66) NOT NULL,
    
    -- Sentiment Data
    sentiment_label VARCHAR(50) NOT NULL,
    sentiment_score DECIMAL(5, 2) NOT NULL,
    confidence DECIMAL(5, 2) NOT NULL,
    
    -- Volume Data
    buy_volume DECIMAL(20, 2) NOT NULL,
    sell_volume DECIMAL(20, 2) NOT NULL,
    trade_count INTEGER NOT NULL,
    
    -- Time Window
    time_window_hours INTEGER NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_market (market_id, calculated_at DESC),
    INDEX idx_condition (condition_id, calculated_at DESC)
);

-- ============================================================================
-- TRADER_PERFORMANCE_SNAPSHOTS TABLE
-- ============================================================================
CREATE TABLE trader_performance_snapshots (
    id SERIAL PRIMARY KEY,
    trader_id INTEGER REFERENCES traders(id),
    wallet_address VARCHAR(42) NOT NULL,
    
    -- Performance Metrics
    total_volume DECIMAL(20, 2) NOT NULL,
    total_trades INTEGER NOT NULL,
    win_rate DECIMAL(5, 2) NOT NULL,
    total_pnl DECIMAL(20, 2) NOT NULL,
    roi_percentage DECIMAL(10, 2) NOT NULL,
    
    -- Period
    period_days INTEGER NOT NULL,
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_trader (trader_id, snapshot_date DESC),
    INDEX idx_date (snapshot_date DESC),
    UNIQUE (trader_id, snapshot_date, period_days)
);

-- ============================================================================
-- WHALE_ALERTS TABLE
-- ============================================================================
CREATE TABLE whale_alerts (
    id SERIAL PRIMARY KEY,
    trade_id INTEGER REFERENCES trades(id),
    transaction_hash VARCHAR(66) NOT NULL,
    
    -- Alert Data
    wallet_address VARCHAR(42) NOT NULL,
    trader_name VARCHAR(100),
    market_title TEXT,
    side VARCHAR(10),
    value DECIMAL(20, 2) NOT NULL,
    
    -- Alert Status
    is_notified BOOLEAN DEFAULT FALSE,
    notified_at TIMESTAMP,
    
    -- Timestamps
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trade_timestamp BIGINT NOT NULL,
    
    INDEX idx_trade (trade_id),
    INDEX idx_wallet (wallet_address),
    INDEX idx_value (value DESC),
    INDEX idx_detected (detected_at DESC)
);

-- ============================================================================
-- SYSTEM_CACHE TABLE
-- ============================================================================
CREATE TABLE system_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    cache_value TEXT NOT NULL, -- JSON data
    
    -- TTL
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_key (cache_key),
    INDEX idx_expires (expires_at)
);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Top Traders View
CREATE VIEW v_top_traders AS
SELECT 
    t.id,
    t.wallet_address,
    t.display_name,
    t.pseudonym,
    t.profile_image_url,
    t.total_volume,
    t.total_trades,
    t.win_rate,
    t.total_pnl,
    t.roi_percentage,
    t.trader_tier,
    t.risk_score,
    t.unique_markets_traded,
    COUNT(DISTINCT p.id) as active_positions
FROM traders t
LEFT JOIN positions p ON t.id = p.trader_id AND p.is_open = TRUE
GROUP BY t.id
ORDER BY t.total_volume DESC;

-- Active Copy Trading View
CREATE VIEW v_active_copy_trading AS
SELECT 
    f.id,
    f.follower_wallet,
    t.wallet_address as following_wallet,
    t.display_name as following_name,
    t.trader_tier,
    f.total_copied_trades,
    f.total_volume_copied,
    f.total_pnl,
    f.started_at,
    f.last_copy_at
FROM copy_trading_follows f
JOIN traders t ON f.following_trader_id = t.id
WHERE f.is_active = TRUE
ORDER BY f.total_volume_copied DESC;

-- Market Activity View
CREATE VIEW v_market_activity AS
SELECT 
    m.id,
    m.condition_id,
    m.slug,
    m.title,
    m.volume,
    m.liquidity,
    m.popularity_tier,
    m.sentiment_label,
    m.sentiment_score,
    COUNT(DISTINCT t.id) as trade_count,
    COUNT(DISTINCT t.wallet_address) as unique_traders,
    SUM(CASE WHEN t.timestamp >= EXTRACT(EPOCH FROM NOW() - INTERVAL '24 hours') THEN 1 ELSE 0 END) as trades_24h
FROM markets m
LEFT JOIN trades t ON m.condition_id = t.market_condition_id
WHERE m.is_active = TRUE
GROUP BY m.id
ORDER BY m.volume DESC;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Update trader statistics
CREATE OR REPLACE FUNCTION update_trader_stats(p_wallet_address VARCHAR)
RETURNS VOID AS $$
BEGIN
    UPDATE traders SET
        total_trades = (SELECT COUNT(*) FROM trades WHERE wallet_address = p_wallet_address),
        total_volume = (SELECT COALESCE(SUM(value), 0) FROM trades WHERE wallet_address = p_wallet_address),
        win_count = (SELECT COUNT(*) FROM positions WHERE wallet_address = p_wallet_address AND cash_pnl > 0),
        loss_count = (SELECT COUNT(*) FROM positions WHERE wallet_address = p_wallet_address AND cash_pnl < 0),
        total_pnl = (SELECT COALESCE(SUM(cash_pnl), 0) FROM positions WHERE wallet_address = p_wallet_address),
        updated_at = CURRENT_TIMESTAMP,
        last_stats_update = CURRENT_TIMESTAMP
    WHERE wallet_address = p_wallet_address;
    
    -- Calculate win rate
    UPDATE traders SET
        win_rate = CASE 
            WHEN (win_count + loss_count) > 0 
            THEN (win_count::DECIMAL / (win_count + loss_count)) * 100 
            ELSE 0 
        END
    WHERE wallet_address = p_wallet_address;
END;
$$ LANGUAGE plpgsql;

-- Clean expired cache
CREATE OR REPLACE FUNCTION clean_expired_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM system_cache WHERE expires_at < CURRENT_TIMESTAMP;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Additional composite indexes for common queries
CREATE INDEX idx_trades_wallet_timestamp ON trades(wallet_address, timestamp DESC);
CREATE INDEX idx_positions_wallet_open ON positions(wallet_address, is_open);
CREATE INDEX idx_markets_active_volume ON markets(is_active, volume DESC);

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Add comment explaining the schema
COMMENT ON TABLE traders IS 'Stores trader profiles and cached performance statistics';
COMMENT ON TABLE trades IS 'Historical trade records from Polymarket';
COMMENT ON TABLE positions IS 'Current and historical positions for traders';
COMMENT ON TABLE markets IS 'Market information with calculated metrics';
COMMENT ON TABLE copy_trading_follows IS 'Active copy trading relationships';
COMMENT ON TABLE copied_trades IS 'Record of all copied trades and their outcomes';

