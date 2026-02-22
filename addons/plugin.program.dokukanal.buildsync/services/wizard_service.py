# -*- coding: utf-8 -*-
"""Wizard: run_wizard_once (beim Start), reset_and_run_wizard (manuell)."""
from resources.lib import first_run


def run_wizard_once():
    """Startet Assistenten nur wenn first_run_done noch nicht gesetzt."""
    first_run.maybe_run()


def reset_and_run_wizard():
    """Setzt first_run_done zurueck und startet Assistenten."""
    first_run.reset_and_run()
