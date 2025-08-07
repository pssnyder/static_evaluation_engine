#!/usr/bin/env python3
"""
Tournament Analysis Tool for Cece v1.3
Extracts and analyzes Cece v1.3 games from tournament PGN files.
"""

import re
import chess
import chess.pgn
import io
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

@dataclass
class GameResult:
    """Container for game analysis results."""
    game_number: int
    white: str
    black: str
    result: str
    termination: str
    plycount: int
    opening: str
    cece_color: str
    cece_result: str  # 'win', 'loss', 'draw'
    moves: List[str]
    key_patterns: List[str]
    eval_available: bool

class TournamentAnalyzer:
    """Analyze tournament results for Cece v1.3 performance."""
    
    def __init__(self, pgn_file_path: str):
        self.pgn_file_path = pgn_file_path
        self.games: List[GameResult] = []
        self.cece_games: List[GameResult] = []
        
    def extract_cece_games(self) -> List[GameResult]:
        """Extract all games where Cece v1.3 played."""
        print("🔍 Extracting Cece v1.3 games from tournament...")
        
        with open(self.pgn_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into individual games
        games_text = content.split('\n\n[Event')
        
        cece_games = []
        game_number = 0
        
        for i, game_text in enumerate(games_text):
            if i > 0:  # Add back the [Event tag for all but first game
                game_text = '[Event' + game_text
            
            # Check if Cece v1.3 is in this game
            if 'Cece_v1.3' not in game_text:
                continue
                
            game_number += 1
            game_result = self._parse_game(game_text, game_number)
            if game_result:
                cece_games.append(game_result)
                
        self.cece_games = cece_games
        print(f"✅ Found {len(cece_games)} games with Cece v1.3")
        return cece_games
    
    def _parse_game(self, game_text: str, game_number: int) -> Optional[GameResult]:
        """Parse a single game from PGN text."""
        try:
            # Parse headers
            white_match = re.search(r'\[White "([^"]+)"\]', game_text)
            black_match = re.search(r'\[Black "([^"]+)"\]', game_text)
            result_match = re.search(r'\[Result "([^"]+)"\]', game_text)
            termination_match = re.search(r'\[Termination "([^"]+)"\]', game_text)
            plycount_match = re.search(r'\[PlyCount "([^"]+)"\]', game_text)
            opening_match = re.search(r'\[Opening "([^"]+)"\]', game_text)
            
            if not white_match or not black_match or not result_match:
                return None
                
            white = white_match.group(1)
            black = black_match.group(1)
            result = result_match.group(1)
            termination = termination_match.group(1) if termination_match else "unknown"
            plycount = int(plycount_match.group(1)) if plycount_match else 0
            opening = opening_match.group(1) if opening_match else "Unknown"
            
            # Determine Cece's color and result
            if white == "Cece_v1.3":
                cece_color = "white"
                if result == "1-0":
                    cece_result = "win"
                elif result == "0-1":
                    cece_result = "loss"
                else:
                    cece_result = "draw"
            elif black == "Cece_v1.3":
                cece_color = "black"
                if result == "0-1":
                    cece_result = "win"
                elif result == "1-0":
                    cece_result = "loss"
                else:
                    cece_result = "draw"
            else:
                return None
            
            # Extract moves
            moves = self._extract_moves(game_text)
            
            # Analyze patterns
            patterns = self._analyze_patterns(moves, cece_color)
            
            # Check if evaluation data is available
            eval_available = '{' in game_text and '}' in game_text
            
            return GameResult(
                game_number=game_number,
                white=white,
                black=black,
                result=result,
                termination=termination,
                plycount=plycount,
                opening=opening,
                cece_color=cece_color,
                cece_result=cece_result,
                moves=moves,
                key_patterns=patterns,
                eval_available=eval_available
            )
            
        except Exception as e:
            print(f"❌ Error parsing game {game_number}: {e}")
            return None
    
    def _extract_moves(self, game_text: str) -> List[str]:
        """Extract move list from game text."""
        # Find the moves section (after headers, before result)
        lines = game_text.split('\\n')
        moves_started = False
        moves_text = ""
        
        for line in lines:
            if line.strip() and not line.startswith('['):
                moves_started = True
            if moves_started:
                moves_text += line + " "
        
        # Clean up and extract moves
        moves_text = re.sub(r'\\{[^}]*\\}', '', moves_text)  # Remove comments
        moves_text = re.sub(r'\\d+\\.', '', moves_text)      # Remove move numbers
        moves_text = re.sub(r'[01]\/[2]\\-[01]|\\*', '', moves_text)  # Remove results
        
        moves = [move.strip() for move in moves_text.split() if move.strip()]
        return moves
    
    def _analyze_patterns(self, moves: List[str], cece_color: str) -> List[str]:
        """Analyze move patterns for Cece v1.3."""
        patterns = []
        
        if not moves:
            return patterns
            
        # Determine Cece's moves (every other move starting from 0 for white, 1 for black)
        cece_moves = []
        start_idx = 0 if cece_color == "white" else 1
        
        for i in range(start_idx, len(moves), 2):
            if i < len(moves):
                cece_moves.append(moves[i])
        
        # Pattern analysis
        if cece_moves:
            first_move = cece_moves[0]
            
            # Check for bad opening moves (v1.3 should avoid these)
            if first_move in ['Nh3', 'Na3', 'h3', 'a3', 'h4', 'a4']:
                patterns.append(f"BAD_OPENING: {first_move}")
            elif first_move in ['Nf3', 'Nc3', 'e4', 'd4', 'Nf6', 'Nc6', 'e5', 'd5']:
                patterns.append(f"GOOD_OPENING: {first_move}")
            
            # Check for early queen development
            for i, move in enumerate(cece_moves[:4]):  # First 4 moves
                if move.startswith('Q') and i < 3:
                    patterns.append(f"EARLY_QUEEN: {move} on move {i+1}")
            
            # Check for knight development to rim
            for i, move in enumerate(cece_moves[:6]):  # First 6 moves  
                if move in ['Nh3', 'Na3', 'Ng5', 'Ne2'] and cece_color == "white":
                    patterns.append(f"RIM_KNIGHT: {move} on move {i+1}")
                elif move in ['Nh6', 'Na6', 'Ng4', 'Ne7'] and cece_color == "black":
                    patterns.append(f"RIM_KNIGHT: {move} on move {i+1}")
            
            # Check for repetitive moves
            move_counts = defaultdict(int)
            for move in cece_moves:
                move_counts[move] += 1
            
            for move, count in move_counts.items():
                if count >= 3:
                    patterns.append(f"REPETITIVE: {move} played {count} times")
        
        return patterns
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate tournament summary for Cece v1.3."""
        if not self.cece_games:
            return {}
        
        total_games = len(self.cece_games)
        wins = sum(1 for g in self.cece_games if g.cece_result == "win")
        losses = sum(1 for g in self.cece_games if g.cece_result == "loss")
        draws = sum(1 for g in self.cece_games if g.cece_result == "draw")
        
        # Analyze by color
        white_games = [g for g in self.cece_games if g.cece_color == "white"]
        black_games = [g for g in self.cece_games if g.cece_color == "black"]
        
        white_wins = sum(1 for g in white_games if g.cece_result == "win")
        black_wins = sum(1 for g in black_games if g.cece_result == "win")
        
        # Pattern analysis
        all_patterns = []
        for game in self.cece_games:
            all_patterns.extend(game.key_patterns)
        
        pattern_counts = defaultdict(int)
        for pattern in all_patterns:
            pattern_type = pattern.split(':')[0]
            pattern_counts[pattern_type] += 1
        
        # Termination analysis
        termination_counts = defaultdict(int)
        for game in self.cece_games:
            termination_counts[game.termination] += 1
        
        return {
            'total_games': total_games,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_rate': wins / total_games if total_games > 0 else 0,
            'white_games': len(white_games),
            'black_games': len(black_games),
            'white_wins': white_wins,
            'black_wins': black_wins,
            'white_win_rate': white_wins / len(white_games) if white_games else 0,
            'black_win_rate': black_wins / len(black_games) if black_games else 0,
            'pattern_counts': dict(pattern_counts),
            'termination_counts': dict(termination_counts),
            'eval_available_count': sum(1 for g in self.cece_games if g.eval_available)
        }
    
    def find_losses(self) -> List[GameResult]:
        """Find all games where Cece v1.3 lost."""
        return [g for g in self.cece_games if g.cece_result == "loss"]
    
    def find_games_with_bad_patterns(self) -> List[GameResult]:
        """Find games with concerning patterns."""
        bad_patterns = ['BAD_OPENING', 'EARLY_QUEEN', 'RIM_KNIGHT']
        
        bad_games = []
        for game in self.cece_games:
            for pattern in game.key_patterns:
                if any(bad in pattern for bad in bad_patterns):
                    bad_games.append(game)
                    break
        
        return bad_games
    
    def export_to_json(self, output_path: str) -> Dict[str, Any]:
        """Export comprehensive tournament analysis to JSON."""
        if not self.cece_games:
            return {}
        
        # Generate basic summary
        summary = self.generate_summary()
        
        # Extract detailed game data
        games_data = []
        for game in self.cece_games:
            game_dict = asdict(game)
            games_data.append(game_dict)
        
        # Performance analysis by opponent
        opponent_analysis = self.analyze_by_opponent()
        
        # Opening analysis
        opening_analysis = self.analyze_openings()
        
        # Time-based analysis (if available)
        game_length_analysis = self.analyze_game_lengths()
        
        # Pattern trend analysis
        pattern_trends = self.analyze_pattern_trends()
        
        # Critical games analysis
        critical_games = self.identify_critical_games()
        
        # Comprehensive data structure
        analysis_data = {
            "metadata": {
                "analysis_date": datetime.now().isoformat(),
                "tournament_file": self.pgn_file_path,
                "engine_version": "Cece_v1.3",
                "total_games_analyzed": len(self.cece_games),
                "analysis_version": "1.0"
            },
            "tournament_summary": summary,
            "detailed_games": games_data,
            "performance_analysis": {
                "by_opponent": opponent_analysis,
                "by_color": {
                    "white": {
                        "games": summary['white_games'],
                        "wins": summary['white_wins'],
                        "win_rate": summary['white_win_rate'],
                        "losses": len([g for g in self.cece_games if g.cece_color == "white" and g.cece_result == "loss"]),
                        "draws": len([g for g in self.cece_games if g.cece_color == "white" and g.cece_result == "draw"])
                    },
                    "black": {
                        "games": summary['black_games'],
                        "wins": summary['black_wins'],
                        "win_rate": summary['black_win_rate'],
                        "losses": len([g for g in self.cece_games if g.cece_color == "black" and g.cece_result == "loss"]),
                        "draws": len([g for g in self.cece_games if g.cece_color == "black" and g.cece_result == "draw"])
                    }
                }
            },
            "opening_analysis": opening_analysis,
            "game_length_analysis": game_length_analysis,
            "pattern_analysis": {
                "pattern_counts": summary['pattern_counts'],
                "pattern_trends": pattern_trends,
                "concerning_patterns": self.find_concerning_patterns()
            },
            "critical_games": critical_games,
            "insights_and_recommendations": self.generate_insights(),
            "visualization_data": self.prepare_visualization_data()
        }
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        return analysis_data
    
    def analyze_by_opponent(self) -> Dict[str, Dict[str, Any]]:
        """Analyze performance against different opponents."""
        opponent_stats = defaultdict(lambda: {"games": 0, "wins": 0, "losses": 0, "draws": 0, "win_rate": 0.0})
        
        for game in self.cece_games:
            opponent = game.black if game.cece_color == "white" else game.white
            opponent_stats[opponent]["games"] += 1
            
            if game.cece_result == "win":
                opponent_stats[opponent]["wins"] += 1
            elif game.cece_result == "loss":
                opponent_stats[opponent]["losses"] += 1
            else:
                opponent_stats[opponent]["draws"] += 1
        
        # Calculate win rates
        for opponent, stats in opponent_stats.items():
            if stats["games"] > 0:
                stats["win_rate"] = stats["wins"] / stats["games"]
        
        return dict(opponent_stats)
    
    def analyze_openings(self) -> Dict[str, Any]:
        """Analyze opening performance."""
        opening_stats = defaultdict(lambda: {"games": 0, "wins": 0, "losses": 0, "draws": 0, "win_rate": 0.0})
        
        for game in self.cece_games:
            opening = game.opening
            opening_stats[opening]["games"] += 1
            
            if game.cece_result == "win":
                opening_stats[opening]["wins"] += 1
            elif game.cece_result == "loss":
                opening_stats[opening]["losses"] += 1
            else:
                opening_stats[opening]["draws"] += 1
        
        # Calculate win rates
        for opening, stats in opening_stats.items():
            if stats["games"] > 0:
                stats["win_rate"] = stats["wins"] / stats["games"]
        
        # Find best and worst openings
        openings_list = [(opening, stats) for opening, stats in opening_stats.items() if stats["games"] >= 2]
        best_openings = sorted(openings_list, key=lambda x: x[1]["win_rate"], reverse=True)[:3]
        worst_openings = sorted(openings_list, key=lambda x: x[1]["win_rate"])[:3]
        
        return {
            "opening_stats": dict(opening_stats),
            "best_openings": best_openings,
            "worst_openings": worst_openings,
            "most_played": sorted(opening_stats.items(), key=lambda x: x[1]["games"], reverse=True)[:5]
        }
    
    def analyze_game_lengths(self) -> Dict[str, Any]:
        """Analyze game length patterns."""
        lengths = [game.plycount for game in self.cece_games if game.plycount > 0]
        
        if not lengths:
            return {"error": "No game length data available"}
        
        # Categorize games by length
        short_games = [l for l in lengths if l <= 30]
        medium_games = [l for l in lengths if 30 < l <= 60]
        long_games = [l for l in lengths if l > 60]
        
        # Analyze results by game length
        short_results = [game.cece_result for game in self.cece_games if 0 < game.plycount <= 30]
        medium_results = [game.cece_result for game in self.cece_games if 30 < game.plycount <= 60]
        long_results = [game.cece_result for game in self.cece_games if game.plycount > 60]
        
        return {
            "average_length": sum(lengths) / len(lengths),
            "shortest_game": min(lengths),
            "longest_game": max(lengths),
            "length_distribution": {
                "short_games": len(short_games),
                "medium_games": len(medium_games),
                "long_games": len(long_games)
            },
            "performance_by_length": {
                "short": self._calculate_performance(short_results),
                "medium": self._calculate_performance(medium_results),
                "long": self._calculate_performance(long_results)
            }
        }
    
    def _calculate_performance(self, results: List[str]) -> Dict[str, float]:
        """Calculate performance statistics for a list of results."""
        if not results:
            return {"win_rate": 0.0, "games": 0}
        
        wins = results.count("win")
        total = len(results)
        
        return {
            "win_rate": wins / total if total > 0 else 0.0,
            "games": total,
            "wins": wins,
            "losses": results.count("loss"),
            "draws": results.count("draw")
        }
    
    def analyze_pattern_trends(self) -> Dict[str, Any]:
        """Analyze how patterns change over the tournament."""
        pattern_timeline = []
        
        for i, game in enumerate(self.cece_games):
            pattern_timeline.append({
                "game_number": i + 1,
                "patterns": game.key_patterns,
                "result": game.cece_result,
                "bad_patterns": len([p for p in game.key_patterns if any(bad in p for bad in ['BAD_OPENING', 'EARLY_QUEEN', 'RIM_KNIGHT'])])
            })
        
        # Calculate trend in bad patterns
        early_games = pattern_timeline[:len(pattern_timeline)//3]
        late_games = pattern_timeline[-len(pattern_timeline)//3:]
        
        early_bad_avg = sum(g["bad_patterns"] for g in early_games) / len(early_games) if early_games else 0
        late_bad_avg = sum(g["bad_patterns"] for g in late_games) / len(late_games) if late_games else 0
        
        return {
            "pattern_timeline": pattern_timeline,
            "improvement_trend": {
                "early_tournament_bad_patterns_avg": early_bad_avg,
                "late_tournament_bad_patterns_avg": late_bad_avg,
                "improvement": early_bad_avg - late_bad_avg
            }
        }
    
    def find_concerning_patterns(self) -> List[Dict[str, Any]]:
        """Find games with the most concerning patterns."""
        concerning_games = []
        
        for game in self.cece_games:
            bad_pattern_count = len([p for p in game.key_patterns if any(bad in p for bad in ['BAD_OPENING', 'EARLY_QUEEN', 'RIM_KNIGHT'])])
            
            if bad_pattern_count > 0:
                concerning_games.append({
                    "game_number": game.game_number,
                    "opponent": game.black if game.cece_color == "white" else game.white,
                    "result": game.cece_result,
                    "bad_pattern_count": bad_pattern_count,
                    "patterns": game.key_patterns,
                    "opening": game.opening
                })
        
        return sorted(concerning_games, key=lambda x: x["bad_pattern_count"], reverse=True)
    
    def identify_critical_games(self) -> Dict[str, List[Dict[str, Any]]]:
        """Identify critical games for analysis."""
        losses = self.find_losses()
        wins = [g for g in self.cece_games if g.cece_result == "win"]
        concerning = self.find_games_with_bad_patterns()
        
        # Long draws (potential missed opportunities)
        long_draws = [g for g in self.cece_games if g.cece_result == "draw" and g.plycount > 80]
        
        return {
            "losses": [asdict(game) for game in losses],
            "wins": [asdict(game) for game in wins[:3]],  # Top 3 wins
            "concerning_patterns": [asdict(game) for game in concerning[:3]],  # Top 3 concerning
            "long_draws": [asdict(game) for game in long_draws[:3]]  # Top 3 long draws
        }
    
    def generate_insights(self) -> List[Dict[str, str]]:
        """Generate insights and recommendations."""
        insights = []
        summary = self.generate_summary()
        
        # Performance insights
        if summary['win_rate'] < 0.4:
            insights.append({
                "type": "performance",
                "severity": "high",
                "title": "Low Win Rate",
                "description": f"Win rate of {summary['win_rate']:.1%} is below target. Focus on improving tactical awareness and endgame technique."
            })
        
        # Color preference insights
        if abs(summary['white_win_rate'] - summary['black_win_rate']) > 0.2:
            better_color = "white" if summary['white_win_rate'] > summary['black_win_rate'] else "black"
            insights.append({
                "type": "color_preference",
                "severity": "medium",
                "title": f"Color Imbalance - Better as {better_color}",
                "description": f"Significant performance difference: {summary['white_win_rate']:.1%} as white vs {summary['black_win_rate']:.1%} as black."
            })
        
        # Pattern insights
        bad_patterns = sum(count for pattern, count in summary['pattern_counts'].items() if pattern in ['BAD_OPENING', 'EARLY_QUEEN', 'RIM_KNIGHT'])
        if bad_patterns > 0:
            insights.append({
                "type": "patterns",
                "severity": "medium",
                "title": "Concerning Opening Patterns",
                "description": f"Detected {bad_patterns} instances of poor opening choices. Review opening book and piece development principles."
            })
        
        # Termination insights
        if summary['termination_counts'].get('rules infraction', 0) > 0:
            insights.append({
                "type": "technical",
                "severity": "high",
                "title": "Rules Infractions",
                "description": "Engine made illegal moves. Check move generation and validation logic."
            })
        
        return insights
    
    def prepare_visualization_data(self) -> Dict[str, Any]:
        """Prepare data optimized for web visualization."""
        return {
            "performance_chart": {
                "labels": ["Wins", "Losses", "Draws"],
                "data": [
                    sum(1 for g in self.cece_games if g.cece_result == "win"),
                    sum(1 for g in self.cece_games if g.cece_result == "loss"),
                    sum(1 for g in self.cece_games if g.cece_result == "draw")
                ],
                "colors": ["#4CAF50", "#F44336", "#FF9800"]
            },
            "color_performance": {
                "white": {
                    "wins": sum(1 for g in self.cece_games if g.cece_color == "white" and g.cece_result == "win"),
                    "total": sum(1 for g in self.cece_games if g.cece_color == "white")
                },
                "black": {
                    "wins": sum(1 for g in self.cece_games if g.cece_color == "black" and g.cece_result == "win"),
                    "total": sum(1 for g in self.cece_games if g.cece_color == "black")
                }
            },
            "game_timeline": [
                {
                    "game": i + 1,
                    "result": game.cece_result,
                    "opponent": game.black if game.cece_color == "white" else game.white,
                    "length": game.plycount,
                    "patterns": len(game.key_patterns)
                }
                for i, game in enumerate(self.cece_games)
            ],
            "opening_heatmap": self.analyze_openings()["opening_stats"],
            "pattern_distribution": self.generate_summary()["pattern_counts"]
        }
    
    def print_game_analysis(self, game: GameResult):
        """Print detailed analysis of a specific game."""
        print(f"\\n🎮 Game #{game.game_number}: {game.white} vs {game.black}")
        print(f"   Result: {game.result} ({game.cece_result} for Cece)")
        print(f"   Cece played: {game.cece_color}")
        print(f"   Opening: {game.opening}")
        print(f"   Termination: {game.termination}")
        print(f"   Moves: {game.plycount}")
        print(f"   Eval available: {'✅' if game.eval_available else '❌'}")
        
        if game.key_patterns:
            print(f"   Patterns detected:")
            for pattern in game.key_patterns:
                if any(bad in pattern for bad in ['BAD_OPENING', 'EARLY_QUEEN', 'RIM_KNIGHT']):
                    print(f"     🚨 {pattern}")
                else:
                    print(f"     ℹ️  {pattern}")
        
        if game.moves:
            # Show first 10 moves
            moves_display = ' '.join(game.moves[:20]) + ('...' if len(game.moves) > 20 else '')
            print(f"   Moves: {moves_display}")

def main():
    """Main analysis function."""
    pgn_file = r"c:\\Program Files (x86)\\Arena\\Tournaments\\Engine Battle 20250806.pgn"
    
    print("🏆 CECE v1.3 TOURNAMENT ANALYSIS")
    print("=" * 50)
    
    analyzer = TournamentAnalyzer(pgn_file)
    cece_games = analyzer.extract_cece_games()
    
    if not cece_games:
        print("❌ No Cece v1.3 games found!")
        return
    
    # Generate summary
    summary = analyzer.generate_summary()
    
    print(f"\\n📊 TOURNAMENT SUMMARY")
    print(f"Total games: {summary['total_games']}")
    print(f"Record: {summary['wins']}W-{summary['losses']}L-{summary['draws']}D")
    print(f"Win rate: {summary['win_rate']:.1%}")
    print(f"As White: {summary['white_wins']}/{summary['white_games']} ({summary['white_win_rate']:.1%})")
    print(f"As Black: {summary['black_wins']}/{summary['black_games']} ({summary['black_win_rate']:.1%})")
    print(f"Games with eval data: {summary['eval_available_count']}/{summary['total_games']}")
    
    if summary['pattern_counts']:
        print(f"\\n🔍 PATTERN ANALYSIS")
        for pattern, count in summary['pattern_counts'].items():
            emoji = "🚨" if pattern in ['BAD_OPENING', 'EARLY_QUEEN', 'RIM_KNIGHT'] else "ℹ️"
            print(f"  {emoji} {pattern}: {count}")
    
    if summary['termination_counts']:
        print(f"\\n🏁 TERMINATION ANALYSIS")
        for term, count in summary['termination_counts'].items():
            print(f"  {term}: {count}")
    
    # Analyze losses
    losses = analyzer.find_losses()
    if losses:
        print(f"\\n💥 LOSS ANALYSIS ({len(losses)} losses)")
        print("-" * 30)
        for loss in losses[:5]:  # Show first 5 losses
            analyzer.print_game_analysis(loss)
    
    # Analyze games with bad patterns
    bad_games = analyzer.find_games_with_bad_patterns()
    if bad_games:
        print(f"\\n🚨 GAMES WITH CONCERNING PATTERNS ({len(bad_games)} games)")
        print("-" * 40)
        for game in bad_games[:3]:  # Show first 3 problematic games
            analyzer.print_game_analysis(game)
    
    # Generate comprehensive JSON report
    print("\\n📄 GENERATING COMPREHENSIVE JSON REPORT...")
    output_path = r"s:\\Maker Stuff\\Programming\\Static Evaluation Chess Engine\\static_evaluation_engine\\results\\historical\\tournament_analysis_results_20250807_1500.json"
    
    try:
        analysis_data = analyzer.export_to_json(output_path)
        print(f"✅ JSON report saved to: {output_path}")
        print(f"📊 Report contains {len(analysis_data.get('detailed_games', []))} games with comprehensive analysis")
        
        # Show key insights
        insights = analysis_data.get('insights_and_recommendations', [])
        if insights:
            print("\\n🔍 KEY INSIGHTS:")
            for insight in insights[:3]:  # Show top 3 insights
                severity_emoji = "🚨" if insight['severity'] == 'high' else "⚠️" if insight['severity'] == 'medium' else "ℹ️"
                print(f"   {severity_emoji} {insight['title']}: {insight['description']}")
    
    except Exception as e:
        print(f"❌ Error generating JSON report: {e}")
    
    return analyzer

if __name__ == "__main__":
    analyzer = main()
