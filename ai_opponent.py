#!/usr/bin/env python3
"""
AI Opponent Modeling System
Machine learning-based opponent tendency analysis and GTO solver
"""

import json
import random
from typing import List, Dict, Tuple
from collections import defaultdict
from poker_bot_enhanced import Card, HandRank


class OpponentModeler:
    """AI-powered opponent modeling and hand range prediction"""

    def __init__(self):
        # Player tendencies database
        self.player_stats = defaultdict(lambda: {
            'vpip': 0.25,  # Voluntarily Put $ In Pot %
            'pfr': 0.18,   # Pre-Flop Raise %
            'aggression': 1.0,  # Aggression factor
            'cbet': 0.65,  # Continuation bet %
            'fold_to_3bet': 0.60,  # Fold to 3-bet %
            'hands_observed': 0
        })

        # Action patterns for range narrowing
        self.action_weights = {
            'raise': {'premium': 0.4, 'strong': 0.3, 'playable': 0.2, 'speculative': 0.1},
            'call': {'premium': 0.1, 'strong': 0.25, 'playable': 0.35, 'speculative': 0.3},
            'check': {'premium': 0.05, 'strong': 0.15, 'playable': 0.35, 'speculative': 0.45},
            'bet': {'premium': 0.35, 'strong': 0.35, 'playable': 0.2, 'speculative': 0.1}
        }

    def estimate_opponent_range(self, hole_cards: List[Card],
                                community_cards: List[Card],
                                num_opponents: int) -> Dict:
        """
        Estimate opponent hand ranges based on board texture and actions
        """
        # Analyze board texture
        board_texture = self._analyze_board_texture(community_cards)

        # Estimate hand strength distribution
        likely_ranges = {
            'made_hands': self._estimate_made_hands(community_cards, board_texture),
            'drawing_hands': self._estimate_draws(community_cards, board_texture),
            'bluffs': 0.15 if len(community_cards) >= 3 else 0.05
        }

        # Calculate probabilities
        total = sum(likely_ranges.values())
        for key in likely_ranges:
            likely_ranges[key] = (likely_ranges[key] / total) * 100

        return {
            'board_texture': board_texture,
            'estimated_ranges': likely_ranges,
            'recommendation': self._get_range_recommendation(likely_ranges),
            'num_opponents': num_opponents
        }

    def _analyze_board_texture(self, community_cards: List[Card]) -> Dict:
        """Analyze board texture (dry, wet, coordinated)"""
        if not community_cards:
            return {'type': 'preflop', 'danger': 0}

        ranks = [c.rank.value for c in community_cards]
        suits = [c.suit for c in community_cards]

        # Check for flush possibility
        suit_counts = {}
        for suit in suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1

        flush_possible = max(suit_counts.values()) >= 3 if suit_counts else False

        # Check for straight possibility
        sorted_ranks = sorted(set(ranks))
        straight_possible = False

        if len(sorted_ranks) >= 3:
            for i in range(len(sorted_ranks) - 2):
                if sorted_ranks[i+2] - sorted_ranks[i] <= 4:
                    straight_possible = True
                    break

        # Check for pairs on board
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1

        paired_board = any(count >= 2 for count in rank_counts.values())

        # Determine texture type
        danger_level = 0
        if flush_possible:
            danger_level += 3
        if straight_possible:
            danger_level += 2
        if paired_board:
            danger_level += 1

        if danger_level >= 4:
            texture_type = 'very_wet'
        elif danger_level >= 2:
            texture_type = 'wet'
        else:
            texture_type = 'dry'

        return {
            'type': texture_type,
            'flush_possible': flush_possible,
            'straight_possible': straight_possible,
            'paired': paired_board,
            'danger': danger_level
        }

    def _estimate_made_hands(self, community_cards: List[Card],
                            board_texture: Dict) -> float:
        """Estimate probability of opponent having made hand"""
        if not community_cards:
            return 0.5

        base_prob = 0.6

        # Adjust based on board texture
        if board_texture['type'] == 'dry':
            base_prob = 0.7  # More likely to have hit something on dry board
        elif board_texture['type'] == 'very_wet':
            base_prob = 0.5  # Could be drawing

        return base_prob

    def _estimate_draws(self, community_cards: List[Card],
                       board_texture: Dict) -> float:
        """Estimate probability of opponent having draw"""
        if len(community_cards) < 3:
            return 0.0

        draw_prob = 0.2

        if board_texture['flush_possible']:
            draw_prob += 0.15
        if board_texture['straight_possible']:
            draw_prob += 0.1

        return min(draw_prob, 0.5)

    def _get_range_recommendation(self, ranges: Dict) -> str:
        """Get recommendation based on opponent ranges"""
        made_hands = ranges['made_hands']

        if made_hands > 60:
            return "Opponent likely has strong made hand - proceed with caution"
        elif made_hands > 40:
            return "Opponent has moderate strength - value bet strong hands"
        else:
            return "Opponent may be drawing or weak - consider betting for value/protection"

    def predict_range_from_actions(self, actions: List[str],
                                   position: str = None,
                                   board: List[Card] = None,
                                   bet_size: float = 0,
                                   pot_size: float = 100) -> Dict:
        """
        Predict opponent range based on action sequence
        Uses AI/ML-inspired pattern matching
        """
        # Initialize range weights
        range_weights = {
            'premium': 0.25,
            'strong': 0.25,
            'playable': 0.25,
            'speculative': 0.25
        }

        # Update based on each action
        for action in actions:
            if action.lower() in self.action_weights:
                weights = self.action_weights[action.lower()]
                # Bayesian update
                for category in range_weights:
                    range_weights[category] *= weights.get(category, 0.1)

        # Normalize
        total = sum(range_weights.values())
        if total > 0:
            for category in range_weights:
                range_weights[category] = (range_weights[category] / total) * 100

        # Adjust for bet sizing
        if bet_size > 0 and pot_size > 0:
            bet_ratio = bet_size / pot_size

            if bet_ratio > 0.75:  # Large bet (polarized)
                range_weights['premium'] *= 1.5
                range_weights['speculative'] *= 1.3  # Could be bluff
                range_weights['playable'] *= 0.5
            elif bet_ratio < 0.33:  # Small bet (merged range)
                range_weights['playable'] *= 1.3
                range_weights['strong'] *= 1.2

            # Normalize again
            total = sum(range_weights.values())
            for category in range_weights:
                range_weights[category] = (range_weights[category] / total) * 100

        # Generate prediction
        most_likely = max(range_weights.items(), key=lambda x: x[1])

        return {
            'range_distribution': range_weights,
            'most_likely_category': most_likely[0],
            'confidence': most_likely[1],
            'actions_analyzed': len(actions),
            'recommendation': self._get_action_recommendation(range_weights, bet_size, pot_size)
        }

    def _get_action_recommendation(self, range_weights: Dict,
                                   bet_size: float, pot_size: float) -> str:
        """Get recommended action based on opponent range"""
        premium_weight = range_weights.get('premium', 0)

        if premium_weight > 50:
            return "Opponent likely has premium hand - consider folding weak hands"
        elif premium_weight > 30:
            return "Opponent has strong range - value bet with strong hands, fold weak"
        else:
            return "Opponent has wide range - consider raising for value/as bluff"

    def learn_from_showdown(self, player_id: str, actions: List[str],
                           hand_strength: str, won: bool):
        """
        Update player model based on showdown
        This simulates ML by tracking player tendencies
        """
        stats = self.player_stats[player_id]

        # Update aggression
        aggressive_actions = sum(1 for a in actions if a in ['raise', 'bet', '3bet'])
        stats['aggression'] = (stats['aggression'] + aggressive_actions / len(actions)) / 2

        # Update VPIP/PFR
        if 'raise' in actions[:2]:  # Pre-flop actions
            stats['pfr'] = (stats['pfr'] * stats['hands_observed'] + 1) / (stats['hands_observed'] + 1)

        stats['hands_observed'] += 1


