# --------------------------------------------
# Module de sauvegarde WMS
# Gère les sauvegardes SQL et exports CSV via PowerShell
# --------------------------------------------
# BY V.VERGULT / C.REDOULES / S.TARRAS / M.BJAOUI

import os
import subprocess
import time

# Codes couleurs ANSI
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

def print_separator():
    print("─" * 60)

def executer_backup_sql():
    """Execute une sauvegarde SQL complète de la base WMS"""
    print("\n[INFO] Lancement de la sauvegarde SQL complète...")
    print_separator()
    
    try:
        # Chemin vers le script PowerShell de Clément
        ps_script = os.path.join(".", "modules", "Backup-Wms.ps1")
        
        # Commande PowerShell
        commande = [
            'powershell',
            '-ExecutionPolicy', 'Bypass',
            '-File', ps_script,
            '-Mode', 'Full'
        ]
        
        # Exécution
        result = subprocess.run(commande, capture_output=True, text=True)
        
        # Affichage du résultat
        if result.stdout:
            print(result.stdout)
        
        # Filtrer le warning mysqldump du stderr
        if result.stderr:
            # Ne pas afficher le warning "Using a password on the command line"
            stderr_lines = result.stderr.split('\n')
            filtered_errors = [line for line in stderr_lines 
                             if 'Using a password on the command line' not in line 
                             and line.strip()]
            if filtered_errors:
                print(f"{Colors.RED}[ERREUR] {' '.join(filtered_errors)}{Colors.RESET}")
        
        if result.returncode == 0:
            print(f"\n{Colors.GREEN}[✓] Sauvegarde SQL complète terminée avec succès !{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}[✗] Échec de la sauvegarde SQL{Colors.RESET}")
            
    except Exception as e:
        print(f"\n{Colors.RED}[ERREUR] Exception lors de l'exécution : {e}{Colors.RESET}")
    
    print_separator()

def executer_export_csv():
    """Execute un export CSV de la table inventory avec jointures"""
    print("\n[INFO] Lancement de l'export CSV de la table inventory...")
    print_separator()
    
    try:
        # Chemin vers le script PowerShell de Clément
        ps_script = os.path.join(".", "modules", "Backup-Wms.ps1")
        
        # Commande PowerShell
        commande = [
            'powershell',
            '-ExecutionPolicy', 'Bypass',
            '-File', ps_script,
            '-Mode', 'Table',
            '-TableName', 'inventory'
        ]
        
        # Exécution
        result = subprocess.run(commande, capture_output=True, text=True)
        
        # Affichage du résultat
        if result.stdout:
            print(result.stdout)
        
        # Filtrer le warning mysqldump du stderr
        if result.stderr:
            stderr_lines = result.stderr.split('\n')
            filtered_errors = [line for line in stderr_lines 
                             if 'Using a password on the command line' not in line 
                             and line.strip()]
            if filtered_errors:
                print(f"{Colors.RED}[ERREUR] {' '.join(filtered_errors)}{Colors.RESET}")
        
        if result.returncode == 0:
            print(f"\n{Colors.GREEN}[✓] Export CSV terminé avec succès !{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}[✗] Échec de l'export CSV{Colors.RESET}")
            
    except Exception as e:
        print(f"\n{Colors.RED}[ERREUR] Exception lors de l'exécution : {e}{Colors.RESET}")
    
    print_separator()

