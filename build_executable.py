"""
Build script for creating cross-platform executables
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def build_frontend():
    """Build React frontend for production"""
    print("Building frontend...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("Error: frontend directory not found")
        return False
    
    # Install dependencies if needed
    if not (frontend_dir / "node_modules").exists():
        print("Installing frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    
    # Build frontend
    subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
    
    return True


def copy_frontend_build():
    """Copy frontend build to backend static directory"""
    print("Copying frontend build...")
    
    frontend_dist = Path("frontend/dist")
    backend_static = Path("backend/static")
    
    # Remove old static directory
    if backend_static.exists():
        shutil.rmtree(backend_static)
    
    # Copy new build
    shutil.copytree(frontend_dist, backend_static)
    
    return True


def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['startup.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('backend', 'backend'),
        ('config.yaml', '.'),
        ('../UAPUFOResearch/UAPUFOResearch', 'UAPUFOResearch/UAPUFOResearch'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
    ],
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
    [],
    exclude_binaries=True,
    name='RawHorse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='RawHorse',
)
"""
    
    with open("rawhorse.spec", "w") as f:
        f.write(spec_content)
    
    print("Created PyInstaller spec file")
    return True


def build_executable():
    """Build executable using PyInstaller"""
    print("Building executable with PyInstaller...")
    
    # Install PyInstaller if not present
    try:
        import PyInstaller
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Build executable
    subprocess.run([
        "pyinstaller",
        "--clean",
        "rawhorse.spec"
    ], check=True)
    
    print("Executable built successfully!")
    print(f"Output directory: {Path('dist/RawHorse').absolute()}")
    
    return True


def main():
    """Main build process"""
    print("=" * 60)
    print("Project RawHorse - Build Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("startup.py").exists():
        print("Error: Must run from project root directory")
        return 1
    
    try:
        # Step 1: Build frontend
        if not build_frontend():
            print("Failed to build frontend")
            return 1
        
        # Step 2: Copy frontend build
        if not copy_frontend_build():
            print("Failed to copy frontend build")
            return 1
        
        # Step 3: Create spec file
        if not create_spec_file():
            print("Failed to create spec file")
            return 1
        
        # Step 4: Build executable
        if not build_executable():
            print("Failed to build executable")
            return 1
        
        print("\n" + "=" * 60)
        print("Build completed successfully!")
        print("=" * 60)
        print("\nExecutable location:")
        print(f"  dist/RawHorse/RawHorse{'.exe' if sys.platform == 'win32' else ''}")
        print("\nTo create a distributable package:")
        print("  1. Copy the entire dist/RawHorse directory")
        print("  2. Distribute as a ZIP or create an installer")
        
        return 0
        
    except Exception as e:
        print(f"\nBuild failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
