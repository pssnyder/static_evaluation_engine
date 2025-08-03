"""
Main Chess Engine - Hybrid Implementation

This engine combines the best of both worlds:
- Uses python-chess for reliable infrastructure (move generation, board representation, etc.)
- Maintains full control over evaluation logic for your custom chess personality
- Provides comprehensive data collection for analysis and tuning

Architecture:
- Delegates complex chess infrastructure to proven libraries
- Focuses your effort on evaluation, pattern recognition, and analysis
- Maintains ethical use of open source while clearly defining your contributions

Author: Your Name
License: GPL-3.0 (compatible with python-chess)
Attribution: Built on python-chess library by Niklas Fiekas
"""

import chess
import chess.engine
import time
from typing import Optional, Dict, Any, List
from hybrid_engine import CustomEvaluationEngine


class ChessEngine:
    """
    Main chess engine class - simplified and focused on YOUR contributions.
    
    This class orchestrates the hybrid approach:
    - Uses python-chess for infrastructure
    - Your custom evaluation for position assessment
    - Your data collection for analysis and tuning
    """
    
    def __init__(self, evaluation_config: Optional[Dict] = None):
        """Initialize the engine with custom evaluation configuration."""
        # Use the hybrid engine that combines python-chess + your evaluation
        self.engine = CustomEvaluationEngine(evaluation_config)
        
        # Engine metadata
        self.info = {
            'name': 'YourChessEngine',
            'version': '1.0',
            'author': 'Your Name',
            'description': 'Hybrid engine focusing on custom evaluation and analysis',
            'license': 'GPL-3.0',
            'attribution': 'Built on python-chess by Niklas Fiekas'
        }
        
        # Configuration
        self.search_depth = 10
        self.time_limit = 5.0
        
        print(f"Initialized {self.info['name']} v{self.info['version']}")
        print(f"Author: {self.info['author']}")
        print(f"Attribution: {self.info['attribution']}")
    
    def set_position(self, fen: Optional[str] = None, moves: Optional[List[str]] = None):
        """Set the board position."""
        self.engine.set_position(fen, moves)
        print(f"Position set: {self.engine.board.fen()}")
    
    def get_best_move(self, depth: Optional[int] = None, 
                     time_limit: Optional[float] = None) -> Optional[chess.Move]:
        """
        Get the best move for the current position.
        
        This delegates the complex search to proven algorithms while
        using YOUR evaluation at each position.
        """
        search_depth = depth or self.search_depth
        search_time = time_limit or self.time_limit
        
        print(f"\\nSearching position (depth: {search_depth}, time: {search_time}s)...")
        
        # Use the hybrid search that combines efficiency with custom evaluation
        search_result = self.engine.search_position(search_depth, search_time)
        
        # Display search statistics
        print(f"Search completed:")
        print(f"  Nodes searched: {search_result.nodes:,}")
        print(f"  Time taken: {search_result.time_ms/1000:.3f}s")
        print(f"  NPS: {search_result.nps:,}")
        print(f"  Evaluation: {search_result.score}")
        print(f"  Thoughts collected: {search_result.thoughts_collected}")
        print(f"  Ideas formed: {search_result.ideas_formed}")
        
        if search_result.pv:
            pv_str = ' '.join(str(move) for move in search_result.pv[:5])
            print(f"  Principal variation: {pv_str}")
            return search_result.pv[0]
        
        return None
    
    def make_move(self, move: str) -> bool:
        """Make a move on the board."""
        success = self.engine.make_move(move)
        if success:
            print(f"Move made: {move}")
            print(f"New position: {self.engine.board.fen()}")
        else:
            print(f"Invalid move: {move}")
        return success
    
    def analyze_position(self) -> Dict[str, Any]:
        """
        Get detailed analysis of the current position.
        
        This showcases YOUR evaluation breakdown and provides
        transparency into the engine's thinking process.
        """
        analysis = self.engine.get_evaluation_breakdown()
        
        print("\\n=== Position Analysis ===")
        print(f"FEN: {self.engine.board.fen()}")
        print(f"Total Score: {analysis['total_score']}")
        print(f"Material: {analysis['material_score']}")
        print(f"Positional: {analysis['positional_score']}")
        print(f"Tactical: {analysis['tactical_score']}")
        print(f"King Safety: {analysis['safety_score']}")
        print(f"Pawn Structure: {analysis['pawn_structure']}")
        print(f"Piece Activity: {analysis['piece_activity']}")
        
        if analysis['custom_patterns']:
            print("\\nCustom Patterns Detected:")
            for pattern, value in analysis['custom_patterns'].items():
                print(f"  {pattern}: {value}")
        
        return analysis
    
    def export_analysis_data(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Export collected analysis data for research and tuning.
        
        This is YOUR data collection system for understanding
        and improving the engine's decision-making process.
        """
        thoughts_data = self.engine.export_thoughts_data()
        ideas_data = self.engine.export_ideas_data()
        
        export_data = {
            'engine_info': self.info,
            'session_summary': {
                'total_thoughts': len(thoughts_data),
                'total_ideas': len(ideas_data),
                'positions_analyzed': len(set(t['position_fen'] for t in thoughts_data)),
                'export_timestamp': time.time()
            },
            'thoughts': thoughts_data,
            'ideas': ideas_data
        }
        
        if filename:
            import json
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"Analysis data exported to: {filename}")
        
        print(f"\\nSession Summary:")
        print(f"  Thoughts collected: {export_data['session_summary']['total_thoughts']}")
        print(f"  Ideas formed: {export_data['session_summary']['total_ideas']}")
        print(f"  Positions analyzed: {export_data['session_summary']['positions_analyzed']}")
        
        return export_data
    
    def tune_evaluation(self, parameter: str, value: float):
        """
        Tune evaluation parameters for experimentation.
        
        This allows you to adjust YOUR evaluation weights and
        see how they affect the engine's play style.
        """
        if parameter in self.engine.evaluator.weights:
            old_value = self.engine.evaluator.weights[parameter]
            self.engine.evaluator.weights[parameter] = value
            print(f"Tuned {parameter}: {old_value} -> {value}")
        elif parameter in self.engine.evaluator.pattern_bonuses:
            old_value = self.engine.evaluator.pattern_bonuses[parameter]
            self.engine.evaluator.pattern_bonuses[parameter] = int(value)
            print(f"Tuned {parameter}: {old_value} -> {int(value)}")
        else:
            print(f"Unknown parameter: {parameter}")
            print("Available weights:", list(self.engine.evaluator.weights.keys()))
            print("Available patterns:", list(self.engine.evaluator.pattern_bonuses.keys()))
    
    def get_evaluation_explanation(self) -> str:
        """Get human-readable explanation of position evaluation."""
        return self.engine.evaluator.get_evaluation_explanation(self.engine.board)
    
    def play_move_sequence(self, moves: List[str]) -> List[Dict[str, Any]]:
        """
        Play a sequence of moves and collect analysis data.
        
        Useful for analyzing games, openings, or specific positions
        with your custom evaluation system.
        """
        move_analyses = []
        
        for i, move_str in enumerate(moves):
            print(f"\\nMove {i+1}: {move_str}")
            
            # Analyze position before move
            pre_analysis = self.analyze_position()
            
            # Make the move
            if not self.make_move(move_str):
                print(f"Invalid move sequence stopped at: {move_str}")
                break
            
            # Analyze position after move
            post_analysis = self.analyze_position()
            
            move_analyses.append({
                'move': move_str,
                'move_number': i + 1,
                'before': pre_analysis,
                'after': post_analysis,
                'evaluation_change': post_analysis['total_score'] - pre_analysis['total_score']
            })
        
        return move_analyses
    
    def benchmark(self, positions: List[str], depth: int = 6) -> Dict[str, Any]:
        """
        Benchmark the engine on a set of positions.
        
        Useful for performance testing and evaluation consistency.
        """
        results = []
        total_time = 0
        total_nodes = 0
        
        print(f"\\nBenchmarking on {len(positions)} positions at depth {depth}...")
        
        for i, fen in enumerate(positions):
            print(f"Position {i+1}/{len(positions)}: {fen[:50]}...")
            
            self.set_position(fen)
            start_time = time.time()
            
            search_result = self.engine.search_position(depth, time_limit=30.0)
            
            elapsed = time.time() - start_time
            total_time += elapsed
            total_nodes += search_result.nodes
            
            results.append({
                'position': fen,
                'best_move': str(search_result.pv[0]) if search_result.pv else None,
                'evaluation': search_result.score,
                'nodes': search_result.nodes,
                'time': elapsed,
                'nps': search_result.nps
            })
        
        avg_time = total_time / len(positions)
        avg_nodes = total_nodes / len(positions)
        overall_nps = total_nodes / total_time if total_time > 0 else 0
        
        benchmark_summary = {
            'positions_tested': len(positions),
            'depth': depth,
            'total_time': total_time,
            'total_nodes': total_nodes,
            'average_time': avg_time,
            'average_nodes': avg_nodes,
            'overall_nps': overall_nps,
            'results': results
        }
        
        print(f"\\nBenchmark Complete:")
        print(f"  Positions: {len(positions)}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Total nodes: {total_nodes:,}")
        print(f"  Average NPS: {overall_nps:,.0f}")
        
        return benchmark_summary
    
    def __str__(self):
        """String representation of the engine."""
        return f"{self.info['name']} v{self.info['version']} by {self.info['author']}"
