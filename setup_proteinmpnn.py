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

def setup_proteinmpnn():
    # Get the absolute path to the ProteinMPNN directory
    proteinmpnn_path = os.path.abspath("ProteinMPNN")

    # Install required dependencies
    print("Installing dependencies...")
    dependencies = [
        "torch",
        "numpy",
        "scipy",
        "biopython",
        "pandas",
        "tqdm"
    ]
    for dep in dependencies:
        run_command(f"pip install {dep}")

    # Create protein_mpnn package directory
    package_dir = os.path.join(proteinmpnn_path, "protein_mpnn")
    os.makedirs(package_dir, exist_ok=True)

    # Create __init__.py
    init_file = os.path.join(package_dir, "__init__.py")
    with open(init_file, "w") as f:
        f.write("""# ProteinMPNN package
from .protein_mpnn_run import *
from .protein_mpnn_utils import *
""")

    # Copy the main Python files to the package directory
    main_files = ["protein_mpnn_run.py", "protein_mpnn_utils.py"]
    for file in main_files:
        src = os.path.join(proteinmpnn_path, file)
        dst = os.path.join(package_dir, file)
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"Copied {file} to package directory")

    # Add the ProteinMPNN directory to PYTHONPATH
    if proteinmpnn_path not in sys.path:
        sys.path.append(proteinmpnn_path)
        print(f"Added {proteinmpnn_path} to Python path")

    # Test the import
    try:
        import protein_mpnn
        print("Successfully imported protein_mpnn")
        return True
    except Exception as e:
        print(f"Error setting up protein_mpnn: {e}")
        return False

if __name__ == "__main__":
    setup_proteinmpnn()

