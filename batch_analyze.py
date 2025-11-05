#!/usr/bin/env python3
"""
Batch Analysis Mode - Analyze multiple poker scenarios at once
Usage: python3 batch_analyze.py scenarios.txt
"""

import sys
import argparse
from typing import List, Tuple
from poker_bot_enhanced import (
    parse_card, HandEvaluator, ProbabilityCalculator, PreFlopAnalyzer,
    Colors, validate_unique_cards, Card
)


class Scenario:
    """Represents a poker scenario to analyze"""

    def __init__(self, name: str, hole_cards: List[Card],
                 community_cards: List[Card], num_opponents: int):
        self.name = name
        self.hole_cards = hole_cards
        self.community_cards = community_cards
        self.num_opponents = num_opponents


def parse_scenario_line(line: str) -> Scenario:
    """Parse a scenario from a line in the format:
    Name | Hole Cards | Community Cards | Opponents
    Example: AA vs KK | As Ah | Ks Kh | 1
    """
    parts = [p.strip() for p in line.split('|')]

    if len(parts) < 3:
        raise ValueError("Invalid format. Expected: Name | Hole Cards | Community Cards | Opponents")

    name = parts[0]
    hole_cards = [parse_card(c) for c in parts[1].split()]

    if len(hole_cards) != 2:
        raise ValueError(f"Must provide exactly 2 hole cards, got {len(hole_cards)}")

    community_cards = []
    if len(parts) > 2 and parts[2]:
        community_cards = [parse_card(c) for c in parts[2].split()]

    num_opponents = 1
    if len(parts) > 3:
        num_opponents = int(parts[3])

    # Validate unique cards
    all_cards = hole_cards + community_cards
    if not validate_unique_cards(all_cards):
        raise ValueError("Duplicate cards detected")

    return Scenario(name, hole_cards, community_cards, num_opponents)


def load_scenarios(filename: str) -> List[Scenario]:
    """Load scenarios from a file"""
    scenarios = []

    try:
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                try:
                    scenario = parse_scenario_line(line)
                    scenarios.append(scenario)
                except Exception as e:
                    print(f"{Colors.YELLOW}Warning: Skipping line {line_num}: {e}{Colors.RESET}")

    except FileNotFoundError:
        print(f"{Colors.RED}Error: File '{filename}' not found{Colors.RESET}")
        sys.exit(1)

    return scenarios


def analyze_scenario(scenario: Scenario, simulations: int = 3000) -> dict:
    """Analyze a single scenario"""

    prob = ProbabilityCalculator.calculate_win_probability(
        scenario.hole_cards,
        scenario.community_cards,
        scenario.num_opponents,
        num_simulations=simulations
    )

    result = {
        'name': scenario.name,
        'hole_cards': scenario.hole_cards,
        'community_cards': scenario.community_cards,
        'num_opponents': scenario.num_opponents,
        'probabilities': prob
    }

    # Add hand evaluation if possible
    if len(scenario.hole_cards + scenario.community_cards) >= 5:
        hand_rank, _ = HandEvaluator.evaluate_hand(
            scenario.hole_cards + scenario.community_cards
        )
        result['hand_rank'] = hand_rank
    else:
        # Pre-flop chen score
        chen_score = PreFlopAnalyzer.calculate_chen_formula(scenario.hole_cards)
        result['chen_score'] = chen_score

    return result


def display_results(results: List[dict], sort_by: str = 'win'):
    """Display batch analysis results"""

    print(f"\n{Colors.CYAN}{Colors.BOLD}{'═' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{'BATCH ANALYSIS RESULTS'.center(80)}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'═' * 80}{Colors.RESET}\n")

    # Sort results
    if sort_by == 'win':
        results.sort(key=lambda r: r['probabilities']['win'], reverse=True)
    elif sort_by == 'name':
        results.sort(key=lambda r: r['name'])

    # Display table header
    print(f"{Colors.BOLD}{'Scenario':<30} {'Hand':<20} {'Win %':>8} {'Tie %':>8} {'Loss %':>8}{Colors.RESET}")
    print(f"{Colors.GRAY}{'-' * 80}{Colors.RESET}")

    # Display each result
    for i, result in enumerate(results, 1):
        prob = result['probabilities']

        # Format cards
        hole_str = ' '.join(str(c) for c in result['hole_cards'])

        # Get hand description
        if 'hand_rank' in result:
            hand_desc = result['hand_rank'].name
        elif 'chen_score' in result:
            hand_desc = f"Chen: {result['chen_score']:.1f}"
        else:
            hand_desc = "Unknown"

        # Color code based on win probability
        if prob['win'] >= 0.7:
            row_color = Colors.GREEN
        elif prob['win'] >= 0.5:
            row_color = Colors.CYAN
        elif prob['win'] >= 0.3:
            row_color = Colors.YELLOW
        else:
            row_color = Colors.RED

        # Print row
        print(f"{row_color}{result['name']:<30}{Colors.RESET} "
              f"{hole_str:<20} "
              f"{prob['win']*100:>7.1f}% "
              f"{prob['tie']*100:>7.1f}% "
              f"{prob['loss']*100:>7.1f}%")

    print(f"\n{Colors.GRAY}Analyzed {len(results)} scenarios{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'═' * 80}{Colors.RESET}\n")


