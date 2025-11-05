#!/usr/bin/env python3
"""
Enhanced Texas Hold'em Probability Bot
Advanced features: colored output, outs calculator, draw detection, pre-flop rankings, EV calculations,
AI opponent modeling, GTO solver, player profiling, bluff detection
"""

import random
import sys
from enum import Enum
from typing import List, Tuple, Optional, Dict, Set
from collections import Counter
from itertools import combinations

# Import advanced modules
try:
    from preflop_charts import PreFlopChart, Position, HandCategory
    from ai_opponent import OpponentModeler, GTO_Solver
    from advanced_ai import AdvancedAI, PlayerProfile, BluffDetector
    ADVANCED_FEATURES = True
except ImportError:
    ADVANCED_FEATURES = False
    print("Note: Advanced features not available. Install all modules for full functionality.")

# ANSI color codes for terminal output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'

    # Card suit colors
    HEARTS = RED
    DIAMONDS = RED
    CLUBS = WHITE
    SPADES = WHITE

    @staticmethod
    def disable():
        """Disable colors (for environments that don't support ANSI)"""
        Colors.RESET = ''
        Colors.BOLD = ''
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.MAGENTA = ''
        Colors.CYAN = ''
        Colors.WHITE = ''
        Colors.GRAY = ''


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

    def colored_str(self) -> str:
        """Return colored string representation"""
        rank_display = {
            Rank.TWO: '2', Rank.THREE: '3', Rank.FOUR: '4', Rank.FIVE: '5',
            Rank.SIX: '6', Rank.SEVEN: '7', Rank.EIGHT: '8', Rank.NINE: '9',
            Rank.TEN: '10', Rank.JACK: 'J', Rank.QUEEN: 'Q',
            Rank.KING: 'K', Rank.ACE: 'A'
        }
        color = Colors.HEARTS if self.suit in [Suit.HEARTS, Suit.DIAMONDS] else Colors.SPADES
        return f"{Colors.BOLD}{color}{rank_display[self.rank]}{self.suit.value}{Colors.RESET}"

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


class DrawAnalyzer:
    """Analyzes potential draws (flush draws, straight draws, etc.)"""

    @staticmethod
    def analyze_draws(hole_cards: List[Card], community_cards: List[Card]) -> Dict:
        """Analyze potential draws and calculate outs"""
        all_cards = hole_cards + community_cards

        # Calculate outs for various draws
        flush_draw_outs = DrawAnalyzer._count_flush_draw_outs(all_cards)
        straight_draw_outs = DrawAnalyzer._count_straight_draw_outs(all_cards)

        # Determine draw types
        draws = []
        total_outs = 0

        if flush_draw_outs >= 9:
            draws.append(("Flush Draw", flush_draw_outs))
            total_outs = max(total_outs, flush_draw_outs)

        if straight_draw_outs >= 8:
            draws.append(("Open-Ended Straight Draw", straight_draw_outs))
            total_outs = max(total_outs, straight_draw_outs)
        elif straight_draw_outs >= 4:
            draws.append(("Gutshot Straight Draw", straight_draw_outs))
            total_outs = max(total_outs, straight_draw_outs)

        # Calculate approximate win probability based on outs
        cards_to_come = 5 - len(community_cards)
        if cards_to_come == 2:  # After flop
            win_prob = DrawAnalyzer._outs_to_probability(total_outs, 2)
        elif cards_to_come == 1:  # After turn
            win_prob = DrawAnalyzer._outs_to_probability(total_outs, 1)
        else:
            win_prob = 0

        return {
            'draws': draws,
            'total_outs': total_outs,
            'estimated_win_probability': win_prob
        }

    @staticmethod
    def _count_flush_draw_outs(cards: List[Card]) -> int:
        """Count outs for flush draws"""
        suit_counts = Counter(card.suit for card in cards)
        max_suit_count = max(suit_counts.values()) if suit_counts else 0

        if max_suit_count == 4:
            return 9  # Flush draw (9 cards left of that suit)
        return 0

    @staticmethod
    def _count_straight_draw_outs(cards: List[Card]) -> int:
        """Count outs for straight draws (simplified)"""
        ranks = sorted(set(card.rank.value for card in cards))

        # Check for open-ended straight draw
        for i in range(len(ranks) - 3):
            if ranks[i+3] - ranks[i] == 3:
                return 8  # Open-ended

        # Check for gutshot
        for i in range(len(ranks) - 2):
            if ranks[i+2] - ranks[i] == 4:
                return 4  # Gutshot

        return 0

    @staticmethod
    def _outs_to_probability(outs: int, cards_to_come: int) -> float:
        """Convert outs to probability (rule of 2 and 4)"""
        if cards_to_come == 2:
            return min(outs * 4, 100) / 100
        elif cards_to_come == 1:
            return min(outs * 2, 100) / 100
        return 0


