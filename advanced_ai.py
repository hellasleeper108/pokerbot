#!/usr/bin/env python3
"""
Advanced AI Module
Player profiling, exploitative strategy, bluff detection, and pattern recognition
"""

import random
from typing import List, Dict, Tuple
from collections import defaultdict, Counter
from poker_bot_enhanced import Card, HandRank


class PlayerProfile:
    """AI-powered player profiling system"""

    PLAYER_TYPES = {
        'TAG': {'vpip': (0.15, 0.25), 'pfr': (0.12, 0.22), 'aggression': (1.5, 3.0), 'name': 'Tight-Aggressive'},
        'LAG': {'vpip': (0.25, 0.40), 'pfr': (0.20, 0.35), 'aggression': (2.0, 4.0), 'name': 'Loose-Aggressive'},
        'TP': {'vpip': (0.08, 0.18), 'pfr': (0.05, 0.12), 'aggression': (0.5, 1.5), 'name': 'Tight-Passive'},
        'LP': {'vpip': (0.35, 0.60), 'pfr': (0.05, 0.15), 'aggression': (0.3, 1.0), 'name': 'Loose-Passive (Fish)'},
        'MANIAC': {'vpip': (0.50, 0.80), 'pfr': (0.40, 0.70), 'aggression': (3.0, 6.0), 'name': 'Maniac'},
        'ROCK': {'vpip': (0.05, 0.12), 'pfr': (0.04, 0.10), 'aggression': (0.8, 1.5), 'name': 'Rock (Nit)'}
    }

    def __init__(self):
        self.player_data = defaultdict(lambda: {
            'hands_seen': 0,
            'vpip_count': 0,
            'pfr_count': 0,
            'aggression_actions': [],
            'bet_sizes': [],
            'showdowns': []
        })

    def classify_player(self, vpip: float, pfr: float, aggression: float) -> Tuple[str, Dict]:
        """
        Classify player type based on statistics
        Returns (player_type, confidence_scores)
        """
        scores = {}

        for player_type, ranges in self.PLAYER_TYPES.items():
            # Calculate how well stats fit this player type
            vpip_fit = 1.0 if ranges['vpip'][0] <= vpip <= ranges['vpip'][1] else 0.0
            pfr_fit = 1.0 if ranges['pfr'][0] <= pfr <= ranges['pfr'][1] else 0.0
            agg_fit = 1.0 if ranges['aggression'][0] <= aggression <= ranges['aggression'][1] else 0.0

            # Calculate distance if outside range
            if vpip_fit == 0:
                if vpip < ranges['vpip'][0]:
                    vpip_fit = max(0, 1 - (ranges['vpip'][0] - vpip) / 0.2)
                else:
                    vpip_fit = max(0, 1 - (vpip - ranges['vpip'][1]) / 0.2)

            if pfr_fit == 0:
                if pfr < ranges['pfr'][0]:
                    pfr_fit = max(0, 1 - (ranges['pfr'][0] - pfr) / 0.2)
                else:
                    pfr_fit = max(0, 1 - (pfr - ranges['pfr'][1]) / 0.2)

            if agg_fit == 0:
                if aggression < ranges['aggression'][0]:
                    agg_fit = max(0, 1 - (ranges['aggression'][0] - aggression) / 1.0)
                else:
                    agg_fit = max(0, 1 - (aggression - ranges['aggression'][1]) / 2.0)

            scores[player_type] = (vpip_fit + pfr_fit + agg_fit) / 3.0

        best_type = max(scores.items(), key=lambda x: x[1])

        return best_type[0], {k: v * 100 for k, v in scores.items()}

    def get_exploitative_strategy(self, player_type: str, situation: str) -> Dict:
        """
        Get exploitative strategy recommendations based on player type
        """
        strategies = {
            'TAG': {
                'general': 'Tight-aggressive opponent. Play straightforward, value bet strong hands.',
                'when_they_bet': 'Give them credit. They usually have it. Fold marginal hands.',
                'when_they_check': 'They might be trapping with monsters or have air. Bet cautiously.',
                'bluff_frequency': 'Low - they fold to aggression but not often bluffing',
                'counter_strategy': 'Play tight, value bet heavily, don\'t bluff much'
            },
            'LAG': {
                'general': 'Loose-aggressive opponent. Widen your calling range, trap with strong hands.',
                'when_they_bet': 'Could be bluffing or value betting. Call down lighter.',
                'when_they_check': 'Rare - might be very strong or very weak. Bet for information.',
                'bluff_frequency': 'High - they bluff often, call them down',
                'counter_strategy': 'Call more, trap with strong hands, let them bluff off'
            },
            'TP': {
                'general': 'Tight-passive (weak). Bet for value, don\'t bluff.',
                'when_they_bet': 'They have a strong hand. Fold unless you beat it.',
                'when_they_check': 'Probably weak. Bet your strong hands for value.',
                'bluff_frequency': 'Very low - never bluffs, always has it when betting',
                'counter_strategy': 'Value bet thin, never bluff, they call with weak hands'
            },
            'LP': {
                'general': 'Loose-passive fish. Value bet everything, never bluff.',
                'when_they_bet': 'Finally connected. Still might be weak pair.',
                'when_they_check': 'Has something weak. Bet for value with any decent hand.',
                'bluff_frequency': 'Never - pure calling station',
                'counter_strategy': 'VALUE BET EVERYTHING! Print money. Never bluff.'
            },
            'MANIAC': {
                'general': 'Maniac. Super aggressive. Let them bluff, trap constantly.',
                'when_they_bet': 'Could be anything. Call with medium strength+.',
                'when_they_check': 'Extremely rare. Might be weak or mega-strong.',
                'bluff_frequency': 'Extreme - bluffs 70%+ of the time',
                'counter_strategy': 'Call down light, trap with monsters, let them hang themselves'
            },
            'ROCK': {
                'general': 'Rock/Nit. Only plays premium hands. Fold to aggression.',
                'when_they_bet': 'Premium hand. Fold unless you have better premium.',
                'when_they_check': 'Doesn\'t want to invest. Bet and they\'ll fold.',
                'bluff_frequency': 'Zero - only bets the nuts',
                'counter_strategy': 'Steal their blinds, fold when they show strength'
            }
        }

        strategy = strategies.get(player_type, strategies['TAG'])
        strategy['player_type'] = self.PLAYER_TYPES[player_type]['name']

        return strategy


