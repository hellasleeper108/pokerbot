#!/usr/bin/env python3
"""
Result Export Tool
Exports poker analysis results to various formats (JSON, CSV, HTML, Markdown)
"""

import json
import csv
from datetime import datetime
from typing import List, Dict
from poker_bot_enhanced import Colors


class ResultExporter:
    """Exports poker analysis results to various formats"""

    @staticmethod
    def export_to_json(data: Dict, filename: str = None) -> str:
        """Export results to JSON format"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"poker_analysis_{timestamp}.json"

        # Add metadata
        export_data = {
            'export_date': datetime.now().isoformat(),
            'export_format': 'json',
            'data': data
        }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

        return filename

    @staticmethod
    def export_to_csv(results: List[Dict], filename: str = None) -> str:
        """Export batch results to CSV format"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"poker_analysis_{timestamp}.csv"

        if not results:
            return None

        # Prepare CSV data
        fieldnames = ['scenario', 'hole_cards', 'community_cards', 'opponents',
                     'win_percent', 'tie_percent', 'loss_percent', 'hand_rank']

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                row = {
                    'scenario': result.get('name', ''),
                    'hole_cards': ' '.join(str(c) for c in result.get('hole_cards', [])),
                    'community_cards': ' '.join(str(c) for c in result.get('community_cards', [])),
                    'opponents': result.get('num_opponents', ''),
                    'win_percent': f"{result['probabilities']['win']*100:.2f}",
                    'tie_percent': f"{result['probabilities']['tie']*100:.2f}",
                    'loss_percent': f"{result['probabilities']['loss']*100:.2f}",
                    'hand_rank': result.get('hand_rank', {}).get('name', 'N/A') if isinstance(result.get('hand_rank'), dict) else str(result.get('hand_rank', 'N/A'))
                }
                writer.writerow(row)

        return filename

    @staticmethod
    def export_to_html(results: List[Dict], filename: str = None, title: str = "Poker Analysis Results") -> str:
        """Export results to HTML format with styling"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"poker_analysis_{timestamp}.html"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #1a1a1a;
            color: #e0e0e0;
        }}
        h1 {{
            color: #4CAF50;
            text-align: center;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .metadata {{
            text-align: center;
            color: #888;
            margin-bottom: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background-color: #2a2a2a;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #333;
        }}
        tr:hover {{
            background-color: #333;
        }}
        .win {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .tie {{
            color: #FFC107;
        }}
        .loss {{
            color: #f44336;
        }}
        .hand {{
            font-weight: bold;
            color: #2196F3;
        }}
        .cards {{
            font-family: monospace;
            background-color: #333;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        .spades, .clubs {{ color: #fff; }}
        .hearts, .diamonds {{ color: #f44336; }}
        .progress-bar {{
            height: 20px;
            background-color: #333;
            border-radius: 10px;
            overflow: hidden;
            position: relative;
        }}
        .progress-fill {{
            height: 100%;
            transition: width 0.3s ease;
        }}
        .progress-win {{
            background-color: #4CAF50;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <h1>♠♥♦♣ {title} ♣♦♥♠</h1>
    <div class="metadata">
        Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
        Total Scenarios: {len(results)}
    </div>

    <table>
        <thead>
            <tr>
                <th>Scenario</th>
                <th>Hole Cards</th>
                <th>Board</th>
                <th>Hand</th>
                <th>Opponents</th>
                <th>Win %</th>
                <th>Tie %</th>
                <th>Loss %</th>
                <th>Win Probability</th>
            </tr>
        </thead>
        <tbody>
"""

        for result in results:
            prob = result['probabilities']
            hole_str = ' '.join(str(c) for c in result.get('hole_cards', []))
            board_str = ' '.join(str(c) for c in result.get('community_cards', [])) or '-'

            hand_rank_name = 'N/A'
            if 'hand_rank' in result:
                if hasattr(result['hand_rank'], 'name'):
                    hand_rank_name = result['hand_rank'].name
                else:
                    hand_rank_name = str(result['hand_rank'])
            elif 'chen_score' in result:
                hand_rank_name = f"Chen: {result['chen_score']:.1f}"

            html_content += f"""
            <tr>
                <td><strong>{result.get('name', 'Unknown')}</strong></td>
                <td><span class="cards">{hole_str}</span></td>
                <td><span class="cards">{board_str}</span></td>
                <td><span class="hand">{hand_rank_name}</span></td>
                <td style="text-align: center;">{result.get('num_opponents', '-')}</td>
                <td class="win">{prob['win']*100:.1f}%</td>
                <td class="tie">{prob['tie']*100:.1f}%</td>
                <td class="loss">{prob['loss']*100:.1f}%</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill progress-win" style="width: {prob['win']*100}%"></div>
                    </div>
                </td>
            </tr>
"""

        html_content += """
        </tbody>
    </table>

    <div class="footer">
        <p>Generated by Texas Hold'em Probability Bot</p>
        <p>For educational purposes only</p>
    </div>
</body>
</html>
"""

        with open(filename, 'w') as f:
            f.write(html_content)

        return filename

    @staticmethod
    def export_to_markdown(results: List[Dict], filename: str = None) -> str:
        """Export results to Markdown format"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"poker_analysis_{timestamp}.md"

        md_content = f"""# Poker Analysis Results

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Scenarios:** {len(results)}

