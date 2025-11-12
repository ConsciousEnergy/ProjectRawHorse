# Custom Icon Setup Guide

This guide shows you how to make the Project RawHorse launcher use the custom logo as its icon.

---

## 🪟 Windows

### Method 1: Using VBS Launcher (Recommended)

1. **Create the icon file:**
   ```bash
   python create_icon.py
   ```
   This creates `PRHLogo.ico` from `PRHLogo.png`

2. **Create a shortcut to the VBS launcher:**
   - Right-click on `LaunchRawHorse.vbs`
   - Select "Create shortcut"
   - Rename to "Project RawHorse"

3. **Set the custom icon:**
   - Right-click the shortcut → **Properties**
   - Click **Change Icon...**
   - Click **Browse...**
   - Navigate to `PRHLogo.ico`
   - Click **OK** → **OK**

4. **Pin to taskbar or desktop:**
   - Drag shortcut to desktop
   - Or right-click → Pin to Taskbar

### Method 2: Direct Shortcut to RUN.bat

1. **Create icon file:**
   ```bash
   python create_icon.py
   ```

2. **Create shortcut:**
   - Right-click on `RUN.bat`
   - Select "Create shortcut"
   - Rename to "Project RawHorse"

3. **Set icon on shortcut:**
   - Right-click shortcut → **Properties**
   - Click **Change Icon...**
   - Browse to `PRHLogo.ico`
   - Click **OK**

4. **Optional: Move to a better location**
   - Move shortcut to Desktop or Start Menu folder:
     ```
     C:\Users\<YourName>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\
     ```

---

## 🐧 Linux

### Method 1: Desktop Entry (Recommended)

1. **Edit the .desktop file:**
   ```bash
   nano ProjectRawHorse.desktop
   ```

2. **Replace `%k` with full path:**
   - Change `%k` to your project path, e.g.:
     ```
     /home/username/project_rawhorse
     ```

3. **Copy to applications:**
   ```bash
   # For all users (requires sudo):
   sudo cp ProjectRawHorse.desktop /usr/share/applications/

   # Or for current user only:
   cp ProjectRawHorse.desktop ~/.local/share/applications/
   ```

4. **Make executable:**
   ```bash
   chmod +x ~/.local/share/applications/ProjectRawHorse.desktop
   ```

5. **Desktop shortcut (optional):**
   ```bash
   cp ProjectRawHorse.desktop ~/Desktop/
   chmod +x ~/Desktop/ProjectRawHorse.desktop
   ```

The icon will automatically use `PRHLogo.png`!

### Method 2: Custom Launcher Script

1. **Create launcher with icon metadata:**
   ```bash
   cat > ~/bin/rawhorse << 'EOF'
   #!/bin/bash
   cd /path/to/project_rawhorse
   ./RUN.sh
   EOF
   chmod +x ~/bin/rawhorse
   ```

2. **Add to application menu:**
   - Use your desktop environment's menu editor
   - Set icon to `PRHLogo.png`

---

## 🍎 macOS

### Method 1: Automator App (Recommended)

1. **Open Automator:**
   - Applications → Automator
   - Choose "Application"

2. **Add shell script action:**
   - Search for "Run Shell Script"
   - Drag to workflow
   - Paste:
     ```bash
     cd /path/to/project_rawhorse
     ./RUN.sh
     ```

3. **Save as Application:**
   - File → Save
   - Name: "Project RawHorse"
   - Save to Applications folder

4. **Set custom icon:**
   - Open `PRHLogo.png` in Preview
   - Edit → Select All (⌘A)
   - Edit → Copy (⌘C)
   - In Finder, select the app you created
   - File → Get Info (⌘I)
   - Click the icon in top-left of info window
   - Edit → Paste (⌘V)

5. **Add to Dock:**
   - Drag app to Dock

### Method 2: Using Script Editor

1. **Open Script Editor**
2. **Create script:**
   ```applescript
   do shell script "cd /path/to/project_rawhorse && ./RUN.sh"
   ```
3. **Save as Application**
4. **Set icon same as Automator method above**

---

## 📦 Quick Setup Script

For automated setup, run:

```bash
# Windows (PowerShell)
python create_icon.py

# Linux
sed -i "s|%k|$(pwd)|g" ProjectRawHorse.desktop
cp ProjectRawHorse.desktop ~/.local/share/applications/
chmod +x ~/.local/share/applications/ProjectRawHorse.desktop

# macOS
# Use Automator method (can't be fully automated)
```

---

## 🎨 Icon Specifications

**PRHLogo.png:**
- Format: PNG with transparency
- Recommended: 512x512px or larger
- Colors: Purple and Gold theme

**PRHLogo.ico (Windows):**
- Format: ICO
- Sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
- Created by `create_icon.py`

---

## Troubleshooting

### Windows: Icon won't change
- Make sure you're changing the shortcut icon, not the .bat file itself
- .bat files can't have custom icons directly
- Use the VBS launcher method

### Linux: Icon doesn't show
- Verify the path in .desktop file is absolute (not relative)
- Check file permissions: `chmod +x ProjectRawHorse.desktop`
- Update desktop database: `update-desktop-database ~/.local/share/applications/`

### macOS: Icon reverts back
- Make sure you copied the icon to the app's icon area in Get Info
- The icon should stick after a restart

---

## Alternative: Convert to Executable

For a more polished experience, use PyInstaller to create a true executable with embedded icon:

```bash
# Windows
pyinstaller --onefile --windowed --icon=PRHLogo.ico --name="Project RawHorse" launcher.py

# macOS
pyinstaller --onefile --windowed --icon=PRHLogo.icns --name="Project RawHorse" launcher.py

# Linux
pyinstaller --onefile --icon=PRHLogo.png --name="Project RawHorse" launcher.py
```

See `build_executable.py` for the full build script.

---

## Quick Reference

| Platform | Icon Format | Location |
|----------|-------------|----------|
| Windows  | .ico        | Shortcut properties |
| Linux    | .png        | .desktop file |
| macOS    | .icns/.png  | App bundle / Get Info |

---

**Enjoy your customized Project RawHorse launcher!** 🐎✨

