#!/usr/bin/env python3
import sys
import os
import subprocess

# --- Vérification et installation des dépendances ---
def installer_dependances():
    """Installe les dépendances nécessaires"""
    dependances = {
        'winrm': 'pywinrm',
        'paramiko': 'paramiko'
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
from modules.systeme_ubuntu import verifier_etat_ubuntu

# --- Fonctions utilitaires ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_title(text):
    print("="*60)
    print(text.center(60))
    print("="*60)

def pause():
    input("\nAppuyez sur Entrée pour continuer...")

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
        print("2) Tester MySQL")
        print("3) Vérifier ressources système Windows")
        print("4) Vérifier ressources système Ubuntu")
        print("0) Retour au menu principal")
        
        choix = input("Votre choix : ").strip()
        
        if choix == "0":
            return
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
    while True:
        clear_screen()
        print_title("Module Sauvegarde WMS")
        print("1) Export SQL")
        print("2) Export CSV")
        print("0) Retour au menu principal")
        
        choix = input("Votre choix : ").strip()
        
        if choix == "0":
            return
        else:
            print("\n[INFO] Option Sauvegarde sélectionnée : ", choix)
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
    menu_principal()
