#!/usr/bin/env python3
"""
Quick UCI validation test for the fixed engine
"""

import subprocess
import time

def quick_uci_test():
    """Quick test of UCI commands."""
    print("🚀 Quick UCI Test")
    print("=" * 20)
    
    exe_path = "../Cece_v1.0.exe"
    
    try:
        engine = subprocess.Popen(
            exe_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send test sequence
        commands = [
            "uci",
            "isready",
            "position startpos",
            "go depth 3",
            "position startpos moves e2e4",
            "go wtime 60000 btime 60000",
            "quit"
        ]
        
        input_text = "\n".join(commands) + "\n"
        stdout, stderr = engine.communicate(input=input_text, timeout=30)
        
        print("=== ENGINE OUTPUT ===")
        print(stdout)
        
        # Check for bestmove responses
        bestmoves = stdout.count("bestmove")
        print(f"\n✅ Found {bestmoves} bestmove responses")
        
        if bestmoves >= 2:
            print("🎉 UCI test PASSED!")
            return True
        else:
            print("❌ UCI test FAILED - missing bestmoves")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    quick_uci_test()
