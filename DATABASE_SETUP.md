# Database Setup Guide

## Overview

This guide explains how to set up a PostgreSQL database for persistent data storage in the Polymarket Whale Tracker application.

---

## Why Database Integration?

Currently, the application relies on:
- **In-memory caching**: Data is lost when the app restarts
- **API calls**: Every page load requires fresh API requests
- **No historical tracking**: Can't track trader performance over time

With database integration, you get:
- ✅ **Persistent storage**: Data survives app restarts
- ✅ **Historical tracking**: Track trader performance over weeks/months
- ✅ **Faster load times**: Cache frequently accessed data
- ✅ **Advanced analytics**: Query historical trends and patterns
- ✅ **Copy trading history**: Track which trades were copied and their outcomes

---

## Prerequisites

### Option 1: PostgreSQL (Recommended)
- PostgreSQL 12+ installed
- Access to create databases

### Option 2: MySQL
- MySQL 8.0+ installed  
- Minor schema adjustments needed

---

## Installation

### PostgreSQL on macOS
```bash
# Install via Homebrew
brew install postgresql

# Start PostgreSQL
brew services start postgresql

# Create database
createdb polymarket_tracker
```

### PostgreSQL on Ubuntu/Debian
```bash
# Install
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database
sudo -u postgres createdb polymarket_tracker
```

### PostgreSQL on Windows
1. Download from https://www.postgresql.org/download/windows/
2. Run installer
3. Use pgAdmin to create database

---

## Database Setup

### 1. Create Database
```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE polymarket_tracker;

# Create user (optional but recommended)
CREATE USER polymarket_user WITH ENCRYPTED PASSWORD 'your_secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE polymarket_tracker TO polymarket_user;

# Exit
\q
```

### 2. Import Schema
```bash
# Navigate to project directory
cd /path/to/polybotw

# Import schema
psql -d polymarket_tracker -f database_schema.sql

# Or if using custom user:
psql -U polymarket_user -d polymarket_tracker -f database_schema.sql
```

### 3. Verify Installation
```bash
# Connect to database
psql -d polymarket_tracker

# List tables
\dt

# You should see tables like:
# - traders
# - trades
# - positions
# - markets
# - copy_trading_follows
# - etc.

# Exit
\q
```

---

## Python Integration

### 1. Install Required Packages
```bash
pip install psycopg2-binary sqlalchemy
```

Or add to `requirements.txt`:
```txt
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
```

### 2. Configuration

Create `.env` file (or update existing):
```bash
# Database Configuration
DATABASE_URL=postgresql://polymarket_user:your_secure_password@localhost:5432/polymarket_tracker

# Or for default user:
DATABASE_URL=postgresql://localhost:5432/polymarket_tracker
```

### 3. Database Connection Module

Create `polymarket/database.py`:
```python
"""Database connection and ORM setup."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/polymarket_tracker')

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4. Example Model Usage

Create `polymarket/models_db.py`:
```python
"""Database models using SQLAlchemy ORM."""

from sqlalchemy import Column, Integer, String, Decimal, Boolean, DateTime, Text
from sqlalchemy.sql import func
from .database import Base

