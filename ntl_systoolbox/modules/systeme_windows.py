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
        
        result = {
            'timestamp': timestamp,
            'host': host,
            'hostname': hostname,
            'status': 'success',
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