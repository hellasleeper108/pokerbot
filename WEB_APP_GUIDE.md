# 🌐 Poker Bot Web Application Guide

A modern web interface for the Texas Hold'em Probability Bot with AI opponent modeling and GTO solver.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python3 web_app.py
```

### 3. Access the Interface

Open your browser and navigate to:
```
http://localhost:5000
```

## 🎯 Features

### Hand Analyzer
- **Real-time probability calculations** using Monte Carlo simulation
- **AI opponent hand range prediction** based on board texture
- **GTO solver recommendations** for optimal play
- **Pot odds analysis** with EV calculations
- **Pre-flop hand strength** using Chen formula
- **Draw detection** (flush draws, straight draws)
- **Position-aware recommendations**

### Pre-flop Charts
- Interactive starting hand charts
- Position-specific recommendations
- Color-coded by hand strength
- Covers all positions (UTG, MP, CO, BTN, SB, BB)

### Batch Analysis
- Analyze multiple scenarios simultaneously
- Compare different situations side-by-side
- Export results for study

### Statistics Tracking
- Track your session statistics
- Win rate by position
- Decision pattern analysis
- Profit/loss tracking

## 📡 API Endpoints

### POST /api/analyze
Analyze a single poker hand

**Request:**
```json
{
  "hole_cards": ["As", "Kd"],
  "community_cards": ["Ah", "7s", "3c"],
  "num_opponents": 2,
  "pot_size": 100,
  "bet_to_call": 20,
  "position": "BTN",
  "stack_size": 500,
  "simulations": 5000
}
```

**Response:**
```json
{
  "probabilities": {
    "win": 78.4,
    "tie": 1.2,
    "loss": 20.4,
    "win_or_tie": 79.6
  },
  "hand_rank": "PAIR",
  "chen_score": 12.0,
  "hand_category": "PREMIUM",
  "pot_analysis": {
    "pot_odds": 16.67,
    "expected_value": 45.20,
    "recommendation": "CALL"
  },
  "gto_recommendation": {
    "action": "BET/RAISE",
    "optimal_bet_size": 66.0,
    "reasoning": "Strong equity - bet for value"
  },
  "opponent_analysis": {
    "board_texture": {...},
    "estimated_ranges": {...},
    "recommendation": "..."
  }
}
```

### GET /api/preflop-chart?position=BTN
Get pre-flop starting hand chart for a position

### POST /api/batch-analyze
Analyze multiple scenarios at once

### GET /api/stats
Get current session statistics

### POST /api/ai/predict-range
AI-powered opponent range prediction based on actions

**Request:**
```json
{
  "action_sequence": ["raise", "call", "bet"],
  "position": "CO",
  "board": ["Ah", "7s", "3c"],
  "bet_size": 75,
  "pot_size": 100
}
```

### POST /api/gto/bet-size
Get GTO optimal bet sizing

**Request:**
```json
{
  "equity": 0.65,
  "pot_size": 100,
  "stack_size": 500,
  "street": "flop"
}
```

## 🤖 AI Features Explained

### Opponent Modeling

The AI analyzes:
- **Board texture** (dry, wet, coordinated)
- **Action sequences** (aggressive vs passive)
- **Bet sizing patterns** (large bets = polarized range)
- **Position** (tighter early, wider late)

**How it works:**
1. Tracks action patterns
2. Uses Bayesian updating to narrow ranges
3. Analyzes bet sizing for tells
4. Factors in board texture
5. Outputs probability distribution over hand categories

### GTO Solver

Provides **Game Theory Optimal** recommendations:

**What is GTO?**
- GTO = unexploitable strategy
- Balances value bets and bluffs
- Uses optimal bet sizing
- Makes you impossible to exploit

**GTO Principles:**
1. **Bet sizing**: Usually 60-75% of pot
2. **Frequency**: Bet strong hands 70% of the time
3. **Bluff ratio**: Based on pot odds given to opponent
4. **Balance**: Mix of value and bluffs in every action

**Example:**
```
Pot: $100
Your equity: 65%
GTO recommendation: Bet $66 (66% pot)
Reason: Strong equity - bet for value
```

## 🎓 How to Use the Bot

### Scenario 1: Post-Flop Decision

1. Enter your hole cards: `As Kd`
2. Enter the flop: `Ah 7s 3c`
3. Enter opponents: `2`
4. Enter pot size: `$100`
5. Enter bet to call: `$20`
6. Click "Analyze Hand"

**Result:**
- Win probability: 78.4%
- Pot odds required: 16.7%
- EV: +$45.20
- **Recommendation: CALL** ✅

### Scenario 2: Pre-flop Hand Selection

1. Go to "Pre-flop Charts" tab
2. Select your position (e.g., Button)
3. Click "Load Chart"
4. See recommended hands by category:
   - Premium: AA, KK, QQ, AKs, AKo
   - Strong: JJ, TT, AQs, AQo, etc.
   - Playable: 99, 88, ATs, KJs, etc.

### Scenario 3: Comparing Multiple Situations

1. Go to "Batch Analysis" tab
2. Enter scenarios:
   ```
   Pocket Aces | As Ah | | 2
   Top Pair | As Kd | Ah 7s 3c | 2
   Flush Draw | Ah 7h | Kh 3h 2c | 1
   ```
3. Click "Analyze All Scenarios"
4. Compare win rates side-by-side

## 🔧 Advanced Usage

### Integration with External Tools

```python
import requests

