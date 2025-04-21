import os
import sys
import subprocess
import shutil

def run_command(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def setup_fpocket():
    # Get the absolute path to the fpocket directory
    fpocket_path = os.path.abspath("fpocket")

    # Install required dependencies
    print("Installing dependencies...")
    dependencies = [
        "numpy",
        "scipy",
        "biopython"
    ]
    for dep in dependencies:
        run_command(f"pip install {dep}")

    # Create fpocket package directory
    package_dir = os.path.join(fpocket_path, "fpocket")
    os.makedirs(package_dir, exist_ok=True)

    # Create __init__.py
    init_file = os.path.join(package_dir, "__init__.py")
    with open(init_file, "w") as f:
        f.write("""# FPocket package
from .fpocket import *
""")

    # Copy Python files to the package directory
    for root, dirs, files in os.walk(fpocket_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                src = os.path.join(root, file)
                # Calculate relative path from fpocket_path
                rel_path = os.path.relpath(root, fpocket_path)
                if rel_path == ".":
                    dst = os.path.join(package_dir, file)
                else:
                    dst_dir = os.path.join(package_dir, rel_path)
                    os.makedirs(dst_dir, exist_ok=True)
                    dst = os.path.join(dst_dir, file)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
                    print(f"Copied {file} to package directory")

    # Add the fpocket directory to PYTHONPATH
    if fpocket_path not in sys.path:
        sys.path.append(fpocket_path)
        print(f"Added {fpocket_path} to Python path")

    # Test the import
    try:
        import fpocket
        print("Successfully imported fpocket")
        return True
    except Exception as e:
        print(f"Error setting up fpocket: {e}")
        return False

if __name__ == "__main__":
    setup_fpocket()

