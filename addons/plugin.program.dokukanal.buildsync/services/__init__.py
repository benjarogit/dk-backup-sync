# -*- coding: utf-8 -*-
"""Services: eine Funktion pro fachlicher Aktion. Nur Rückgaben, keine Dialoge."""
from services import backup_service
from services import favorites_service
from services import network_service
from services import autoclean_service
from services import wizard_service
from services import skin_install_service
from services import sync_addon_data_service
from services import sync_remote_service
from services import image_rotation_service
__all__ = [
    'backup_service', 'favorites_service', 'network_service', 'autoclean_service',
    'wizard_service', 'skin_install_service', 'sync_addon_data_service',
    'sync_remote_service', 'image_rotation_service',
]