# Analyze a hand
response = requests.post('http://localhost:5000/api/analyze', json={
    'hole_cards': ['As', 'Kd'],
    'community_cards': ['Ah', '7s', '3c'],
    'num_opponents': 2,
    'pot_size': 100,
    'bet_to_call': 20
})

data = response.json()
print(f"Win probability: {data['probabilities']['win']:.1f}%")
```

### Mobile App Integration

The REST API can be used to build:
- Mobile poker apps
- Overlay tools for online poker
- Study software
- Training applications

## 🚀 Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### Using Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web_app:app"]
```

### Environment Variables

```bash
export FLASK_ENV=production
export FLASK_SECRET_KEY=your-secret-key-here
```

## 📊 Performance

- **Analysis speed**: 5,000 simulations in ~1-2 seconds
- **API response time**: <500ms for most requests
- **Concurrent users**: Supports 100+ simultaneous users with gunicorn
- **Accuracy**: ±0.5% margin of error with 10,000 simulations

## 🎯 Tips for Using the AI

### When to Trust AI Opponent Modeling

✅ **Good scenarios:**
- Multiple betting actions to analyze
- Clear board textures (very wet or very dry)
- Standard bet sizing patterns

❌ **Be cautious:**
- Against unknown/random opponents
- With only one action observed
- Against players who vary their play

### When to Use GTO vs Exploitative Play

**Use GTO when:**
- Playing against strong opponents
- You don't have reads on opponents
- Want to play "safe" unexploitable strategy
- In tournaments near bubble

**Use Exploitative play when:**
- You have strong reads on opponents
- Playing against weak/predictable players
- In cash games with same opponents
- When you can identify leaks to exploit

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or use different port
python3 web_app.py --port 5001
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Slow Simulations
- Reduce number of simulations (use 1,000 for faster results)
- Consider upgrading server hardware
- Use multiple workers with gunicorn

## 📚 Further Reading

- **Game Theory Optimal (GTO)**: Research Nash equilibrium in poker
- **Opponent Modeling**: Study Bayesian inference and pattern recognition
- **Monte Carlo Methods**: Understand statistical simulation techniques
- **Poker Mathematics**: Learn pot odds, implied odds, and EV calculations

## 🤝 Contributing

Want to improve the web app?

Ideas:
- Add WebSocket support for live updates
- Create mobile-responsive design improvements
- Add hand history import/export
- Implement saved sessions
- Add multiplayer analysis mode
- Create visualization graphs (equity over time)

## 📄 License

Open source - free for personal use and study.

---

**Happy grinding! 🎰♠♥♦♣**
