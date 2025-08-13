#!/usr/bin/env python3
"""
Detailed Game Analysis for Cece v1.3
Analyzes specific games to understand behavioral patterns and issues
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import chess
import chess.pgn
from io import StringIO

@dataclass
class DetailedGame:
    """Detailed game data with move-by-move analysis."""
    game_number: int
    white: str
    black: str
    result: str
    cece_color: str
    cece_result: str
    opening: str
    termination: str
    plycount: int
    moves: List[str]
    evaluations: List[float]  # Engine evaluations if available
    time_spent: List[float]   # Time per move if available
    move_analysis: List[Dict[str, Any]]  # Per-move analysis

class DetailedGameAnalyzer:
    """Analyzes individual games in detail."""
    
    def __init__(self, pgn_file: str):
        self.pgn_file = pgn_file
        self.games_data = []
    
    def extract_game_by_number(self, game_number: int) -> Optional[str]:
        """Extract a specific game by its number."""
        try:
            with open(self.pgn_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into individual games
            games = re.split(r'\n\n(?=\[Event)', content)
            
            for i, game_text in enumerate(games, 1):
                if i == game_number:
                    return game_text.strip()
            
            return None
        except Exception as e:
            print(f"Error extracting game {game_number}: {e}")
            return None
    
    def parse_detailed_game(self, game_text: str, game_number: int) -> Optional[DetailedGame]:
        """Parse a game with detailed move-by-move analysis."""
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
            if "Cece_v1.3" in white:
                cece_color = "white"
                cece_result = "win" if result == "1-0" else ("loss" if result == "0-1" else "draw")
            elif "Cece_v1.3" in black:
                cece_color = "black"
                cece_result = "win" if result == "0-1" else ("loss" if result == "1-0" else "draw")
            else:
                return None
            
            # Extract moves and analysis
            moves, evaluations, time_spent, move_analysis = self.parse_moves_with_analysis(game_text)
            
            return DetailedGame(
                game_number=game_number,
                white=white,
                black=black,
                result=result,
                cece_color=cece_color,
                cece_result=cece_result,
                opening=opening,
                termination=termination,
                plycount=plycount,
                moves=moves,
                evaluations=evaluations,
                time_spent=time_spent,
                move_analysis=move_analysis
            )
            
        except Exception as e:
            print(f"Error parsing game: {e}")
            return None
    
    def parse_moves_with_analysis(self, game_text: str) -> Tuple[List[str], List[float], List[float], List[Dict]]:
        """Parse moves with evaluations and time data."""
        moves = []
        evaluations = []
        time_spent = []
        move_analysis = []
        
        try:
            # Find the moves section (after headers)
            moves_start = game_text.find('\n\n')
            if moves_start == -1:
                return moves, evaluations, time_spent, move_analysis
            
            moves_text = game_text[moves_start:].strip()
            
            # Remove game result
            moves_text = re.sub(r'\s+(1-0|0-1|1/2-1/2)\s*$', '', moves_text)
            
            # Parse moves with annotations
            move_pattern = r'(\d+\.)\s*([^\s]+)(?:\s+\{([^}]*)\})?\s*([^\s]+)?(?:\s+\{([^}]*)\})?'
            
            for match in re.finditer(move_pattern, moves_text):
                move_num = match.group(1)
                white_move = match.group(2)
                white_annotation = match.group(3) or ""
                black_move = match.group(4)
                black_annotation = match.group(5) or ""
                
                # Add white move
                if white_move and not white_move.startswith('{'):
                    moves.append(white_move)
                    eval_val, time_val = self.extract_eval_and_time(white_annotation)
                    evaluations.append(eval_val)
                    time_spent.append(time_val)
                    
                    analysis = {
                        'move_number': len(moves),
                        'move': white_move,
                        'color': 'white',
                        'evaluation': eval_val,
                        'time': time_val,
                        'annotation': white_annotation
                    }
                    move_analysis.append(analysis)
                
                # Add black move
                if black_move and not black_move.startswith('{'):
                    moves.append(black_move)
                    eval_val, time_val = self.extract_eval_and_time(black_annotation)
                    evaluations.append(eval_val)
                    time_spent.append(time_val)
                    
                    analysis = {
                        'move_number': len(moves),
                        'move': black_move,
                        'color': 'black',
                        'evaluation': eval_val,
                        'time': time_val,
                        'annotation': black_annotation
                    }
                    move_analysis.append(analysis)
            
        except Exception as e:
            print(f"Error parsing moves: {e}")
        
        return moves, evaluations, time_spent, move_analysis
    
    def extract_eval_and_time(self, annotation: str) -> Tuple[Optional[float], Optional[float]]:
        """Extract evaluation and time from move annotation."""
        eval_val = None
        time_val = None
        
        if annotation:
            # Look for evaluation (format: eval +1.23 or eval -0.45)
            eval_match = re.search(r'eval\s+([-+]?\d*\.?\d+)', annotation)
            if eval_match:
                eval_val = float(eval_match.group(1))
            
            # Look for time (format: time 1.234)
            time_match = re.search(r'time\s+(\d*\.?\d+)', annotation)
            if time_match:
                time_val = float(time_match.group(1))
        
        return eval_val, time_val
    
    def analyze_game_phases(self, game: DetailedGame) -> Dict[str, Any]:
        """Analyze different phases of the game."""
        total_moves = len(game.moves)
        
        phases = {
            'opening': {'start': 0, 'end': min(20, total_moves)},
            'middlegame': {'start': min(20, total_moves), 'end': min(40, total_moves)},
            'endgame': {'start': min(40, total_moves), 'end': total_moves}
        }
        
        analysis = {}
        
        for phase_name, phase_range in phases.items():
            start_idx = phase_range['start']
            end_idx = phase_range['end']
            
            if start_idx >= end_idx:
                continue
            
            phase_moves = game.moves[start_idx:end_idx]
            phase_evals = [e for e in game.evaluations[start_idx:end_idx] if e is not None]
            phase_times = [t for t in game.time_spent[start_idx:end_idx] if t is not None]
            
            # Calculate Cece's moves in this phase
            cece_move_indices = []
            if game.cece_color == "white":
                cece_move_indices = [i for i in range(start_idx, end_idx, 2)]
            else:
                cece_move_indices = [i for i in range(start_idx + 1, end_idx, 2)]
            
            cece_evals = [game.evaluations[i] for i in cece_move_indices if i < len(game.evaluations) and game.evaluations[i] is not None]
            cece_times = [game.time_spent[i] for i in cece_move_indices if i < len(game.time_spent) and game.time_spent[i] is not None]
            
            analysis[phase_name] = {
                'total_moves': len(phase_moves),
                'cece_moves': len(cece_move_indices),
                'avg_eval': sum(phase_evals) / len(phase_evals) if phase_evals else None,
                'cece_avg_eval': sum(cece_evals) / len(cece_evals) if cece_evals else None,
                'avg_time': sum(phase_times) / len(phase_times) if phase_times else None,
                'cece_avg_time': sum(cece_times) / len(cece_times) if cece_times else None,
                'eval_trend': self.calculate_trend(phase_evals) if len(phase_evals) > 2 else None,
                'cece_eval_trend': self.calculate_trend(cece_evals) if len(cece_evals) > 2 else None
            }
        
        return analysis
    
    def calculate_trend(self, values: List[float]) -> str:
        """Calculate if values are improving, declining, or stable."""
        if len(values) < 3:
            return "insufficient_data"
        
        first_third = values[:len(values)//3]
        last_third = values[-len(values)//3:]
        
        first_avg = sum(first_third) / len(first_third)
        last_avg = sum(last_third) / len(last_third)
        
        diff = last_avg - first_avg
        
        if abs(diff) < 0.2:
            return "stable"
        elif diff > 0:
            return "improving"
        else:
            return "declining"
    
    def identify_critical_moments(self, game: DetailedGame) -> List[Dict[str, Any]]:
        """Identify critical moments in the game."""
        critical_moments = []
        
        if not game.evaluations or len(game.evaluations) < 5:
            return critical_moments
        
        # Look for large evaluation swings
        for i in range(1, len(game.evaluations) - 1):
            if game.evaluations[i] is None:
                continue
            
            prev_eval = game.evaluations[i-1] if game.evaluations[i-1] is not None else game.evaluations[i]
            curr_eval = game.evaluations[i]
            next_eval = game.evaluations[i+1] if game.evaluations[i+1] is not None else curr_eval
            
            # Check for significant swing
            swing = abs(curr_eval - prev_eval)
            
            if swing > 1.0:  # Significant evaluation change
                is_cece_move = (game.cece_color == "white" and i % 2 == 0) or (game.cece_color == "black" and i % 2 == 1)
                
                critical_moments.append({
                    'move_number': i + 1,
                    'move': game.moves[i] if i < len(game.moves) else "unknown",
                    'is_cece_move': is_cece_move,
                    'eval_before': prev_eval,
                    'eval_after': curr_eval,
                    'swing': swing,
                    'type': 'blunder' if is_cece_move and curr_eval < prev_eval else 'opponent_blunder' if not is_cece_move and curr_eval > prev_eval else 'tactical_shot'
                })
        
        return sorted(critical_moments, key=lambda x: x['swing'], reverse=True)[:5]
    
    def analyze_specific_game(self, game_number: int) -> Dict[str, Any]:
        """Perform comprehensive analysis of a specific game."""
        game_text = self.extract_game_by_number(game_number)
        if not game_text:
            return {'error': f'Game {game_number} not found'}
        
        game = self.parse_detailed_game(game_text, game_number)
        if not game:
            return {'error': f'Could not parse game {game_number}'}
        
        # Perform various analyses
        phase_analysis = self.analyze_game_phases(game)
        critical_moments = self.identify_critical_moments(game)
        
        # Basic statistics
        cece_move_count = (len(game.moves) + (1 if game.cece_color == "white" else 0)) // 2
        total_time = sum(t for t in game.time_spent if t is not None)
        avg_time_per_move = total_time / len([t for t in game.time_spent if t is not None]) if any(game.time_spent) else None
        
        return {
            'game_info': {
                'number': game.game_number,
                'white': game.white,
                'black': game.black,
                'result': game.result,
                'cece_color': game.cece_color,
                'cece_result': game.cece_result,
                'opening': game.opening,
                'termination': game.termination,
                'total_moves': len(game.moves),
                'cece_moves': cece_move_count
            },
            'time_management': {
                'total_time': total_time,
                'avg_time_per_move': avg_time_per_move,
                'has_time_data': any(t is not None for t in game.time_spent)
            },
            'evaluation_data': {
                'has_eval_data': any(e is not None for e in game.evaluations),
                'eval_count': len([e for e in game.evaluations if e is not None]),
                'final_eval': game.evaluations[-1] if game.evaluations and game.evaluations[-1] is not None else None
            },
            'phase_analysis': phase_analysis,
            'critical_moments': critical_moments,
            'first_20_moves': game.moves[:20],
            'last_10_moves': game.moves[-10:] if len(game.moves) >= 10 else game.moves
        }

def main():
    """Analyze specific games in detail."""
    pgn_file = r"c:\Program Files (x86)\Arena\Tournaments\Engine Battle 20250806.pgn"
    
    analyzer = DetailedGameAnalyzer(pgn_file)
    
    print("🔍 DETAILED GAME ANALYSIS - CECE v1.3")
    print("=" * 45)
    
    # Analyze the loss (Game #25)
    print("\\n💥 ANALYZING THE LOSS (Game #25)")
    print("-" * 35)
    
    loss_analysis = analyzer.analyze_specific_game(25)
    
    if 'error' in loss_analysis:
        print(f"❌ {loss_analysis['error']}")
    else:
        print_game_analysis(loss_analysis)
    
    # Also analyze a few draws for comparison
    print("\\n🤝 ANALYZING SAMPLE DRAWS")
    print("-" * 25)
    
    # Find some draw games (we know most games were draws)
    for game_num in [1, 5, 10]:  # Sample a few different games
        draw_analysis = analyzer.analyze_specific_game(game_num)
        
        if 'error' not in draw_analysis and draw_analysis['game_info']['cece_result'] == 'draw':
            print(f"\\n📊 Draw Analysis - Game #{game_num}")
            print_game_analysis(draw_analysis, brief=True)

def print_game_analysis(analysis: Dict[str, Any], brief: bool = False):
    """Print formatted game analysis."""
    info = analysis['game_info']
    
    print(f"🎮 {info['white']} vs {info['black']}")
    print(f"   Result: {info['result']} ({info['cece_result']} for Cece)")
    print(f"   Cece played: {info['cece_color']}")
    print(f"   Opening: {info['opening']}")
    print(f"   Termination: {info['termination']}")
    print(f"   Total moves: {info['total_moves']}")
    
    if analysis['time_management']['has_time_data']:
        time_mgmt = analysis['time_management']
        print(f"   Total time: {time_mgmt['total_time']:.1f}s")
        print(f"   Avg time/move: {time_mgmt['avg_time_per_move']:.2f}s")
    
    if analysis['evaluation_data']['has_eval_data']:
        eval_data = analysis['evaluation_data']
        print(f"   Evaluation data: {eval_data['eval_count']} moves")
        if eval_data['final_eval'] is not None:
            print(f"   Final evaluation: {eval_data['final_eval']:+.2f}")
    
    if not brief:
        # Phase analysis
        print("\\n   📈 PHASE ANALYSIS:")
        for phase, data in analysis['phase_analysis'].items():
            if data['cece_avg_eval'] is not None:
                trend = data['cece_eval_trend'] or "unknown"
                print(f"     {phase.title()}: avg eval {data['cece_avg_eval']:+.2f}, trend: {trend}")
        
        # Critical moments
        if analysis['critical_moments']:
            print("\\n   🚨 CRITICAL MOMENTS:")
            for moment in analysis['critical_moments'][:3]:
                icon = "⚠️" if moment['is_cece_move'] else "✅"
                print(f"     {icon} Move {moment['move_number']}: {moment['move']} "
                      f"(eval {moment['eval_before']:+.2f} → {moment['eval_after']:+.2f})")
        
        # Opening moves
        print(f"\\n   🎯 Opening: {' '.join(analysis['first_20_moves'])}")

if __name__ == "__main__":
    main()
