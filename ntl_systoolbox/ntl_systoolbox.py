#!/usr/bin/env python3
import sys
import os

# --- Fonctions utilitaires ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_title(text):
    print("="*60)
    print(text.center(60))
    print("="*60)

def pause():
    input("\nAppuyez sur Entrée pour continuer...")

# --- Menu principal basique ---
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
            print("\n[INFO] Option sélectionnée : ", choix)
            pause()

if __name__ == "__main__":
    menu_principal()