class GTO_Solver:
    """
    Simplified GTO (Game Theory Optimal) Solver
    Provides unexploitable strategy recommendations
    """

    def __init__(self):
        # GTO frequencies (simplified)
        self.gto_frequencies = {
            'value_bet': 0.7,
            'bluff': 0.3,
            'check': 0.5
        }

    def get_gto_action(self, equity: float, pot_size: float,
                      stack_size: float) -> Dict:
        """
        Get GTO-optimal action recommendation
        Based on simplified game theory principles
        """
        # GTO bet sizing formula: aim for ~2/3 pot for value
        optimal_bet_size = pot_size * 0.66

        # Adjust for stack size (SPR - Stack to Pot Ratio)
        spr = stack_size / pot_size if pot_size > 0 else 10

        if spr < 3:  # Short stack - more aggressive
            optimal_bet_size = min(stack_size, pot_size * 0.75)
        elif spr > 10:  # Deep stack - more cautious
            optimal_bet_size = pot_size * 0.5

        # Determine action based on equity
        if equity > 0.65:
            action = 'BET/RAISE'
            reasoning = 'Strong equity - bet for value'
            bet_frequency = 0.85
        elif equity > 0.50:
            action = 'BET/CALL'
            reasoning = 'Marginal equity - bet thin value or call'
            bet_frequency = 0.65
        elif equity > 0.35:
            action = 'CHECK/CALL'
            reasoning = 'Bluff-catching range - check/call or check/fold'
            bet_frequency = 0.35
        else:
            action = 'CHECK/FOLD'
            reasoning = 'Low equity - check/fold or occasional bluff'
            bet_frequency = 0.15

        # Calculate bluff frequency (based on pot odds given to opponent)
        optimal_bluff_ratio = (pot_size / (pot_size + optimal_bet_size)) * 0.5

        return {
            'action': action,
            'optimal_bet_size': round(optimal_bet_size, 2),
            'bet_frequency': round(bet_frequency * 100, 1),
            'bluff_ratio': round(optimal_bluff_ratio * 100, 1),
            'reasoning': reasoning,
            'stack_to_pot_ratio': round(spr, 2),
            'note': 'GTO strategy aims for unexploitable play'
        }

    def calculate_optimal_bet_size(self, equity: float, pot_size: float,
                                   stack_size: float, street: str = 'flop') -> Dict:
        """
        Calculate GTO-optimal bet sizing
        """
        # Street-specific multipliers
        street_multipliers = {
            'flop': 0.66,
            'turn': 0.66,
            'river': 0.75  # Larger on river for polarization
        }

        multiplier = street_multipliers.get(street.lower(), 0.66)

        # Base bet size
        base_bet = pot_size * multiplier

        # Adjust for equity
        if equity > 0.70:
            # Very strong - can bet larger
            bet_size = pot_size * 0.75
        elif equity > 0.55:
            # Strong - standard sizing
            bet_size = base_bet
        elif equity > 0.40:
            # Marginal - smaller sizing
            bet_size = pot_size * 0.50
        else:
            # Weak - small bet as bluff or check
            bet_size = pot_size * 0.33

        # Cap at stack size
        bet_size = min(bet_size, stack_size)

        # Calculate optimal bet frequency
        # GTO: bet frequency = pot / (pot + bet) for breakeven bluffs
        bluff_breakeven = pot_size / (pot_size + bet_size)
        value_frequency = equity

        return {
            'recommended_bet': round(bet_size, 2),
            'bet_as_percentage_of_pot': round((bet_size / pot_size) * 100, 1),
            'value_bet_frequency': round(value_frequency * 100, 1),
            'bluff_frequency': round(bluff_breakeven * 100, 1),
            'pot_odds_given': round(bet_size / (pot_size + bet_size) * 100, 1),
            'street': street,
            'explanation': f"Bet {bet_size:.0f} into {pot_size:.0f} ({(bet_size/pot_size)*100:.0f}% pot)"
        }

    def get_balanced_range(self, position: str, action_before: str) -> Dict:
        """
        Get GTO-balanced range for a position
        Mixes value hands and bluffs optimally
        """
        # Simplified GTO ranges by position
        ranges = {
            'BTN': {
                'raise': 0.45,  # Raise 45% of hands from button
                'call': 0.20,
                'fold': 0.35
            },
            'CO': {
                'raise': 0.35,
                'call': 0.15,
                'fold': 0.50
            },
            'UTG': {
                'raise': 0.15,
                'call': 0.05,
                'fold': 0.80
            }
        }

        pos_range = ranges.get(position, ranges['CO'])

        # Adjust for action before
        if action_before == 'raise':
            # Tighten up when facing a raise
            pos_range['raise'] *= 0.4  # 3-bet less
            pos_range['call'] *= 0.6
            pos_range['fold'] = 1 - (pos_range['raise'] + pos_range['call'])

        return {
            'position': position,
            'action_before': action_before,
            'frequencies': {k: round(v * 100, 1) for k, v in pos_range.items()},
            'style': 'GTO Balanced',
            'note': 'These frequencies make you unexploitable'
        }


