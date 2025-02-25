#!/usr/bin/env python3

import shutil
from pathlib import Path
import sys

def uninstall_application():
    home = Path.home()
    
    # Remove application files
    app_dir = home / ".local/share/telly-spelly"
    if app_dir.exists():
        shutil.rmtree(app_dir)
    
    # Remove launcher
    launcher = home / ".local/bin/telly-spelly"
    if launcher.exists():
        launcher.unlink()
    
    # Remove desktop file
    desktop_file = home / ".local/share/applications/org.kde.telly_spelly.desktop"
    if desktop_file.exists():
        desktop_file.unlink()
    
    # Remove icon
    icon_file = home / ".local/share/icons/hicolor/256x256/apps/telly-spelly.png"
    if icon_file.exists():
        icon_file.unlink()
    
    print("Application uninstalled successfully!")

if __name__ == "__main__":
    try:
        uninstall_application()
    except Exception as e:
        print(f"Uninstallation failed: {e}")
        sys.exit(1) 
