#!/usr/bin/env python3
"""
Production-ready upload script for Sofascrape
"""
import os
import subprocess
import sys
import shutil
import platform

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
    return True

def upload_to_testpypi():
    """Upload the package to TestPyPI"""
    print("Looking for TestPyPI token...")
    testpypi_token = os.getenv("TESTPYPI_API_TOKEN")
    if not testpypi_token:
        print("ERROR: TESTPYPI_API_TOKEN environment variable not set!")
        print("Please set it before running this script:")
        if platform.system() == "Windows":
            print("In Command Prompt: set TESTPYPI_API_TOKEN=your_token_here")
            print("In PowerShell: $env:TESTPYPI_API_TOKEN=\"your_token_here\"")
        else:
            print("export TESTPYPI_API_TOKEN=your_token_here")
        return False
        
    print("Uploading to TestPyPI...")
    result = subprocess.run([
        sys.executable, "-m", "twine", "upload", 
        "--repository", "testpypi", 
        "dist/*",
        "--username", "__token__",
        "--password", testpypi_token
    ])
    
    if result.returncode == 0:
        print("✓ Successfully uploaded to TestPyPI!")
        print("You can view your package at: https://test.pypi.org/project/sofascrape/")
    else:
        print("✗ Upload to TestPyPI failed!")
        return False
    return True

def upload_to_pypi():
    """Upload the package to PyPI"""
    print("Looking for PyPI token...")
    pypi_token = os.getenv("PYPI_API_TOKEN")
    if not pypi_token:
        print("ERROR: PYPI_API_TOKEN environment variable not set!")
        print("Please set it before running this script:")
        if platform.system() == "Windows":
            print("In Command Prompt: set PYPI_API_TOKEN=your_token_here")
            print("In PowerShell: $env:PYPI_API_TOKEN=\"your_token_here\"")
        else:
            print("export PYPI_API_TOKEN=your_token_here")
        return False
        
    print("Uploading to PyPI...")
    result = subprocess.run([
        sys.executable, "-m", "twine", "upload", 
        "dist/*",
        "--username", "__token__",
        "--password", pypi_token
    ])
    
    if result.returncode == 0:
        print("✓ Successfully uploaded to PyPI!")
        print("You can view your package at: https://pypi.org/project/sofascrape/")
    else:
        print("✗ Upload to PyPI failed!")
        return False
    return True

def main():
    """Main function to handle the complete upload process"""
    print("🚀 Sofascrape Production Upload Script")
    print("="*50)
    
    # Clean previous builds
    clean_dist()
    
    # Build the package
    if not build_package():
        print("Build failed, exiting...")
        sys.exit(1)
    
    # Ask user which upload they want to perform
    print("\nChoose upload option:")
    print("1. Upload to TestPyPI only")
    print("2. Upload to PyPI only") 
    print("3. Upload to both (TestPyPI first, then PyPI)")
    print("4. Just build (no upload)")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    
    success = False
    
    if choice == "1":
        print("\n📦 Uploading to TestPyPI...")
        success = upload_to_testpypi()
        if success:
            print("\n✅ TestPyPI upload completed successfully!")
        else:
            print("\n❌ TestPyPI upload failed!")
            sys.exit(1)
    elif choice == "2":
        print("\n📦 Uploading to PyPI...")
        success = upload_to_pypi()
        if success:
            print("\n✅ PyPI upload completed successfully!")
        else:
            print("\n❌ PyPI upload failed!")
            sys.exit(1)
    elif choice == "3":
        print("\n📦 First uploading to TestPyPI...")
        success = upload_to_testpypi()
        if success:
            print("✅ TestPyPI upload completed successfully!")
            print("\n📦 Now uploading to PyPI...")
            success = upload_to_pypi()
            if success:
                print("✅ PyPI upload completed successfully!")
                print("\n🎉 Both uploads completed successfully!")
            else:
                print("❌ PyPI upload failed!")
                sys.exit(1)
        else:
            print("❌ TestPyPI upload failed!")
            sys.exit(1)
    elif choice == "4":
        print("\n✅ Package built successfully. No uploads performed.")
        print("The built package is in the 'dist' folder.")
    else:
        print("❌ Invalid choice. Please run again and select 1-4.")
        sys.exit(1)

if __name__ == "__main__":
    main()