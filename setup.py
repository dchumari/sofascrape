from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sofascrape",
    version="0.1.2",
    author="Chumari",
    author_email="dchumari@gmail.com",
    description="A Python library for scraping and interacting with SofaScore APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dchumari/sofascrape.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "playwright>=1.30.0",
        "beautifulsoup4>=4.11.0",
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.0.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
        ],
    },
)