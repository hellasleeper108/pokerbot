#!/usr/bin/env python3
"""
Quick Analysis Mode - Fast poker hand analysis from command line
Usage: python3 quick_analyze.py "As Kd" "Ah 7s 3c" --opponents 2
"""

import sys
import argparse
from poker_bot_enhanced import (
    parse_card, HandEvaluator, ProbabilityCalculator, PreFlopAnalyzer,
    DrawAnalyzer, Colors, validate_unique_cards
)


def quick_analyze(hole_cards_str: str, community_cards_str: str = "",
                 num_opponents: int = 1, simulations: int = 5000):
    """Quickly analyze a poker situation"""

    try:
        # Parse cards
        hole_cards = [parse_card(c) for c in hole_cards_str.split()]
        if len(hole_cards) != 2:
            print(f"{Colors.RED}Error: Must provide exactly 2 hole cards{Colors.RESET}")
            return 1

        community_cards = []
        if community_cards_str:
            community_cards = [parse_card(c) for c in community_cards_str.split()]
            if len(community_cards) > 5:
                print(f"{Colors.RED}Error: Maximum 5 community cards{Colors.RESET}")
                return 1

        # Validate unique cards
        all_cards = hole_cards + community_cards
        if not validate_unique_cards(all_cards):
            print(f"{Colors.RED}Error: Duplicate cards detected{Colors.RESET}")
            return 1

    except ValueError as e:
        print(f"{Colors.RED}Error parsing cards: {e}{Colors.RESET}")
        return 1

    # Display situation
    print(f"\n{Colors.CYAN}{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BOLD}QUICK POKER ANALYSIS{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.RESET}\n")

    print(f"{Colors.BOLD}Your Hand:{Colors.RESET} {hole_cards[0].colored_str()} {hole_cards[1].colored_str()}")

    if community_cards:
        print(f"{Colors.BOLD}Board:{Colors.RESET}     {' '.join(c.colored_str() for c in community_cards)}")

        # Show current hand
        current_hand = HandEvaluator.evaluate_hand(hole_cards + community_cards)
        hand_color = Colors.GREEN if current_hand[0].value >= 6 else Colors.YELLOW
        print(f"{Colors.BOLD}Current:{Colors.RESET}   {hand_color}{current_hand[0].name}{Colors.RESET}")

    print(f"{Colors.BOLD}Opponents:{Colors.RESET} {num_opponents}")

    # Pre-flop analysis
    if not community_cards:
        chen_score = PreFlopAnalyzer.calculate_chen_formula(hole_cards)
        category, cat_color = PreFlopAnalyzer.get_hand_category(chen_score)
        print(f"{Colors.BOLD}Strength:{Colors.RESET}  {cat_color}{category}{Colors.RESET} (Chen: {chen_score:.1f})")

    # Draw analysis
    if community_cards and len(community_cards) < 5:
        draw_info = DrawAnalyzer.analyze_draws(hole_cards, community_cards)
        if draw_info['draws']:
            print(f"\n{Colors.MAGENTA}{Colors.BOLD}Draws:{Colors.RESET}")
            for draw_name, outs in draw_info['draws']:
                print(f"  • {draw_name}: {Colors.YELLOW}{outs} outs{Colors.RESET}")

    # Calculate probabilities
    print(f"\n{Colors.GRAY}Running {simulations} simulations...{Colors.RESET}")

    prob = ProbabilityCalculator.calculate_win_probability(
        hole_cards, community_cards, num_opponents, num_simulations=simulations
    )

    # Display results
    print(f"\n{Colors.BOLD}PROBABILITIES{Colors.RESET}")

    # Create visual bars
    bar_length = 40

    # Win bar
    win_filled = int(bar_length * prob['win'])
    win_bar = '█' * win_filled + '░' * (bar_length - win_filled)
    print(f"  {Colors.GREEN}Win  [{win_bar}] {prob['win']*100:5.1f}%{Colors.RESET}")

    # Tie bar
    tie_filled = int(bar_length * prob['tie'])
    tie_bar = '█' * tie_filled + '░' * (bar_length - tie_filled)
    print(f"  {Colors.YELLOW}Tie  [{tie_bar}] {prob['tie']*100:5.1f}%{Colors.RESET}")

    # Loss bar
    loss_filled = int(bar_length * prob['loss'])
    loss_bar = '█' * loss_filled + '░' * (bar_length - loss_filled)
    print(f"  {Colors.RED}Loss [{loss_bar}] {prob['loss']*100:5.1f}%{Colors.RESET}")

    print(f"\n{Colors.BOLD}Win or Tie: {Colors.CYAN}{prob['win_or_tie']*100:.2f}%{Colors.RESET}")

    print(f"\n{Colors.CYAN}{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.RESET}\n")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Quick poker hand analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Pre-flop analysis
  python3 quick_analyze.py "As Kd" --opponents 2

  # Post-flop analysis
  python3 quick_analyze.py "As Kd" "Ah 7s 3c" --opponents 2

  # Turn analysis
  python3 quick_analyze.py "Jh Jd" "9h 8h 2c 7s" --opponents 3

  # High precision
  python3 quick_analyze.py "As Kd" "Ah Kh Qh" --opponents 1 --simulations 20000

Card format: Rank + Suit
  Ranks: A K Q J 10 9 8 7 6 5 4 3 2
  Suits: s(♠) h(♥) d(♦) c(♣)
  Example: As = Ace of Spades, 10h = Ten of Hearts
        """
    )

    parser.add_argument('hole_cards', help='Your 2 hole cards (e.g., "As Kd")')
    parser.add_argument('community_cards', nargs='?', default='',
                       help='Community cards: 0-5 cards (e.g., "Ah 7s 3c")')
    parser.add_argument('-o', '--opponents', type=int, default=1,
                       help='Number of opponents (default: 1)')
    parser.add_argument('-s', '--simulations', type=int, default=5000,
                       help='Number of simulations (default: 5000, more = slower but more accurate)')
    parser.add_argument('--no-color', action='store_true',
                       help='Disable colored output')

    args = parser.parse_args()

    if args.no_color:
        Colors.disable()

    return quick_analyze(args.hole_cards, args.community_cards,
                        args.opponents, args.simulations)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Cancelled{Colors.RESET}")
        sys.exit(130)
