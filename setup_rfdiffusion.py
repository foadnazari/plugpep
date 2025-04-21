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

def setup_rfdiffusion():
    # Get the absolute path to the RFdiffusion directory
    rfdiffusion_path = os.path.abspath("RFdiffusion")

    # Install required dependencies
    print("Installing dependencies...")
    dependencies = [
        "torch",
        "numpy",
        "scipy",
        "biopython",
        "pandas",
        "tqdm",
        "e3nn",
        "pytorch3d",
        "sidechainnet"
    ]
    for dep in dependencies:
        run_command(f"pip install {dep}")

    # Create rfdiffusion package directory
    package_dir = os.path.join(rfdiffusion_path, "rfdiffusion")
    os.makedirs(package_dir, exist_ok=True)

    # Create __init__.py
    init_file = os.path.join(package_dir, "__init__.py")
    with open(init_file, "w") as f:
        f.write("""# RFdiffusion package
from .inference import *
from .utils import *
""")

    # Copy Python files to the package directory
    for root, dirs, files in os.walk(rfdiffusion_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                src = os.path.join(root, file)
                # Calculate relative path from rfdiffusion_path
                rel_path = os.path.relpath(root, rfdiffusion_path)
                if rel_path == ".":
                    dst = os.path.join(package_dir, file)
                else:
                    dst_dir = os.path.join(package_dir, rel_path)
                    os.makedirs(dst_dir, exist_ok=True)
                    dst = os.path.join(dst_dir, file)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
                    print(f"Copied {file} to package directory")

    # Add the RFdiffusion directory to PYTHONPATH
    if rfdiffusion_path not in sys.path:
        sys.path.append(rfdiffusion_path)
        print(f"Added {rfdiffusion_path} to Python path")

    # Test the import
    try:
        import rfdiffusion
        print("Successfully imported rfdiffusion")
        return True
    except Exception as e:
        print(f"Error setting up rfdiffusion: {e}")
        return False

if __name__ == "__main__":
    setup_rfdiffusion()
