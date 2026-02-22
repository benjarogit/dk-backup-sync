# -*- coding: utf-8 -*-
"""Remote-Struktur: ensure_remote_structure (fuer Service-Start)."""
import sys
import os
addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)


def ensure_remote_structure():
    """Legt Remote-Ordnerstruktur an. Returns True wenn ok."""
    import auto_ftp_sync
    return auto_ftp_sync.ensure_remote_structure()
