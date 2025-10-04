#!/usr/bin/env python3
"""
Upload script for PyPI
"""
import os
import subprocess
import sys

def upload_to_pypi():
    """Upload the package to PyPI"""
    print("Building the package...")
    result = subprocess.run([sys.executable, "-m", "build"], check=True)
    
    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)
    
    print("Uploading to PyPI...")
    # Using the token directly since the .pypirc file has placeholders
    # Get token from environment variable
    pypi_token = os.getenv("PYPI_API_TOKEN")
    if not pypi_token:
        print("PYPI_API_TOKEN environment variable not set!")
        sys.exit(1)
        
    result = subprocess.run([
        sys.executable, "-m", "twine", "upload", 
        "dist/*",
        "--username", "__token__",
        "--password", pypi_token
    ], check=True)
    
    if result.returncode == 0:
        print("Successfully uploaded to PyPI!")
    else:
        print("Upload to PyPI failed!")
        sys.exit(1)

if __name__ == "__main__":
    upload_to_pypi()