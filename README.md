# Texas Hold'em Probability Bot - Enhanced Edition

A comprehensive poker assistant that calculates win probabilities and provides expert decision-making guidance using Monte Carlo simulation. Now with advanced features including colored output, draw detection, pre-flop rankings, and multiple analysis modes!

## 🎯 Features

### Core Features
- **Monte Carlo Simulation**: Accurate probability calculations using thousands of simulations
- **Complete Hand Evaluation**: Correctly ranks all poker hands from high card to royal flush
- **Multi-opponent Support**: Calculate probabilities against 1-9 opponents
- **Real-time Analysis**: Get probabilities at pre-flop, flop, turn, and river

### Enhanced Features (NEW!)
- **🎨 Colored Terminal Output**: Beautiful color-coded interface for better readability
- **📊 Visual Progress Bars**: Live progress tracking during simulations
- **🃏 Pre-flop Hand Rankings**: Chen formula-based hand strength analysis
- **🎯 Draw Detection**: Automatic detection of flush draws and straight draws
- **🔢 Outs Calculator**: Calculates your outs and improvement probabilities
- **💰 Expected Value (EV) Calculator**: Precise EV calculations for bet sizing decisions
- **⚡ Quick Analysis Mode**: Fast command-line analysis for quick lookups
- **📋 Batch Analysis Mode**: Analyze multiple scenarios at once and compare them
- **✅ Enhanced Error Handling**: Robust input validation and helpful error messages

### Professional Tools
- **📈 Pre-flop Range Charts**: Position-aware starting hand recommendations with visual grid
- **📊 Statistics Tracker**: Track and analyze your poker sessions with detailed metrics
- **💾 Export Results**: Save analysis to JSON, CSV, HTML, or Markdown formats
- **🎲 Hand Range Analysis**: Comprehensive pre-flop hand strength calculator
- **📉 Session Tracking**: Monitor win rates, profit/loss, and decision patterns

### 🌐 Web Application & AI (NEWEST!)
- **🌐 Modern Web Interface**: Beautiful responsive web UI with real-time analysis
- **🤖 AI Opponent Modeling**: Machine learning-based hand range prediction
- **🎯 GTO Solver**: Game Theory Optimal strategy recommendations
- **📡 REST API**: Full API for mobile apps and external integrations
- **⚡ Real-time Calculations**: Instant probability updates in the browser
- **🔮 Predictive Analytics**: AI-powered opponent tendency analysis

## 🚀 Quick Start

### Installation

#### Command-Line Tools (No Dependencies)
```bash
# Clone or download the repository
cd pokerbot

# No installation needed - pure Python!
python3 poker_bot_enhanced.py
```

#### Web Application (Requires Flask)
```bash
# Install dependencies
pip install -r requirements.txt

# Start web server
python3 web_app.py

# Open browser to http://localhost:5000
```

### Basic Usage

#### 🌐 Web Interface (Recommended!)
```bash
python3 web_app.py
# Then visit: http://localhost:5000
```

**Features:**
- Beautiful modern UI with real-time analysis
- AI opponent modeling
- GTO solver recommendations
- Interactive charts and graphs
- Mobile-friendly responsive design

#### Command-Line Tools
```bash
# Interactive enhanced mode
python3 poker_bot_enhanced.py

# Quick analysis from command line
python3 quick_analyze.py "As Kd" "Ah 7s 3c" --opponents 2

# Batch analysis of multiple scenarios
python3 batch_analyze.py scenarios.txt

# Pre-flop range charts
python3 preflop_charts.py

# Statistics tracker
python3 stats_tracker.py

# Export results
python3 export_results.py

# Original simple mode
python3 poker_bot.py
```

## 📖 Usage Modes

### 1. Enhanced Interactive Mode

The main enhanced interface with all features:

```bash
python3 poker_bot_enhanced.py
```

Features:
- Beautiful colored output
- Pre-flop Chen formula analysis
- Draw detection and outs calculation
- Visual probability bars
- EV calculations
- Progress tracking