if __name__ == "__main__":
    # Test AI components
    print("🤖 Testing AI Opponent Modeling System\n")

    # Test opponent modeler
    modeler = OpponentModeler()

    print("Test 1: Action sequence analysis")
    prediction = modeler.predict_range_from_actions(
        actions=['raise', 'bet', 'bet'],
        position='CO',
        bet_size=75,
        pot_size=100
    )
    print(f"Range distribution: {prediction['range_distribution']}")
    print(f"Most likely: {prediction['most_likely_category']} ({prediction['confidence']:.1f}%)")
    print(f"Recommendation: {prediction['recommendation']}\n")

    # Test GTO solver
    print("Test 2: GTO Solver")
    solver = GTO_Solver()

    gto_action = solver.get_gto_action(equity=0.68, pot_size=100, stack_size=500)
    print(f"Action: {gto_action['action']}")
    print(f"Optimal bet: ${gto_action['optimal_bet_size']}")
    print(f"Reasoning: {gto_action['reasoning']}\n")

    # Test bet sizing
    print("Test 3: Optimal bet sizing")
    bet_rec = solver.calculate_optimal_bet_size(
        equity=0.65, pot_size=100, stack_size=300, street='river'
    )
    print(f"Recommended bet: ${bet_rec['recommended_bet']}")
    print(f"Explanation: {bet_rec['explanation']}")

    print("\n✅ AI system tests complete!")
