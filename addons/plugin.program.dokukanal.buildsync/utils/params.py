# -*- coding: utf-8 -*-
"""
Parse URL parameters (action, mode, name, ...).
get_action() / get_mode() for router; action takes precedence.
"""
from urllib.parse import parse_qsl, unquote_plus


def parse_param_string(paramstring):
    """Parse query string (without ?) into a dict."""
    if not paramstring:
        return {}
    return dict(parse_qsl(paramstring, keep_blank_values=True))


class Params:
    """Read parameters from plugin URL. get_action() / get_mode() for router."""

    def __init__(self, paramstring):
        self.params = parse_param_string(paramstring or '')

    def get(self, key, default=None):
        val = self.params.get(key)
        if val is None:
            return default
        return unquote_plus(val) if isinstance(val, str) else val

    def get_action(self):
        """action=... (main parameter for router)."""
        return self.get('action') or self.get('mode')

    def get_mode(self):
        """mode=... (fallback for backward compatibility)."""
        return self.get('mode') or self.get('action')

    def get_name(self):
        return self.get('name')

    def get_folder(self):
        return self.get('folder')

    def get_path(self):
        return self.get('path')

    def get_cmd(self):
        return self.get('cmd')
