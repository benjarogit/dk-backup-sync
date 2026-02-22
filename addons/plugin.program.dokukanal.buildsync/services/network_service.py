# -*- coding: utf-8 -*-
"""Netzwerk: test_connection, test_image_sources. Rueckgabe (bool, str)."""
import sys
import os
addon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if addon_path not in sys.path:
    sys.path.insert(0, addon_path)


def test_connection(connection_number=None):
    """Testet Verbindung (1/2/3 oder aktive). Returns (success, message)."""
    import auto_ftp_sync
    conn_num = int(connection_number) if connection_number in ('1', '2', '3') else None
    if conn_num is not None:
        return auto_ftp_sync.test_connection(conn_num)
    return auto_ftp_sync.test_current_connection()


def test_image_sources():
    """Testet Bildquellen-URL. Returns (success, message, tested_source)."""
    import auto_ftp_sync
    return auto_ftp_sync.test_image_sources()


def get_connection_summary(connection_number=None):
    """Zusammenfassung der Verbindungseinstellungen (fuer Dialog)."""
    import auto_ftp_sync
    return auto_ftp_sync.get_connection_summary(connection_number)


def get_image_source_summary(connection_number=None):
    """Zusammenfassung der aktiven Bildquelle (fuer Dialog vor Test)."""
    import auto_ftp_sync
    return auto_ftp_sync.get_image_source_summary(connection_number)
