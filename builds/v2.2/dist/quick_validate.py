import subprocess
import sys
import os

exe_path = "./Cece_v2.2.exe"
if not os.path.exists(exe_path):
    print("ERROR: Executable not found")
    sys.exit(1)

try:
    result = subprocess.run([exe_path], input="uci\nquit\n", text=True, capture_output=True, timeout=5)
    if "uciok" in result.stdout:
        print("SUCCESS: Cece v2.2 executable is working!")
        print("Output:", result.stdout[:200])
        sys.exit(0)
    else:
        print("ERROR: No UCI response")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
