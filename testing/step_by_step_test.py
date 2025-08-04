#!/usr/bin/env python3
"""
Simple step-by-step UCI test
"""

import subprocess
import time

def step_by_step_test():
    """Test UCI commands one by one."""
    
    print("🔍 Step-by-step UCI test")
    print("=" * 30)
    
    engine_path = "../dist/Cece_v1.0.exe"
    
    try:
        engine = subprocess.Popen(
            engine_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        def send_and_wait(command, wait_for=None, timeout=5):
            """Send command and wait for specific response."""
            print(f"\n📤 SEND: {command}")
            if engine.stdin:
                engine.stdin.write(f"{command}\n")
                engine.stdin.flush()
            
            start_time = time.time()
            responses = []
            
            while time.time() - start_time < timeout:
                if engine.stdout:
                    line = engine.stdout.readline()
                    if line:
                        line = line.strip()
                        responses.append(line)
                        print(f"📥 RECV: {line}")
                        
                        if wait_for and line == wait_for:
                            print(f"✅ Got expected response: {wait_for}")
                            return True, responses
                        elif line.startswith("bestmove"):
                            print(f"✅ Got bestmove: {line}")
                            return True, responses
                else:
                    time.sleep(0.1)
            
            print(f"⏰ Timeout waiting for response")
            return False, responses
        
        # Test sequence
        print("\n=== UCI Initialization ===")
        success, _ = send_and_wait("uci", "uciok", 3)
        if not success:
            print("❌ UCI failed")
            return False
        
        print("\n=== Ready Check ===")
        success, _ = send_and_wait("isready", "readyok", 3)
        if not success:
            print("❌ isready failed")
            return False
        
        print("\n=== Position Setting ===")
        success, _ = send_and_wait("position startpos", None, 2)
        print("Position command sent, no specific response expected")
        
        print("\n=== Search Test (depth 3) ===")
        success, _ = send_and_wait("go depth 3", None, 10)
        if not success:
            print("❌ Search failed - no bestmove received")
        
        print("\n=== Cleanup ===")
        if engine.stdin:
            engine.stdin.write("quit\n")
            engine.stdin.flush()
        
        engine.wait(timeout=3)
        print("✅ Engine terminated")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    step_by_step_test()
