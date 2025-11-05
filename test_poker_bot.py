#!/usr/bin/env python3
"""
Test suite for Texas Hold'em Probability Bot
"""

from poker_bot import (
    Card, Rank, Suit, Deck, HandEvaluator, HandRank,
    ProbabilityCalculator, parse_card
)


def test_card_creation():
    """Test card creation and string representation"""
    print("Testing card creation...")
    card = Card(Rank.ACE, Suit.SPADES)
    assert str(card) == "A♠"

    card2 = Card(Rank.TEN, Suit.HEARTS)
    assert str(card2) == "10♥"

    print("  ✓ Card creation works")


def test_deck():
    """Test deck creation and dealing"""
    print("Testing deck...")
    deck = Deck()
    assert len(deck.cards) == 52

    dealt = deck.deal(5)
    assert len(dealt) == 5
    assert len(deck.cards) == 47

    print("  ✓ Deck works correctly")


def test_hand_evaluation():
    """Test hand evaluation for all hand types"""
    print("Testing hand evaluation...")

    # Royal Flush
    cards = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.QUEEN, Suit.SPADES),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.TEN, Suit.SPADES)
    ]
    rank, _ = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.ROYAL_FLUSH
    print("  ✓ Royal Flush detected")

    # Straight Flush
    cards = [
        Card(Rank.NINE, Suit.HEARTS),
        Card(Rank.EIGHT, Suit.HEARTS),
        Card(Rank.SEVEN, Suit.HEARTS),
        Card(Rank.SIX, Suit.HEARTS),
        Card(Rank.FIVE, Suit.HEARTS)
    ]
    rank, _ = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.STRAIGHT_FLUSH
    print("  ✓ Straight Flush detected")

    # Four of a Kind
    cards = [
        Card(Rank.KING, Suit.SPADES),
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.KING, Suit.CLUBS),
        Card(Rank.ACE, Suit.SPADES)
    ]
    rank, _ = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.FOUR_OF_A_KIND
    print("  ✓ Four of a Kind detected")

    # Full House
    cards = [
        Card(Rank.QUEEN, Suit.SPADES),
        Card(Rank.QUEEN, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.DIAMONDS),
        Card(Rank.EIGHT, Suit.CLUBS),
        Card(Rank.EIGHT, Suit.SPADES)
    ]
    rank, _ = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.FULL_HOUSE
    print("  ✓ Full House detected")

    # Flush
    cards = [
        Card(Rank.ACE, Suit.DIAMONDS),
        Card(Rank.JACK, Suit.DIAMONDS),
        Card(Rank.NINE, Suit.DIAMONDS),
        Card(Rank.SIX, Suit.DIAMONDS),
        Card(Rank.THREE, Suit.DIAMONDS)
    ]
    rank, _ = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.FLUSH
    print("  ✓ Flush detected")

    # Straight
    cards = [
        Card(Rank.NINE, Suit.SPADES),
        Card(Rank.EIGHT, Suit.HEARTS),
        Card(Rank.SEVEN, Suit.DIAMONDS),
        Card(Rank.SIX, Suit.CLUBS),
        Card(Rank.FIVE, Suit.SPADES)
    ]
    rank, _ = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.STRAIGHT
    print("  ✓ Straight detected")

    # Three of a Kind
    cards = [
        Card(Rank.SEVEN, Suit.SPADES),
        Card(Rank.SEVEN, Suit.HEARTS),
        Card(Rank.SEVEN, Suit.DIAMONDS),
        Card(Rank.ACE, Suit.CLUBS),
        Card(Rank.KING, Suit.SPADES)
    ]
    rank, _ = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.THREE_OF_A_KIND
    print("  ✓ Three of a Kind detected")

    # Two Pair
    cards = [
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.JACK, Suit.HEARTS),
        Card(Rank.FIVE, Suit.DIAMONDS),
        Card(Rank.FIVE, Suit.CLUBS),
        Card(Rank.ACE, Suit.SPADES)
    ]
    rank, _ = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.TWO_PAIR
    print("  ✓ Two Pair detected")

    # Pair
    cards = [
        Card(Rank.TEN, Suit.SPADES),
        Card(Rank.TEN, Suit.HEARTS),
        Card(Rank.ACE, Suit.CLUBS),
        Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.EIGHT, Suit.SPADES)
    ]
    rank, _ = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.PAIR
    print("  ✓ Pair detected")

    # High Card
    cards = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.KING, Suit.HEARTS),
        Card(Rank.QUEEN, Suit.DIAMONDS),
        Card(Rank.EIGHT, Suit.CLUBS),
        Card(Rank.FIVE, Suit.SPADES)
    ]
    rank, _ = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.HIGH_CARD
    print("  ✓ High Card detected")


