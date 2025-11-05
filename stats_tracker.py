#!/usr/bin/env python3
"""
Statistics Tracker
Track and analyze poker hand statistics over multiple sessions
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from collections import defaultdict, Counter
from poker_bot_enhanced import Colors, HandRank


class PokerStats:
    """Track and analyze poker statistics"""

    def __init__(self, stats_file: str = "poker_stats.json"):
        self.stats_file = stats_file
        self.hands_played = []
        self.load_stats()

    def load_stats(self):
        """Load statistics from file"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    self.hands_played = data.get('hands', [])
            except Exception as e:
                print(f"{Colors.YELLOW}Warning: Could not load stats: {e}{Colors.RESET}")
                self.hands_played = []
        else:
            self.hands_played = []

    def save_stats(self):
        """Save statistics to file"""
        try:
            data = {
                'last_updated': datetime.now().isoformat(),
                'total_hands': len(self.hands_played),
                'hands': self.hands_played
            }
            with open(self.stats_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"{Colors.RED}Error saving stats: {e}{Colors.RESET}")

    def add_hand(self, hand_data: Dict):
        """Add a hand to statistics"""
        hand_data['timestamp'] = datetime.now().isoformat()
        self.hands_played.append(hand_data)
        self.save_stats()

    def get_summary(self) -> Dict:
        """Get summary statistics"""
        if not self.hands_played:
            return {}

        # Calculate statistics
        total_hands = len(self.hands_played)
        decisions = [h.get('decision') for h in self.hands_played if 'decision' in h]
        outcomes = [h.get('outcome') for h in self.hands_played if 'outcome' in h]
        positions = [h.get('position') for h in self.hands_played if 'position' in h]

        # Pre-flop decisions
        decision_counts = Counter(decisions)

        # Hand outcomes
        outcome_counts = Counter(outcomes)

        # Position statistics
        position_counts = Counter(positions)

        # Calculate win rates by position
        position_wins = defaultdict(lambda: {'wins': 0, 'total': 0})
        for hand in self.hands_played:
            if 'position' in hand and 'outcome' in hand:
                pos = hand['position']
                position_wins[pos]['total'] += 1
                if hand['outcome'] == 'win':
                    position_wins[pos]['wins'] += 1

        position_win_rates = {}
        for pos, stats in position_wins.items():
            if stats['total'] > 0:
                position_win_rates[pos] = (stats['wins'] / stats['total']) * 100

        # Calculate average equity
        equities = [h.get('equity', 0) for h in self.hands_played if 'equity' in h]
        avg_equity = sum(equities) / len(equities) if equities else 0

        # Hand strength analysis
        hand_categories = [h.get('hand_category') for h in self.hands_played if 'hand_category' in h]
        category_counts = Counter(hand_categories)

        # Calculate profit/loss
        profits = [h.get('profit', 0) for h in self.hands_played if 'profit' in h]
        total_profit = sum(profits)

        return {
            'total_hands': total_hands,
            'decision_counts': dict(decision_counts),
            'outcome_counts': dict(outcome_counts),
            'position_counts': dict(position_counts),
            'position_win_rates': position_win_rates,
            'average_equity': avg_equity,
            'category_counts': dict(category_counts),
            'total_profit': total_profit,
            'avg_profit_per_hand': total_profit / total_hands if total_hands > 0 else 0
        }

    def display_summary(self):
        """Display formatted summary statistics"""
        summary = self.get_summary()

        if not summary:
            print(f"{Colors.YELLOW}No hands tracked yet{Colors.RESET}")
            return

        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}{'POKER STATISTICS SUMMARY'.center(70)}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

        # General stats
        print(f"{Colors.BOLD}Overall Statistics:{Colors.RESET}")
        print(f"  Total hands played: {Colors.CYAN}{summary['total_hands']}{Colors.RESET}")
        print(f"  Average equity: {Colors.YELLOW}{summary['average_equity']:.1f}%{Colors.RESET}")

        if summary.get('total_profit'):
            profit_color = Colors.GREEN if summary['total_profit'] >= 0 else Colors.RED
            print(f"  Total profit/loss: {profit_color}${summary['total_profit']:.2f}{Colors.RESET}")
            print(f"  Avg per hand: {profit_color}${summary['avg_profit_per_hand']:.2f}{Colors.RESET}")

        # Decision breakdown
        if summary['decision_counts']:
            print(f"\n{Colors.BOLD}Pre-flop Decisions:{Colors.RESET}")
            for decision, count in sorted(summary['decision_counts'].items(), key=lambda x: x[1], reverse=True):
                pct = (count / summary['total_hands']) * 100
                bar_length = int(pct / 2)
                bar = '█' * bar_length + '░' * (50 - bar_length)
                print(f"  {decision:10} {Colors.CYAN}[{bar}]{Colors.RESET} {count:3} ({pct:5.1f}%)")

        # Outcomes
        if summary['outcome_counts']:
            print(f"\n{Colors.BOLD}Hand Outcomes:{Colors.RESET}")
            for outcome, count in sorted(summary['outcome_counts'].items(), key=lambda x: x[1], reverse=True):
                pct = (count / summary['total_hands']) * 100
                color = Colors.GREEN if outcome == 'win' else Colors.RED if outcome == 'loss' else Colors.YELLOW
                print(f"  {outcome:10} {color}{count:3} ({pct:5.1f}%){Colors.RESET}")

        # Position statistics
        if summary['position_win_rates']:
            print(f"\n{Colors.BOLD}Win Rate by Position:{Colors.RESET}")
            for pos, win_rate in sorted(summary['position_win_rates'].items(), key=lambda x: x[1], reverse=True):
                color = Colors.GREEN if win_rate >= 60 else Colors.YELLOW if win_rate >= 40 else Colors.RED
                bar_length = int(win_rate / 2)
                bar = '█' * bar_length + '░' * (50 - bar_length)
                print(f"  {pos:12} {color}[{bar}]{Colors.RESET} {win_rate:5.1f}%")

        # Hand categories
        if summary['category_counts']:
            print(f"\n{Colors.BOLD}Hands by Category:{Colors.RESET}")
            for category, count in sorted(summary['category_counts'].items(), key=lambda x: x[1], reverse=True):
                pct = (count / summary['total_hands']) * 100
                print(f"  {category:15} {Colors.CYAN}{count:3}{Colors.RESET} ({pct:5.1f}%)")

        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

    def display_recent_hands(self, num_hands: int = 10):
        """Display recent hands"""
        if not self.hands_played:
            print(f"{Colors.YELLOW}No hands tracked yet{Colors.RESET}")
            return

        recent = self.hands_played[-num_hands:]

        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.RESET}")
        print(f"{Colors.BOLD}{'RECENT HANDS'.center(80)}{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

        print(f"{Colors.BOLD}{'#':>3} {'Hand':<10} {'Position':<8} {'Decision':<10} {'Equity':<8} {'Outcome':<8} {'Profit':>10}{Colors.RESET}")
        print(f"{Colors.GRAY}{'-' * 80}{Colors.RESET}")

        for i, hand in enumerate(reversed(recent), 1):
            hand_str = hand.get('hand_notation', 'N/A')
            position = hand.get('position', 'N/A')
            decision = hand.get('decision', 'N/A')
            equity = hand.get('equity', 0)
            outcome = hand.get('outcome', 'N/A')
            profit = hand.get('profit', 0)

            # Color coding
            outcome_color = Colors.GREEN if outcome == 'win' else Colors.RED if outcome == 'loss' else Colors.YELLOW
            profit_color = Colors.GREEN if profit >= 0 else Colors.RED

            print(f"{i:>3} {hand_str:<10} {position:<8} {decision:<10} {equity:>6.1f}%  {outcome_color}{outcome:<8}{Colors.RESET} {profit_color}{profit:>9.2f}{Colors.RESET}")

        print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

    def clear_stats(self):
        """Clear all statistics"""
        self.hands_played = []
        self.save_stats()
        print(f"{Colors.GREEN}✓ Statistics cleared{Colors.RESET}")


class SessionTracker:
    """Track statistics for a single session"""

    def __init__(self):
        self.session_hands = []
        self.start_time = datetime.now()

    def add_hand(self, hand_data: Dict):
        """Add hand to session"""
        hand_data['session_timestamp'] = datetime.now().isoformat()
        self.session_hands.append(hand_data)

    def get_session_summary(self) -> Dict:
        """Get session summary"""
        if not self.session_hands:
            return {}

        total_hands = len(self.session_hands)
        wins = sum(1 for h in self.session_hands if h.get('outcome') == 'win')
        losses = sum(1 for h in self.session_hands if h.get('outcome') == 'loss')

        profits = [h.get('profit', 0) for h in self.session_hands]
        total_profit = sum(profits)

        duration = datetime.now() - self.start_time

        return {
            'total_hands': total_hands,
            'wins': wins,
            'losses': losses,
            'win_rate': (wins / total_hands * 100) if total_hands > 0 else 0,
            'total_profit': total_profit,
            'duration': str(duration).split('.')[0],  # Remove microseconds
        }

    def display_session_summary(self):
        """Display session summary"""
        summary = self.get_session_summary()

        if not summary:
            print(f"{Colors.YELLOW}No hands in current session{Colors.RESET}")
            return

        print(f"\n{Colors.MAGENTA}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{'SESSION SUMMARY'.center(60)}{Colors.RESET}")
        print(f"{Colors.MAGENTA}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

        print(f"{Colors.BOLD}Session Duration:{Colors.RESET} {summary['duration']}")
        print(f"{Colors.BOLD}Hands Played:{Colors.RESET} {summary['total_hands']}")
        print(f"{Colors.BOLD}Wins:{Colors.RESET} {Colors.GREEN}{summary['wins']}{Colors.RESET}")
        print(f"{Colors.BOLD}Losses:{Colors.RESET} {Colors.RED}{summary['losses']}{Colors.RESET}")
        print(f"{Colors.BOLD}Win Rate:{Colors.RESET} {summary['win_rate']:.1f}%")

        profit_color = Colors.GREEN if summary['total_profit'] >= 0 else Colors.RED
        print(f"{Colors.BOLD}Profit/Loss:{Colors.RESET} {profit_color}${summary['total_profit']:.2f}{Colors.RESET}")

        print(f"\n{Colors.MAGENTA}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")


def main():
    """Interactive stats tracker"""
    stats = PokerStats()

    print(f"\n{Colors.MAGENTA}{Colors.BOLD}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{'POKER STATISTICS TRACKER'.center(70)}{Colors.RESET}")
    print(f"{Colors.MAGENTA}{Colors.BOLD}{'=' * 70}{Colors.RESET}\n")

    print(f"{Colors.BOLD}Options:{Colors.RESET}")
    print(f"  1. View summary statistics")
    print(f"  2. View recent hands")
    print(f"  3. Add test data")
    print(f"  4. Clear statistics")
    print()

    try:
        choice = input(f"{Colors.BOLD}Select option (1-4):{Colors.RESET} ").strip()

        if choice == "1":
            stats.display_summary()

        elif choice == "2":
            num = int(input(f"{Colors.BOLD}Number of recent hands to show:{Colors.RESET} ") or "10")
            stats.display_recent_hands(num)

        elif choice == "3":
            # Add some test data
            test_hands = [
                {'hand_notation': 'AA', 'position': 'BTN', 'decision': 'RAISE', 'equity': 85.0, 'outcome': 'win', 'profit': 50.0, 'hand_category': 'PREMIUM'},
                {'hand_notation': 'AKs', 'position': 'CO', 'decision': 'RAISE', 'equity': 67.0, 'outcome': 'win', 'profit': 30.0, 'hand_category': 'PREMIUM'},
                {'hand_notation': 'JJ', 'position': 'UTG', 'decision': 'RAISE', 'equity': 56.0, 'outcome': 'loss', 'profit': -25.0, 'hand_category': 'STRONG'},
                {'hand_notation': '72o', 'position': 'BB', 'decision': 'FOLD', 'equity': 15.0, 'outcome': 'fold', 'profit': -1.0, 'hand_category': 'WEAK'},
                {'hand_notation': 'AQo', 'position': 'MP', 'decision': 'CALL', 'equity': 42.0, 'outcome': 'loss', 'profit': -20.0, 'hand_category': 'STRONG'},
            ]

            for hand in test_hands:
                stats.add_hand(hand)

            print(f"{Colors.GREEN}✓ Added {len(test_hands)} test hands{Colors.RESET}")
            stats.display_summary()

        elif choice == "4":
            confirm = input(f"{Colors.YELLOW}Are you sure? This cannot be undone (yes/no):{Colors.RESET} ")
            if confirm.lower() == 'yes':
                stats.clear_stats()

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Exiting...{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}\n")


if __name__ == "__main__":
    main()
