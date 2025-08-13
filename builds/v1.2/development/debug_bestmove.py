#!/usr/bin/env python3
"""
Debug test for bestmove 0000 issue
"""

import subprocess
import time

def debug_bestmove_issue():
    """Debug why engine returns bestmove 0000."""
    
    print("🔍 Debugging bestmove 0000 issue")
    print("=" * 40)
    
    # Test a simple starting position first
    test_cases = [
        ("startpos", "Starting position"),
        ("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1", "After 1.e4"),
        ("2r1q1k1/8/b2b1r1p/Pp1pNpp1/3Pn3/1RPQ3P/P1B1NPP1/4R1K1 w - - 3 28", "Puzzle position")
    ]
    
    engine_path = "../dist/Cece_v1.0.exe"
    
    for position, description in test_cases:
        print(f"\n🎯 Testing: {description}")
        print(f"Position: {position}")
        
        try:
            engine = subprocess.Popen(
                engine_path,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            # Send commands with careful timing
            commands = [
                "uci",
                "isready", 
                f"position {'startpos' if position == 'startpos' else 'fen ' + position}",
                "go depth 3"
            ]
            
            all_output = []
            
            for cmd in commands:
                print(f"SEND: {cmd}")
                if engine.stdin:
                    engine.stdin.write(f"{cmd}\n")
                    engine.stdin.flush()
                
                # Read response for this command
                if cmd == "uci":
                    # Wait for uciok
                    while True:
                        if engine.stdout:
                            line = engine.stdout.readline()
                            if line:
                                line = line.strip()
                                all_output.append(line)
                                print(f"RECV: {line}")
                                if line == "uciok":
                                    break
                elif cmd == "isready":
                    # Wait for readyok
                    while True:
                        if engine.stdout:
                            line = engine.stdout.readline()
                            if line:
                                line = line.strip()
                                all_output.append(line)
                                print(f"RECV: {line}")
                                if line == "readyok":
                                    break
                elif cmd.startswith("position"):
                    # Brief pause for position setting
                    time.sleep(0.2)
                    # Read any immediate response
                    while True:
                        if engine.stdout and engine.poll() is None:
                            try:
                                line = engine.stdout.readline()
                                if line:
                                    line = line.strip()
                                    all_output.append(line)
                                    print(f"RECV: {line}")
                                else:
                                    break
                            except:
                                break
                        else:
                            break
                elif cmd.startswith("go"):
                    # Wait for bestmove with timeout
                    start_time = time.time()
                    while time.time() - start_time < 10:  # 10 second timeout
                        if engine.stdout:
                            line = engine.stdout.readline()
                            if line:
                                line = line.strip()
                                all_output.append(line)
                                print(f"RECV: {line}")
                                if line.startswith("bestmove"):
                                    break
                        else:
                            time.sleep(0.1)
            
            # Clean up
            if engine.stdin:
                engine.stdin.write("quit\n")
                engine.stdin.flush()
            engine.wait(timeout=3)
            
            # Analysis
            print("\n📊 Analysis:")
            bestmoves = [line for line in all_output if line.startswith("bestmove")]
            if bestmoves:
                print(f"✅ Found bestmove: {bestmoves[-1]}")
            else:
                print("❌ No bestmove found")
                print("Last few lines of output:")
                for line in all_output[-5:]:
                    print(f"  {line}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    debug_bestmove_issue()
