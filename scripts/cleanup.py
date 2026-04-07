import os
import glob

# Paths
DATA_PATHS = ["data/raw", "data/processed"]

def cleanup_old_files(directory, keep_n=1):
    """Deletes all but the N most recent files in a directory."""
    files = glob.glob(os.path.join(directory, "*.csv"))
    if not files:
        return
        
    # Sort by creation time (most recent first)
    files.sort(key=os.path.getctime, reverse=True)
    
    # Identify files to delete
    to_delete = files[keep_n:]
    
    for file_path in to_delete:
        try:
            os.remove(file_path)
            print(f"🗑️ Deleted old file: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"❌ Error deleting {file_path}: {e}")

def main():
    print("🧹 Starting local storage cleanup...")
    for path in DATA_PATHS:
        if os.path.exists(path):
            cleanup_old_files(path)
    print("✨ Cleanup complete.")

if __name__ == "__main__":
    main()
