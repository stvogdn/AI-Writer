"""Development setup script for AI Writer."""

import subprocess
import sys


def run_command(command: list[str], description: str) -> bool:
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def main():
    """Set up development environment."""
    print("🚀 Setting up AI Writer development environment")

    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and sys.base_prefix == sys.prefix:
        print("⚠️  Warning: Not in a virtual environment")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("Exiting. Please create and activate a virtual environment first.")
            return

    # Install development dependencies
    success = run_command(
        ["uv", "sync", "--dev"],
        "Installing development dependencies with uv"
    )
    if not success:
        return

    # Install pre-commit hooks
    success = run_command(
        ["pre-commit", "install"],
        "Installing pre-commit hooks"
    )
    if not success:
        return

    # Run initial checks
    print("\n🔍 Running initial code quality checks...")

    # Run black
    run_command(
        ["uv", "run", "black", "src/", "tests/", "scripts/"],
        "Formatting code with black"
    )

    # Run ruff
    run_command(
        ["uv", "run", "ruff", "check", "src/", "tests/", "--fix"],
        "Linting code with ruff"
    )

    # Run mypy
    run_command(
        ["uv", "run", "mypy", "src/ai_writer/"],
        "Type checking with mypy"
    )

    # Run tests
    run_command(
        ["uv", "run", "pytest", "tests/", "-v"],
        "Running test suite"
    )

    print("\n🎉 Development environment setup complete!")
    print("\n📋 Available commands:")
    print("   • uv run pytest                  - Run tests")
    print("   • uv run black .                 - Format code")
    print("   • uv run ruff check .            - Lint code")
    print("   • uv run mypy src/ai_writer/     - Type check code")
    print("   • uv run pre-commit run --all-files  - Run all checks")
    print("   • uv run ai-writer               - Run application")


if __name__ == "__main__":
    main()
