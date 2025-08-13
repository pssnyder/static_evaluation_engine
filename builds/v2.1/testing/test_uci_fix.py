#!/usr/bin/env python3
"""
Quick test to verify UCI bug fix for Cece v2.1

This test simulates the basic UCI commands to verify the engine
now returns proper move format instead of "bestmove 0000".
"""

import subprocess
import sys
import time
from pathlib import Path

def test_uci_communication():
    """Test basic UCI communication with the fixed engine."""
    
    exe_path = Path("../dist/Cece_v2.1.exe")
    if not exe_path.exists():
        print(f"Error: {exe_path} not found!")
        return False
    
    print("Testing UCI communication with Cece v2.1...")
    print("=" * 50)
    
    # Start the engine
    process = subprocess.Popen(
        [str(exe_path)], 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    def send_command(cmd):
        print(f">>> {cmd}")
        process.stdin.write(cmd + "\n")
        process.stdin.flush()
    
    def read_response(timeout=5):
        responses = []
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if process.stdout.readable():
                line = process.stdout.readline()
                if line:
                    line = line.strip()
                    print(f"<<< {line}")
                    responses.append(line)
                    if line.startswith("bestmove"):
                        break
            time.sleep(0.01)
        
        return responses
    
    try:
        # Test basic UCI handshake
        send_command("uci")
        responses = read_response()
        
        if not any("uciok" in r for r in responses):
            print("❌ UCI handshake failed")
            return False
        print("✅ UCI handshake successful")
        
        # Test isready
        send_command("isready")
        responses = read_response()
        
        if not any("readyok" in r for r in responses):
            print("❌ Engine not ready")
            return False
        print("✅ Engine ready")
        
        # Test position and search
        send_command("position startpos")
        send_command("go depth 3")
        
        responses = read_response(timeout=10)
        
        # Check for proper bestmove format
        bestmove_found = False
        for response in responses:
            if response.startswith("bestmove"):
                bestmove_found = True
                # Should not be "bestmove 0000" for starting position
                if "bestmove 0000" in response:
                    print(f"❌ Engine returned null move: {response}")
                    return False
                else:
                    print(f"✅ Engine returned valid move: {response}")
                    # Verify move format (should be like e2e4, g1f3, etc.)
                    move = response.split()[1]
                    if len(move) == 4 and move[0] in 'abcdefgh' and move[1] in '12345678':
                        print(f"✅ Move format is valid UCI: {move}")
                        return True
                    else:
                        print(f"❌ Invalid move format: {move}")
                        return False
        
        if not bestmove_found:
            print("❌ No bestmove response received")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        send_command("quit")
        process.terminate()
        process.wait(timeout=5)
    
    return False

if __name__ == "__main__":
    success = test_uci_communication()
    if success:
        print("\n🎉 UCI bug fix successful! Engine now returns proper moves.")
    else:
        print("\n💥 UCI communication still has issues.")
    
    sys.exit(0 if success else 1)
