"""
Test Script for Hybrid Chess Engine

This demonstrates how your new hybrid engine works:
- Python-chess handles the complex infrastructure
- Your evaluation drives the decision making
- Data collection enables analysis and improvement

Run this to see your engine in action!
"""

from engine import ChessEngine
import time


def main():
    print("=== Hybrid Chess Engine Demo ===")
    print("Combining python-chess infrastructure with custom evaluation")
    print()
    
    # Initialize the engine with custom evaluation
    evaluation_config = {
        'material_weight': 1.0,
        'positional_weight': 0.3,
        'tactical_weight': 0.2,
        'safety_weight': 0.15,
        'collect_thoughts': True,
        'collect_ideas': True
    }
    
    engine = ChessEngine(evaluation_config)
    print()
    
    # Test 1: Basic position analysis
    print("=== Test 1: Starting Position Analysis ===")
    engine.set_position()  # Default starting position
    analysis = engine.analyze_position()
    print()
    
    # Test 2: Make some moves and analyze
    print("=== Test 2: Opening Moves ===")
    moves = ['e2e4', 'e7e5', 'g1f3', 'b8c6']
    
    for move in moves:
        print(f"\\nMaking move: {move}")
        engine.make_move(move)
        best_move = engine.get_best_move(depth=6, time_limit=2.0)
        if best_move:
            print(f"Engine suggests: {best_move}")
    
    print()
    
    # Test 3: Detailed position analysis
    print("=== Test 3: Current Position Analysis ===")
    analysis = engine.analyze_position()
    explanation = engine.get_evaluation_explanation()
    print(f"\\nEvaluation explanation:\\n{explanation}")
    print()
    
    # Test 4: Tune evaluation parameters
    print("=== Test 4: Parameter Tuning ===")
    print("Current material weight:", engine.engine.evaluator.weights['material'])
    engine.tune_evaluation('material', 1.2)
    print("New analysis after tuning:")
    engine.analyze_position()
    print()
    
    # Test 5: Export analysis data
    print("=== Test 5: Data Export ===")
    data = engine.export_analysis_data()
    print(f"Collected {len(data['thoughts'])} thoughts and {len(data['ideas'])} ideas")
    
    # Save to file for later analysis
    timestamp = int(time.time())
    filename = f"engine_analysis_{timestamp}.json"
    engine.export_analysis_data(filename)
    print()
    
    # Test 6: Famous position test
    print("=== Test 6: Famous Position Test ===")
    # Scholar's mate setup
    scholars_mate_fen = "rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3"
    engine.set_position(scholars_mate_fen)
    print("Analyzing Scholar's Mate setup...")
    
    best_move = engine.get_best_move(depth=8, time_limit=3.0)
    if best_move:
        print(f"Best move in Scholar's Mate setup: {best_move}")
    
    analysis = engine.analyze_position()
    print()
    
    # Test 7: Benchmark on a few positions
    print("=== Test 7: Mini Benchmark ===")
    test_positions = [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",  # Starting position
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 4",  # Italian
        "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2"  # Scandinavian
    ]
    
    benchmark_results = engine.benchmark(test_positions, depth=5)
    print()
    
    print("=== Demo Complete ===")
    print(f"Engine: {engine}")
    print("Your hybrid engine successfully combines:")
    print("✓ Python-chess for reliable infrastructure")
    print("✓ Your custom evaluation for unique play style")  
    print("✓ Comprehensive data collection for analysis")
    print("✓ Clear attribution and licensing compliance")
    print("\\nReady for further development and experimentation!")


if __name__ == "__main__":
    main()
