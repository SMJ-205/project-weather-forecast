import subprocess
import sys
import os
from datetime import datetime

# Move to the project root directory
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Helper script to run the full ETL pipeline sequentially."""
    print(f"--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
    print("🚀 Starting WeatherDataOps Pipeline...")
    
    scripts = [
        "scripts/extract.py",
        "scripts/transform.py",
        "scripts/load.py",
        "scripts/cleanup.py"
    ]
    
    try:
        for script in scripts:
            print(f"Running {script}...")
            # Use the current Python executable to ensure compatibility
            subprocess.run([sys.executable, script], check=True)
            
        print("✅ Pipeline completed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Pipeline failed at {e.cmd}: Exit code {e.returncode}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