class BluffDetector:
    """AI bluff detection system"""

    def __init__(self):
        self.bluff_indicators = {
            'bet_size': 0.0,
            'timing': 0.0,
            'board_texture': 0.0,
            'action_sequence': 0.0,
            'position': 0.0
        }

    def analyze_bluff_likelihood(self, bet_size: float, pot_size: float,
                                 board_texture: Dict, action_history: List[str],
                                 position: str) -> Dict:
        """
        Analyze likelihood that opponent is bluffing
        Returns probability and indicators
        """
        bluff_probability = 0.0
        indicators = []

        # Bet sizing analysis
        bet_ratio = bet_size / pot_size if pot_size > 0 else 1.0

        if bet_ratio > 0.8:
            bluff_probability += 0.25
            indicators.append(f"Large bet ({bet_ratio*100:.0f}% pot) - could be polarized (nuts or bluff)")
        elif bet_ratio < 0.33:
            bluff_probability -= 0.15
            indicators.append(f"Small bet ({bet_ratio*100:.0f}% pot) - usually value/protection")

        # Board texture
        if board_texture.get('type') == 'dry':
            bluff_probability += 0.15
            indicators.append("Dry board - easier to bluff")
        elif board_texture.get('type') == 'very_wet':
            bluff_probability -= 0.10
            indicators.append("Wet board - harder to bluff, could have draws")

        # Action sequence
        aggressive_count = sum(1 for a in action_history if a in ['raise', 'bet', '3bet'])
        if aggressive_count >= 3:
            bluff_probability += 0.20
            indicators.append("Multiple aggressive actions - higher bluff frequency")

        # Position
        if position in ['BTN', 'CO']:
            bluff_probability += 0.10
            indicators.append("Late position - more bluffing opportunities")

        # Normalize to 0-100%
        bluff_probability = max(0, min(1, bluff_probability + 0.30))  # Base 30% bluff rate

        # Determine confidence level
        if bluff_probability > 0.65:
            confidence = "High"
            recommendation = "Strong bluff candidate - consider calling/raising"
        elif bluff_probability > 0.45:
            confidence = "Medium"
            recommendation = "Possible bluff - call with bluff-catchers"
        else:
            confidence = "Low"
            recommendation = "Likely has it - fold weak hands"

        return {
            'bluff_probability': bluff_probability * 100,
            'confidence': confidence,
            'indicators': indicators,
            'recommendation': recommendation
        }


