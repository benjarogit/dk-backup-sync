# -*- coding: utf-8 -*-
"""
Zentrale Auslesung der Plugin-URL-Parameter (mode, action, name, …).
Kodi übergibt sys.argv[2] z. B. als "?mode=backup" oder "?action=category&name=maintenance".
"""
from urllib.parse import parse_qsl, unquote_plus


def parse_param_string(paramstring):
    """
    Parst den Query-String (ohne führendes ?) in ein Dict.
    paramstring: sys.argv[2].lstrip('?').
    """
    if not paramstring:
        return {}
    return dict(parse_qsl(paramstring, keep_blank_values=True))


class Params:
    """
    Liest Parameter aus dem Plugin-URL (z. B. plugin://id/?mode=backup).
    get_mode() / get_action() geben den ausgewählten Modus zurück.
    """

    def __init__(self, paramstring):
        self.params = parse_param_string(paramstring or '')

    def get(self, key, default=None):
        val = self.params.get(key)
        if val is None:
            return default
        return unquote_plus(val) if isinstance(val, str) else val

    def get_mode(self):
        """mode=... (z. B. main, settings, backup, restore, wizard, info, about)."""
        return self.get('mode') or self.get('action')

    def get_action(self):
        return self.get('action')

    def get_name(self):
        return self.get('name')

    def get_folder(self):
        return self.get('folder')

    def get_path(self):
        return self.get('path')

    def get_cmd(self):
        return self.get('cmd')
