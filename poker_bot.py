#!/usr/bin/env python3
"""
Texas Hold'em Probability Bot
Calculates probabilities and provides decision assistance for Texas Hold'em poker.
"""

import random
from enum import Enum
from typing import List, Tuple, Optional
from collections import Counter
from itertools import combinations


class Suit(Enum):
    """Card suits"""
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'
    SPADES = '♠'


class Rank(Enum):
    """Card ranks with numerical values for comparison"""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


class Card:
    """Represents a playing card"""

    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        rank_display = {
            Rank.TWO: '2', Rank.THREE: '3', Rank.FOUR: '4', Rank.FIVE: '5',
            Rank.SIX: '6', Rank.SEVEN: '7', Rank.EIGHT: '8', Rank.NINE: '9',
            Rank.TEN: '10', Rank.JACK: 'J', Rank.QUEEN: 'Q',
            Rank.KING: 'K', Rank.ACE: 'A'
        }
        return f"{rank_display[self.rank]}{self.suit.value}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        return hash((self.rank, self.suit))


class Deck:
    """Represents a deck of 52 playing cards"""

    def __init__(self):
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        self.shuffle()

    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)

    def deal(self, n: int = 1) -> List[Card]:
        """Deal n cards from the deck"""
        if n > len(self.cards):
            raise ValueError("Not enough cards in deck")
        dealt = self.cards[:n]
        self.cards = self.cards[n:]
        return dealt

    def remove_cards(self, cards_to_remove: List[Card]):
        """Remove specific cards from the deck (for known cards)"""
        self.cards = [card for card in self.cards if card not in cards_to_remove]


