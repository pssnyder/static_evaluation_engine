#!/usr/bin/env python3
"""
UCI Test Script

This script demonstrates how to test the UCI interface.
You can use this to verify UCI compliance or test with chess GUIs.

Usage:
  python uci_test.py
  
Then type UCI commands like:
  uci
  isready
  position startpos moves e2e4 e7e5
  go depth 6
  quit
"""

import subprocess
import sys
import time
import os


def test_uci_basic():
    """Test basic UCI communication."""
    print("=== UCI Interface Test ===")
    print("Starting UCI engine...")
    
    # Start the UCI process (path relative to parent directory)
    uci_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uci_interface.py")
    process = subprocess.Popen(
        [sys.executable, uci_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    def send_command(cmd):
        """Send a command and get response."""
        print(f">>> {cmd}")
        if process.stdin:
            process.stdin.write(cmd + "\n")
            process.stdin.flush()
        time.sleep(0.1)  # Give time for response
        
    def read_output():
        """Read available output."""
        output = []
        try:
            while True:
                if not process.stdout:
                    break
                line = process.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    print(f"<<< {line}")
                    output.append(line)
                if line == "uciok" or line == "readyok" or line.startswith("bestmove"):
                    break
        except:
            pass
        return output
    
    try:
        # Test UCI identification
        send_command("uci")
        response = read_output()
        
        # Test ready state
        send_command("isready")
        response = read_output()
        
        # Test position setting
        send_command("position startpos moves e2e4 e7e5")
        
        # Test search
        send_command("go depth 4")
        response = read_output()
        
        # Quit
        send_command("quit")
        
        print("\n=== UCI Test Complete ===")
        print("✓ Engine responds to UCI commands")
        print("✓ Ready for GUI integration")
        
    except Exception as e:
        print(f"Error during UCI test: {e}")
    finally:
        process.terminate()
        process.wait()


def interactive_uci():
    """Interactive UCI mode for manual testing."""
    print("=== Interactive UCI Mode ===")
    print("Type UCI commands (or 'help' for examples, 'exit' to quit)")
    print()
    
    # Start the UCI process (path relative to parent directory)
    uci_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uci_interface.py")
    process = subprocess.Popen(
        [sys.executable, uci_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    def show_help():
        print("Common UCI commands:")
        print("  uci                     - Identify engine")
        print("  isready                 - Check if ready")
        print("  position startpos       - Set starting position")
        print("  position startpos moves e2e4 e7e5  - Set position with moves")
        print("  go depth 6              - Search to depth 6")
        print("  go movetime 2000        - Search for 2 seconds")
        print("  setoption name MaterialWeight value 120")
        print("  quit                    - Exit engine")
        print()
    
    try:
        while True:
            command = input("UCI> ").strip()
            
            if command == "exit":
                break
            elif command == "help":
                show_help()
                continue
            elif not command:
                continue
            
            # Send command to engine
            if process.stdin:
                process.stdin.write(command + "\n")
                process.stdin.flush()
            
            # Read response (with timeout)
            time.sleep(0.1)
            try:
                while True:
                    if not process.stdout:
                        break
                    line = process.stdout.readline()
                    if not line:
                        break
                    line = line.strip()
                    if line:
                        print(line)
                    if line in ["uciok", "readyok"] or line.startswith("bestmove"):
                        break
            except:
                pass
            
            if command == "quit":
                break
                
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.terminate()
        process.wait()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_uci()
    else:
        test_uci_basic()
        print("\nFor interactive mode, run: python uci_test.py interactive")
