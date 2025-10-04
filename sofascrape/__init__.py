"""
Sofascrape - A Python library for scraping and interacting with SofaScore APIs
"""

from .client import SofascrapeClient
from .models import FormatOptions

__version__ = "0.1.0"
__author__ = "Chumari"
__email__ = "dchumari@gmail.com"

__all__ = ["SofascrapeClient", "FormatOptions"]