class EquityCalculator:
    """Calculate hand equity over multiple streets"""

    @staticmethod
    def calculate_equity_progression(hole_cards: List[Card],
                                    community_progression: List[List[Card]],
                                    num_opponents: int = 1) -> List[Dict]:
        """
        Calculate equity at each street
        Returns list of equity data points for graphing
        """
        from poker_bot_enhanced import ProbabilityCalculator

        equity_points = []

        # Pre-flop
        prob = ProbabilityCalculator.calculate_win_probability(
            hole_cards, [], num_opponents, num_simulations=3000
        )
        equity_points.append({
            'street': 'Pre-flop',
            'equity': prob['win'] * 100,
            'cards': []
        })

        # Each subsequent street
        for i, community in enumerate(community_progression):
            prob = ProbabilityCalculator.calculate_win_probability(
                hole_cards, community, num_opponents, num_simulations=3000
            )

            street_name = ['Flop', 'Turn', 'River'][min(i, 2)]

            equity_points.append({
                'street': street_name,
                'equity': prob['win'] * 100,
                'cards': [str(c) for c in community]
            })

        return equity_points


class PatternRecognizer:
    """Recognize betting patterns and tendencies"""

    def __init__(self):
        self.patterns = {
            'continuation_bet': {
                'sequence': ['raise_preflop', 'bet_flop'],
                'meaning': 'Standard c-bet - often independent of hand strength',
                'counter': 'Float or raise to test strength'
            },
            'check_raise': {
                'sequence': ['check', 'raise'],
                'meaning': 'Usually strong hand or bluff. Rarely medium strength',
                'counter': 'Only continue with very strong hands'
            },
            'donk_bet': {
                'sequence': ['call_preflop', 'bet_flop_oop'],
                'meaning': 'Unusual play - often weak players with medium hands',
                'counter': 'Raise for information or fold'
            },
            'slow_play': {
                'sequence': ['check', 'call'],
                'meaning': 'Might be trapping with strong hand',
                'counter': 'Bet cautiously, prepare for check-raise'
            },
            'triple_barrel': {
                'sequence': ['bet', 'bet', 'bet'],
                'meaning': 'Very strong or pure bluff. Polarized range.',
                'counter': 'Call or fold, rarely raise'
            }
        }

    def identify_pattern(self, action_sequence: List[str]) -> Dict:
        """Identify betting pattern from action sequence"""
        identified = []

        # Check for continuation bet
        if len(action_sequence) >= 2:
            if 'raise' in action_sequence[0].lower() and 'bet' in action_sequence[1].lower():
                identified.append({
                    'pattern': 'Continuation Bet',
                    'description': self.patterns['continuation_bet']['meaning'],
                    'counter_strategy': self.patterns['continuation_bet']['counter']
                })

        # Check for triple barrel
        if action_sequence.count('bet') >= 3:
            identified.append({
                'pattern': 'Triple Barrel Bluff',
                'description': self.patterns['triple_barrel']['meaning'],
                'counter_strategy': self.patterns['triple_barrel']['counter']
            })

        # Check for check-raise
        for i in range(len(action_sequence) - 1):
            if action_sequence[i] == 'check' and 'raise' in action_sequence[i+1]:
                identified.append({
                    'pattern': 'Check-Raise',
                    'description': self.patterns['check_raise']['meaning'],
                    'counter_strategy': self.patterns['check_raise']['counter']
                })
                break

        if not identified:
            identified.append({
                'pattern': 'Standard Play',
                'description': 'No unusual patterns detected',
                'counter_strategy': 'Play based on hand strength and position'
            })

        return {'patterns': identified}