class Trader(Base):
    """Trader model."""
    __tablename__ = 'traders'
    
    id = Column(Integer, primary_key=True)
    wallet_address = Column(String(42), unique=True, nullable=False)
    display_name = Column(String(100))
    pseudonym = Column(String(100))
    profile_image_url = Column(Text)
    bio = Column(Text)
    
    # Statistics
    total_volume = Column(Decimal(20, 2), default=0)
    total_trades = Column(Integer, default=0)
    win_rate = Column(Decimal(5, 2), default=0)
    total_pnl = Column(Decimal(20, 2), default=0)
    roi_percentage = Column(Decimal(10, 2), default=0)
    trader_tier = Column(String(50))
    risk_score = Column(Decimal(5, 2), default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class Trade(Base):
    """Trade model."""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    transaction_hash = Column(String(66), unique=True, nullable=False)
    wallet_address = Column(String(42), nullable=False)
    
    # Trade details
    market_condition_id = Column(String(66))
    market_slug = Column(String(200))
    market_title = Column(Text)
    side = Column(String(10), nullable=False)
    size = Column(Decimal(20, 8), nullable=False)
    price = Column(Decimal(10, 8), nullable=False)
    value = Column(Decimal(20, 2), nullable=False)
    timestamp = Column(Integer, nullable=False)
    
    is_whale_trade = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
```

### 5. Integration with App

Update `app.py`:
```python
from polymarket.database import get_db, engine
from polymarket.models_db import Trader, Trade

# Initialize database tables
from polymarket.database import Base
Base.metadata.create_all(bind=engine)

# Use in routes
@app.route('/api/traders/cached')
def get_cached_traders():
    """Get traders from database cache."""
    db = next(get_db())
    traders = db.query(Trader).order_by(Trader.total_volume.desc()).limit(20).all()
    
    return jsonify({
        'success': True,
        'traders': [{
            'wallet': t.wallet_address,
            'name': t.display_name or t.pseudonym,
            'volume': float(t.total_volume),
            'win_rate': float(t.win_rate),
            'tier': t.trader_tier
        } for t in traders]
    })
```

---

## Data Population Strategies

### Strategy 1: Background Worker
Create a background task that periodically fetches and stores data:

```python
import time
import threading
from polymarket.database import get_db
from polymarket.models_db import Trader, Trade

def populate_database_worker():
    """Background worker to populate database."""
    while True:
        try:
            # Fetch whale trades
            whale_trades = whale_tracker.get_recent_whales(limit=100)
            
            db = next(get_db())
            
            # Store trades
            for trade in whale_trades:
                existing = db.query(Trade).filter_by(
                    transaction_hash=trade['transactionHash']
                ).first()
                
                if not existing:
                    new_trade = Trade(
                        transaction_hash=trade['transactionHash'],
                        wallet_address=trade['wallet'],
                        market_condition_id=trade['conditionId'],
                        market_title=trade['market'],
                        side=trade['side'],
                        size=trade['size'],
                        price=trade['price'],
                        value=trade['value'],
                        timestamp=trade['timestamp'],
                        is_whale_trade=True
                    )
                    db.add(new_trade)
                
                # Update or create trader
                trader = db.query(Trader).filter_by(
                    wallet_address=trade['wallet']
                ).first()
                
                if not trader:
                    trader = Trader(
                        wallet_address=trade['wallet'],
                        display_name=trade['trader']
                    )
                    db.add(trader)
            
            db.commit()
            print(f"✅ Stored {len(whale_trades)} trades")
            
        except Exception as e:
            print(f"❌ Error populating database: {e}")
        
        time.sleep(60)  # Run every minute

# Start worker
threading.Thread(target=populate_database_worker, daemon=True).start()
```

### Strategy 2: On-Demand Updates
Update database when users visit pages:

```python
@app.route('/trader/<wallet_address>')
def trader_profile(wallet_address):
    """Trader profile with database caching."""
    db = next(get_db())
    
    # Check if trader exists in database
    trader = db.query(Trader).filter_by(wallet_address=wallet_address).first()
    
    # If not exists or data is stale, fetch from API
    if not trader or (trader.updated_at < datetime.now() - timedelta(hours=1)):
        stats = trader_analytics.calculate_trader_stats(wallet_address)
        
        if not trader:
            trader = Trader(wallet_address=wallet_address)
            db.add(trader)
        
        # Update trader stats
        trader.total_volume = stats['total_volume']
        trader.total_trades = stats['total_trades']
        trader.win_rate = stats['win_rate']
        trader.total_pnl = stats['total_pnl']
        trader.roi_percentage = stats['roi_percentage']
        trader.trader_tier = stats['trader_tier']
        trader.risk_score = stats['risk_score']
        
        db.commit()
    
    return render_template('trader_profile.html', wallet=wallet_address)
```

---

## Maintenance

### Backup Database
```bash
# Create backup
pg_dump polymarket_tracker > backup_$(date +%Y%m%d).sql

# Restore from backup
psql polymarket_tracker < backup_20241006.sql
```

### Clean Old Data
```sql
-- Delete old cache entries
DELETE FROM system_cache WHERE expires_at < NOW();

-- Archive old trades (keep last 90 days)
DELETE FROM trades WHERE timestamp < EXTRACT(EPOCH FROM NOW() - INTERVAL '90 days');
```

### Optimize Performance
```sql
-- Analyze tables for query optimization
ANALYZE traders;
ANALYZE trades;
ANALYZE positions;

-- Reindex if needed
REINDEX TABLE traders;
REINDEX TABLE trades;
```

---

## Monitoring

### Check Database Size
```sql
SELECT pg_size_pretty(pg_database_size('polymarket_tracker'));
```

### View Table Sizes
```sql
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Check Active Connections
```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'polymarket_tracker';
```

---

## Troubleshooting

### Connection Issues
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Or on Linux:
sudo systemctl status postgresql

# Check connection
psql -d polymarket_tracker -c "SELECT 1"
```

### Permission Issues
```sql
-- Grant all permissions to user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO polymarket_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO polymarket_user;
```

### Performance Issues
- Add more indexes for frequently queried columns
- Use connection pooling (pgbouncer)
- Increase PostgreSQL memory settings in postgresql.conf
- Archive old data to separate tables

---

## Next Steps

Once database is set up:

1. ✅ **Test connection** from Python
2. ✅ **Start background worker** to populate data
3. ✅ **Update API routes** to use database caching
4. ✅ **Implement copy trading storage**
5. ✅ **Add historical performance tracking**

---

## Support

For database-related issues:
- Check PostgreSQL logs: `/usr/local/var/log/postgres.log` (macOS)
- Review SQLAlchemy documentation: https://www.sqlalchemy.org/
- PostgreSQL documentation: https://www.postgresql.org/docs/

---

## Security Best Practices

1. **Never commit database passwords** to version control
2. **Use strong passwords** for database users
3. **Limit database access** to localhost unless needed
4. **Regular backups** of important data
5. **Monitor for unusual activity** in database logs
6. **Use SSL connections** for production deployments

