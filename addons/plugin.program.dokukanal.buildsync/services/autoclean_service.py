# -*- coding: utf-8 -*-
"""AutoClean: run_autoclean, set_next_run. Rueckgabe (bool, str)."""
from core import settings
from resources.lib import auto_clean


def run_autoclean():
    """Fuehrt AutoClean aus. Returns (True, statistik_text)."""
    statistik = auto_clean.run_auto_clean()
    msg = settings.L(30162)
    if statistik:
        msg = msg + "\n\n" + statistik
    return (True, msg)


def set_next_run():
    """Setzt naechsten Laufzeitpunkt."""
    auto_clean.set_next_run()
