#!/usr/bin/env python3
"""
Upload script for TestPyPI
"""
import os
import subprocess
import sys

def upload_to_testpypi():
    """Upload the package to TestPyPI"""
    print("Building the package...")
    result = subprocess.run([sys.executable, "-m", "build"], check=True)
    
    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)
    
    print("Uploading to TestPyPI...")
    # Using the token directly since the .pypirc file has placeholders
    # Get token from environment variable
    testpypi_token = os.getenv("TESTPYPI_API_TOKEN")
    if not testpypi_token:
        print("TESTPYPI_API_TOKEN environment variable not set!")
        sys.exit(1)
        
    result = subprocess.run([
        sys.executable, "-m", "twine", "upload", 
        "--repository", "testpypi", 
        "dist/*",
        "--username", "__token__",
        "--password", testpypi_token
    ], check=True)
    
    if result.returncode == 0:
        print("Successfully uploaded to TestPyPI!")
    else:
        print("Upload to TestPyPI failed!")
        sys.exit(1)

if __name__ == "__main__":
    upload_to_testpypi()