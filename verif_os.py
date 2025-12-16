#!/usr/bin/env python3
"""
Module d'audit Ubuntu Server pour NTL-SysToolbox
Connexion SSH depuis le Host
"""

import paramiko
import json
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

RESET = '\033[0m'
VERT = '\033[92m'
ROUGE = '\033[91m'
BLEU = '\033[94m'
CYAN = '\033[96m'
BOLD = '\033[1m'


def titre(texte):
    print("\n" + CYAN + BOLD + "=" * 60)
    print(texte.center(60))
    print("=" * 60 + RESET)


def ok(texte):
    print(VERT + "  ✓ " + RESET + texte)


def erreur(texte):
    print(ROUGE + "  ✗ " + RESET + texte)


def info(texte):
    print(BLEU + texte + RESET)


def ssh_cmd(ssh, cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    return stdout.read().decode().strip()


def verifier_etat_ubuntu(host, username, password, output_json=True):
    """Vérifie l'état système du serveur"""
    timestamp = datetime.now().isoformat()

 