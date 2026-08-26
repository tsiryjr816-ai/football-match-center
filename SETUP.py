#!/usr/bin/env python3
"""
Football Match Center - Quick Setup Guide
"""

print("""
⚽ FOOTBALL MATCH CENTER - SETUP
================================

✅ FILES CREATED:
  1. collector.py          - Data collection script
  2. prediction_engine.js  - Match prediction algorithm
  3. .env.example          - Environment template
  4. .gitignore           - Git exclusions

📋 STEP-BY-STEP SETUP:

1️⃣  GET API KEY:
    Visit: https://www.football-data.org/client/register
    (FREE tier available!)

2️⃣  CONFIGURE:
    cp .env.example .env
    Edit .env and add your API key

3️⃣  RUN COLLECTOR:
    pip install requests
    python collector.py
    
    ✨ This updates matches.json with:
       - Last 30 days of matches
       - Next 7 days upcoming
       - 5 major leagues (PL, La Liga, Serie A, Bundesliga, Ligue 1)

4️⃣  OPEN IN BROWSER:
    Open index.html in your browser
    
    🎯 Features:
       ✓ Live match tracking
       ✓ Match predictions (65%+ confidence)
       ✓ Head-to-head analysis
       ✓ Form analysis
       ✓ Mobile responsive

📊 PREDICTION SCORES:

Confidence levels:
  • 85-100% - Strong prediction
  • 70-84%  - Solid prediction  
  • 65-69%  - Weak signal
  • <65%    - Insufficient data

Factors considered:
  • Head-to-head (30%)
  • Recent form (25%)
  • Home advantage (15%)
  • Betting patterns (20%)
  • Momentum (10%)

🔄 UPDATE DATA:

Schedule collector to run periodically:
  
  # Every 6 hours (Linux/Mac)
  0 */6 * * * cd /path/to/repo && python collector.py

⚠️  NOTES:

  • Predictions need 2+ finished H2H matches
  • More data = higher accuracy
  • API free tier: 10 requests/min limit
  • Data cached client-side for performance

📚 RESOURCES:

  • Football-data.org: https://www.football-data.org
  • API Docs: https://www.football-data.org/documentation
  • Prediction Algorithm: See prediction_engine.js

💡 IMPROVEMENTS FOR FUTURE:

  [ ] Machine learning model for better accuracy
  [ ] Player stats integration
  [ ] Injury data
  [ ] Team standings consideration
  [ ] Expected Goals (xG) analysis
  [ ] Live score updates (WebSocket)
  [ ] Bet placement tracker
  [ ] Historical accuracy metrics

🎯 CURRENT STATUS:

✅ Collector ready
✅ Predictions implemented
✅ UI with confidence scores
⏳ Awaiting data population

Start now:
  1. Get API key
  2. python collector.py
  3. Open index.html

Need help? Check prediction_engine.js for algorithm details.
""")