**Example Session:**
```
════════════════════════════════════════════════════════════
              TEXAS HOLD'EM PROBABILITY BOT - ENHANCED
════════════════════════════════════════════════════════════

Your Hand: A♠ K♦
Opponents: 2

Hand Strength (Chen Formula):
  Score: 12.0
  Category: PREMIUM

Calculating pre-flop win probability (5000 simulations)...
[████████████████████████████████████████] 100.0%

Win Probabilities:
  Win          [████████████████░░░░░░░░░░░░░░░] 46.2%
  Tie          [█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 2.1%
  Loss         [█████████████████░░░░░░░░░░░░░░] 51.7%
```

### 2. Quick Analysis Mode

Fast command-line analysis for quick lookups:

```bash
# Basic usage
python3 quick_analyze.py "As Kd" "Ah 7s 3c" --opponents 2

# Pre-flop analysis
python3 quick_analyze.py "Jh Jd" --opponents 3

# High precision
python3 quick_analyze.py "As Kd" "Ah Kh Qh" --simulations 20000
```

**Options:**
- `-o, --opponents N`: Number of opponents (default: 1)
- `-s, --simulations N`: Number of simulations (default: 5000)
- `--no-color`: Disable colored output

**Example Output:**
```
═══════════════════════════════════════════════════════════
QUICK POKER ANALYSIS
═══════════════════════════════════════════════════════════

Your Hand: A♠ K♦
Board:     A♥ 7♠ 3♣
Current:   PAIR
Opponents: 2

Running 5000 simulations...

PROBABILITIES
  Win  [████████████████████████████████░░░░░░░░] 78.4%
  Tie  [█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]  1.2%
  Loss [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 20.4%

Win or Tie: 79.60%
```

### 3. Batch Analysis Mode

Analyze multiple scenarios from a file:

```bash
# Create example file
python3 batch_analyze.py --create-example

# Analyze scenarios
python3 batch_analyze.py example_scenarios.txt

# Detailed output
python3 batch_analyze.py scenarios.txt --detailed

# High precision
python3 batch_analyze.py scenarios.txt --simulations 10000
```

**Scenario File Format:**
```
# Comments start with #
Name | Hole Cards | Community Cards | Opponents

# Examples:
Pocket Aces | As Ah | | 2
Flush draw | Ah 7h | Kh 3h 2c | 1
Top pair | As Kd | Ah 7s 3c | 2
```

**Options:**
- `-s, --simulations N`: Simulations per scenario (default: 3000)
- `--sort [win|name]`: Sort results by win rate or name
- `--detailed`: Show detailed results for each scenario
- `--create-example`: Create an example scenarios file

**Example Output:**
```
════════════════════════════════════════════════════════════
                  BATCH ANALYSIS RESULTS
════════════════════════════════════════════════════════════

Scenario                       Hand                 Win %   Tie %  Loss %
────────────────────────────────────────────────────────────────────────
Pocket Aces                    As Ah                 73.2%   0.8%  26.0%
Top pair                       As Kd                 78.4%   1.2%  20.4%
Flush draw                     Ah 7h                 32.1%   0.3%  67.6%

Analyzed 3 scenarios
```

### 4. Pre-flop Range Charts

Visual starting hand recommendations based on position:

```bash
python3 preflop_charts.py
```

**Features:**
- Position-aware hand ranges (UTG, MP, CO, BTN, Blinds)
- Visual hand strength grid with color coding
- Specific hand recommendations with action advice
- Range percentage calculations

**Options:**
1. View hand strength grid - See all 169 starting hands color-coded by strength
2. View position-specific chart - Get recommendations for specific positions
3. Get hand recommendation - Get specific advice for your hand and position
4. View all positions - See recommended ranges for all positions

**Example:**
```
Hand: A♠ K♦
Position: Button
Category: PREMIUM

→ ACTION: RAISE
Premium hand - always raise
```

### 5. Statistics Tracker

Track and analyze your poker sessions:

```bash
python3 stats_tracker.py
```

**Features:**
- Session tracking with win/loss records
- Position-based win rate analysis
- Decision pattern tracking (raise, call, fold frequencies)
- Profit/loss calculations
- Hand category distribution
- Recent hands review

**Stored Data:**
- Hand notation and category
- Position played from
- Pre-flop decision
- Equity percentage
- Outcome (win/loss/fold)
- Profit/loss amount

### 6. Export Results

Export your analysis to various formats:

