#!/usr/bin/env python3
"""
Arena Simulation Test for Cece v1.0
Tests the exact UCI sequence that Arena uses
"""

import subprocess
import time
import threading
import os

def test_arena_sequence():
    """Test the exact UCI command sequence Arena uses."""
    
    print("🏁 Arena UCI Simulation Test")
    print("=" * 40)
    
    # Path to executable
    exe_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist", "Cece_v1.0.exe")
    
    if not os.path.exists(exe_path):
        print(f"❌ Executable not found: {exe_path}")
        return False
    
    print(f"🎯 Testing: {exe_path}")
    
    try:
        # Start engine process
        engine = subprocess.Popen(
            exe_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Track all output
        output_lines = []
        
        def read_output():
            """Read engine output continuously."""
            try:
                while engine.poll() is None:
                    if engine.stdout:
                        line = engine.stdout.readline()
                        if line:
                            line = line.strip()
                            output_lines.append(line)
                            print(f"ENGINE: {line}")
            except:
                pass
        
        # Start output reader
        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()
        
        def send_command(cmd: str, wait_time: float = 1.0):
            """Send command and wait for response."""
            print(f"\n📤 SENDING: {cmd}")
            if engine.stdin:
                engine.stdin.write(f"{cmd}\n")
                engine.stdin.flush()
            time.sleep(wait_time)
        
        # Simulate Arena's exact UCI sequence
        print("\n🔄 Starting Arena UCI sequence...")
        
        # 1. Initialize UCI
        send_command("uci", 2.0)
        
        # 2. Check if ready
        send_command("isready", 1.0)
        
        # 3. Start new game
        send_command("ucinewgame", 1.0)
        
        # 4. Set position
        send_command("position startpos", 0.5)
        
        # 5. Request move with various time controls
        print("\n🕐 Testing different time controls...")
        
        # Test 1: Depth-based search
        send_command("go depth 5", 5.0)
        
        # Test 2: Time-based search  
        send_command("position startpos moves e2e4", 0.5)
        send_command("go movetime 2000", 3.0)
        
        # Test 3: Tournament time control
        send_command("position startpos", 0.5)
        send_command("go wtime 300000 btime 300000 winc 5000 binc 5000", 3.0)
        
        # Test 4: Infinite search then stop
        send_command("position startpos moves e2e4 e7e5", 0.5)
        send_command("go infinite", 1.0)
        send_command("stop", 2.0)
        
        # Quit
        send_command("quit", 1.0)
        
        # Wait for engine to exit
        engine.wait(timeout=5)
        
        print("\n📊 Analysis of UCI responses:")
        print("=" * 40)
        
        # Check for required UCI responses
        has_uciok = any("uciok" in line for line in output_lines)
        has_readyok = any("readyok" in line for line in output_lines)
        has_bestmove = any("bestmove" in line for line in output_lines)
        has_id_name = any("id name" in line for line in output_lines)
        
        print(f"✅ UCI OK response: {'YES' if has_uciok else 'NO'}")
        print(f"✅ Ready OK response: {'YES' if has_readyok else 'NO'}")
        print(f"✅ ID Name provided: {'YES' if has_id_name else 'NO'}")
        print(f"✅ Best move provided: {'YES' if has_bestmove else 'NO'}")
        
        # Count bestmove responses
        bestmove_count = sum(1 for line in output_lines if "bestmove" in line)
        print(f"🎯 Total bestmove responses: {bestmove_count}")
        
        if bestmove_count == 0:
            print("\n❌ PROBLEM: Engine not providing bestmove responses!")
            print("   This is why Arena shows 'engine not responding'")
        else:
            print(f"\n✅ SUCCESS: Engine provided {bestmove_count} moves")
        
        # Show all bestmove lines
        print("\n🎯 Bestmove responses:")
        for line in output_lines:
            if "bestmove" in line:
                print(f"   {line}")
        
        return bestmove_count > 0
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_arena_sequence()
    if success:
        print("\n🎉 Arena simulation test PASSED!")
        print("   Engine should work in Arena")
    else:
        print("\n💥 Arena simulation test FAILED!")
        print("   Engine needs debugging for Arena compatibility")
