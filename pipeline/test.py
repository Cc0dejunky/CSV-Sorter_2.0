import subprocess
import time
import os
import sys

def start_system():
    # 1. FIND THE API FILE
    # We'll check common names. Update these if yours is different!
    api_filenames = ["api_server.py", "api.py", "server.py"]
    api_path = None
    
    for name in api_filenames:
        if os.path.exists(name):
            api_path = name
            break
            
    if not api_path:
        print("❌ ERROR: Could not find your API script (api_server.py, etc.)")
        print("Check your folder and rename the file or update test.py.")
        return

    print(f"🚀 Starting System (using {api_path})...")

    # 2. START API
    # We use 'python' instead of 'sys.executable' for better compatibility in Bash
    api_process = subprocess.Popen(["python", api_path])

    # 3. WAIT AND CHECK PORT
    print("⏳ Giving the API 5 seconds to open Port 8000...")
    time.sleep(5)

    # 4. START TUI
    print("🖥️ Launching Review Tool...")
    try:
        # We run this in a way that stays open
        subprocess.run(["python", "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Manual Exit detected.")
    finally:
        print("🛑 Cleaning up background processes...")
        api_process.terminate()

if __name__ == "__main__":
    start_system()