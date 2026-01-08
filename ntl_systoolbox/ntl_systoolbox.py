#!/usr/bin/env python3
import sys
import os
import subprocess
import time

# --- Vérification et installation des dépendances ---
def installer_dependances():
    """Installe les dépendances nécessaires"""
    dependances = {
        'winrm': 'pywinrm',
        'paramiko': 'paramiko',
        'nmap': 'python-nmap'
    }
    
    for module, package in dependances.items():
        try:
            __import__(module)
        except ImportError:
            print(f"Installation de {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
            print(f"✓ {package} installé !")

# Installer les dépendances au démarrage
installer_dependances()

# --- Imports après installation ---
import winrm
import paramiko
import getpass

# --- Fichiers Modules ---
from modules.diagnostic_ad import verifier_services_ad_dns
from modules.systeme_windows import verifier_etat_windows
from modules.systeme_ubuntu import verifier_etat_ubuntu
from modules.sauvegarde_wms import (
    executer_backup_sql,
    executer_export_csv,
    afficher_contenu_inventory,
    tester_connexion_db,
    lister_backups
)

# --- Identifiants par défaut ---
USERS = {
    "admin": "admin",
    "technicien": "technicien"
}

MAX_TENTATIVES = 3

# --- Fonctions utilitaires ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_title(text):
    print("╔" + "═"*58 + "╗")
    print("║" + text.center(58) + "║")
    print("╚" + "═"*58 + "╝")

def pause():
    input("\nAppuyez sur Entrée pour continuer...")

# --- Authentification ---
def authentification():
    """Gère l'authentification de l'utilisateur"""
    tentatives = 0
    
    while tentatives < MAX_TENTATIVES:
        clear_screen()
        print("╔" + "═"*58 + "╗")
        print("║" + "NTL-SysToolbox - Authentification".center(58) + "║")
        print("╠" + "═"*58 + "╣")
        print("║" + " "*58 + "║")
        print("║" + "Veuillez vous identifier pour accéder au système".center(58) + "║")
        print("║" + " "*58 + "║")
        print("╚" + "═"*58 + "╝")
        print()
        
        username = input("Nom d'utilisateur : ").strip()
        password = getpass.getpass("Mot de passe      : ")
        
        # Vérification des identifiants
        if username in USERS and USERS[username] == password:
            clear_screen()
            print("\n✓ Authentification réussie !")
            print(f"✓ Bienvenue {username.upper()} !")
            time.sleep(1.5)
            return True
        else:
            tentatives += 1
            restantes = MAX_TENTATIVES - tentatives
            
            clear_screen()
            print("\n" + "="*60)
            print("✗ ERREUR D'AUTHENTIFICATION".center(60))
            print("="*60)
            print("\n[ERREUR] Identifiants incorrects !")
            print(f"[ERREUR] Nom d'utilisateur ou mot de passe invalide.")
            
            if restantes > 0:
                print(f"\n[INFO] Il vous reste {restantes} tentative(s).")
                time.sleep(2)
            else:
                print("\n[ERREUR] Nombre maximum de tentatives atteint !")
                print("[ERREUR] Accès refusé au système.")
                print("\n[INFO] Le programme va se fermer pour des raisons de sécurité.")
                time.sleep(3)
                return False
    
    return False

# --- Menu principal ---
def menu_principal():
    while True:
        clear_screen()
        print_title("NTL-SysToolbox")
        print("1) Module Diagnostic")
        print("2) Module de Sauvegarde WMS")
        print("3) Module Audit d'Obsolescence")
        print("0) Quitter le menu")
        
        choix = input("Votre choix : ").strip()
        
        if choix == "0":
            clear_screen()
            print_title("Merci d'avoir utilisé NTL-SysToolbox !")
            sys.exit(0)
        else:
            if choix == "1":
                sous_menu_diagnostic()
            elif choix == "2":
                sous_menu_sauvegarde()
            elif choix == "3":
                sous_menu_audit()
            else:
                print("\n[ERREUR] Choix invalide, réessayez.")
                pause()

# --- Sous-menus ---
def sous_menu_diagnostic():
    while True:
        clear_screen()
        print_title("Module Diagnostic")
        print("1) Vérifier services AD/DNS")
        print("2) Tester la connexion à la base de données")
        print("3) Vérifier ressources système Windows")
        print("4) Vérifier ressources système Ubuntu")
        print("0) Retour au menu principal")
        
        choix = input("Votre choix : ").strip()
        
        if choix == "0":
            return
        elif choix == "1":
            # APPEL DU FICHIER diagnostic_ad.py
            clear_screen()
            print_title("Vérification services AD/DNS")
            host = input("\nIP du contrôleur de domaine: ").strip()
            username = input("Nom d'utilisateur: ").strip()
            password = getpass.getpass("Mot de passe: ")
            print("\n")
            verifier_services_ad_dns(host, username, password)
            pause()
        elif choix == "2":
            # APPEL DU MODULE sauvegarde_wms.py - Test connexion DB
            clear_screen()
            print_title("Test de connexion à la base de données")
            tester_connexion_db()
            pause()
        elif choix == "3":
            # APPEL DU FICHIER systeme_windows.py
            clear_screen()
            print_title("Vérification ressources Windows Server")
            host = input("\nIP du serveur Windows: ").strip()
            username = input("Nom d'utilisateur: ").strip()
            password = getpass.getpass("Mot de passe: ")
            print("\n")
            verifier_etat_windows(host, username, password)
            pause()
        elif choix == "4":
            # APPEL DU FICHIER systeme_ubuntu.py
            clear_screen()
            print_title("Vérification ressources Ubuntu Server")
            host = input("\nIP du serveur Ubuntu: ").strip()
            username = input("Nom d'utilisateur SSH: ").strip()
            password = getpass.getpass("Mot de passe: ")
            print("\n")
            verifier_etat_ubuntu(host, username, password)
            pause()
        else:
            print("\n[INFO] Option Diagnostic sélectionnée : ", choix)
            pause()

def sous_menu_sauvegarde():
    """Menu de sauvegarde WMS avec appel des fonctions PowerShell"""
    while True:
        clear_screen()
        print_title("Module Sauvegarde WMS")
        print("1) Sauvegarde SQL complète")
        print("2) Export CSV de la table inventory")
        print("3) Afficher le contenu de la table inventory")
        print("4) Lister les sauvegardes disponibles")
        print("5) Tester la connexion à la base de données")
        print("0) Retour au menu principal")
        
        choix = input("Votre choix : ").strip()
        
        if choix == "0":
            return
        elif choix == "1":
            # Sauvegarde SQL complète via PowerShell
            clear_screen()
            print_title("Sauvegarde SQL Complète")
            executer_backup_sql()
            pause()
        elif choix == "2":
            # Export CSV via PowerShell
            clear_screen()
            print_title("Export CSV Inventory")
            executer_export_csv()
            pause()
        elif choix == "3":
            # Affichage du contenu de la table
            clear_screen()
            print_title("Contenu de la table Inventory")
            afficher_contenu_inventory()
            pause()
        elif choix == "4":
            # Liste des sauvegardes
            clear_screen()
            print_title("Sauvegardes Disponibles")
            lister_backups()
            pause()
        elif choix == "5":
            # Test de connexion
            clear_screen()
            print_title("Test Connexion Base de Données")
            tester_connexion_db()
            pause()
        else:
            print("\n[ERREUR] Choix invalide, réessayez.")
            pause()

def sous_menu_audit():
    while True:
        clear_screen()
        print_title("Module Audit Obsolescence")
        print("1) Inventaire réseau")
        print("2) Vérifier OS obsolètes")
        print("0) Retour au menu principal")
        
        choix = input("Votre choix : ").strip()
        
        if choix == "0":
            return
        else:
            print("\n[INFO] Option Audit sélectionnée : ", choix)
            pause()

if __name__ == "__main__":
    # Authentification obligatoire au démarrage
    if not authentification():
        clear_screen()
        print("\n[SYSTÈME] Fermeture du programme.")
        sys.exit(1)
    
    # Si authentification réussie, lancer le menu
    menu_principal()
