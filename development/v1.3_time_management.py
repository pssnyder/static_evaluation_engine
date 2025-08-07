#!/usr/bin/env python3
"""
Update engine.py parameters for v1.3 with better time management.
This addresses the issue of finishing games with too much time remaining.
"""

import chess
import time
from typing import Optional

def calculate_move_time(remaining_time: float, increment: float, move_number: int, 
                       game_phase: str = "opening") -> float:
    """
    Calculate appropriate time allocation for a move.
    
    Args:
        remaining_time: Time remaining on clock (seconds)
        increment: Time increment per move (seconds)  
        move_number: Current move number
        game_phase: "opening", "middlegame", or "endgame"
    
    Returns:
        Recommended time to spend on this move (seconds)
    """
    
    # Reserve some time for final moves (10% buffer)
    available_time = remaining_time * 0.9
    
    # Add increment to available time (we'll get it back)
    available_time += increment
    
    # Phase-based time allocation percentages
    time_allocation = {
        "opening": 0.08,     # 8% - quick development moves
        "middlegame": 0.04,  # 4% - standard calculation
        "endgame": 0.06      # 6% - precise calculation needed
    }
    
    # Get base percentage for this phase
    base_percentage = time_allocation.get(game_phase, 0.04)
    
    # Adjust for move urgency
    if move_number <= 12:  # Opening
        phase = "opening"
    elif move_number <= 40:  # Middlegame
        phase = "middlegame"
    else:  # Endgame
        phase = "endgame"
    
    # Calculate time to spend
    move_time = available_time * time_allocation[phase]
    
    # Minimum and maximum bounds
    min_time = 0.5  # At least 0.5 seconds
    max_time = min(30.0, remaining_time * 0.3)  # At most 30s or 30% of remaining
    
    return max(min_time, min(move_time, max_time))

def get_v13_engine_settings() -> dict:
    """Get recommended engine settings for v1.3."""
    
    return {
        # Search parameters
        "default_depth": 6,           # Up from 3 for better tactics
        "max_depth": 10,              # Allow deeper search when time permits
        "min_depth": 4,               # Never search less than 4 ply
        
        # Time management
        "time_buffer_ratio": 0.1,     # Reserve 10% of time
        "move_time_opening": 0.08,    # 8% of time in opening
        "move_time_middlegame": 0.04, # 4% of time in middlegame  
        "move_time_endgame": 0.06,    # 6% of time in endgame
        
        # Search enhancements
        "use_iterative_deepening": True,
        "use_aspiration_windows": True,
        "use_transposition_table": True,
        
        # Evaluation
        "use_v13_evaluation": True,
        "tal_style_bonus": True,
        "dynamic_piece_values": True,
        
        # Development phase
        "opening_move_limit": 12,
        "endgame_piece_threshold": 14,
    }

def demonstrate_time_management():
    """Demonstrate the new time management system."""
    
    print("🕐 CECE v1.3 TIME MANAGEMENT DEMONSTRATION")
    print("=" * 50)
    
    # Simulate different game scenarios
    scenarios = [
        {
            "name": "2+1 Game Start",
            "remaining_time": 120.0,
            "increment": 1.0,
            "move_number": 1
        },
        {
            "name": "2+1 Game Middlegame", 
            "remaining_time": 85.0,
            "increment": 1.0,
            "move_number": 20
        },
        {
            "name": "2+1 Game Endgame",
            "remaining_time": 45.0,
            "increment": 1.0,
            "move_number": 45
        },
        {
            "name": "15+10 Tournament Game",
            "remaining_time": 900.0,
            "increment": 10.0,
            "move_number": 15
        },
        {
            "name": "Bullet 1+0 Game",
            "remaining_time": 35.0,
            "increment": 0.0,
            "move_number": 25
        }
    ]
    
    for scenario in scenarios:
        move_time = calculate_move_time(
            scenario["remaining_time"],
            scenario["increment"], 
            scenario["move_number"]
        )
        
        print(f"\n{scenario['name']}:")
        print(f"  Remaining: {scenario['remaining_time']:.1f}s")
        print(f"  Move #{scenario['move_number']}")
        print(f"  Recommended time: {move_time:.2f}s")
        print(f"  Percentage of remaining: {move_time/scenario['remaining_time']*100:.1f}%")
    
    print(f"\n📊 COMPARISON WITH CURRENT SYSTEM:")
    print(f"Old system: Fixed 3-ply depth, conservative timing")
    print(f"New system: 6-ply depth, adaptive timing based on game phase")
    print(f"Expected result: Better tactics, proper time utilization")

if __name__ == "__main__":
    demonstrate_time_management()
    
    print(f"\n🔧 RECOMMENDED ENGINE SETTINGS:")
    settings = get_v13_engine_settings()
    for key, value in settings.items():
        print(f"  {key}: {value}")
