# Texas Hold'em Probability Bot

A powerful poker assistant that calculates win probabilities and provides decision-making guidance at every stage of a Texas Hold'em hand using Monte Carlo simulation.

## Features

- **Real-time Probability Calculations**: Get accurate win/tie/loss probabilities at any stage
- **Monte Carlo Simulation**: Uses thousands of simulations for precise probability estimates
- **Hand Evaluation**: Correctly ranks all poker hands from high card to royal flush
- **Pot Odds Calculator**: Compares your equity to pot odds and recommends actions
- **Interactive CLI**: Step through pre-flop, flop, turn, and river with live analysis
- **Multi-opponent Support**: Calculate probabilities against any number of opponents

## How It Works

The bot uses Monte Carlo simulation to calculate probabilities:

1. Takes your known cards (hole cards + community cards)
2. Simulates thousands of possible scenarios
3. Deals random cards for opponents and remaining community cards
4. Evaluates all hands and determines winners
5. Calculates win/tie/loss percentages based on simulation results

## Installation

No external dependencies required! Just Python 3.6+

```bash
# Make the script executable (optional)
chmod +x poker_bot.py

# Run the bot
python3 poker_bot.py
```

## Usage

### Interactive Mode

Simply run the script and follow the prompts:

```bash
python3 poker_bot.py
```

The bot will guide you through:
1. Entering your hole cards
2. Specifying number of opponents
3. Pre-flop probability analysis
4. Flop analysis with pot odds recommendations
5. Turn analysis
6. River analysis

### Card Format

Enter cards using this format: **Rank + Suit**

- **Ranks**: A, K, Q, J, 10, 9, 8, 7, 6, 5, 4, 3, 2
- **Suits**: s (♠), h (♥), d (♦), c (♣)

**Examples**:
- `As` = Ace of Spades
- `Kh` = King of Hearts
- `10d` = Ten of Diamonds
- `2c` = Two of Clubs

### Example Session

```
TEXAS HOLD'EM PROBABILITY BOT
============================================================

Enter your hole cards:
  (e.g., 'As Kh'): As Kd

Your hole cards: A♠ K♦

Number of opponents: 2

============================================================
PRE-FLOP ANALYSIS
============================================================

Calculating pre-flop win probability...

Win probability: 46.32%
Tie probability: 2.14%
Loss probability: 51.54%

Enter flop cards (or press Enter to skip): Ah 7s 3c

Flop: A♥ 7♠ 3♣
Current hand: PAIR

Calculating post-flop win probability...

Win probability: 84.21%
Tie probability: 1.05%
Loss probability: 14.74%

Current pot size: $100
Bet to call: $20

Pot odds: 16.67%
You need 16.67% equity to call profitably

RECOMMENDATION: CALL
```

## Understanding the Output

### Win Probability
The percentage chance you'll win the hand against all opponents.

### Tie Probability
The percentage chance you'll split the pot with one or more opponents.

### Loss Probability
The percentage chance you'll lose the hand.

### Pot Odds
The ratio of the bet you must call to the total pot after calling:
```
Pot Odds = Bet to Call / (Current Pot + Bet to Call)
```

### Call/Fold Recommendation
- **CALL**: Your win+tie probability exceeds the pot odds (profitable long-term)
- **FOLD**: Your equity is lower than the pot odds required (unprofitable long-term)

## Hand Rankings

The bot correctly evaluates all poker hands:

1. **Royal Flush**: A♠ K♠ Q♠ J♠ 10♠
2. **Straight Flush**: 9♥ 8♥ 7♥ 6♥ 5♥
3. **Four of a Kind**: K♠ K♥ K♦ K♣ A♠
4. **Full House**: Q♠ Q♥ Q♦ 8♣ 8♠
5. **Flush**: A♦ J♦ 9♦ 6♦ 3♦
6. **Straight**: 9♠ 8♥ 7♦ 6♣ 5♠
7. **Three of a Kind**: 7♠ 7♥ 7♦ A♣ K♠
8. **Two Pair**: J♠ J♥ 5♦ 5♣ A♠
9. **Pair**: 10♠ 10♥ A♣ K♦ 8♠
10. **High Card**: A♠ K♥ Q♦ 8♣ 5♠

## Using as a Library

You can also import and use the bot's components in your own code:

```python
from poker_bot import Card, Rank, Suit, ProbabilityCalculator, HandEvaluator

# Create cards
hole_cards = [Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)]
flop = [Card(Rank.ACE, Suit.HEARTS), Card(Rank.SEVEN, Suit.SPADES), Card(Rank.THREE, Suit.CLUBS)]

# Calculate probabilities
prob = ProbabilityCalculator.calculate_win_probability(
    hole_cards=hole_cards,
    community_cards=flop,
    num_opponents=2,
    num_simulations=10000
)

print(f"Win probability: {prob['win']*100:.2f}%")

# Evaluate hand
hand_rank, tiebreakers = HandEvaluator.evaluate_hand(hole_cards + flop)
print(f"Current hand: {hand_rank.name}")
```

## Advanced Usage

### Adjust Simulation Accuracy

You can modify the number of simulations in the code for different speed/accuracy tradeoffs:

- **Fast** (1,000 simulations): ~1% margin of error
- **Default** (5,000-10,000 simulations): ~0.5% margin of error
- **Precise** (50,000+ simulations): <0.2% margin of error

### Use in Tournament vs Cash Game

The bot calculates mathematical probabilities. Consider these adjustments for different game types:

- **Cash Games**: Follow pot odds recommendations strictly
- **Tournaments**: Factor in ICM (Independent Chip Model) and survival considerations
- **Short-handed**: Adjust aggression with weaker hands (broader ranges)

## Tips for Using the Bot

1. **Pre-flop**: Use to understand starting hand strength against multiple opponents
2. **Post-flop**: Compare win probability to pot odds for +EV decisions
3. **Drawing hands**: Check if you have sufficient equity to continue
4. **Bluffing**: The bot calculates showdown equity only (doesn't factor in fold equity)
5. **Opponent ranges**: The bot assumes random opponent hands; adjust mentally for player tendencies

## Limitations

- Assumes opponents have random hands (doesn't model specific ranges)
- Calculates showdown equity only (doesn't factor in fold equity)
- Does not account for position, stack sizes, or tournament ICM
- Best used as a learning tool and equity calculator

## Technical Details

- **Language**: Python 3.6+
- **Algorithm**: Monte Carlo simulation
- **Hand Evaluation**: Custom evaluator supporting 5-7 card hands
- **Accuracy**: Configurable through simulation count
- **Performance**: ~10,000 simulations per second (hardware dependent)

## Contributing

This is a standalone poker bot for analyzing Texas Hold'em probabilities. Feel free to extend it with:

- Pre-flop hand range charts
- Opponent modeling and range assignment
- GTO (Game Theory Optimal) strategy recommendations
- Multi-hand batch analysis
- Web interface or GUI

## License

Open source - use freely for learning and personal poker improvement!

---

**Disclaimer**: This tool is for educational purposes and to improve your poker understanding. Use responsibly and in accordance with the rules of your poker game or platform.