```bash
python3 export_results.py
```

**Supported Formats:**
- **JSON**: Machine-readable format with full metadata
- **CSV**: Spreadsheet-compatible for Excel/Google Sheets
- **HTML**: Beautiful styled reports with progress bars
- **Markdown**: GitHub-compatible documentation format

**Use Cases:**
- Share analysis with study groups
- Import into spreadsheets for further analysis
- Create poker study materials
- Document hand histories

## 📊 Understanding the Analysis

### Pre-flop Hand Strength (Chen Formula)

The bot uses the Chen formula to rate pre-flop hands:

| Score | Category | Description | Examples |
|-------|----------|-------------|----------|
| 12+ | PREMIUM | Best starting hands | AA, KK, AKs |
| 8-11 | STRONG | Very playable | QQ, AK, JJ |
| 6-7 | PLAYABLE | Good in position | 99, AJ, KQs |
| 4-5 | MARGINAL | Situational | 88, A9, KJ |
| <4 | WEAK | Usually fold | 72o, J3, etc. |

### Draw Detection

The bot automatically detects:

**Flush Draws** (9 outs):
- 4 cards of the same suit after flop/turn
- ~35% to hit by river (from flop)
- ~18% to hit on next card

**Straight Draws**:
- Open-ended (8 outs): ~32% by river, ~17% next card
- Gutshot (4 outs): ~16% by river, ~8% next card

### Pot Odds Analysis

**Pot Odds** = Amount to Call / (Pot Size + Amount to Call)

**Recommendation Logic:**
- ✅ **CALL**: Your equity > pot odds (positive expected value)
- ❌ **FOLD**: Your equity < pot odds (negative expected value)

**Example:**
```
Pot: $100
Bet to call: $20
Pot odds: 16.7% (you need 16.7% equity to call)
Your equity: 32%
→ CALL (profitable long-term)
```

### Expected Value (EV)

**EV** = (Win% × Total Pot) - (Loss% × Call Amount)

- **Positive EV**: Profitable call
- **Negative EV**: Unprofitable call

## 🎴 Card Format

Enter cards using: **Rank + Suit**

**Ranks**: `A` `K` `Q` `J` `10` `9` `8` `7` `6` `5` `4` `3` `2`

**Suits**:
- `s` = ♠ Spades
- `h` = ♥ Hearts
- `d` = ♦ Diamonds
- `c` = ♣ Clubs

**Examples**:
- `As` = Ace of Spades
- `Kh` = King of Hearts
- `10d` = Ten of Diamonds
- `2c` = Two of Clubs

## 💡 Advanced Tips

### Using the Bot Effectively

1. **Pre-flop**: Use Chen score to understand starting hand strength
2. **Post-flop**: Check for draws and calculate outs
3. **Decision Making**: Compare your equity to pot odds
4. **EV Calculation**: Use EV for optimal bet sizing
5. **Batch Analysis**: Compare similar situations to learn patterns

### Simulation Accuracy

| Simulations | Accuracy | Speed | Best For |
|-------------|----------|-------|----------|
| 1,000 | ±2% | Very Fast | Quick checks |
| 5,000 | ±1% | Fast | Default (good balance) |
| 10,000 | ±0.5% | Medium | Important decisions |
| 20,000+ | ±0.2% | Slow | Maximum precision |

### Tournament vs Cash Games

**Cash Games**: Follow pot odds strictly
- Call when equity > pot odds
- Focus on +EV decisions

**Tournaments**: Consider ICM and survival
- May need >10% more equity than pot odds
- Factor in stack sizes and bubble situations

## 🔧 Using as a Library

Import components into your own Python code:

```python
from poker_bot_enhanced import (
    Card, Rank, Suit,
    HandEvaluator, ProbabilityCalculator,
    PreFlopAnalyzer, DrawAnalyzer
)

# Create cards
hole = [Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)]
flop = [Card(Rank.ACE, Suit.HEARTS), Card(Rank.SEVEN, Suit.SPADES),
        Card(Rank.THREE, Suit.CLUBS)]

# Calculate probabilities
prob = ProbabilityCalculator.calculate_win_probability(
    hole_cards=hole,
    community_cards=flop,
    num_opponents=2,
    num_simulations=10000
)
print(f"Win probability: {prob['win']*100:.1f}%")

# Evaluate hand
hand_rank, _ = HandEvaluator.evaluate_hand(hole + flop)
print(f"Current hand: {hand_rank.name}")

# Chen formula
chen_score = PreFlopAnalyzer.calculate_chen_formula(hole)
print(f"Chen score: {chen_score:.1f}")

# Draw analysis
draws = DrawAnalyzer.analyze_draws(hole, flop)
for draw_name, outs in draws['draws']:
    print(f"{draw_name}: {outs} outs")
```

