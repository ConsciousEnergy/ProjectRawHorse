"""
Convert PRHLogo.png to .ico format for Windows
Run this script to create an icon file for the launcher
"""
from PIL import Image
import os

def create_icon():
    """Convert PNG logo to ICO format with multiple sizes"""
    try:
        # Open the PNG logo
        logo_path = "PRHLogo.png"
        if not os.path.exists(logo_path):
            print(f"Error: {logo_path} not found!")
            return False
        
        img = Image.open(logo_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create icon with multiple sizes (Windows standard)
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Save as ICO with multiple sizes
        output_path = "PRHLogo.ico"
        img.save(output_path, format='ICO', sizes=icon_sizes)
        
        print(f"✓ Successfully created {output_path}")
        print(f"  Icon includes sizes: {', '.join([f'{w}x{h}' for w, h in icon_sizes])}")
        return True
        
    except ImportError:
        print("Error: Pillow library not installed")
        print("Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"Error creating icon: {e}")
        return False

if __name__ == "__main__":
    print("Project RawHorse - Icon Creator")
    print("=" * 50)
    print()
    
    if create_icon():
        print()
        print("Next steps:")
        print("1. Right-click on RUN.bat")
        print("2. Create shortcut")
        print("3. Right-click shortcut → Properties")
        print("4. Click 'Change Icon...'")
        print("5. Browse to PRHLogo.ico")
        print("6. Click OK")
    else:
        print()
        print("Icon creation failed. See error above.")