---

## Results Summary

| Scenario | Hole Cards | Board | Hand | Opponents | Win % | Tie % | Loss % |
|----------|------------|-------|------|-----------|-------|-------|--------|
"""

        for result in results:
            prob = result['probabilities']
            hole_str = ' '.join(str(c) for c in result.get('hole_cards', []))
            board_str = ' '.join(str(c) for c in result.get('community_cards', [])) or '-'

            hand_rank_name = 'N/A'
            if 'hand_rank' in result:
                if hasattr(result['hand_rank'], 'name'):
                    hand_rank_name = result['hand_rank'].name
                else:
                    hand_rank_name = str(result['hand_rank'])
            elif 'chen_score' in result:
                hand_rank_name = f"Chen {result['chen_score']:.1f}"

            md_content += f"| {result.get('name', 'Unknown')} | `{hole_str}` | `{board_str}` | {hand_rank_name} | {result.get('num_opponents', '-')} | **{prob['win']*100:.1f}%** | {prob['tie']*100:.1f}% | {prob['loss']*100:.1f}% |\n"

        md_content += f"""

---

## Detailed Analysis

"""

        for i, result in enumerate(results, 1):
            prob = result['probabilities']
            hole_str = ' '.join(str(c) for c in result.get('hole_cards', []))
            board_str = ' '.join(str(c) for c in result.get('community_cards', [])) or 'Pre-flop'

            md_content += f"""
### {i}. {result.get('name', 'Scenario')}

- **Hole Cards:** `{hole_str}`
- **Board:** `{board_str}`
- **Opponents:** {result.get('num_opponents', 'N/A')}
- **Win Probability:** {prob['win']*100:.2f}%
- **Tie Probability:** {prob['tie']*100:.2f}%
- **Loss Probability:** {prob['loss']*100:.2f}%

"""

        md_content += """
---

*Generated by Texas Hold'em Probability Bot*
*For educational purposes only*
"""

        with open(filename, 'w') as f:
            f.write(md_content)

        return filename


def main():
    """Test export functionality"""
    import sys

    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}POKER RESULTS EXPORT TOOL{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")

    # Example data
    example_results = [
        {
            'name': 'Pocket Aces',
            'hole_cards': ['A♠', 'A♥'],
            'community_cards': [],
            'num_opponents': 2,
            'probabilities': {'win': 0.73, 'tie': 0.01, 'loss': 0.26},
            'chen_score': 21.0
        },
        {
            'name': 'Top Pair',
            'hole_cards': ['A♠', 'K♦'],
            'community_cards': ['A♥', '7♠', '3♣'],
            'num_opponents': 2,
            'probabilities': {'win': 0.78, 'tie': 0.01, 'loss': 0.21},
            'hand_rank': 'PAIR'
        }
    ]

    print(f"{Colors.BOLD}Export Formats:{Colors.RESET}")
    print(f"  1. JSON")
    print(f"  2. CSV")
    print(f"  3. HTML")
    print(f"  4. Markdown")
    print(f"  5. All formats")
    print()

    try:
        choice = input(f"{Colors.BOLD}Select format (1-5):{Colors.RESET} ").strip()

        if choice == "1":
            filename = ResultExporter.export_to_json({'results': example_results})
            print(f"{Colors.GREEN}✓ Exported to {filename}{Colors.RESET}")

        elif choice == "2":
            filename = ResultExporter.export_to_csv(example_results)
            print(f"{Colors.GREEN}✓ Exported to {filename}{Colors.RESET}")

        elif choice == "3":
            filename = ResultExporter.export_to_html(example_results)
            print(f"{Colors.GREEN}✓ Exported to {filename}{Colors.RESET}")

        elif choice == "4":
            filename = ResultExporter.export_to_markdown(example_results)
            print(f"{Colors.GREEN}✓ Exported to {filename}{Colors.RESET}")

        elif choice == "5":
            files = []
            files.append(ResultExporter.export_to_json({'results': example_results}))
            files.append(ResultExporter.export_to_csv(example_results))
            files.append(ResultExporter.export_to_html(example_results))
            files.append(ResultExporter.export_to_markdown(example_results))

            print(f"{Colors.GREEN}✓ Exported to all formats:{Colors.RESET}")
            for f in files:
                print(f"  - {f}")

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Cancelled{Colors.RESET}")

    print()


if __name__ == "__main__":
    main()