def display_detailed_result(result: dict):
    """Display detailed analysis of a single result"""

    print(f"\n{Colors.BOLD}Scenario:{Colors.RESET} {result['name']}")
    print(f"{Colors.BOLD}Hand:{Colors.RESET}     {' '.join(c.colored_str() for c in result['hole_cards'])}")

    if result['community_cards']:
        print(f"{Colors.BOLD}Board:{Colors.RESET}    {' '.join(c.colored_str() for c in result['community_cards'])}")

    if 'hand_rank' in result:
        hand_color = Colors.GREEN if result['hand_rank'].value >= 6 else Colors.YELLOW
        print(f"{Colors.BOLD}Rank:{Colors.RESET}     {hand_color}{result['hand_rank'].name}{Colors.RESET}")

    print(f"{Colors.BOLD}Opponents:{Colors.RESET} {result['num_opponents']}")

    prob = result['probabilities']

    print(f"\n{Colors.BOLD}Probabilities:{Colors.RESET}")
    print(f"  {Colors.GREEN}Win:  {prob['win']*100:5.1f}%{Colors.RESET}")
    print(f"  {Colors.YELLOW}Tie:  {prob['tie']*100:5.1f}%{Colors.RESET}")
    print(f"  {Colors.RED}Loss: {prob['loss']*100:5.1f}%{Colors.RESET}")


def create_example_file(filename: str = "example_scenarios.txt"):
    """Create an example scenarios file"""

    content = """# Poker Scenarios - Batch Analysis
# Format: Name | Hole Cards | Community Cards | Opponents
#
# Card format: Rank (A,K,Q,J,10,9-2) + Suit (s,h,d,c)
# Examples: As = Ace of Spades, 10h = Ten of Hearts
#
# Leave Community Cards empty for pre-flop analysis
# Opponents defaults to 1 if not specified

# Classic matchups
AA vs KK preflop | As Ah | | 1
AA vs KK on flop | As Ah | Kc 7d 2h | 1
Pocket Aces | As Ah | | 3

# Drawing hands
Flush draw | Ah 7h | Kh 3h 2c | 2
Straight draw | 9s 8s | 7h 6d 2c | 2
Gutshot | Jh 10h | 8d 7c 2s | 1

# Made hands
Top pair | As Kd | Ah 7s 3c | 2
Two pair | Jh Js | Jc 3s 3h | 2
Set | 7h 7d | 7s Ah Kc | 3

# Weak hands
Low pair | 3h 3d | Ah Kc Qd | 2
High cards | As Kh | 9d 7c 2s | 2

# Dominated hands
Ace weak kicker | Ah 2d | | 1
Ace vs Ace | As Kh | Ah Qd | 1
"""

    try:
        with open(filename, 'w') as f:
            f.write(content)
        print(f"{Colors.GREEN}Created example file: {filename}{Colors.RESET}")
        return True
    except Exception as e:
        print(f"{Colors.RED}Error creating example file: {e}{Colors.RESET}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Batch poker hand analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
File Format:
  Each line: Name | Hole Cards | Community Cards | Opponents

  Example:
    Pocket Aces | As Ah | | 2
    Flush draw | Ah 7h | Kh 3h 2c | 1

  Lines starting with # are comments
  Blank lines are ignored

Examples:
  python3 batch_analyze.py scenarios.txt
  python3 batch_analyze.py scenarios.txt --simulations 10000
  python3 batch_analyze.py --create-example
        """
    )

    parser.add_argument('file', nargs='?', help='Scenarios file to analyze')
    parser.add_argument('-s', '--simulations', type=int, default=3000,
                       help='Simulations per scenario (default: 3000)')
    parser.add_argument('--sort', choices=['win', 'name'], default='win',
                       help='Sort results by win rate or name (default: win)')
    parser.add_argument('--create-example', action='store_true',
                       help='Create an example scenarios file')
    parser.add_argument('--detailed', action='store_true',
                       help='Show detailed results for each scenario')
    parser.add_argument('--no-color', action='store_true',
                       help='Disable colored output')

    args = parser.parse_args()

    if args.no_color:
        Colors.disable()

    # Create example file
    if args.create_example:
        create_example_file()
        return 0

    # Require file argument if not creating example
    if not args.file:
        parser.print_help()
        return 1

    # Load scenarios
    print(f"{Colors.GRAY}Loading scenarios from {args.file}...{Colors.RESET}")
    scenarios = load_scenarios(args.file)

    if not scenarios:
        print(f"{Colors.YELLOW}No valid scenarios found{Colors.RESET}")
        return 1

    print(f"{Colors.GREEN}Loaded {len(scenarios)} scenarios{Colors.RESET}")

    # Analyze scenarios
    results = []
    print(f"\n{Colors.GRAY}Analyzing scenarios ({args.simulations} simulations each)...{Colors.RESET}\n")

    for i, scenario in enumerate(scenarios, 1):
        print(f"{Colors.GRAY}[{i}/{len(scenarios)}] {scenario.name}...{Colors.RESET}", end='\r')
        result = analyze_scenario(scenario, args.simulations)
        results.append(result)

    print()  # New line after progress

    # Display results
    if args.detailed:
        for result in results:
            display_detailed_result(result)
            print()
    else:
        display_results(results, args.sort)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Cancelled{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        sys.exit(1)
