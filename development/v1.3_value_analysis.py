#!/usr/bin/env python3
"""
Analysis of current evaluation scoring values to prepare for v1.3 redesign.
This script identifies all static values vs calculated values in the evaluation.
"""

import chess
from evaluation import Evaluation

def analyze_current_scoring():
    """Analyze all scoring values in the current evaluation system."""
    
    print("🔍 CECE v1.3 EVALUATION REDESIGN - CURRENT VALUE ANALYSIS")
    print("=" * 70)
    
    evaluator = Evaluation()
    
    print("📊 PIECE VALUES (Base Material)")
    print("-" * 40)
    for piece_type, value in evaluator.piece_values.items():
        piece_name = chess.piece_name(piece_type).capitalize()
        print(f"{piece_name}: {value} centipawns")
    
    print(f"\n🏰 PIECE-SQUARE TABLE VALUES (Static)")
    print("-" * 40)
    
    # Sample key PST values
    pst_samples = {
        'Knight h3 (rim)': evaluator.knight_table[evaluator._square_to_table_index(chess.H3, chess.WHITE)],
        'Knight d4 (center)': evaluator.knight_table[evaluator._square_to_table_index(chess.D4, chess.WHITE)],
        'Queen h8 (corner)': evaluator.queen_table[evaluator._square_to_table_index(chess.H8, chess.WHITE)],
        'Queen d4 (center)': evaluator.queen_table[evaluator._square_to_table_index(chess.D4, chess.WHITE)],
        'Pawn e4 (center)': evaluator.pawn_table[evaluator._square_to_table_index(chess.E4, chess.WHITE)],
        'Pawn a2 (side)': evaluator.pawn_table[evaluator._square_to_table_index(chess.A2, chess.WHITE)]
    }
    
    for desc, value in pst_samples.items():
        pawn_equiv = value / 100
        print(f"{desc}: {value:4d} ({pawn_equiv:+.2f} pawns)")
    
    print(f"\n⚔️ TACTICAL SCORING (Mixed)")
    print("-" * 40)
    
    # These are the static values we can find in the code
    tactical_values = {
        'SEE bonus cap': 200,
        'Bad capture penalty divisor': 2,
        'King area attack penalty': 15,
        'King area attack bonus': 10,
        'Exposed king penalty': 100,
        'Castling rights bonus': 15,
        'Castled bonus': 50,
        'Early game castling urgency': 30,
        'Pawn shield bonus': 20
    }
    
    for desc, value in tactical_values.items():
        pawn_equiv = value / 100
        print(f"{desc}: {value:4d} ({pawn_equiv:+.2f} pawns)")
    
    print(f"\n🧮 CALCULATED/DYNAMIC VALUES")
    print("-" * 40)
    print("These values are computed dynamically:")
    print("• Material balance (piece_values × count)")
    print("• SEE capture evaluation (piece exchange calculation)")
    print("• Threat values (based on piece_values)")
    print("• Hanging piece penalties (based on piece_values)")
    print("• Mobility bonuses (move count × multiplier)")

def identify_value_types():
    """Categorize evaluation values by how they're determined."""
    
    print(f"\n📋 VALUE CATEGORIZATION FOR v1.3 REDESIGN")
    print("=" * 50)
    
    categories = {
        "STATIC INTEGER VALUES (Need Pawn-Relative Conversion)": [
            "PST table values (-80 to +60)",
            "King safety attack penalties (15, 10)",
            "Castling bonuses (15, 50, 30)",
            "Exposed king penalty (100)",
            "SEE bonus cap (200)",
            "Pawn shield bonus (20)"
        ],
        
        "PIECE-VALUE BASED (Already Relative)": [
            "Material balance calculation", 
            "SEE capture evaluation",
            "Threat assessment scores",
            "Hanging piece penalties"
        ],
        
        "COUNT-BASED (May Need Scaling)": [
            "Mobility bonuses (moves × 2)",
            "King area attacks (count × penalty)",
            "Piece development tracking"
        ],
        
        "POSITIONAL MULTIPLIERS (Check Logic)": [
            "Bad capture penalty (÷ 2)",
            "Activity bonus scaling",
            "Game phase adjustments"
        ]
    }
    
    for category, items in categories.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")

if __name__ == "__main__":
    analyze_current_scoring()
    identify_value_types()