class PreFlopAnalyzer:
    """Analyzes pre-flop hand strength"""

    @staticmethod
    def calculate_chen_formula(hole_cards: List[Card]) -> float:
        """
        Calculate hand strength using Chen formula.
        Returns a score (higher is better, max ~20 for AA)
        """
        card1, card2 = hole_cards
        rank1, rank2 = card1.rank.value, card2.rank.value

        # Start with highest card
        high_card = max(rank1, rank2)
        score = PreFlopAnalyzer._rank_to_chen_score(high_card)

        # Multiply pairs by 2, max 5 for AA
        if rank1 == rank2:
            score = max(score * 2, 5)

        # Add bonus for suited cards
        if card1.suit == card2.suit:
            score += 2

        # Subtract gap penalty
        gap = abs(rank1 - rank2)
        if gap == 1:
            score += 1  # Bonus for connected cards
        elif gap == 2:
            score -= 1
        elif gap == 3:
            score -= 2
        elif gap == 4:
            score -= 4
        elif gap >= 5:
            score -= 5

        # Add bonus for 0-1 gap with at least one high card
        if gap <= 1 and high_card >= 12:
            score += 1

        return max(score, 0)

    @staticmethod
    def _rank_to_chen_score(rank: int) -> float:
        """Convert rank to Chen formula base score"""
        if rank == 14:  # Ace
            return 10
        elif rank == 13:  # King
            return 8
        elif rank == 12:  # Queen
            return 7
        elif rank == 11:  # Jack
            return 6
        else:
            return rank / 2

    @staticmethod
    def get_hand_category(chen_score: float) -> Tuple[str, str]:
        """Categorize hand strength based on Chen score"""
        if chen_score >= 12:
            return ("PREMIUM", Colors.GREEN)
        elif chen_score >= 8:
            return ("STRONG", Colors.CYAN)
        elif chen_score >= 6:
            return ("PLAYABLE", Colors.YELLOW)
        elif chen_score >= 4:
            return ("MARGINAL", Colors.YELLOW)
        else:
            return ("WEAK", Colors.RED)


class ProbabilityCalculator:
    """Calculates win probabilities using Monte Carlo simulation"""

    @staticmethod
    def calculate_win_probability(hole_cards: List[Card],
                                  community_cards: List[Card],
                                  num_opponents: int = 1,
                                  num_simulations: int = 10000,
                                  progress_callback=None) -> dict:
        """
        Calculate win probability using Monte Carlo simulation.

        Args:
            hole_cards: Your two hole cards
            community_cards: Community cards (0-5 cards)
            num_opponents: Number of opponents
            num_simulations: Number of simulations to run
            progress_callback: Optional callback for progress updates

        Returns:
            Dictionary with win, tie, and loss probabilities
        """
        wins = 0
        ties = 0
        losses = 0

        known_cards = hole_cards + community_cards
        cards_needed = 5 - len(community_cards)

        for i in range(num_simulations):
            # Progress callback
            if progress_callback and i % 500 == 0:
                progress_callback(i, num_simulations)

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
    def calculate_expected_value(win_prob: float, pot_size: float, bet_to_call: float) -> float:
        """Calculate expected value of calling"""
        ev_win = win_prob * (pot_size + bet_to_call)
        ev_loss = (1 - win_prob) * bet_to_call
        return ev_win - ev_loss

    @staticmethod
    def should_call(win_probability: float, pot_odds: float) -> bool:
        """Determine if calling is profitable based on pot odds"""
        return win_probability > pot_odds


def print_header(text: str, color=Colors.CYAN):
    """Print a formatted header"""
    print(f"\n{color}{Colors.BOLD}{'=' * 60}")
    print(f"{text.center(60)}")
    print(f"{'=' * 60}{Colors.RESET}\n")


