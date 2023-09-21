"""
Sitec __main__ Module
"""
import sys

from huti.cli.app import app

if __name__ == "__main__":
    app(args=sys.argv[1:])
