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

OUI_VENDOR_MAP = {
    "00:1A:2B": "Cisco",
    "00:1B:63": "Apple",
    "00:1C:BF": "Dell",
    "00:1D:D8": "HP",
    "3C:5A:B4": "Huawei",
    "BC:EA:FA": "Intel",
}


def normalize_mac(mac: str) -> str:
    mac = mac.strip().replace("-", ":").upper()
    parts = mac.split(":")
    if len(parts) == 6:
        return ":".join(p.zfill(2) for p in parts)
    return mac


def guess_vendor(mac: str) -> str:
    mac_norm = normalize_mac(mac)
    if len(mac_norm) < 8:
        return "Inconnu"
    oui = mac_norm[:8]
    return OUI_VENDOR_MAP.get(oui, "Inconnu")


def detect_os_from_ttl(ttl: Optional[int]) -> str:
    if ttl is None:
        return "Inconnu"
    if ttl >= 200:
        return "Equipement réseau (probable)"
    if 120 <= ttl < 200:
        return "Windows"
    if 60 <= ttl < 120:
        return "Linux/Unix"
    if 30 <= ttl < 60:
        return "OS réseau"
    return "Inconnu"


if __name__ == "__main__":
    print("Module Diagnostic Réseau - utilitaires MAC/OS prêts")


def ping_ip(ip: str) -> Tuple[bool, Optional[int]]:
    system = platform.system().lower()
    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", str(PING_TIMEOUT_MS_WINDOWS), ip]
    else:
        cmd = ["ping", "-c", "1", "-W", str(PING_TIMEOUT_SEC_LINUX), ip]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        output = result.stdout or ""
        reachable = (result.returncode == 0)
        ttl = None

        m = re.search(r"ttl[= ](\d+)", output, flags=re.IGNORECASE)
        if m:
            try:
                ttl = int(m.group(1))
            except ValueError:
                ttl = None

        return reachable, ttl
    except Exception:
        return False, None


def get_arp_mac(ip: str) -> str:
    system = platform.system().lower()
    if system == "windows":
        cmd = ["arp", "-a", ip]
        sep = "-"
    else:
        cmd = ["arp", "-n", ip]
        sep = ":"

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        out = result.stdout or ""
        for token in out.split():
            if sep in token and len(token) >= 17:
                return normalize_mac(token)
    except Exception:
        pass
    return "Inconnue"


def get_hostname_reverse_dns(ip: str) -> str:
    try:
        socket.setdefaulttimeout(DNS_TIMEOUT_SEC)
        name, _, _ = socket.gethostbyaddr(ip)
        return name
    except Exception:
        return "Inconnu"


if __name__ == "__main__":
    ok, ttl = ping_ip("8.8.8.8")
    print("Test ping 8.8.8.8:", ok, "TTL =", ttl)


def prompt_yes_no(question: str, default_yes: bool = True) -> bool:
    suffix = " (o/n) " if default_yes else " (n/o) "
    while True:
        choice = input(question + suffix).strip().lower()
        if choice == "" and default_yes:
            return True
        if choice == "" and not default_yes:
            return False
        if choice in ("o", "oui", "y", "yes"):
            return True
        if choice in ("n", "non", "no"):
            return False
        print("[ERREUR] Réponse non reconnue. Tape 'o' ou 'n'.")


def parse_network_input(raw: str) -> ipaddress.IPv4Network:
    raw = raw.strip()
    if "/" in raw:
        net = ipaddress.ip_network(raw, strict=False)
        if not isinstance(net, ipaddress.IPv4Network):
            raise ValueError("Seuls les réseaux IPv4 sont supportés.")
        return net

    ip = ipaddress.ip_address(raw)
    if not isinstance(ip, ipaddress.IPv4Address):
        raise ValueError("Seuls les réseaux IPv4 sont supportés.")

    use_default = prompt_yes_no(
        f"Aucune taille fournie. Utiliser /{DEFAULT_PREFIX} par défaut ?",
        default_yes=True,
    )
    if use_default:
        prefix = DEFAULT_PREFIX
    else:
        while True:
            s = input("Entrez la taille du réseau (ex: 24 pour /24) : ").strip()
            try:
                prefix = int(s)
                if 0 <= prefix <= 32:
                    break
                print("[ERREUR] Le préfixe doit être entre 0 et 32.")
            except ValueError:
                print("[ERREUR] Valeur invalide.")

    net = ipaddress.ip_network(f"{ip}/{prefix}", strict=False)
    if str(ip) != str(net.network_address):
        print(
            f"[INFO] Adresse ajustée vers le réseau : "
            f"{net.network_address}/{net.prefixlen}"
        )
    return net


def print_table_header() -> None:
    header = f"{'IP':<15} {'Statut':<6} {'Hostname':<30} {'MAC':<20} {'Fabricant':<20} {'OS estimé':<22}"
    print("\n" + header)
    print("-" * len(header))


def print_host_line(h: HostInfo) -> None:
    print(
        f"{h.ip:<15} "
        f"{h.status:<6} "
        f"{h.hostname[:29]:<30} "
        f"{h.mac:<20} "
        f"{h.vendor[:19]:<20} "
        f"{h.os_guess[:21]:<22}"
    )


if __name__ == "__main__":
    net = parse_network_input("192.168.1.0/24")
    print("Réseau analysé :", net)