def print_progress_bar(current: int, total: int, bar_length: int = 40):
    """Print a progress bar"""
    progress = current / total
    filled = int(bar_length * progress)
    bar = '█' * filled + '░' * (bar_length - filled)
    percent = progress * 100
    print(f"\r{Colors.CYAN}[{bar}] {percent:.1f}%{Colors.RESET}", end='', flush=True)
    if current == total:
        print()  # New line when complete


def parse_card(card_str: str) -> Card:
    """Parse a card string like 'As' (Ace of Spades) or '10h' (10 of Hearts)"""
    try:
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
            rank = rank_map.get(card_str[:-1])
            if rank is None:
                raise ValueError(f"Invalid rank: {card_str[:-1]}")

        # Parse suit
        suit_char = card_str[-1]
        suit_map = {'H': Suit.HEARTS, 'D': Suit.DIAMONDS,
                    'C': Suit.CLUBS, 'S': Suit.SPADES}
        suit = suit_map.get(suit_char)
        if suit is None:
            raise ValueError(f"Invalid suit: {suit_char}")

        return Card(rank, suit)
    except Exception as e:
        raise ValueError(f"Invalid card format '{card_str}': {e}")


def validate_unique_cards(cards: List[Card]) -> bool:
    """Check if all cards are unique"""
    return len(cards) == len(set(cards))


def display_probability_bar(label: str, probability: float, color: str):
    """Display a probability with a visual bar"""
    bar_length = 30
    filled = int(bar_length * probability)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"  {label:12} {color}[{bar}]{Colors.RESET} {probability*100:5.1f}%")


