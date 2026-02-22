# -*- coding: utf-8 -*-
"""Bildrotation: download_random_image (fuer Service-Start)."""
import sys
import os
addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)


def download_random_image():
    """Laedt zufaelliges Hintergrundbild. Returns True bei Erfolg."""
    import auto_ftp_sync
    return auto_ftp_sync.download_random_image()
