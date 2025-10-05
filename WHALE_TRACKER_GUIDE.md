# 🐋 Whale Activity Tracker Guide

## What You Have Now

A complete **real-time whale activity monitoring system** that tracks large trades (≥$10,000) on Polymarket and displays them with full details.

## 🌐 Access Your Dashboard

```
http://localhost:8080
```

Click the **"🐋 Whale Activity"** tab to see live whale trades.

## 📊 What Data Is Displayed

### Full Trade Information:
- ✅ **Market Name** - Full market title (e.g., "Will PSG win the 2025–26 Champions League?")
- ✅ **Outcome** - What side they bet on (Yes/No, Up/Down, etc.)
- ✅ **Trader Name** - Username or pseudonym
- ✅ **Trade Value** - Total USD value of the trade
- ✅ **Trade Size** - Number of shares @ price per share
- ✅ **Timestamp** - When the trade happened
- ✅ **Direct Link** - Click "🔗 View" to open on Polymarket
- ✅ **Wallet Address** - Hover over trader name to see full wallet
- ✅ **Condition ID** - Unique market identifier

### Example Data Showing:
```
Time: 11:00:22
Market: Will PSG win the 2025–26 Champions League?
Outcome: Yes
Trader: Coinfighter
Side: BUY
Value: $32,156
Size: 214,376 shares @ $0.1500
Link: 🔗 View (clickable to Polymarket)
```

## 🎯 Features

### 1. Real-Time Monitoring
- Checks for new whales every **5 seconds**
- Frontend updates every **10 seconds**
- No manual refresh needed

### 2. Live Alerts
- New whale trades slide in automatically
- Shows last 5 alerts at the top
- Each alert includes:
  - Market name with direct link
  - Trader info
  - Trade details
  - Outcome they bet on

### 3. Historical Table
- Shows last 20 whale trades
- Sortable columns
- All data in one view
- Clickable links to markets

### 4. Desktop Notifications (Optional)
- Browser popup alerts for new whales
- Works even when tab is in background
- Shows trader and market info

## 🔗 Market Links

All markets have direct links to Polymarket:
```
https://polymarket.com/event/[market-slug]
```

Example:
- Market: "Will PSG win the 2025–26 Champions League?"
- Link: https://polymarket.com/event/will-psg-win-the-202526-champions-league

## 💻 Run Standalone CLI Version

For terminal-only monitoring:

```bash
cd /Users/pratibhagautam/polybotw
python3 whale_tracker.py
```

This will print alerts directly to your terminal:
```
🐋 WHALE ALERT! Unusual Bet Activity Detected

💰 Value: $32,156.36
📊 Market: Will PSG win the 2025–26 Champions League?
🎯 Side: BUY (Yes)
👤 Trader: Coinfighter
📈 Size: 214,375 shares @ $0.1500
⏰ Time: 2025-10-05 11:00:22
🔗 Transaction: 0x2ac0d47...
```

## ⚙️ Customization

### Change Minimum Trade Amount

Edit `app.py`:
```python
# Line 17: Change from $10,000 to any amount
whale_tracker = WhaleTracker(min_trade_amount=5000)  # $5k minimum
```

Or for CLI version, edit `whale_tracker.py`:
```python
tracker = WhaleTracker(min_trade_amount=20000)  # $20k minimum
```

### Change Update Frequency

Edit `app.py`:
```python
# Line 22: Change polling interval (seconds)
whale_tracker.run_monitor(interval=10)  # Check every 10 seconds instead of 5
```

Edit `templates/index.html` (line 662):
```javascript
// Change frontend check interval
setInterval(checkForNewWhales, 5000);  // Check every 5 seconds instead of 10
```

## 🚀 Starting/Stopping

### Start
```bash
cd /Users/pratibhagautam/polybotw
python3 app.py
```

### Stop
```bash
pkill -f "python3 app.py"
```

### Check Status
```bash
lsof -ti:8080
```
If it returns a number, server is running.

## 📱 API Endpoints

Access whale data programmatically:

### Get Recent Whales
```bash
curl "http://localhost:8080/api/whale-activity?limit=20"
```

### Get New Whales Only
```bash
curl "http://localhost:8080/api/whale-activity/live"
```

### Response Format
```json
{
  "success": true,
  "count": 3,
  "whales": [
    {
      "market": "Will PSG win the 2025–26 Champions League?",
      "marketSlug": "will-psg-win-the-202526-champions-league",
      "trader": "Coinfighter",
      "wallet": "0xefb8d10a3fc82297b2e53538bb93a1c73215c8e1",
      "side": "BUY",
      "outcome": "Yes",
      "value": 32156.36,
      "size": 214375.72,
      "price": 0.15,
      "timestamp": 1759642222,
      "transactionHash": "0x2ac0d479...",
      "conditionId": "0x6e9f90a6...",
      "iconUrl": "https://..."
    }
  ]
}
```

## 🎨 What Your Users See

### Dashboard View:
1. **Stats Cards** (top) - Total volume, liquidity, active markets
2. **Three Tabs**:
   - Markets - Browse all markets
   - Events - Major events
   - **🐋 Whale Activity** - Live whale tracking

### Whale Activity Tab:
1. **Alert Banner** - "Monitoring trades ≥ $10,000"
2. **Live Alerts** (top) - New whales slide in automatically
3. **Historical Table** - Last 20 whale trades with all details
4. **Auto-refresh** - Updates every 10 seconds

## 💡 Use Cases

### For Your Users:
- ✅ **Follow smart money** - See what experienced traders are betting on
- ✅ **Market sentiment** - Understand where big money is moving
- ✅ **Early signals** - Catch large bets before price moves
- ✅ **Decision support** - Use whale activity to inform their bets
- ✅ **Learn from pros** - See how successful traders position themselves

### What Makes It Valuable:
1. **Real-time** - 5-second updates, faster than manually checking
2. **Filtered** - Only significant trades (≥$10k), no noise
3. **Complete info** - Market, trader, outcome, links - everything needed
4. **No trading required** - Read-only, zero risk, pure data
5. **Direct links** - One click to bet on same markets as whales

## 🔐 Data Source

- **Source**: Polymarket Data API (`/trades` endpoint)
- **Filter**: `filterType=CASH&filterAmount=10000`
- **Rate Limit**: 30 requests / 10 seconds
- **Authentication**: None required (public data)
- **Update Frequency**: Every 5 seconds

## 📊 Current Live Example

Real whale trades being tracked right now:

1. **Coinfighter** - $32,156 BUY on "Will PSG win the 2025–26 Champions League?" (Yes)
2. **aenews2** - $18,182 BUY on Box Office prediction (No)
3. **CCPig** - $14,100 SELL on "Xi Jinping out in 2025?" (No)
4. **dubdubdub2** - $32,000 BUY on various markets
5. **Jayachamarajendra** - $45,411 BUY

## ✅ Everything Working

- ✅ Market names displaying correctly
- ✅ Trader names showing (not wallet addresses)
- ✅ Outcomes visible (Yes/No, Up/Down)
- ✅ Direct links to Polymarket working
- ✅ Real-time updates every 5-10 seconds
- ✅ Value calculations accurate
- ✅ Trade details complete
- ✅ Historical data preserved
- ✅ Desktop notifications supported
- ✅ Mobile responsive design

## 🎉 You're All Set!

Your whale tracker is **live and fully functional** at:
```
http://localhost:8080
```

Click the **🐋 Whale Activity** tab and watch the whales swim! 🐋📈
