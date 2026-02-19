"""Build script for AI Writer."""

import shutil
import subprocess
from pathlib import Path


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


def clean_build_dirs():
    """Clean up build directories."""
    dirs_to_clean = ["build", "dist", "src/ai_writer.egg-info"]
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"🧹 Cleaning {dir_name}")
            shutil.rmtree(dir_path)


def main():
    """Build the AI Writer package."""
    print("🏗️  Building AI Writer package")

    # Clean previous builds
    clean_build_dirs()

    # Run tests first
    success = run_command(
        ["uv", "run", "pytest", "tests/", "-v"],
        "Running test suite"
    )
    if not success:
        print("❌ Tests failed. Fix issues before building.")
        return

    # Run code quality checks
    success = run_command(
        ["uv", "run", "ruff", "check", "src/", "tests/"],
        "Linting code"
    )
    if not success:
        print("❌ Linting failed. Fix issues before building.")
        return

    # Type checking
    success = run_command(
        ["uv", "run", "mypy", "src/ai_writer/"],
        "Type checking"
    )
    if not success:
        print("⚠️  Type checking failed, but continuing build...")

    # Build wheel
    success = run_command(
        ["uv", "build"],
        "Building wheel package"
    )
    if not success:
        return

    print("\n🎉 Build completed successfully!")
    print("\n📦 Built packages:")
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            print(f"   • {file.name}")

    print("\n📋 Next steps:")
    print("   • Test installation: uv pip install dist/*.whl")
    print("   • Upload to PyPI: uv run twine upload dist/*")


if __name__ == "__main__":
    main()
