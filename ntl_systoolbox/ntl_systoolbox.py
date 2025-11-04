#!/usr/bin/env python3
import sys
import os

if __name__ == "__main__":
    print("NTL-SysToolbox - Script en cours de développement")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_title(text):
    print("="*60)
    print(text.center(60))
    print("="*60)

def pause():
    input("\nAppuyez sur Entrée pour continuer...")