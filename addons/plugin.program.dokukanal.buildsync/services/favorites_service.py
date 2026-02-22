# -*- coding: utf-8 -*-
"""Favoriten-Sync: save_favorites. Rueckgabe (success, msg_id, fmt_args)."""
from typing import Tuple, Optional, Dict, Any
import sys
import os
addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)


def save_favorites(no_notification=False):
    """
    Synchronisiert Standard- und statische Favoriten.
    Returns: (success, msg_id, fmt_args) mit optionalem fmt_args-Dict.
    """
    import auto_ftp_sync
    return auto_ftp_sync.sync_favourites(no_notification=no_notification)
