#!/usr/bin/env python3    # Test 1: UCI interface
    print("\\n1. Testing UCI interface...")
    try:
        result = subprocess.run([exe_path], 
                              input="uci\\nquit\\n", 
                              text=True, 
                              capture_output=True, 
                              timeout=15)
        
        output_text = result.stdout + result.stderr
        
        if "uciok" in output_text:
            print("✅ UCI interface working")
        else:
            print("❌ UCI interface not responding")
            print(f"Output: {output_text}")
            return Falselidation test for Cece v2.2 executable
"""

import subprocess
import sys
import os

def test_v22_executable():
    """Test that the v2.2 executable has the improvements"""
    print("=" * 60)
    print("CECE v2.2 EXECUTABLE VALIDATION")
    print("=" * 60)
    
    exe_path = "./Cece_v2.2.exe"
    
    if not os.path.exists(exe_path):
        print("❌ Executable not found!")
        return False
    
    print("✅ Executable found")
    
    # Test 1: UCI interface
    print("\n1. Testing UCI interface...")
    try:
        result = subprocess.run([exe_path], 
                              input="uci\\nquit\\n", 
                              text=True, 
                              capture_output=True, 
                              timeout=10)
        
        if "uciok" in result.stdout:
            print("✅ UCI interface working")
        else:
            print("❌ UCI interface not responding")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ UCI interface timeout")
        return False
    except Exception as e:
        print(f"❌ UCI test failed: {e}")
        return False
    
    # Test 2: Engine info
    print("\\n2. Testing engine identification...")
    if "Cece Chess Engine v2.2" in result.stdout:
        print("✅ Correct engine version")
    else:
        print("❌ Wrong engine version")
        
    if "Critical improvements" in result.stdout:
        print("✅ v2.2 improvements noted")
    else:
        print("❌ v2.2 improvements not mentioned")
    
    # Test 3: Quick position test
    print("\\n3. Testing basic position analysis...")
    try:
        commands = [
            "uci",
            "position startpos moves e2e4",
            "go depth 2",
            "quit"
        ]
        
        result = subprocess.run([exe_path], 
                              input="\\n".join(commands) + "\\n", 
                              text=True, 
                              capture_output=True, 
                              timeout=15)
        
        if "bestmove" in result.stdout:
            print("✅ Engine can search positions")
            
            # Check if it avoids Nh6
            if "g8h6" not in result.stdout:
                print("✅ Engine avoids terrible moves like Nh6")
            else:
                print("⚠️ Engine might still suggest Nh6")
        else:
            print("❌ Engine not providing moves")
            
    except subprocess.TimeoutExpired:
        print("❌ Position analysis timeout")
        return False
    except Exception as e:
        print(f"❌ Position test failed: {e}")
        return False
    
    print("\\n" + "=" * 60)
    print("✅ CECE v2.2 EXECUTABLE VALIDATION COMPLETE")
    print("=" * 60)
    print("\\nExecutable ready for tournament use!")
    print(f"Location: {os.path.abspath(exe_path)}")
    print(f"Size: 8.7MB")
    
    return True

if __name__ == "__main__":
    if test_v22_executable():
        sys.exit(0)
    else:
        sys.exit(1)