class AdvancedAI:
    """Master AI system combining all advanced features"""

    def __init__(self):
        self.profiler = PlayerProfile()
        self.bluff_detector = BluffDetector()
        self.pattern_recognizer = PatternRecognizer()

    def analyze_opponent(self, vpip: float = 0.25, pfr: float = 0.18,
                        aggression: float = 2.0, action_history: List[str] = None,
                        bet_size: float = 0, pot_size: float = 100,
                        board_texture: Dict = None) -> Dict:
        """
        Complete opponent analysis combining all AI systems
        """
        # Player profiling
        player_type, confidence_scores = self.profiler.classify_player(vpip, pfr, aggression)
        strategy = self.profiler.get_exploitative_strategy(player_type, 'general')

        # Pattern recognition
        patterns = {'patterns': []}
        if action_history:
            patterns = self.pattern_recognizer.identify_pattern(action_history)

        # Bluff detection
        bluff_analysis = {'bluff_probability': 30, 'confidence': 'Unknown'}
        if bet_size > 0 and board_texture and action_history:
            bluff_analysis = self.bluff_detector.analyze_bluff_likelihood(
                bet_size, pot_size, board_texture, action_history, 'BTN'
            )

        return {
            'player_profile': {
                'type': player_type,
                'full_name': self.profiler.PLAYER_TYPES[player_type]['name'],
                'confidence_scores': confidence_scores,
                'stats': {
                    'vpip': vpip * 100,
                    'pfr': pfr * 100,
                    'aggression': aggression
                }
            },
            'exploitative_strategy': strategy,
            'patterns_detected': patterns,
            'bluff_analysis': bluff_analysis
        }


if __name__ == "__main__":
    print("🤖 Advanced AI System Tests\n")

    ai = AdvancedAI()

    # Test 1: TAG player
    print("Test 1: Tight-Aggressive Player")
    analysis = ai.analyze_opponent(
        vpip=0.20, pfr=0.17, aggression=2.5,
        action_history=['raise', 'bet', 'bet'],
        bet_size=75, pot_size=100,
        board_texture={'type': 'dry', 'flush_possible': False}
    )

    print(f"Player Type: {analysis['player_profile']['full_name']}")
    print(f"Strategy: {analysis['exploitative_strategy']['general']}")
    print(f"Bluff Probability: {analysis['bluff_analysis']['bluff_probability']:.1f}%")
    print()

    # Test 2: Loose-Passive Fish
    print("Test 2: Loose-Passive Fish")
    analysis = ai.analyze_opponent(
        vpip=0.45, pfr=0.10, aggression=0.5,
        action_history=['call', 'call', 'bet'],
        bet_size=30, pot_size=100,
        board_texture={'type': 'wet', 'flush_possible': True}
    )

    print(f"Player Type: {analysis['player_profile']['full_name']}")
    print(f"Counter Strategy: {analysis['exploitative_strategy']['counter_strategy']}")
    print()

    # Test 3: Maniac
    print("Test 3: Maniac Player")
    analysis = ai.analyze_opponent(
        vpip=0.65, pfr=0.55, aggression=4.5,
        action_history=['raise', '3bet', 'bet', 'bet'],
        bet_size=150, pot_size=100,
        board_texture={'type': 'dry', 'flush_possible': False}
    )

    print(f"Player Type: {analysis['player_profile']['full_name']}")
    print(f"Bluff Likelihood: {analysis['bluff_analysis']['confidence']}")
    print(f"Recommendation: {analysis['bluff_analysis']['recommendation']}")

    print("\n✅ Advanced AI tests complete!")
