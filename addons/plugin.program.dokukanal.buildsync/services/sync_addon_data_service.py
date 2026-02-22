# -*- coding: utf-8 -*-
"""Addon-Data-Sync (ZIP) fuer Service-Start."""
import sys
import os
addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)


def sync_addon_data():
    """Synchronisiert addon_data per ZIP. Returns False wenn uebersprungen."""
    import auto_ftp_sync
    return auto_ftp_sync.sync_addon_data()
