# -*- coding: utf-8 -*-
"""Service-Entry: Kodi startet diese Datei (addon.xml xbmc.service)."""
import sys
import os
addon_path = os.path.dirname(os.path.abspath(__file__))
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)
if __name__ == "__main__":
    import auto_ftp_sync
    auto_ftp_sync.run_startup()
