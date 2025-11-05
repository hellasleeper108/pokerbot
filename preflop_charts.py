#!/usr/bin/env python3
"""
Pre-flop Range Charts Generator
Generates starting hand recommendations based on position and table dynamics
"""

from enum import Enum
from typing import List, Set, Dict
from poker_bot_enhanced import Card, Rank, Suit, Colors, PreFlopAnalyzer


class Position(Enum):
    """Player positions at the table"""
    UTG = "Under the Gun"  # Early position
    UTG1 = "UTG+1"
    UTG2 = "UTG+2"
    MP = "Middle Position"
    MP1 = "MP+1"
    CO = "Cutoff"  # Late position
    BTN = "Button"  # Best position
    SB = "Small Blind"
    BB = "Big Blind"


class HandCategory(Enum):
    """Hand strength categories"""
    PREMIUM = "Premium"  # Top tier hands
    STRONG = "Strong"    # Very playable
    PLAYABLE = "Playable"  # Good in position
    SPECULATIVE = "Speculative"  # Small pairs, suited connectors
    MARGINAL = "Marginal"  # Borderline hands


class PreFlopChart:
    """Generates and displays pre-flop starting hand charts"""

    # Hand rankings for different positions (tighter early, looser late)
    PREMIUM_HANDS = {
        'AA', 'KK', 'QQ', 'AKs', 'AKo'
    }

    STRONG_HANDS = {
        'JJ', 'TT', 'AQs', 'AQo', 'AJs', 'AJo', 'KQs'
    }

    PLAYABLE_HANDS = {
        '99', '88', 'ATs', 'ATo', 'KJs', 'KJo', 'KQo', 'QJs', 'QJo', 'JTs'
    }

    SPECULATIVE_HANDS = {
        '77', '66', '55', '44', '33', '22',  # Small pairs
        'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s',  # Suited aces
        'KTs', 'K9s', 'QTs', 'Q9s', 'JTs', 'J9s', 'T9s', 'T8s', '98s', '87s', '76s', '65s'  # Suited connectors
    }

    MARGINAL_HANDS = {
        'A9o', 'A8o', 'A7o', 'A6o', 'A5o', 'A4o', 'A3o', 'A2o',
        'KTo', 'K9o', 'QTo', 'Q9o', 'JTo', 'J9o', 'T9o'
    }

    @staticmethod
    def get_hand_notation(card1: Card, card2: Card) -> str:
        """Convert two cards to standard notation (e.g., AKs, AKo, 99)"""
        rank1 = PreFlopChart._rank_to_char(card1.rank)
        rank2 = PreFlopChart._rank_to_char(card2.rank)

        # Pairs
        if card1.rank == card2.rank:
            return f"{rank1}{rank2}"

        # Order by rank (higher first)
        if card1.rank.value > card2.rank.value:
            high, low = rank1, rank2
        else:
            high, low = rank2, rank1

        # Suited or offsuit
        suffix = 's' if card1.suit == card2.suit else 'o'
        return f"{high}{low}{suffix}"

    @staticmethod
    def _rank_to_char(rank: Rank) -> str:
        """Convert rank to character"""
        char_map = {
            Rank.ACE: 'A', Rank.KING: 'K', Rank.QUEEN: 'Q', Rank.JACK: 'J', Rank.TEN: 'T',
            Rank.NINE: '9', Rank.EIGHT: '8', Rank.SEVEN: '7', Rank.SIX: '6',
            Rank.FIVE: '5', Rank.FOUR: '4', Rank.THREE: '3', Rank.TWO: '2'
        }
        return char_map[rank]

    @staticmethod
    def categorize_hand(hand_notation: str) -> HandCategory:
        """Categorize a hand by its notation"""
        if hand_notation in PreFlopChart.PREMIUM_HANDS:
            return HandCategory.PREMIUM
        elif hand_notation in PreFlopChart.STRONG_HANDS:
            return HandCategory.STRONG
        elif hand_notation in PreFlopChart.PLAYABLE_HANDS:
            return HandCategory.PLAYABLE
        elif hand_notation in PreFlopChart.SPECULATIVE_HANDS:
            return HandCategory.SPECULATIVE
        elif hand_notation in PreFlopChart.MARGINAL_HANDS:
            return HandCategory.MARGINAL
        return None

    @staticmethod
    def get_position_range(position: Position, num_players: int = 9) -> Dict[HandCategory, Set[str]]:
        """Get recommended hand range for a specific position"""
        ranges = {
            HandCategory.PREMIUM: PreFlopChart.PREMIUM_HANDS.copy(),
            HandCategory.STRONG: set(),
            HandCategory.PLAYABLE: set(),
            HandCategory.SPECULATIVE: set(),
            HandCategory.MARGINAL: set()
        }

        # Early position (UTG, UTG+1, UTG+2) - tight range
        if position in [Position.UTG, Position.UTG1, Position.UTG2]:
            ranges[HandCategory.STRONG] = {'JJ', 'TT', 'AQs', 'AKo'}
            ranges[HandCategory.PLAYABLE] = {'99', 'AQo', 'AJs', 'KQs'}

        # Middle position - moderately tight
        elif position in [Position.MP, Position.MP1]:
            ranges[HandCategory.STRONG] = PreFlopChart.STRONG_HANDS.copy()
            ranges[HandCategory.PLAYABLE] = {'99', '88', 'ATs', 'AQo', 'KJs', 'KQo', 'QJs'}
            ranges[HandCategory.SPECULATIVE] = {'77', '66', 'A5s', 'A4s', 'JTs', 'T9s', '98s'}

        # Late position (CO, BTN) - wider range
        elif position in [Position.CO, Position.BTN]:
            ranges[HandCategory.STRONG] = PreFlopChart.STRONG_HANDS.copy()
            ranges[HandCategory.PLAYABLE] = PreFlopChart.PLAYABLE_HANDS.copy()
            ranges[HandCategory.SPECULATIVE] = PreFlopChart.SPECULATIVE_HANDS.copy()
            if position == Position.BTN:
                # Button can play even wider
                ranges[HandCategory.MARGINAL] = {'A9o', 'KTo', 'QTo', 'JTo', 'K9s', 'Q9s'}

        # Blinds - depends on action
        elif position == Position.SB:
            ranges[HandCategory.STRONG] = PreFlopChart.STRONG_HANDS.copy()
            ranges[HandCategory.PLAYABLE] = {'99', '88', 'ATs', 'AQo', 'KJs', 'QJs'}
            ranges[HandCategory.SPECULATIVE] = {'77', '66', '55', 'A5s', 'A4s', 'KTs', 'QTs', 'JTs'}

        elif position == Position.BB:
            # BB already invested, can see flop with wider range
            ranges[HandCategory.STRONG] = PreFlopChart.STRONG_HANDS.copy()
            ranges[HandCategory.PLAYABLE] = PreFlopChart.PLAYABLE_HANDS.copy()
            ranges[HandCategory.SPECULATIVE] = {'77', '66', '55', '44', '33', '22',
                                                'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s',
                                                'KTs', 'QTs', 'JTs', 'T9s', '98s', '87s'}

        return ranges

    @staticmethod
    def display_position_chart(position: Position, num_players: int = 9):
        """Display a visual chart for a specific position"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}PRE-FLOP STARTING HANDS - {position.value.upper()}{Colors.RESET}")
        print(f"{Colors.GRAY}{num_players}-handed game{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

        ranges = PreFlopChart.get_position_range(position, num_players)

        # Display by category
        categories = [
            (HandCategory.PREMIUM, Colors.GREEN, "Always raise/3-bet"),
            (HandCategory.STRONG, Colors.CYAN, "Raise in most situations"),
            (HandCategory.PLAYABLE, Colors.YELLOW, "Raise or call depending on action"),
            (HandCategory.SPECULATIVE, Colors.MAGENTA, "Call or raise for value/suited"),
            (HandCategory.MARGINAL, Colors.RED, "Proceed with caution")
        ]

        for category, color, description in categories:
            if ranges[category]:
                hands = sorted(ranges[category])
                print(f"{color}{Colors.BOLD}{category.value}:{Colors.RESET} {Colors.GRAY}{description}{Colors.RESET}")

                # Format hands in rows
                hand_str = ""
                for i, hand in enumerate(hands):
                    hand_str += f"{color}{hand:4}{Colors.RESET} "
                    if (i + 1) % 10 == 0:
                        print(f"  {hand_str}")
                        hand_str = ""
                if hand_str:
                    print(f"  {hand_str}")
                print()

        # Calculate total range
        total_hands = sum(len(hands) for hands in ranges.values())
        # Total possible starting hands is 169 (13 pairs + 78 suited + 78 offsuit)
        total_combos = 0
        for hand_set in ranges.values():
            for hand in hand_set:
                if hand[-1] in ['s', 'o']:  # Non-pairs
                    total_combos += 4 if hand[-1] == 's' else 12
                else:  # Pairs
                    total_combos += 6

        print(f"{Colors.BOLD}Range Summary:{Colors.RESET}")
        print(f"  Total hands: {total_hands}")
        print(f"  Total combos: {total_combos}/1326 ({total_combos/1326*100:.1f}%)")
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

    @staticmethod
    def display_grid_chart():
        """Display a visual grid of all starting hands with color coding"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{'PRE-FLOP HAND STRENGTH GRID'.center(80)}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']

        # Print header
        print(f"      ", end="")
        for rank in ranks:
            print(f"{Colors.BOLD}{rank:4}{Colors.RESET}", end="")
        print()

        # Print grid
        for i, rank1 in enumerate(ranks):
            print(f"{Colors.BOLD}{rank1:4}{Colors.RESET}  ", end="")
            for j, rank2 in enumerate(ranks):
                if i == j:
                    # Pair
                    hand = f"{rank1}{rank2}"
                elif i < j:
                    # Suited (above diagonal)
                    hand = f"{rank1}{rank2}s"
                else:
                    # Offsuit (below diagonal)
                    hand = f"{rank2}{rank1}o"

                category = PreFlopChart.categorize_hand(hand)

                if category == HandCategory.PREMIUM:
                    color = Colors.GREEN
                elif category == HandCategory.STRONG:
                    color = Colors.CYAN
                elif category == HandCategory.PLAYABLE:
                    color = Colors.YELLOW
                elif category == HandCategory.SPECULATIVE:
                    color = Colors.MAGENTA
                elif category == HandCategory.MARGINAL:
                    color = Colors.RED
                else:
                    color = Colors.GRAY

                print(f"{color}{hand:4}{Colors.RESET}", end="")
            print()

        # Legend
        print(f"\n{Colors.BOLD}Legend:{Colors.RESET}")
        print(f"  {Colors.GREEN}█{Colors.RESET} Premium   {Colors.CYAN}█{Colors.RESET} Strong   {Colors.YELLOW}█{Colors.RESET} Playable   {Colors.MAGENTA}█{Colors.RESET} Speculative   {Colors.RED}█{Colors.RESET} Marginal   {Colors.GRAY}█{Colors.RESET} Fold")
        print(f"  Diagonal = Pairs | Above = Suited | Below = Offsuit")
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

    @staticmethod
    def get_recommendation(hole_cards: List[Card], position: Position,
                          action_before: str = "none", num_players: int = 9) -> Dict:
        """Get specific recommendation for a hand in a position"""
        hand_notation = PreFlopChart.get_hand_notation(hole_cards[0], hole_cards[1])
        category = PreFlopChart.categorize_hand(hand_notation)
        ranges = PreFlopChart.get_position_range(position, num_players)

        # Check if hand is in position range
        in_range = False
        for cat, hands in ranges.items():
            if hand_notation in hands:
                in_range = True
                break

        # Generate recommendation
        recommendation = {
            'hand': hand_notation,
            'category': category,
            'in_range': in_range,
            'action': 'FOLD',
            'description': ''
        }

        if not in_range:
            recommendation['action'] = 'FOLD'
            recommendation['description'] = 'Hand not in recommended range for this position'
            return recommendation

        # Action recommendations based on category and prior action
        if category == HandCategory.PREMIUM:
            if action_before == "raise":
                recommendation['action'] = '3-BET/4-BET'
                recommendation['description'] = 'Premium hand - raise for value'
            else:
                recommendation['action'] = 'RAISE'
                recommendation['description'] = 'Premium hand - always raise'

        elif category == HandCategory.STRONG:
            if action_before == "raise":
                recommendation['action'] = 'CALL/3-BET'
                recommendation['description'] = 'Strong hand - call or 3-bet for value'
            else:
                recommendation['action'] = 'RAISE'
                recommendation['description'] = 'Strong hand - open raise'

        elif category == HandCategory.PLAYABLE:
            if action_before == "raise":
                recommendation['action'] = 'CALL'
                recommendation['description'] = 'Playable hand - call to see flop'
            else:
                recommendation['action'] = 'RAISE'
                recommendation['description'] = 'Playable hand - open raise'

        elif category == HandCategory.SPECULATIVE:
            if action_before == "raise":
                recommendation['action'] = 'CALL'
                recommendation['description'] = 'Speculative hand - call for implied odds'
            else:
                recommendation['action'] = 'RAISE/LIMP'
                recommendation['description'] = 'Speculative hand - raise or limp'

        elif category == HandCategory.MARGINAL:
            if action_before == "raise":
                recommendation['action'] = 'FOLD'
                recommendation['description'] = 'Marginal hand - fold to aggression'
            else:
                recommendation['action'] = 'LIMP/FOLD'
                recommendation['description'] = 'Marginal hand - proceed with caution'

        return recommendation


