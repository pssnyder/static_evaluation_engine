#!/usr/bin/env python3
"""
Time Control Debug Test
Tests specifically why engine doesn't respond to wtime/btime commands
"""

import subprocess
import threading
import time
import os

def test_time_controls():
    """Test time control handling specifically."""
    
    print("⏰ Time Control Debug Test")
    print("=" * 30)
    
    exe_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist", "Cece_v1.0.exe")
    
    try:
        engine = subprocess.Popen(
            exe_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        responses = []
        
        def read_output():
            while engine.poll() is None:
                if engine.stdout:
                    line = engine.stdout.readline()
                    if line:
                        line = line.strip()
                        responses.append(line)
                        print(f"ENGINE: {line}")
        
        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()
        
        def send_cmd(cmd, wait=1.0):
            print(f"SEND: {cmd}")
            if engine.stdin:
                engine.stdin.write(f"{cmd}\n")
                engine.stdin.flush()
            time.sleep(wait)
        
        # Initialize
        send_cmd("uci", 2)
        send_cmd("isready", 1)
        send_cmd("ucinewgame", 1)
        send_cmd("position startpos", 0.5)
        
        # Test different time controls
        print("\n=== Testing Time Controls ===")
        
        # Test 1: Very long time control (should work)
        print("\n1. Testing long time control (5 minutes each):")
        send_cmd("go wtime 300000 btime 300000", 8)
        
        # Test 2: Short time control
        print("\n2. Testing short time control (30 seconds each):")
        send_cmd("position startpos moves e2e4", 0.5)
        send_cmd("go wtime 30000 btime 30000", 5)
        
        # Test 3: With increment
        print("\n3. Testing with increment:")
        send_cmd("position startpos", 0.5)
        send_cmd("go wtime 60000 btime 60000 winc 1000 binc 1000", 5)
        
        send_cmd("quit", 1)
        engine.wait(timeout=5)
        
        # Analysis
        print("\n=== Analysis ===")
        bestmove_count = sum(1 for r in responses if "bestmove" in r)
        search_count = sum(1 for r in responses if "Searching" in r)
        
        print(f"Search attempts: {search_count}")
        print(f"Bestmove responses: {bestmove_count}")
        
        if bestmove_count < 3:
            print("❌ PROBLEM: Missing bestmove responses for time controls")
            print("   Arena needs bestmove for every 'go' command")
        else:
            print("✅ All time controls working")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_time_controls()
