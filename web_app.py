#!/usr/bin/env python3
"""
Poker Bot Web Application
Flask-based web interface with AI opponent modeling and GTO solver
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import secrets
from datetime import datetime
from typing import List, Dict

from poker_bot_enhanced import (
    Card, Rank, Suit, HandEvaluator, ProbabilityCalculator,
    PreFlopAnalyzer, DrawAnalyzer, parse_card, validate_unique_cards
)
from preflop_charts import PreFlopChart, Position
from stats_tracker import PokerStats
from ai_opponent import OpponentModeler, GTO_Solver
from advanced_ai import AdvancedAI

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

# Initialize components
stats = PokerStats()
opponent_ai = OpponentModeler()
gto_solver = GTO_Solver()
advanced_ai = AdvancedAI()


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_hand():
    """
    Analyze a poker hand
    POST /api/analyze
    {
        "hole_cards": ["As", "Kd"],
        "community_cards": ["Ah", "7s", "3c"],
        "num_opponents": 2,
        "pot_size": 100,
        "bet_to_call": 20,
        "position": "BTN"
    }
    """
    try:
        data = request.get_json()

        # Parse cards
        hole_cards = [parse_card(c) for c in data['hole_cards']]
        community_cards = [parse_card(c) for c in data.get('community_cards', [])]

        if len(hole_cards) != 2:
            return jsonify({'error': 'Must provide exactly 2 hole cards'}), 400

        # Validate unique cards
        all_cards = hole_cards + community_cards
        if not validate_unique_cards(all_cards):
            return jsonify({'error': 'Duplicate cards detected'}), 400

        num_opponents = data.get('num_opponents', 1)
        num_simulations = data.get('simulations', 5000)

        # Calculate probabilities
        prob = ProbabilityCalculator.calculate_win_probability(
            hole_cards, community_cards, num_opponents, num_simulations
        )

        # Evaluate current hand
        hand_rank = None
        if len(hole_cards + community_cards) >= 5:
            rank, _ = HandEvaluator.evaluate_hand(hole_cards + community_cards)
            hand_rank = rank.name

        # Pre-flop analysis
        chen_score = PreFlopAnalyzer.calculate_chen_formula(hole_cards)
        category, _ = PreFlopAnalyzer.get_hand_category(chen_score)

        # Draw analysis
        draws = None
        if community_cards and len(community_cards) < 5:
            draws = DrawAnalyzer.analyze_draws(hole_cards, community_cards)

        # Pot odds analysis
        pot_analysis = None
        if 'pot_size' in data and 'bet_to_call' in data:
            pot_size = float(data['pot_size'])
            bet_to_call = float(data['bet_to_call'])
            pot_odds = ProbabilityCalculator.calculate_pot_odds(pot_size, bet_to_call)
            ev = ProbabilityCalculator.calculate_expected_value(
                prob['win_or_tie'], pot_size, bet_to_call
            )
            should_call = ProbabilityCalculator.should_call(prob['win_or_tie'], pot_odds)

            pot_analysis = {
                'pot_odds': pot_odds * 100,
                'expected_value': ev,
                'recommendation': 'CALL' if should_call else 'FOLD'
            }

        # Position-based recommendation
        position_rec = None
        if 'position' in data:
            try:
                position = Position[data['position']]
                action_before = data.get('action_before', 'none')
                rec = PreFlopChart.get_recommendation(hole_cards, position, action_before)
                position_rec = {
                    'hand': rec['hand'],
                    'category': rec['category'].value if rec['category'] else None,
                    'in_range': rec['in_range'],
                    'action': rec['action'],
                    'description': rec['description']
                }
            except KeyError:
                pass

        # AI opponent analysis
        opponent_analysis = opponent_ai.estimate_opponent_range(
            hole_cards, community_cards, num_opponents
        )

        # GTO recommendation
        gto_recommendation = None
        if pot_analysis:
            gto_recommendation = gto_solver.get_gto_action(
                prob['win'], pot_size, data.get('stack_size', 1000)
            )

        result = {
            'probabilities': {
                'win': prob['win'] * 100,
                'tie': prob['tie'] * 100,
                'loss': prob['loss'] * 100,
                'win_or_tie': prob['win_or_tie'] * 100
            },
            'hand_rank': hand_rank,
            'chen_score': chen_score,
            'hand_category': category,
            'draws': draws,
            'pot_analysis': pot_analysis,
            'position_recommendation': position_rec,
            'opponent_analysis': opponent_analysis,
            'gto_recommendation': gto_recommendation
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/preflop-chart', methods=['GET'])
def get_preflop_chart():
    """Get pre-flop chart for a position"""
    position_str = request.args.get('position', 'BTN')

    try:
        position = Position[position_str]
        ranges = PreFlopChart.get_position_range(position)

        # Convert to serializable format
        chart_data = {}
        for category, hands in ranges.items():
            chart_data[category.value] = list(hands)

        return jsonify({
            'position': position.value,
            'ranges': chart_data
        })

    except KeyError:
        return jsonify({'error': 'Invalid position'}), 400


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get current statistics"""
    summary = stats.get_summary()
    return jsonify(summary)