def main():
    """Interactive pre-flop chart tool"""
    import sys

    title = "TEXAS HOLD'EM PRE-FLOP STARTING HAND CHARTS"
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{title.center(80)}{Colors.RESET}")
    print(f"{Colors.MAGENTA}{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

    print(f"{Colors.BOLD}Options:{Colors.RESET}")
    print(f"  1. View hand strength grid")
    print(f"  2. View position-specific chart")
    print(f"  3. Get hand recommendation")
    print(f"  4. View all positions")
    print()

    try:
        choice = input(f"{Colors.BOLD}Select option (1-4):{Colors.RESET} ").strip()

        if choice == "1":
            PreFlopChart.display_grid_chart()

        elif choice == "2":
            print(f"\n{Colors.BOLD}Positions:{Colors.RESET}")
            positions = [Position.UTG, Position.UTG1, Position.MP, Position.CO,
                        Position.BTN, Position.SB, Position.BB]
            for i, pos in enumerate(positions, 1):
                print(f"  {i}. {pos.value}")

            pos_choice = int(input(f"\n{Colors.BOLD}Select position (1-7):{Colors.RESET} ")) - 1
            if 0 <= pos_choice < len(positions):
                PreFlopChart.display_position_chart(positions[pos_choice])

        elif choice == "3":
            from poker_bot_enhanced import parse_card

            hole_input = input(f"\n{Colors.BOLD}Enter your hole cards (e.g., 'As Kh'):{Colors.RESET} ").strip()
            hole_cards = [parse_card(c) for c in hole_input.split()]

            if len(hole_cards) != 2:
                print(f"{Colors.RED}Error: Must enter exactly 2 cards{Colors.RESET}")
                return

            print(f"\n{Colors.BOLD}Positions:{Colors.RESET}")
            positions = [Position.UTG, Position.UTG1, Position.MP, Position.CO,
                        Position.BTN, Position.SB, Position.BB]
            for i, pos in enumerate(positions, 1):
                print(f"  {i}. {pos.value}")

            pos_choice = int(input(f"\n{Colors.BOLD}Select your position (1-7):{Colors.RESET} ")) - 1
            if 0 <= pos_choice < len(positions):
                position = positions[pos_choice]

                action = input(f"\n{Colors.BOLD}Action before you (none/limp/raise):{Colors.RESET} ").strip().lower()
                if action not in ['none', 'limp', 'raise']:
                    action = 'none'

                rec = PreFlopChart.get_recommendation(hole_cards, position, action)

                print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
                print(f"{Colors.BOLD}RECOMMENDATION{Colors.RESET}")
                print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

                print(f"{Colors.BOLD}Hand:{Colors.RESET}     {hole_cards[0].colored_str()} {hole_cards[1].colored_str()} ({rec['hand']})")
                print(f"{Colors.BOLD}Position:{Colors.RESET} {position.value}")

                if rec['category']:
                    cat_color = {
                        HandCategory.PREMIUM: Colors.GREEN,
                        HandCategory.STRONG: Colors.CYAN,
                        HandCategory.PLAYABLE: Colors.YELLOW,
                        HandCategory.SPECULATIVE: Colors.MAGENTA,
                        HandCategory.MARGINAL: Colors.RED
                    }.get(rec['category'], Colors.WHITE)
                    print(f"{Colors.BOLD}Category:{Colors.RESET} {cat_color}{rec['category'].value}{Colors.RESET}")

                action_color = Colors.GREEN if rec['action'] in ['RAISE', '3-BET/4-BET'] else Colors.YELLOW if 'CALL' in rec['action'] else Colors.RED
                print(f"\n{action_color}{Colors.BOLD}→ ACTION: {rec['action']}{Colors.RESET}")
                print(f"{Colors.GRAY}{rec['description']}{Colors.RESET}")

                print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

        elif choice == "4":
            positions = [Position.UTG, Position.UTG1, Position.MP, Position.CO,
                        Position.BTN, Position.SB, Position.BB]
            for pos in positions:
                PreFlopChart.display_position_chart(pos)
                input(f"{Colors.GRAY}Press Enter for next position...{Colors.RESET}")

    except (ValueError, IndexError, KeyboardInterrupt):
        print(f"\n{Colors.YELLOW}Exiting...{Colors.RESET}\n")
        return


if __name__ == "__main__":
    main()