## 📚 Files Overview

| File | Purpose |
|------|---------|
| `poker_bot.py` | Original simple interactive bot |
| `poker_bot_enhanced.py` | Enhanced bot with all features |
| `quick_analyze.py` | Command-line quick analysis tool |
| `batch_analyze.py` | Batch scenario analyzer |
| `preflop_charts.py` | Position-aware pre-flop range charts (NEW!) |
| `stats_tracker.py` | Session statistics tracker (NEW!) |
| `export_results.py` | Export results to JSON/CSV/HTML/MD (NEW!) |
| `test_poker_bot.py` | Test suite for core functionality |
| `example_scenarios.txt` | Example batch analysis scenarios |
| `README.md` | This documentation |

## 🎯 Example Scenarios

### Scenario 1: Pre-flop Premium Hand
```bash
python3 quick_analyze.py "As Ah" --opponents 3
# Expected: ~65-75% win rate
```

### Scenario 2: Flush Draw
```bash
python3 quick_analyze.py "Ah 7h" "Kh 3h 2c" --opponents 1
# Should detect flush draw with 9 outs
```

### Scenario 3: Coin Flip
```bash
python3 quick_analyze.py "As Kd" "7h 7d 2c" --opponents 1
# Expected: ~50% each (classic race situation)
```

### Scenario 4: Dominated Hand
```bash
python3 quick_analyze.py "Ah Qd" "As Kh" --opponents 1
# Expected: ~25-30% (dominated by better kicker)
```

## ⚠️ Limitations

- **Assumes random opponent hands**: Doesn't model specific ranges
- **Showdown equity only**: Doesn't account for fold equity or bluffs
- **No position awareness**: Doesn't factor in position advantage
- **No stack depth consideration**: All-in situations only
- **No ICM calculations**: Tournament equity not modeled

## 🎓 Educational Use

This bot is perfect for:
- Learning pot odds and equity calculations
- Understanding pre-flop hand strength
- Practicing bankroll management
- Studying common poker situations
- Improving decision-making skills

## 🤝 Contributing

Ideas for future enhancements:
- [x] Pre-flop range charts generator ✓
- [x] Hand range analysis and assignment ✓
- [x] Statistics tracker ✓
- [x] Export functionality (JSON, CSV, HTML, Markdown) ✓
- [ ] GTO (Game Theory Optimal) recommendations
- [ ] Web-based GUI interface
- [ ] Opponent modeling with AI/ML
- [ ] Multi-table tournament (MTT) ICM calculator
- [ ] Real-time odds overlay for online poker
- [ ] Advanced hand history analyzer with pattern recognition

## 📄 License

Open source - use freely for learning and personal poker improvement!

---

## 🚀 Quick Reference

```bash
# Interactive enhanced mode
python3 poker_bot_enhanced.py

# Quick pre-flop check
python3 quick_analyze.py "As Kd" --opponents 2

# Quick post-flop check
python3 quick_analyze.py "Jh Jd" "9h 8h 2c" --opponents 1

# Batch compare scenarios
python3 batch_analyze.py --create-example
python3 batch_analyze.py example_scenarios.txt

# Pre-flop range charts (NEW!)
python3 preflop_charts.py

# Track statistics (NEW!)
python3 stats_tracker.py

# Export results (NEW!)
python3 export_results.py

# High precision analysis
python3 quick_analyze.py "As Kd" "Ah Kh Qh" -s 50000
```

---

**Disclaimer**: This tool is for educational purposes and personal poker improvement. Use responsibly and in accordance with the rules of your poker game or platform. The bot calculates mathematical probabilities and does not guarantee winning results.

**Good luck at the tables! 🎰♠♥♦♣**