@app.route('/api/stats/add', methods=['POST'])
def add_hand_to_stats():
    """Add a hand to statistics"""
    data = request.get_json()
    stats.add_hand(data)
    return jsonify({'success': True})


@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """
    Analyze multiple scenarios
    POST /api/batch-analyze
    {
        "scenarios": [
            {
                "name": "Scenario 1",
                "hole_cards": ["As", "Ah"],
                "community_cards": [],
                "num_opponents": 2
            }
        ],
        "simulations": 3000
    }
    """
    try:
        data = request.get_json()
        scenarios = data.get('scenarios', [])
        simulations = data.get('simulations', 3000)

        results = []

        for scenario in scenarios:
            hole_cards = [parse_card(c) for c in scenario['hole_cards']]
            community_cards = [parse_card(c) for c in scenario.get('community_cards', [])]
            num_opponents = scenario.get('num_opponents', 1)

            prob = ProbabilityCalculator.calculate_win_probability(
                hole_cards, community_cards, num_opponents, simulations
            )

            hand_rank = None
            if len(hole_cards + community_cards) >= 5:
                rank, _ = HandEvaluator.evaluate_hand(hole_cards + community_cards)
                hand_rank = rank.name

            results.append({
                'name': scenario.get('name', 'Unnamed'),
                'probabilities': {
                    'win': prob['win'] * 100,
                    'tie': prob['tie'] * 100,
                    'loss': prob['loss'] * 100
                },
                'hand_rank': hand_rank
            })

        return jsonify({'results': results})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/predict-range', methods=['POST'])
def predict_opponent_range():
    """
    AI-powered opponent hand range prediction
    POST /api/ai/predict-range
    {
        "action_sequence": ["raise", "call", "bet"],
        "position": "CO",
        "board": ["Ah", "7s", "3c"],
        "bet_size": 75,
        "pot_size": 100
    }
    """
    try:
        data = request.get_json()

        prediction = opponent_ai.predict_range_from_actions(
            actions=data.get('action_sequence', []),
            position=data.get('position'),
            board=[parse_card(c) for c in data.get('board', [])],
            bet_size=data.get('bet_size', 0),
            pot_size=data.get('pot_size', 0)
        )

        return jsonify(prediction)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/gto/bet-size', methods=['POST'])
def get_gto_bet_size():
    """
    Get GTO bet sizing recommendation
    POST /api/gto/bet-size
    {
        "equity": 0.65,
        "pot_size": 100,
        "stack_size": 500,
        "street": "flop"
    }
    """
    try:
        data = request.get_json()

        recommendation = gto_solver.calculate_optimal_bet_size(
            equity=data.get('equity', 0.5),
            pot_size=data.get('pot_size', 100),
            stack_size=data.get('stack_size', 500),
            street=data.get('street', 'flop')
        )

        return jsonify(recommendation)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/analyze-opponent', methods=['POST'])
def analyze_opponent_advanced():
    """
    Advanced AI opponent analysis with player profiling and bluff detection
    POST /api/ai/analyze-opponent
    {
        "vpip": 0.25,
        "pfr": 0.18,
        "aggression": 2.0,
        "action_history": ["raise", "bet"],
        "bet_size": 75,
        "pot_size": 100,
        "board_texture": {"type": "dry", "flush_possible": false}
    }
    """
    try:
        data = request.get_json()

        analysis = advanced_ai.analyze_opponent(
            vpip=data.get('vpip', 0.25),
            pfr=data.get('pfr', 0.18),
            aggression=data.get('aggression', 2.0),
            action_history=data.get('action_history', []),
            bet_size=data.get('bet_size', 0),
            pot_size=data.get('pot_size', 100),
            board_texture=data.get('board_texture', {'type': 'unknown'})
        )

        return jsonify(analysis)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0'
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🎰 POKER BOT WEB SERVER STARTING")
    print("="*60)
    print("\n🌐 Access the web interface at: http://localhost:5000")
    print("📊 API documentation at: http://localhost:5000/api/docs")
    print("\n✨ Features:")
    print("  • Real-time probability calculations")
    print("  • AI opponent modeling")
    print("  • GTO solver recommendations")
    print("  • Pre-flop range charts")
    print("  • Statistics tracking")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