def test_seven_card_evaluation():
    """Test evaluation with 7 cards (like Texas Hold'em)"""
    print("Testing 7-card hand evaluation...")

    # Should find the best 5-card hand
    cards = [
        Card(Rank.ACE, Suit.SPADES),
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.KING, Suit.DIAMONDS),
        Card(Rank.QUEEN, Suit.CLUBS),
        Card(Rank.JACK, Suit.SPADES),
        Card(Rank.TWO, Suit.HEARTS),
        Card(Rank.THREE, Suit.DIAMONDS)
    ]
    rank, _ = HandEvaluator.evaluate_hand(cards)
    assert rank == HandRank.PAIR
    print("  ✓ Best hand extracted from 7 cards")


def test_parse_card():
    """Test card parsing from string"""
    print("Testing card parsing...")

    card = parse_card("As")
    assert card.rank == Rank.ACE and card.suit == Suit.SPADES

    card = parse_card("10h")
    assert card.rank == Rank.TEN and card.suit == Suit.HEARTS

    card = parse_card("2d")
    assert card.rank == Rank.TWO and card.suit == Suit.DIAMONDS

    print("  ✓ Card parsing works")


def test_probability_calculator():
    """Test probability calculations"""
    print("Testing probability calculator...")

    # Pocket Aces should have high pre-flop win rate against 1 opponent
    hole_cards = [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS)]
    prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, [], num_opponents=1, num_simulations=1000
    )

    assert prob['win'] > 0.7  # AA should win >70% against random hand
    assert abs(prob['win'] + prob['tie'] + prob['loss'] - 1.0) < 0.01
    print(f"  ✓ Pocket Aces win rate: {prob['win']*100:.1f}%")

    # Test with community cards
    flop = [
        Card(Rank.ACE, Suit.DIAMONDS),
        Card(Rank.KING, Suit.CLUBS),
        Card(Rank.SEVEN, Suit.SPADES)
    ]
    prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, flop, num_opponents=1, num_simulations=1000
    )

    assert prob['win'] > 0.9  # Set of Aces should be very strong
    print(f"  ✓ Set of Aces win rate: {prob['win']*100:.1f}%")


def test_pot_odds():
    """Test pot odds calculations"""
    print("Testing pot odds calculator...")

    pot_odds = ProbabilityCalculator.calculate_pot_odds(100, 20)
    assert abs(pot_odds - 0.1667) < 0.01  # Should be ~16.67%

    # Should call with 20% equity
    assert ProbabilityCalculator.should_call(0.20, pot_odds) == True

    # Should fold with 10% equity
    assert ProbabilityCalculator.should_call(0.10, pot_odds) == False

    print("  ✓ Pot odds calculations correct")


def run_example_scenario():
    """Run a complete example scenario"""
    print("\n" + "="*60)
    print("EXAMPLE SCENARIO")
    print("="*60)

    # Scenario: You have As Kd
    hole_cards = [Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.DIAMONDS)]
    print(f"\nYour hole cards: {hole_cards[0]} {hole_cards[1]}")

    # Pre-flop against 2 opponents
    print("\nPre-flop analysis (vs 2 opponents)...")
    prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, [], num_opponents=2, num_simulations=2000
    )
    print(f"  Win: {prob['win']*100:.1f}% | Tie: {prob['tie']*100:.1f}% | Loss: {prob['loss']*100:.1f}%")

    # Flop: Ah 7s 3c
    flop = [
        Card(Rank.ACE, Suit.HEARTS),
        Card(Rank.SEVEN, Suit.SPADES),
        Card(Rank.THREE, Suit.CLUBS)
    ]
    print(f"\nFlop: {flop[0]} {flop[1]} {flop[2]}")

    rank, _ = HandEvaluator.evaluate_hand(hole_cards + flop)
    print(f"Your hand: {rank.name}")

    prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, flop, num_opponents=2, num_simulations=2000
    )
    print(f"  Win: {prob['win']*100:.1f}% | Tie: {prob['tie']*100:.1f}% | Loss: {prob['loss']*100:.1f}%")

    # Pot odds decision
    pot_size = 100
    bet_to_call = 20
    pot_odds = ProbabilityCalculator.calculate_pot_odds(pot_size, bet_to_call)
    should_call = ProbabilityCalculator.should_call(prob['win_or_tie'], pot_odds)

    print(f"\nPot: ${pot_size} | Bet to call: ${bet_to_call}")
    print(f"Pot odds: {pot_odds*100:.1f}%")
    print(f"Recommendation: {'CALL' if should_call else 'FOLD'}")


def main():
    """Run all tests"""
    print("="*60)
    print("POKER BOT TEST SUITE")
    print("="*60)
    print()

    try:
        test_card_creation()
        test_deck()
        test_hand_evaluation()
        test_seven_card_evaluation()
        test_parse_card()
        test_probability_calculator()
        test_pot_odds()

        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)

        run_example_scenario()

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
