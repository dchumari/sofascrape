#!/usr/bin/env python3
"""
Comprehensive upload script for Sofascrape
"""
import os
import subprocess
import sys
import shutil

def clean_dist():
    """Clean the dist directory"""
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("Cleaned dist directory")

def build_package():
    """Build the package"""
    print("Building the package...")
    result = subprocess.run([sys.executable, "-m", "build"], check=True)
    
    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)
    
    print("Package built successfully!")

def upload_to_testpypi():
    """Upload the package to TestPyPI"""
    print("Uploading to TestPyPI...")
    # Get token from environment variable
    testpypi_token = os.getenv("TESTPYPI_API_TOKEN")
    if not testpypi_token:
        print("TESTPYPI_API_TOKEN environment variable not set!")
        return False
        
    result = subprocess.run([
        sys.executable, "-m", "twine", "upload", 
        "--repository", "testpypi", 
        "dist/*",
        "--username", "__token__",
        "--password", testpypi_token
    ])
    
    if result.returncode == 0:
        print("Successfully uploaded to TestPyPI!")
    else:
        print("Upload to TestPyPI failed!")
        return False
    return True

def upload_to_pypi():
    """Upload the package to PyPI"""
    print("Uploading to PyPI...")
    # Get token from environment variable
    pypi_token = os.getenv("PYPI_API_TOKEN")
    if not pypi_token:
        print("PYPI_API_TOKEN environment variable not set!")
        return False
        
    result = subprocess.run([
        sys.executable, "-m", "twine", "upload", 
        "dist/*",
        "--username", "__token__",
        "--password", pypi_token
    ])
    
    if result.returncode == 0:
        print("Successfully uploaded to PyPI!")
    else:
        print("Upload to PyPI failed!")
        return False
    return True

def main():
    """Main function to handle the complete upload process"""
    print("Starting Sofascrape upload process...")
    
    # Clean previous builds
    clean_dist()
    
    # Build the package
    build_package()
    
    # Ask user which upload they want to perform
    print("\nChoose upload option:")
    print("1. Upload to TestPyPI only")
    print("2. Upload to PyPI only") 
    print("3. Upload to both (TestPyPI first)")
    print("4. Just build (no upload)")
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == "1":
        success = upload_to_testpypi()
        if success:
            print("\nTestPyPI upload completed successfully!")
        else:
            print("\nTestPyPI upload failed!")
            sys.exit(1)
    elif choice == "2":
        success = upload_to_pypi()
        if success:
            print("\nPyPI upload completed successfully!")
        else:
            print("\nPyPI upload failed!")
            sys.exit(1)
    elif choice == "3":
        # First upload to TestPyPI
        success = upload_to_testpypi()
        if success:
            print("\nTestPyPI upload completed successfully!")
            print("Now uploading to PyPI...")
            success = upload_to_pypi()
            if success:
                print("\nPyPI upload completed successfully!")
            else:
                print("\nPyPI upload failed!")
                sys.exit(1)
        else:
            print("\nTestPyPI upload failed!")
            sys.exit(1)
    elif choice == "4":
        print("\nPackage built successfully. No uploads performed.")
    else:
        print("Invalid choice. Please run again and select 1-4.")
        sys.exit(1)

if __name__ == "__main__":
    main()