class HandRank(Enum):
    """Poker hand rankings"""
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class HandEvaluator:
    """Evaluates poker hands and determines their rank"""

    @staticmethod
    def evaluate_hand(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """
        Evaluate a 5-7 card hand and return its rank and tiebreaker values.
        Returns (HandRank, [tiebreaker values in descending order])
        """
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate")

        # Try all 5-card combinations if we have more than 5 cards
        if len(cards) > 5:
            best_hand = None
            best_rank = None
            for combo in combinations(cards, 5):
                rank, tiebreakers = HandEvaluator._evaluate_five_cards(list(combo))
                if best_rank is None or HandEvaluator._compare_hands(
                    (rank, tiebreakers), (best_rank, best_hand)) > 0:
                    best_rank = rank
                    best_hand = tiebreakers
            return best_rank, best_hand
        else:
            return HandEvaluator._evaluate_five_cards(cards)

    @staticmethod
    def _evaluate_five_cards(cards: List[Card]) -> Tuple[HandRank, List[int]]:
        """Evaluate exactly 5 cards"""
        ranks = sorted([card.rank.value for card in cards], reverse=True)
        suits = [card.suit for card in cards]
        rank_counts = Counter(ranks)

        is_flush = len(set(suits)) == 1
        is_straight = HandEvaluator._is_straight(ranks)

        # Check for straight with Ace low (A-2-3-4-5)
        if sorted(ranks) == [2, 3, 4, 5, 14]:
            is_straight = True
            ranks = [5, 4, 3, 2, 1]  # Ace is low in this case

        # Get rank groups (e.g., pairs, trips, quads)
        rank_groups = sorted(rank_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

        # Royal Flush
        if is_flush and is_straight and ranks[0] == 14:
            return HandRank.ROYAL_FLUSH, ranks

        # Straight Flush
        if is_flush and is_straight:
            return HandRank.STRAIGHT_FLUSH, ranks

        # Four of a Kind
        if rank_groups[0][1] == 4:
            return HandRank.FOUR_OF_A_KIND, [rank_groups[0][0], rank_groups[1][0]]

        # Full House
        if rank_groups[0][1] == 3 and rank_groups[1][1] == 2:
            return HandRank.FULL_HOUSE, [rank_groups[0][0], rank_groups[1][0]]

        # Flush
        if is_flush:
            return HandRank.FLUSH, ranks

        # Straight
        if is_straight:
            return HandRank.STRAIGHT, ranks

        # Three of a Kind
        if rank_groups[0][1] == 3:
            kickers = sorted([r for r, count in rank_groups[1:]], reverse=True)
            return HandRank.THREE_OF_A_KIND, [rank_groups[0][0]] + kickers

        # Two Pair
        if rank_groups[0][1] == 2 and rank_groups[1][1] == 2:
            pairs = sorted([rank_groups[0][0], rank_groups[1][0]], reverse=True)
            kicker = rank_groups[2][0]
            return HandRank.TWO_PAIR, pairs + [kicker]

        # Pair
        if rank_groups[0][1] == 2:
            kickers = sorted([r for r, count in rank_groups[1:]], reverse=True)
            return HandRank.PAIR, [rank_groups[0][0]] + kickers

        # High Card
        return HandRank.HIGH_CARD, ranks

    @staticmethod
    def _is_straight(ranks: List[int]) -> bool:
        """Check if ranks form a straight"""
        if len(set(ranks)) != 5:
            return False
        return max(ranks) - min(ranks) == 4

    @staticmethod
    def _compare_hands(hand1: Tuple[HandRank, List[int]],
                      hand2: Tuple[HandRank, List[int]]) -> int:
        """
        Compare two hands. Returns:
        1 if hand1 wins, -1 if hand2 wins, 0 if tie
        """
        rank1, tiebreakers1 = hand1
        rank2, tiebreakers2 = hand2

        if rank1.value > rank2.value:
            return 1
        elif rank1.value < rank2.value:
            return -1

        # Same rank, compare tiebreakers
        for tb1, tb2 in zip(tiebreakers1, tiebreakers2):
            if tb1 > tb2:
                return 1
            elif tb1 < tb2:
                return -1

        return 0


class ProbabilityCalculator:
    """Calculates win probabilities using Monte Carlo simulation"""

    @staticmethod
    def calculate_win_probability(hole_cards: List[Card],
                                  community_cards: List[Card],
                                  num_opponents: int = 1,
                                  num_simulations: int = 10000) -> dict:
        """
        Calculate win probability using Monte Carlo simulation.

        Args:
            hole_cards: Your two hole cards
            community_cards: Community cards (0-5 cards)
            num_opponents: Number of opponents
            num_simulations: Number of simulations to run

        Returns:
            Dictionary with win, tie, and loss probabilities
        """
        wins = 0
        ties = 0
        losses = 0

        known_cards = hole_cards + community_cards
        cards_needed = 5 - len(community_cards)

        for _ in range(num_simulations):
            # Create a new deck without known cards
            deck = Deck()
            deck.remove_cards(known_cards)
            deck.shuffle()

            # Deal remaining community cards
            sim_community = community_cards + deck.deal(cards_needed)

            # Evaluate player's hand
            player_cards = hole_cards + sim_community
            player_hand = HandEvaluator.evaluate_hand(player_cards)

            # Deal and evaluate opponent hands
            opponent_hands = []
            for _ in range(num_opponents):
                opponent_hole = deck.deal(2)
                opponent_cards = opponent_hole + sim_community
                opponent_hands.append(HandEvaluator.evaluate_hand(opponent_cards))

            # Compare with all opponents
            player_wins = True
            player_ties = False

            for opp_hand in opponent_hands:
                result = HandEvaluator._compare_hands(player_hand, opp_hand)
                if result < 0:
                    player_wins = False
                    break
                elif result == 0:
                    player_ties = True

            if player_wins and not player_ties:
                wins += 1
            elif player_wins and player_ties:
                ties += 1
            else:
                losses += 1

        return {
            'win': wins / num_simulations,
            'tie': ties / num_simulations,
            'loss': losses / num_simulations,
            'win_or_tie': (wins + ties) / num_simulations
        }

    @staticmethod
    def calculate_pot_odds(pot_size: float, bet_to_call: float) -> float:
        """Calculate pot odds as a percentage"""
        return bet_to_call / (pot_size + bet_to_call)

    @staticmethod
    def should_call(win_probability: float, pot_odds: float) -> bool:
        """Determine if calling is profitable based on pot odds"""
        return win_probability > pot_odds


def parse_card(card_str: str) -> Card:
    """Parse a card string like 'As' (Ace of Spades) or '10h' (10 of Hearts)"""
    card_str = card_str.strip().upper()

    # Parse rank
    if card_str[:-1] == 'A':
        rank = Rank.ACE
    elif card_str[:-1] == 'K':
        rank = Rank.KING
    elif card_str[:-1] == 'Q':
        rank = Rank.QUEEN
    elif card_str[:-1] == 'J':
        rank = Rank.JACK
    elif card_str[:-1] == '10':
        rank = Rank.TEN
    else:
        rank_map = {'2': Rank.TWO, '3': Rank.THREE, '4': Rank.FOUR,
                   '5': Rank.FIVE, '6': Rank.SIX, '7': Rank.SEVEN,
                   '8': Rank.EIGHT, '9': Rank.NINE}
        rank = rank_map[card_str[:-1]]

    # Parse suit
    suit_char = card_str[-1]
    suit_map = {'H': Suit.HEARTS, 'D': Suit.DIAMONDS,
                'C': Suit.CLUBS, 'S': Suit.SPADES}
    suit = suit_map[suit_char]

    return Card(rank, suit)


def main():
    """Interactive CLI for the poker bot"""
    print("=" * 60)
    print("TEXAS HOLD'EM PROBABILITY BOT")
    print("=" * 60)
    print("\nThis bot calculates win probabilities and assists with")
    print("decision-making at every stage of a Texas Hold'em hand.")
    print("\nCard format: Rank + Suit (e.g., As, Kh, 10d, 2c)")
    print("  Ranks: A, K, Q, J, 10, 9, 8, 7, 6, 5, 4, 3, 2")
    print("  Suits: s (spades), h (hearts), d (diamonds), c (clubs)")
    print("=" * 60)

    # Get hole cards
    print("\nEnter your hole cards:")
    hole_input = input("  (e.g., 'As Kh'): ").strip().split()
    hole_cards = [parse_card(card) for card in hole_input]

    if len(hole_cards) != 2:
        print("Error: You must enter exactly 2 hole cards")
        return

    print(f"\nYour hole cards: {hole_cards[0]} {hole_cards[1]}")

    # Get number of opponents
    num_opponents = int(input("\nNumber of opponents: "))

    # Pre-flop analysis
    print("\n" + "=" * 60)
    print("PRE-FLOP ANALYSIS")
    print("=" * 60)

    print("\nCalculating pre-flop win probability...")
    preflop_prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, [], num_opponents, num_simulations=5000
    )

    print(f"\nWin probability: {preflop_prob['win']*100:.2f}%")
    print(f"Tie probability: {preflop_prob['tie']*100:.2f}%")
    print(f"Loss probability: {preflop_prob['loss']*100:.2f}%")

    # Flop
    flop_input = input("\nEnter flop cards (or press Enter to skip): ").strip()
    if not flop_input:
        return

    flop_cards = [parse_card(card) for card in flop_input.split()]
    if len(flop_cards) != 3:
        print("Error: Flop must have exactly 3 cards")
        return

    print(f"\nFlop: {' '.join(str(c) for c in flop_cards)}")

    # Evaluate current hand
    current_hand = HandEvaluator.evaluate_hand(hole_cards + flop_cards)
    print(f"Current hand: {current_hand[0].name}")

    print("\nCalculating post-flop win probability...")
    flop_prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, flop_cards, num_opponents, num_simulations=5000
    )

    print(f"\nWin probability: {flop_prob['win']*100:.2f}%")
    print(f"Tie probability: {flop_prob['tie']*100:.2f}%")
    print(f"Loss probability: {flop_prob['loss']*100:.2f}%")

    # Pot odds calculation
    pot_size = float(input("\nCurrent pot size: $"))
    bet_to_call = float(input("Bet to call: $"))

    pot_odds = ProbabilityCalculator.calculate_pot_odds(pot_size, bet_to_call)
    print(f"\nPot odds: {pot_odds*100:.2f}%")
    print(f"You need {pot_odds*100:.2f}% equity to call profitably")

    should_call = ProbabilityCalculator.should_call(flop_prob['win_or_tie'], pot_odds)
    print(f"\nRECOMMENDATION: {'CALL' if should_call else 'FOLD'}")

    # Turn
    turn_input = input("\nEnter turn card (or press Enter to skip): ").strip()
    if not turn_input:
        return

    turn_card = parse_card(turn_input)
    community_cards = flop_cards + [turn_card]

    print(f"\nBoard: {' '.join(str(c) for c in community_cards)}")
    current_hand = HandEvaluator.evaluate_hand(hole_cards + community_cards)
    print(f"Current hand: {current_hand[0].name}")

    print("\nCalculating turn win probability...")
    turn_prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, community_cards, num_opponents, num_simulations=5000
    )

    print(f"\nWin probability: {turn_prob['win']*100:.2f}%")
    print(f"Tie probability: {turn_prob['tie']*100:.2f}%")
    print(f"Loss probability: {turn_prob['loss']*100:.2f}%")

    # River
    river_input = input("\nEnter river card (or press Enter to skip): ").strip()
    if not river_input:
        return

    river_card = parse_card(river_input)
    community_cards = community_cards + [river_card]

    print(f"\nFinal board: {' '.join(str(c) for c in community_cards)}")
    final_hand = HandEvaluator.evaluate_hand(hole_cards + community_cards)
    print(f"\nYour final hand: {final_hand[0].name}")

    print("\nCalculating river win probability...")
    river_prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, community_cards, num_opponents, num_simulations=10000
    )

    print(f"\nWin probability: {river_prob['win']*100:.2f}%")
    print(f"Tie probability: {river_prob['tie']*100:.2f}%")
    print(f"Loss probability: {river_prob['loss']*100:.2f}%")


if __name__ == "__main__":
    main()
