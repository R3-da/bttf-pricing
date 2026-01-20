import sys
import os

# Add current directory to path so src can be found
sys.path.insert(0, os.getcwd())

try:
    from src.main import app
    print("Import successful")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
