#!/usr/bin/env python3
"""
Build script for creating executables for Windows (.exe) and Linux.

This script uses PyInstaller to create standalone binaries.
"""

import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def install_pyinstaller():
    """Install PyInstaller if not already installed."""
    print("\nChecking PyInstaller installation...")
    try:
        import PyInstaller
        print(f"PyInstaller is already installed (version {PyInstaller.__version__})")
        return True
    except ImportError:
        print("PyInstaller not found. Installing...")
        return run_command(
            [sys.executable, "-m", "pip", "install", "pyinstaller"],
            "Installing PyInstaller"
        )


def create_spec_file():
    """Create a PyInstaller spec file for the application."""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['molbox_tester/main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['telnetlib3'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='molbox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    spec_path = Path("molbox.spec")
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    print(f"\nCreated spec file: {spec_path}")
    return spec_path


def build_executable():
    """Build the executable using PyInstaller."""
    system = platform.system()
    print(f"\nBuilding for platform: {system}")
    
    # Create spec file
    spec_file = create_spec_file()
    
    # Build with PyInstaller
    success = run_command(
        [sys.executable, "-m", "PyInstaller", "--clean", str(spec_file)],
        f"Building executable for {system}"
    )
    
    if not success:
        print("\nBuild failed!")
        return False
    
    # Check output
    dist_dir = Path("dist")
    if system == "Windows":
        executable = dist_dir / "molbox.exe"
    else:
        executable = dist_dir / "molbox"
    
    if executable.exists():
        print(f"\n{'='*60}")
        print(f"SUCCESS! Executable created:")
        print(f"{'='*60}")
        print(f"  Location: {executable.absolute()}")
        print(f"  Size: {executable.stat().st_size / 1024 / 1024:.2f} MB")
        print(f"\nYou can now run: {executable}")
        return True
    else:
        print(f"\nError: Expected executable not found at {executable}")
        return False


def main():
    """Main build process."""
    print("="*60)
    print("molbox_tester Build Script")
    print("="*60)
    print(f"Platform: {platform.system()} {platform.machine()}")
    print(f"Python: {sys.version}")
    
    # Step 1: Install PyInstaller
    if not install_pyinstaller():
        print("\nFailed to install PyInstaller!")
        sys.exit(1)
    
    # Step 2: Install dependencies
    if not run_command(
        [sys.executable, "-m", "pip", "install", "."],
        "Installing package dependencies"
    ):
        print("\nFailed to install dependencies!")
        sys.exit(1)
    
    # Step 3: Build executable
    if not build_executable():
        sys.exit(1)
    
    print("\n" + "="*60)
    print("Build completed successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