def afficher_contenu_inventory():
    """Affiche le contenu de la table inventory directement"""
    print("\n[INFO] Affichage du contenu de la table inventory...")
    print_separator()
    
    try:
        # Commande Docker pour afficher le contenu
        commande = [
            'docker', 'exec', '-it', 'wms-db',
            'mysql', '-uwms_backup', '-pBackupWMS2025',
            'wms', '-e', 'SELECT * FROM inventory;'
        ]
        
        # Exécution
        result = subprocess.run(commande, capture_output=True, text=True)
        
        # Affichage du résultat
        if result.stdout:
            print(result.stdout)
        
        # Filtrer les warnings du stderr
        if result.stderr:
            stderr_lines = result.stderr.split('\n')
            filtered_errors = [line for line in stderr_lines 
                             if 'Warning' not in line 
                             and 'Using a password on the command line' not in line
                             and line.strip()]
            if filtered_errors:
                print(f"{Colors.RED}[ERREUR] {' '.join(filtered_errors)}{Colors.RESET}")
        
        if result.returncode == 0:
            print(f"\n{Colors.GREEN}[✓] Affichage terminé{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}[✗] Échec de l'affichage{Colors.RESET}")
            
    except Exception as e:
        print(f"\n{Colors.RED}[ERREUR] Exception lors de l'exécution : {e}{Colors.RESET}")
    
    print_separator()

def tester_connexion_db():
    """Teste la connexion à la base de données WMS"""
    print("\n[INFO] Test de connexion à la base de données WMS...")
    print_separator()
    
    try:
        # Commande Docker pour tester la connexion
        commande = [
            'docker', 'exec', 'wms-db',
            'mysql', '-uwms_backup', '-pBackupWMS2025',
            '-e', 'SELECT "Connexion OK" AS status;'
        ]
        
        # Exécution
        result = subprocess.run(commande, capture_output=True, text=True)
        
        # Affichage du résultat
        if result.returncode == 0:
            print(f"{Colors.GREEN}[✓] Connexion à la base de données WMS : OK{Colors.RESET}")
            print(f"{Colors.GREEN}[✓] Utilisateur : wms_backup{Colors.RESET}")
            print(f"{Colors.GREEN}[✓] Base de données : wms{Colors.RESET}")
        else:
            print(f"{Colors.RED}[✗] Impossible de se connecter à la base de données{Colors.RESET}")
            # Filtrer le warning du stderr
            if result.stderr:
                stderr_lines = result.stderr.split('\n')
                filtered_errors = [line for line in stderr_lines 
                                 if 'Using a password on the command line' not in line 
                                 and line.strip()]
                if filtered_errors:
                    print(f"{Colors.RED}[ERREUR] {' '.join(filtered_errors)}{Colors.RESET}")
            
    except Exception as e:
        print(f"\n{Colors.RED}[ERREUR] Exception lors de l'exécution : {e}{Colors.RESET}")
    
    print_separator()

def lister_backups():
    """Liste les fichiers de sauvegarde disponibles"""
    print("\n[INFO] Liste des sauvegardes disponibles...")
    print_separator()
    
    backup_sql_dir = os.path.join(".", "backups", "sql")
    backup_csv_dir = os.path.join(".", "backups", "csv")
    
    # Sauvegardes SQL
    print("\nSauvegardes SQL :")
    if os.path.exists(backup_sql_dir):
        sql_files = [f for f in os.listdir(backup_sql_dir) if f.endswith('.sql')]
        if sql_files:
            for i, fichier in enumerate(sorted(sql_files, reverse=True)[:5], 1):
                taille = os.path.getsize(os.path.join(backup_sql_dir, fichier))
                taille_mb = taille / (1024 * 1024)
                print(f"  {i}. {fichier} ({taille_mb:.2f} MB)")
        else:
            print("  Aucune sauvegarde SQL trouvée")
    else:
        print("  Répertoire de sauvegarde SQL non trouvé")
    
    # Exports CSV
    print("\nExports CSV :")
    if os.path.exists(backup_csv_dir):
        csv_files = [f for f in os.listdir(backup_csv_dir) if f.endswith('.csv')]
        if csv_files:
            for i, fichier in enumerate(sorted(csv_files, reverse=True)[:5], 1):
                taille = os.path.getsize(os.path.join(backup_csv_dir, fichier))
                taille_kb = taille / 1024
                print(f"  {i}. {fichier} ({taille_kb:.2f} KB)")
        else:
            print("  Aucun export CSV trouvé")
    else:
        print("  Répertoire d'export CSV non trouvé")
    
    print_separator()
