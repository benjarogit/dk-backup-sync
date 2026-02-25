# -*- coding: utf-8 -*-
"""Service-Entry: Kodi startet diese Datei (addon.xml xbmc.service)."""
import sys
import os
import threading

addon_path = os.path.dirname(os.path.abspath(__file__))
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)

if __name__ == "__main__":
    # Autostop (Pause-Stop / Sleep-Timer) in eigenem Thread, nur aktiv wenn in Einstellungen aktiviert
    try:
        from services import autostop_service
        _t = threading.Thread(target=autostop_service.run_loop, daemon=True)
        _t.start()
    except Exception:
        pass
    import auto_ftp_sync
    auto_ftp_sync.run_startup()