def main():
    """Enhanced interactive CLI for the poker bot"""
    print_header("TEXAS HOLD'EM PROBABILITY BOT - ENHANCED", Colors.MAGENTA)

    print(f"{Colors.BOLD}Features:{Colors.RESET}")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Monte Carlo probability calculations")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Pre-flop hand strength analysis")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Draw detection (flush/straight draws)")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Outs calculator")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Pot odds & EV analysis")
    print(f"  {Colors.GREEN}✓{Colors.RESET} Color-coded recommendations")

    if ADVANCED_FEATURES:
        print(f"  {Colors.CYAN}★{Colors.RESET} AI opponent modeling")
        print(f"  {Colors.CYAN}★{Colors.RESET} GTO solver recommendations")
        print(f"  {Colors.CYAN}★{Colors.RESET} Player profiling & bluff detection")
        print(f"  {Colors.CYAN}★{Colors.RESET} Position-aware pre-flop charts")

    print(f"\n{Colors.YELLOW}Card format:{Colors.RESET} Rank + Suit (e.g., As, Kh, 10d, 2c)")
    print(f"  Ranks: A, K, Q, J, 10, 9, 8, 7, 6, 5, 4, 3, 2")
    print(f"  Suits: s (spades), h (hearts), d (diamonds), c (clubs)")

    all_cards = []

    # Get hole cards
    print_header("YOUR HOLE CARDS", Colors.BLUE)

    while True:
        try:
            hole_input = input(f"{Colors.BOLD}Enter your 2 hole cards{Colors.RESET} (e.g., 'As Kh'): ").strip().split()
            hole_cards = [parse_card(card) for card in hole_input]

            if len(hole_cards) != 2:
                print(f"{Colors.RED}✗ Error: You must enter exactly 2 hole cards{Colors.RESET}")
                continue

            if not validate_unique_cards(hole_cards):
                print(f"{Colors.RED}✗ Error: Duplicate cards detected{Colors.RESET}")
                continue

            all_cards.extend(hole_cards)
            break
        except ValueError as e:
            print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")

    print(f"\n{Colors.BOLD}Your hole cards:{Colors.RESET} {hole_cards[0].colored_str()} {hole_cards[1].colored_str()}")

    # Get position
    player_position = None
    if ADVANCED_FEATURES:
        print(f"\n{Colors.BOLD}Select your position:{Colors.RESET}")
        print("  1. UTG (Under the Gun)")
        print("  2. MP (Middle Position)")
        print("  3. CO (Cutoff)")
        print("  4. BTN (Button)")
        print("  5. SB (Small Blind)")
        print("  6. BB (Big Blind)")

        while True:
            try:
                pos_choice = input(f"\n{Colors.BOLD}Position (1-6):{Colors.RESET} ").strip()
                position_map = {
                    '1': Position.UTG, '2': Position.MP, '3': Position.CO,
                    '4': Position.BTN, '5': Position.SB, '6': Position.BB
                }
                if pos_choice in position_map:
                    player_position = position_map[pos_choice]
                    break
                else:
                    print(f"{Colors.RED}✗ Error: Please enter 1-6{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")

    # Get number of opponents
    while True:
        try:
            num_opponents = int(input(f"\n{Colors.BOLD}Number of opponents:{Colors.RESET} "))
            if num_opponents < 1 or num_opponents > 9:
                print(f"{Colors.YELLOW}! Warning: Typically 1-9 opponents{Colors.RESET}")
            break
        except ValueError:
            print(f"{Colors.RED}✗ Error: Please enter a number{Colors.RESET}")

    # Pre-flop analysis
    print_header("PRE-FLOP ANALYSIS", Colors.CYAN)

    # Chen formula analysis
    chen_score = PreFlopAnalyzer.calculate_chen_formula(hole_cards)
    category, cat_color = PreFlopAnalyzer.get_hand_category(chen_score)

    print(f"{Colors.BOLD}Hand Strength (Chen Formula):{Colors.RESET}")
    print(f"  Score: {Colors.YELLOW}{chen_score:.1f}{Colors.RESET}")
    print(f"  Category: {cat_color}{Colors.BOLD}{category}{Colors.RESET}\n")

    # Position-aware pre-flop recommendations
    if ADVANCED_FEATURES and player_position:
        try:
            print(f"{Colors.CYAN}{Colors.BOLD}Position-Aware Analysis:{Colors.RESET}")
            print(f"  Your Position: {Colors.YELLOW}{player_position.value}{Colors.RESET}")

            action_before = input(f"\n  Action before you (none/limp/raise): ").strip().lower()
            if action_before not in ['none', 'limp', 'raise']:
                action_before = 'none'

            recommendation = PreFlopChart.get_recommendation(hole_cards, player_position, action_before)

            rec_color = Colors.GREEN if recommendation['in_range'] else Colors.RED
            print(f"\n  Hand: {Colors.YELLOW}{recommendation['hand']}{Colors.RESET}")
            print(f"  In Range: {rec_color}{Colors.BOLD}{'YES' if recommendation['in_range'] else 'NO'}{Colors.RESET}")
            print(f"  Recommendation: {rec_color}{Colors.BOLD}{recommendation['action']}{Colors.RESET}")
            print(f"  {Colors.GRAY}{recommendation['description']}{Colors.RESET}\n")
        except Exception as e:
            import traceback
            if '--debug' in sys.argv:
                print(f"{Colors.YELLOW}⚠ Position analysis error:{Colors.RESET}")
                traceback.print_exc()
            else:
                print(f"{Colors.YELLOW}⚠ Position analysis unavailable: {e}{Colors.RESET}\n")

    print(f"{Colors.GRAY}Calculating pre-flop win probability (5000 simulations)...{Colors.RESET}")

    preflop_prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, [], num_opponents, num_simulations=5000,
        progress_callback=lambda c, t: print_progress_bar(c, t) if c % 500 == 0 else None
    )
    print_progress_bar(5000, 5000)  # Complete the bar

    print(f"\n{Colors.BOLD}Win Probabilities:{Colors.RESET}")
    display_probability_bar("Win", preflop_prob['win'], Colors.GREEN)
    display_probability_bar("Tie", preflop_prob['tie'], Colors.YELLOW)
    display_probability_bar("Loss", preflop_prob['loss'], Colors.RED)

    # Flop
    print_header("FLOP", Colors.CYAN)
    flop_input = input(f"{Colors.BOLD}Enter flop cards{Colors.RESET} (or press Enter to quit): ").strip()
    if not flop_input:
        return

    try:
        flop_cards = [parse_card(card) for card in flop_input.split()]
        if len(flop_cards) != 3:
            print(f"{Colors.RED}✗ Error: Flop must have exactly 3 cards{Colors.RESET}")
            return

        all_new_cards = all_cards + flop_cards
        if not validate_unique_cards(all_new_cards):
            print(f"{Colors.RED}✗ Error: Duplicate cards detected{Colors.RESET}")
            return

        all_cards = all_new_cards
    except ValueError as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD}Flop:{Colors.RESET} {' '.join(c.colored_str() for c in flop_cards)}")

    # Evaluate current hand
    current_hand = HandEvaluator.evaluate_hand(hole_cards + flop_cards)
    hand_color = Colors.GREEN if current_hand[0].value >= 6 else Colors.YELLOW
    print(f"{Colors.BOLD}Current hand:{Colors.RESET} {hand_color}{current_hand[0].name}{Colors.RESET}")

    # Draw analysis
    draw_info = DrawAnalyzer.analyze_draws(hole_cards, flop_cards)
    if draw_info['draws']:
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}Draws Detected:{Colors.RESET}")
        for draw_name, outs in draw_info['draws']:
            print(f"  {Colors.MAGENTA}•{Colors.RESET} {draw_name}: {Colors.YELLOW}{outs} outs{Colors.RESET}")
        print(f"  Estimated improvement: ~{draw_info['estimated_win_probability']*100:.1f}%")

    print(f"\n{Colors.GRAY}Calculating post-flop win probability (10000 simulations)...{Colors.RESET}")

    flop_prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, flop_cards, num_opponents, num_simulations=10000,
        progress_callback=lambda c, t: print_progress_bar(c, t) if c % 1000 == 0 else None
    )
    print_progress_bar(10000, 10000)

    print(f"\n{Colors.BOLD}Win Probabilities:{Colors.RESET}")
    display_probability_bar("Win", flop_prob['win'], Colors.GREEN)
    display_probability_bar("Tie", flop_prob['tie'], Colors.YELLOW)
    display_probability_bar("Loss", flop_prob['loss'], Colors.RED)

    # Pot odds calculation
    print(f"\n{Colors.BOLD}POT ODDS ANALYSIS{Colors.RESET}")
    pot_size = 0
    bet_to_call = 0
    stack_size = 1000

    try:
        pot_size = float(input("Current pot size: $"))
        bet_to_call = float(input("Bet to call: $"))

        if ADVANCED_FEATURES:
            stack_input = input(f"Your stack size (default $1000): $").strip()
            if stack_input:
                stack_size = float(stack_input)

        pot_odds = ProbabilityCalculator.calculate_pot_odds(pot_size, bet_to_call)
        ev = ProbabilityCalculator.calculate_expected_value(flop_prob['win_or_tie'], pot_size, bet_to_call)

        print(f"\n{Colors.BOLD}Analysis:{Colors.RESET}")
        print(f"  Pot odds required: {Colors.YELLOW}{pot_odds*100:.2f}%{Colors.RESET}")
        print(f"  Your equity: {Colors.CYAN}{flop_prob['win_or_tie']*100:.2f}%{Colors.RESET}")
        print(f"  Expected value: {Colors.GREEN if ev > 0 else Colors.RED}${ev:.2f}{Colors.RESET}")

        should_call = ProbabilityCalculator.should_call(flop_prob['win_or_tie'], pot_odds)

        if should_call:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ RECOMMENDATION: CALL{Colors.RESET}")
            print(f"{Colors.GREEN}You have sufficient equity to call profitably{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ RECOMMENDATION: FOLD{Colors.RESET}")
            print(f"{Colors.RED}Insufficient equity - calling would be -EV{Colors.RESET}")

        # GTO Solver recommendations
        if ADVANCED_FEATURES:
            gto_solver = GTO_Solver()
            gto_action = gto_solver.get_gto_action(flop_prob['win'], pot_size, stack_size)

            print(f"\n{Colors.CYAN}{Colors.BOLD}GTO SOLVER RECOMMENDATION:{Colors.RESET}")
            print(f"  Action: {Colors.YELLOW}{Colors.BOLD}{gto_action['action']}{Colors.RESET}")
            print(f"  Reasoning: {Colors.GRAY}{gto_action['reasoning']}{Colors.RESET}")

            if gto_action.get('bet_frequency'):
                print(f"  Bet Frequency: {Colors.CYAN}{gto_action['bet_frequency']:.1f}%{Colors.RESET}")
            if gto_action.get('bluff_ratio'):
                print(f"  Bluff Ratio: {Colors.CYAN}{gto_action['bluff_ratio']:.1f}%{Colors.RESET}")
            if gto_action.get('optimal_bet_size'):
                print(f"  Optimal Bet Size: {Colors.YELLOW}${gto_action['optimal_bet_size']:.2f}{Colors.RESET}")

    except ValueError:
        print(f"{Colors.YELLOW}Skipping pot odds analysis{Colors.RESET}")

    # AI Opponent Analysis
    if ADVANCED_FEATURES:
        analyze_opponent = input(f"\n{Colors.CYAN}Analyze opponent? (y/n):{Colors.RESET} ").strip().lower()

        if analyze_opponent == 'y':
            print(f"\n{Colors.CYAN}{Colors.BOLD}AI OPPONENT ANALYSIS{Colors.RESET}")

            try:
                vpip = float(input("  Opponent VPIP % (e.g., 25 for 25%): ")) / 100
                pfr = float(input("  Opponent PFR % (e.g., 18 for 18%): ")) / 100
                aggression = float(input("  Opponent Aggression Factor (e.g., 2.0): "))

                action_input = input("  Recent actions (e.g., raise,bet or press Enter): ").strip()
                action_history = action_input.split(',') if action_input else []

                bet_size_input = input("  Opponent's bet size (default 0): $").strip()
                opponent_bet = float(bet_size_input) if bet_size_input else 0

                # Run advanced AI analysis
                advanced_ai = AdvancedAI()
                opponent_modeler = OpponentModeler()

                # Get board texture from opponent modeler
                opponent_range = opponent_modeler.estimate_opponent_range(hole_cards, flop_cards, num_opponents)
                board_texture = opponent_range['board_texture']

                ai_analysis = advanced_ai.analyze_opponent(
                    vpip=vpip,
                    pfr=pfr,
                    aggression=aggression,
                    action_history=action_history,
                    bet_size=opponent_bet,
                    pot_size=pot_size,
                    board_texture=board_texture
                )

                # Player Profile
                profile = ai_analysis['player_profile']
                print(f"\n  {Colors.BOLD}Player Type:{Colors.RESET} {Colors.YELLOW}{profile['full_name']}{Colors.RESET}")
                print(f"  {Colors.GRAY}VPIP: {profile['stats']['vpip']:.1f}%, PFR: {profile['stats']['pfr']:.1f}%, Aggression: {profile['stats']['aggression']:.1f}{Colors.RESET}")

                # Exploitative Strategy
                exploit = ai_analysis['exploitative_strategy']
                print(f"\n  {Colors.BOLD}Counter Strategy:{Colors.RESET}")
                if exploit.get('general'):
                    print(f"    {Colors.CYAN}General:{Colors.RESET} {exploit['general']}")
                if exploit.get('counter_strategy'):
                    print(f"    {Colors.CYAN}Key Approach:{Colors.RESET} {exploit['counter_strategy']}")
                if exploit.get('when_they_bet'):
                    print(f"    {Colors.CYAN}When They Bet:{Colors.RESET} {exploit['when_they_bet']}")
                if exploit.get('bluff_frequency'):
                    print(f"    {Colors.CYAN}Bluff Tendency:{Colors.RESET} {exploit['bluff_frequency']}")

                # Bluff Analysis
                if ai_analysis['bluff_analysis'] and ai_analysis['bluff_analysis'].get('indicators'):
                    bluff = ai_analysis['bluff_analysis']
                    print(f"\n  {Colors.BOLD}Bluff Analysis:{Colors.RESET}")
                    if bluff.get('likelihood'):
                        print(f"    Likelihood: {Colors.YELLOW}{bluff['likelihood']}{Colors.RESET}")
                    if bluff.get('confidence'):
                        print(f"    Confidence: {bluff['confidence']}")
                    if bluff.get('probability'):
                        print(f"    Probability: {bluff['probability']*100:.1f}%")

                    print(f"    Indicators:")
                    for indicator in bluff['indicators']:
                        print(f"      {Colors.GRAY}• {indicator}{Colors.RESET}")

                    if bluff.get('recommendation'):
                        print(f"    {Colors.CYAN}{bluff['recommendation']}{Colors.RESET}")

                # Pattern Recognition
                if ai_analysis.get('patterns_detected'):
                    patterns_data = ai_analysis['patterns_detected']
                    if isinstance(patterns_data, dict) and patterns_data.get('patterns'):
                        patterns = patterns_data['patterns']
                        if patterns:
                            print(f"\n  {Colors.BOLD}Betting Patterns Detected:{Colors.RESET}")
                            for pattern in patterns:
                                pattern_name = pattern.get('pattern', pattern.get('name', 'Unknown'))
                                print(f"    {Colors.MAGENTA}• {pattern_name}{Colors.RESET}: {pattern.get('description', '')}")
                                if pattern.get('counter_strategy'):
                                    print(f"      {Colors.CYAN}Counter:{Colors.RESET} {Colors.GRAY}{pattern['counter_strategy']}{Colors.RESET}")

            except ValueError as e:
                print(f"{Colors.RED}✗ Error in opponent analysis: {e}{Colors.RESET}")

    # Turn
    print_header("TURN", Colors.CYAN)
    turn_input = input(f"{Colors.BOLD}Enter turn card{Colors.RESET} (or press Enter to quit): ").strip()
    if not turn_input:
        return

    try:
        turn_card = parse_card(turn_input)
        all_new_cards = all_cards + [turn_card]
        if not validate_unique_cards(all_new_cards):
            print(f"{Colors.RED}✗ Error: Duplicate card{Colors.RESET}")
            return
        all_cards = all_new_cards
    except ValueError as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
        return

    community_cards = flop_cards + [turn_card]

    print(f"\n{Colors.BOLD}Board:{Colors.RESET} {' '.join(c.colored_str() for c in community_cards)}")
    current_hand = HandEvaluator.evaluate_hand(hole_cards + community_cards)
    hand_color = Colors.GREEN if current_hand[0].value >= 6 else Colors.YELLOW
    print(f"{Colors.BOLD}Current hand:{Colors.RESET} {hand_color}{current_hand[0].name}{Colors.RESET}")

    print(f"\n{Colors.GRAY}Calculating turn win probability (10000 simulations)...{Colors.RESET}")

    turn_prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, community_cards, num_opponents, num_simulations=10000,
        progress_callback=lambda c, t: print_progress_bar(c, t) if c % 1000 == 0 else None
    )
    print_progress_bar(10000, 10000)

    print(f"\n{Colors.BOLD}Win Probabilities:{Colors.RESET}")
    display_probability_bar("Win", turn_prob['win'], Colors.GREEN)
    display_probability_bar("Tie", turn_prob['tie'], Colors.YELLOW)
    display_probability_bar("Loss", turn_prob['loss'], Colors.RED)

    # River
    print_header("RIVER", Colors.CYAN)
    river_input = input(f"{Colors.BOLD}Enter river card{Colors.RESET} (or press Enter to quit): ").strip()
    if not river_input:
        return

    try:
        river_card = parse_card(river_input)
        all_new_cards = all_cards + [river_card]
        if not validate_unique_cards(all_new_cards):
            print(f"{Colors.RED}✗ Error: Duplicate card{Colors.RESET}")
            return
        all_cards = all_new_cards
    except ValueError as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.RESET}")
        return

    community_cards = community_cards + [river_card]

    print(f"\n{Colors.BOLD}Final Board:{Colors.RESET} {' '.join(c.colored_str() for c in community_cards)}")
    final_hand = HandEvaluator.evaluate_hand(hole_cards + community_cards)

    hand_color = Colors.GREEN if final_hand[0].value >= 6 else Colors.YELLOW
    print(f"\n{Colors.BOLD}Your Final Hand:{Colors.RESET} {hand_color}{Colors.BOLD}{final_hand[0].name}{Colors.RESET}")

    print(f"\n{Colors.GRAY}Calculating river win probability (15000 simulations)...{Colors.RESET}")

    river_prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, community_cards, num_opponents, num_simulations=15000,
        progress_callback=lambda c, t: print_progress_bar(c, t) if c % 1000 == 0 else None
    )
    print_progress_bar(15000, 15000)

    print(f"\n{Colors.BOLD}Final Win Probabilities:{Colors.RESET}")
    display_probability_bar("Win", river_prob['win'], Colors.GREEN)
    display_probability_bar("Tie", river_prob['tie'], Colors.YELLOW)
    display_probability_bar("Loss", river_prob['loss'], Colors.RED)

    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}Analysis complete! Good luck at the tables!{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Session ended by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}✗ Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)
