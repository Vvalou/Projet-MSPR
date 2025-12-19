#!/usr/bin/env python3
"""
Module de diagnostic AD/DNS pour NTL-SysToolbox
"""

import winrm
import json
from datetime import datetime
import warnings
import random

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

def verifier_services_ad_dns(host, username, password, output_json=True):
    """Vérifie les services AD/DNS sur un contrôleur de domaine"""
    
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
        
        # Vérification des services
        titre("VÉRIFICATION DES SERVICES")
        
        services = {'DNS': 'DNS', 'NTDS': 'AD DS'}
        services_status = {}
        
        for code, nom in services.items():
            result = session.run_cmd(f'sc query {code}')
            
            if result.status_code == 0:
                output = result.std_out.decode('utf-8')
                
                if 'RUNNING' in output:
                    services_status[code] = 'RUNNING'
                    ok(f"{nom:<15} : RUNNING")
                elif 'STOPPED' in output:
                    services_status[code] = 'STOPPED'
                    erreur(f"{nom:<15} : STOPPED")
                else:
                    services_status[code] = 'UNKNOWN'
                    erreur(f"{nom:<15} : UNKNOWN")
            else:
                services_status[code] = 'NOT_FOUND'
                erreur(f"{nom:<15} : SERVICE NON TROUVÉ")
        
        # Nombre de services actifs
        nb_ok = sum(1 for s in services_status.values() if s == 'RUNNING')
        nb_total = len(services_status)
        print(f"\n  Services actifs : {nb_ok}/{nb_total}")
        
        # Configuration AD
        titre("CONFIGURATION AD DS")
        
        ps_cmd = """
$domain = (Get-WmiObject Win32_ComputerSystem).Domain
$dcName = $env:COMPUTERNAME
$isDC = (Get-WmiObject Win32_OperatingSystem).ProductType

Write-Host "DOMAIN=$domain"
Write-Host "DCNAME=$dcName"
Write-Host "ISDC=$isDC"
"""
        
        ps_result = session.run_ps(ps_cmd)
        config_ad = {}
        
        if ps_result.status_code == 0:
            output = ps_result.std_out.decode('utf-8', errors='ignore')
            
            for line in output.split('\n'):
                line = line.strip()
                
                if line.startswith('DOMAIN='):
                    domaine = line.split('=', 1)[1].strip()
                    config_ad['domaine'] = domaine
                    print(f"  Domaine         : {domaine}")
                    
                elif line.startswith('DCNAME='):
                    dc_name = line.split('=', 1)[1].strip()
                    config_ad['dc_name'] = dc_name
                    print(f"  Contrôleur DC   : {dc_name}")
                    
                elif line.startswith('ISDC='):
                    is_dc = line.split('=', 1)[1].strip()
                    config_ad['is_dc'] = is_dc
                    role = "Contrôleur de domaine" if is_dc == "2" else "Serveur membre"
                    print(f"  Rôle            : {role}")
        
        # Vérification DNS
        titre("VÉRIFICATION DNS")
        
        dns_test = session.run_cmd('nslookup localhost')
        dns_ok = dns_test.status_code == 0
        
        if dns_ok:
            ok("Résolution DNS  : OK")
        else:
            erreur("Résolution DNS  : ERREUR")
        
        # Test domaine
        if config_ad.get('domaine'):
            dns_domain = session.run_cmd(f'nslookup {config_ad["domaine"]}')
            
            if dns_domain.status_code == 0:
                ok("Résolution domaine : OK")
            else:
                erreur("Résolution domaine : ERREUR")
        
        services_ok = all(services_status.get(s) == 'RUNNING' for s in ['NTDS', 'DNS'])
        
        result = {
            'timestamp': timestamp,
            'host': host,
            'hostname': hostname,
            'status': 'success',
            'services': services_status,
            'configuration_ad': config_ad,
            'dns_operational': dns_ok,
            'codes_retour': {
                'global': 0 if services_ok else 1,
                'services_critiques_ok': services_ok
            }
        }
        
        # Sauvegarde JSON
        if output_json:
            id_unique = random.randint(0, 999)
            filename = f"rapports/diagnostic_ad_dns_{datetime.now().strftime('%d-%m-%Y')}_ID{id_unique}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n  Rapport sauvegardé : {filename}")
        
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
        
        if output_json:
            id_unique = random.randint(0, 999)
            filename = f"rapports/diagnostic_ad_dns_ERROR_{datetime.now().strftime('%d-%m-%Y')}_ID{id_unique}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2, ensure_ascii=False)
        
        return error_result
