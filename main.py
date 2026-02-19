"""DEPRECATED: Use 'ai-writer' command or 'python -m ai_writer.main' instead.

This file exists for backward compatibility only.
"""

import sys
import warnings

def main():
    """Deprecated entry point with migration warning."""
    warnings.warn(
        "Using main.py directly is deprecated. "
        "Use 'ai-writer' command or 'python -m ai_writer.main' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    try:
        from ai_writer.main import main as new_main
        return new_main()
    except ImportError:
        print("ERROR: AI Writer package not installed properly.")
        print("Please install with: pip install -e .")
        return 1

if __name__ == "__main__":
    sys.exit(main())
