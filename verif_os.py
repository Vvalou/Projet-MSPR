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

    try:
        info(f"\nConnexion SSH à {host}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=username, password=password, timeout=10)

        ok("Connexion SSH établie")

        titre("INFORMATIONS SYSTÈME")

        os_name = ssh_cmd(ssh, "lsb_release -ds || cat /etc/os-release | grep PRETTY_NAME")
        kernel = ssh_cmd(ssh, "uname -r")
        hostname = ssh_cmd(ssh, "hostname")
        uptime = ssh_cmd(ssh, "uptime -p")

        print(f"  Hostname        : {hostname}")
        print(f"  OS              : {os_name}")
        print(f"  Kernel          : {kernel}")
        print(f"  Uptime          : {uptime}")

        info_os = {
            "os": os_name,
            "kernel": kernel,
            "uptime": uptime
        }

        titre("UTILISATION DES RESSOURCES")

        cpu_name = ssh_cmd(ssh, "lscpu | grep 'Model name' | awk -F ':' '{print $2}'")
        cpu_cores = ssh_cmd(ssh, "nproc")
        cpu_usage = ssh_cmd(
            ssh,
            "top -bn1 | grep 'Cpu(s)' | awk '{print 100-$8}'"
        )

        print(f"  CPU             : {cpu_name.strip()} ({cpu_cores} cœurs)")
        print(f"  Utilisation CPU : {float(cpu_usage):.2f}%")

        info_cpu = {
            "name": cpu_name.strip(),
            "cores": cpu_cores,
            "usage": round(float(cpu_usage), 2)
        }

        ram_total = ssh_cmd(ssh, "free -g | awk '/Mem:/ {print $2}'")
        ram_used = ssh_cmd(ssh, "free -g | awk '/Mem:/ {print $3}'")
        ram_percent = ssh_cmd(
            ssh,
            "free | awk '/Mem:/ {printf \"%.2f\", $3/$2*100}'"
        )

        print(f"  RAM             : {ram_used} GB / {ram_total} GB ({ram_percent}%)")

        info_ram = {
            "total": ram_total,
            "used": ram_used,
            "percent": ram_percent
        }

        print("\n  Disques:")
        disk_raw = ssh_cmd(
            ssh,
            "df -h --output=source,size,used,pcent,target | grep '^/dev/'"
        )

        disques = []
        for line in disk_raw.splitlines():
            parts = line.split()
            disque = {
                "device": parts[0],
                "total": parts[1],
                "used": parts[2],
                "percent": parts[3],
                "mount": parts[4]
            }
            disques.append(disque)
            ok(f"{parts[4]:<10} : {parts[2]} / {parts[1]} ({parts[3]})")

        ssh.close()

        result = {
            "timestamp": timestamp,
            "host": host,
            "hostname": hostname,
            "status": "success",
            "info_os": info_os,
            "info_cpu": info_cpu,
            "info_ram": info_ram,
            "disques": disques,
            "codes_retour": {"global": 0}
        }

        if output_json:
            filename = f"ubuntu_audit_{host.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n  Rapport sauvegardé : {filename}")

        return result

    except Exception as e:
        erreur(f"\n[ERREUR] {str(e)}")

        error_result = {
            "timestamp": timestamp,
            "host": host,
            "status": "error",
            "error": str(e),
            "codes_retour": {"global": 1}
        }

        return error_result


