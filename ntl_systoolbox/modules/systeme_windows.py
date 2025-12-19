# ---------------------------------------------- #

#Module d'audit Windows Server pour NTL-SysToolbox

# ---------------------------------------------- #

import winrm
import json
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

# Couleurs pour l'affichage
RESET = '\033[0m'
VERT = '\033[92m'
ROUGE = '\033[91m'
BLEU = '\033[94m'
CYAN = '\033[96m'
BOLD = '\033[1m'

def titre(texte):
    """Affiche un titre en cyan"""
    print("\n" + CYAN + BOLD + "=" * 60)
    print(texte.center(60))
    print("=" * 60 + RESET)

def ok(texte):
    """Affiche ✓ en vert"""
    print(VERT + "  ✓ " + RESET + texte)

def erreur(texte):
    """Affiche ✗ en rouge"""
    print(ROUGE + "  ✗ " + RESET + texte)

def info(texte):
    """Affiche une info en bleu"""
    print(BLEU + texte + RESET)

def verifier_etat_windows(host, username, password, output_json=True):
    """Vérifie l'état système d'un serveur Windows"""
    
    timestamp = datetime.now().isoformat()
    
    try:
        # Connexion
        info(f"\n[INFO] Connexion à {host}...")
        session = winrm.Session(
            f'http://{host}:5985/wsman',
            auth=(username, password),
            transport='ntlm',
            server_cert_validation='ignore'
        )
        
        # Test connexion
        test = session.run_cmd('hostname')
        if test.status_code != 0:
            raise Exception("Connexion impossible")
        
        hostname = test.std_out.decode('utf-8').strip()
        ok(f"[OK] Connecté à {hostname}")
        
        # Informations système
        titre("INFORMATIONS SYSTÈME")
        
        ps_os = """
$os = Get-WmiObject Win32_OperatingSystem
$bootTime = $os.ConvertToDateTime($os.LastBootUpTime)
$uptime = (Get-Date) - $bootTime

Write-Host "OS=$($os.Caption)"
Write-Host "VERSION=$($os.Version)"
Write-Host "UPTIME_DAYS=$([int]$uptime.TotalDays)"
Write-Host "UPTIME_HOURS=$($uptime.Hours)"
Write-Host "UPTIME_MINUTES=$($uptime.Minutes)"
"""
        
        result_os = session.run_ps(ps_os)
        info_os = {}
        
        if result_os.status_code == 0:
            output = result_os.std_out.decode('utf-8', errors='ignore')
            
            for line in output.split('\n'):
                line = line.strip()
                
                if line.startswith('OS='):
                    os_name = line.split('=', 1)[1].strip()
                    info_os['os'] = os_name
                    print(f"  OS              : {os_name}")
                    
                elif line.startswith('VERSION='):
                    version = line.split('=', 1)[1].strip()
                    info_os['version'] = version
                    print(f"  Version         : {version}")
                    
                elif line.startswith('UPTIME_DAYS='):
                    days = line.split('=', 1)[1].strip()
                    info_os['uptime_days'] = days
                    
                elif line.startswith('UPTIME_HOURS='):
                    hours = line.split('=', 1)[1].strip()
                    info_os['uptime_hours'] = hours
                    
                elif line.startswith('UPTIME_MINUTES='):
                    minutes = line.split('=', 1)[1].strip()
                    info_os['uptime_minutes'] = minutes
            
            # Afficher uptime
            if 'uptime_days' in info_os:
                print(f"  Uptime          : {info_os['uptime_days']} jours, {info_os['uptime_hours']} heures, {info_os['uptime_minutes']} minutes")
        
        # Utilisation des ressources
        titre("UTILISATION DES RESSOURCES")
        
        # CPU
        ps_cpu = """
$cpu = Get-WmiObject Win32_Processor | Select-Object -First 1

Write-Host "CPU_NAME=$($cpu.Name.Trim())"
Write-Host "CPU_CORES=$($cpu.NumberOfCores)"
Write-Host "CPU_USAGE=$($cpu.LoadPercentage)"
"""
        
        result_cpu = session.run_ps(ps_cpu)
        info_cpu = {}
        
        if result_cpu.status_code == 0:
            output = result_cpu.std_out.decode('utf-8', errors='ignore')
            
            for line in output.split('\n'):
                line = line.strip()
                
                if line.startswith('CPU_NAME='):
                    cpu_name = line.split('=', 1)[1].strip()
                    info_cpu['name'] = cpu_name
                    
                elif line.startswith('CPU_CORES='):
                    cores = line.split('=', 1)[1].strip()
                    info_cpu['cores'] = cores
                    
                elif line.startswith('CPU_USAGE='):
                    usage = line.split('=', 1)[1].strip()
                    info_cpu['usage'] = usage
            
            # Affichage CPU
            if 'name' in info_cpu and 'cores' in info_cpu:
                print(f"  CPU             : {info_cpu['name']} ({info_cpu['cores']} cœurs)")
                print(f"  Utilisation CPU : {info_cpu['usage']}%")
        
        # RAM
        ps_ram = """
$ram = Get-WmiObject Win32_OperatingSystem
$total = [math]::Round($ram.TotalVisibleMemorySize/1MB, 2)
$free = [math]::Round($ram.FreePhysicalMemory/1MB, 2)
$used = [math]::Round($total - $free, 2)
$percent = [math]::Round(($used/$total)*100, 2)

Write-Host "RAM_TOTAL=$total"
Write-Host "RAM_USED=$used"
Write-Host "RAM_PERCENT=$percent"
"""
        
        result_ram = session.run_ps(ps_ram)
        info_ram = {}
        
        if result_ram.status_code == 0:
            output = result_ram.std_out.decode('utf-8', errors='ignore')
            
            for line in output.split('\n'):
                line = line.strip()
                
                if line.startswith('RAM_TOTAL='):
                    total = line.split('=', 1)[1].strip()
                    info_ram['total'] = total
                    
                elif line.startswith('RAM_USED='):
                    used = line.split('=', 1)[1].strip()
                    info_ram['used'] = used
                    
                elif line.startswith('RAM_PERCENT='):
                    percent = line.split('=', 1)[1].strip()
                    info_ram['percent'] = percent
            
            if 'total' in info_ram:
                print(f"  RAM             : {info_ram['used']} GB / {info_ram['total']} GB ({info_ram['percent']}%)")
        
        # Disques
        ps_disk = """
Get-WmiObject Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    $total = [math]::Round($_.Size/1GB, 2)
    $free = [math]::Round($_.FreeSpace/1GB, 2)
    $used = [math]::Round($total - $free, 2)
    $percent = [math]::Round(($used/$total)*100, 2)
    
    Write-Host "DISK=$($_.DeviceID)|$total|$used|$percent"
}
"""
        
        result_disk = session.run_ps(ps_disk)
        disques = []
        
        print("\n  Disques:")
        
        if result_disk.status_code == 0:
            output = result_disk.std_out.decode('utf-8', errors='ignore')
            
            for line in output.split('\n'):
                line = line.strip()
                
                if line.startswith('DISK='):
                    data = line.split('=', 1)[1].strip()
                    parts = data.split('|')
                    
                    if len(parts) == 4:
                        lettre = parts[0]
                        total = parts[1]
                        used = parts[2]
                        percent = parts[3]
                        
                        disques.append({
                            'lettre': lettre,
                            'total': total,
                            'used': used,
                            'percent': percent
                        })
                        
                        ok(f"{lettre:<3}         : {used} GB / {total} GB ({percent}%)")
        
        result = {
            'timestamp': timestamp,
            'host': host,
            'hostname': hostname,
            'status': 'success',
            'info_os': info_os,
            'info_cpu': info_cpu,
            'info_ram': info_ram,
            'disques': disques,
            'codes_retour': {'global': 0}
        }
        
        return result
        
    except Exception as e:
        erreur(f"\n[ERREUR] {str(e)}")
        
        error_result = {
            'timestamp': timestamp,
            'host': host,
            'status': 'error',
            'error': str(e),
            'codes_retour': {'global': 1}
        }
        
        return error_result