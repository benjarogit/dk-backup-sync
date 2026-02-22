# -*- coding: utf-8 -*-
"""
Merge logic for Kodi favourites.xml (Python standard library only).
Union merge: all devices are equal; result = union of local and server (deduplicated).
Sync uses merge_union only.
"""
import xml.etree.ElementTree as ET
import os


def _normalize_action(text):
    """Normalize favourite action string for deduplication (strip whitespace)."""
    if text is None:
        return ''
    return (text.strip() or '')


def parse_favourites(file_path):
    """
    Parse a Kodi favourites.xml and return list of favourite action strings (order preserved).
    Returns empty list if file missing, invalid, or no favourites.
    """
    if not file_path or not os.path.isfile(file_path):
        return []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        if root is None or root.tag != 'favourites':
            return []
        actions = []
        for child in root:
            if child.tag == 'favourite' and child.text is not None:
                action = _normalize_action(child.text)
                if action:
                    actions.append(action)
        return actions
    except (ET.ParseError, OSError, IOError):
        return []


def write_favourites(file_path, action_list):
    """
    Write a Kodi favourites.xml from a list of action strings.
    action_list: list of strings (each becomes one <favourite> text).
    """
    root = ET.Element('favourites')
    for action in (action_list or []):
        if not isinstance(action, str) or not action.strip():
            continue
        elem = ET.SubElement(root, 'favourite')
        elem.text = action.strip()
    tree = ET.ElementTree(root)
    try:
        if hasattr(ET, 'indent'):
            ET.indent(tree, space='  ', level=0)
    except (TypeError, AttributeError):
        pass  # Python < 3.9 or indent not available
    with open(file_path, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True, default_namespace=None, method='xml')
    return True


def merge_union(local_actions, server_actions):
    """
    Union merge: no main/subsystem; every device is equal.
    Result = local + (server entries not in local). Deduplicated, local order first.
    """
    seen = {_normalize_action(a) for a in (local_actions or [])}
    out = list(local_actions or [])
    for a in (server_actions or []):
        key = _normalize_action(a)
        if key and key not in seen:
            seen.add(key)
            out.append(a)
    return out
