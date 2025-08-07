#!/usr/bin/env python3
"""
Web Visualization Preview for Cece v1.3 Tournament Analysis
Generates HTML preview of the tournament data for visualization testing
"""

import json
import os
from datetime import datetime

def generate_html_preview():
    """Generate an HTML preview of the tournament analysis data."""
    
    # Load the analysis data
    json_file = r"s:\Maker Stuff\Programming\Static Evaluation Chess Engine\static_evaluation_engine\results\historical\tournament_analysis_results_20250807_1500.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cece v1.3 Tournament Analysis</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .insights {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .insight {{
            margin: 10px 0;
            padding: 10px;
            border-left: 4px solid #ffc107;
            background: white;
        }}
        .severity-high {{ border-left-color: #dc3545; }}
        .severity-medium {{ border-left-color: #fd7e14; }}
        .severity-low {{ border-left-color: #28a745; }}
        .opening-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .opening-table th, .opening-table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        .opening-table th {{
            background-color: #f2f2f2;
        }}
        .win-rate-good {{ color: #28a745; font-weight: bold; }}
        .win-rate-bad {{ color: #dc3545; font-weight: bold; }}
        .win-rate-average {{ color: #fd7e14; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏆 Cece v1.3 Tournament Analysis</h1>
            <p><strong>Tournament:</strong> Engine Battle 20250806</p>
            <p><strong>Analysis Date:</strong> {data['metadata']['analysis_date'][:19]}</p>
            <p><strong>Games Analyzed:</strong> {data['metadata']['total_games_analyzed']}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{data['tournament_summary']['wins']}</div>
                <div class="stat-label">Wins</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{data['tournament_summary']['losses']}</div>
                <div class="stat-label">Losses</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{data['tournament_summary']['draws']}</div>
                <div class="stat-label">Draws</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{data['tournament_summary']['win_rate']:.1%}</div>
                <div class="stat-label">Win Rate</div>
            </div>
        </div>

        <div class="chart-container">
            <h3>📊 Performance Overview</h3>
            <canvas id="performanceChart" width="400" height="200"></canvas>
        </div>

        <div class="chart-container">
            <h3>⚫⚪ Performance by Color</h3>
            <canvas id="colorChart" width="400" height="200"></canvas>
        </div>

        <div class="chart-container">
            <h3>📈 Game Timeline</h3>
            <canvas id="timelineChart" width="400" height="200"></canvas>
        </div>

        <div class="insights">
            <h3>🔍 Key Insights & Recommendations</h3>
"""
    
    # Add insights
    for insight in data['insights_and_recommendations']:
        severity_class = f"severity-{insight['severity']}"
        severity_emoji = "🚨" if insight['severity'] == 'high' else "⚠️" if insight['severity'] == 'medium' else "ℹ️"
        html_content += f"""
            <div class="insight {severity_class}">
                <strong>{severity_emoji} {insight['title']}</strong><br>
                {insight['description']}
            </div>
"""
    
    # Add opening analysis table
    html_content += f"""
        </div>

        <div class="chart-container">
            <h3>🎯 Opening Performance Analysis</h3>
            <table class="opening-table">
                <thead>
                    <tr>
                        <th>Opening</th>
                        <th>Games</th>
                        <th>Wins</th>
                        <th>Draws</th>
                        <th>Losses</th>
                        <th>Win Rate</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add opening data
    opening_data = data['visualization_data']['opening_heatmap']
    for opening, stats in sorted(opening_data.items(), key=lambda x: x[1]['win_rate'], reverse=True):
        win_rate = stats['win_rate']
        win_rate_class = 'win-rate-good' if win_rate >= 0.5 else 'win-rate-bad' if win_rate < 0.3 else 'win-rate-average'
        
        html_content += f"""
                    <tr>
                        <td>{opening}</td>
                        <td>{stats['games']}</td>
                        <td>{stats['wins']}</td>
                        <td>{stats['draws']}</td>
                        <td>{stats['losses']}</td>
                        <td class="{win_rate_class}">{win_rate:.1%}</td>
                    </tr>
"""
    
    html_content += """
                </tbody>
            </table>
        </div>
    </div>

    <script>
        // Performance Overview Chart
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        const performanceChart = new Chart(performanceCtx, {
            type: 'doughnut',
            data: {
                labels: ['Wins', 'Losses', 'Draws'],
                datasets: [{
                    data: """ + str([data['tournament_summary']['wins'], data['tournament_summary']['losses'], data['tournament_summary']['draws']]) + """,
                    backgroundColor: ['#4CAF50', '#F44336', '#FF9800'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // Color Performance Chart
        const colorCtx = document.getElementById('colorChart').getContext('2d');
        const colorChart = new Chart(colorCtx, {
            type: 'bar',
            data: {
                labels: ['White', 'Black'],
                datasets: [{
                    label: 'Win Rate',
                    data: [""" + f"{data['tournament_summary']['white_win_rate']:.3f}, {data['tournament_summary']['black_win_rate']:.3f}" + """],
                    backgroundColor: ['#007bff', '#6c757d'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1,
                        ticks: {
                            callback: function(value) {
                                return (value * 100).toFixed(0) + '%';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });

        // Timeline Chart
        const timelineCtx = document.getElementById('timelineChart').getContext('2d');
        const timelineData = """ + json.dumps(data['visualization_data']['game_timeline']) + """;
        
        const timelineChart = new Chart(timelineCtx, {
            type: 'line',
            data: {
                labels: timelineData.map(game => game.game),
                datasets: [{
                    label: 'Game Results',
                    data: timelineData.map(game => {
                        if (game.result === 'win') return 1;
                        if (game.result === 'loss') return -1;
                        return 0;
                    }),
                    borderColor: '#007bff',
                    backgroundColor: 'rgba(0, 123, 255, 0.1)',
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        min: -1.5,
                        max: 1.5,
                        ticks: {
                            callback: function(value) {
                                if (value === 1) return 'Win';
                                if (value === 0) return 'Draw';
                                if (value === -1) return 'Loss';
                                return '';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    </script>
</body>
</html>
"""
    
    # Save the HTML file
    output_path = r"s:\Maker Stuff\Programming\Static Evaluation Chess Engine\static_evaluation_engine\results\historical\tournament_analysis_preview_20250807_1500.html"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path

if __name__ == "__main__":
    html_file = generate_html_preview()
    print(f"🌐 HTML preview generated: {html_file}")
    print("📊 Open this file in a web browser to see the tournament analysis visualization")
    print("🔍 This preview demonstrates how the JSON data can be used for web dashboards")
