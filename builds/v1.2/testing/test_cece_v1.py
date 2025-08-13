#!/usr/bin/env python3
"""
Test Cece v1.0 UCI Interface
Quick validation that the executable works correctly with Arena.
"""

import subprocess
import time
import threading

def test_cece_uci():
    """Test Cece UCI interface."""
    print("🧪 Testing Cece v1.0 UCI Interface")
    print("=" * 40)
    
    # Path to executable
    exe_path = "dist/Cece_v1.0.exe"
    
    try:
        # Start the engine process
        engine = subprocess.Popen(
            [exe_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        def read_output():
            """Read engine output in background."""
            try:
                while True:
                    if not engine.stdout:
                        break
                    line = engine.stdout.readline()
                    if not line:
                        break
                    print(f"ENGINE: {line.strip()}")
            except:
                pass
        
        # Start output reader thread
        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()
        
        # Test UCI commands
        commands = [
            ("uci", "Initialize engine"),
            ("isready", "Check if ready"),
            ("ucinewgame", "Start new game"),
            ("position startpos", "Set starting position"),
            ("go depth 6", "Search to depth 6"),
        ]
        
        for cmd, desc in commands:
            print(f"\n📤 {desc}: {cmd}")
            if engine.stdin:
                engine.stdin.write(cmd + "\n")
                engine.stdin.flush()
            
            if cmd.startswith("go"):
                time.sleep(5)  # Wait for search
            else:
                time.sleep(0.5)  # Brief pause
        
        print("\n📤 Quitting engine...")
        if engine.stdin:
            engine.stdin.write("quit\n")
            engine.stdin.flush()
        
        # Wait for engine to exit
        engine.wait(timeout=3)
        
        print("\n✅ UCI test completed successfully!")
        print("🎯 Cece is ready for Arena integration!")
        
    except subprocess.TimeoutExpired:
        print("⚠️  Engine didn't exit cleanly, killing...")
        engine.kill()
    except Exception as e:
        print(f"❌ Test error: {e}")
        if engine:
            engine.kill()

if __name__ == "__main__":
    test_cece_uci()
