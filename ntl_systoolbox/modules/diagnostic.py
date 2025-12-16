#!/usr/bin/env python3

"""
Module Diagnostic Réseau (NTL-SysToolbox)

- Entrée intuitive : adresse réseau
- Scan réseau et export (en cours de dev)
"""

from __future__ import annotations

import csv
import datetime as dt
import ipaddress
import platform
import re
import socket
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ========= Réglages =========

PING_TIMEOUT_MS_WINDOWS = 120
PING_TIMEOUT_SEC_LINUX = 1
DNS_TIMEOUT_SEC = 0.25
DEFAULT_PREFIX = 24
SHOW_DOWN_HOSTS = False  # False = n'affiche que UP
FAST_MODE = False        # True = reverse DNS ignoré (hostname=SKIP)

# ===========================


@dataclass
class HostInfo:
    ip: str
    status: str  # UP / DOWN
    hostname: str = "Inconnu"
    mac: str = "Inconnue"
    vendor: str = "Inconnu"
    os_guess: str = "Inconnu"
    ttl: Optional[int] = None


if __name__ == "__main__":
    print("Module Diagnostic Réseau - initialisation")
