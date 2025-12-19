# NTL-SysToolbox

> Outil d'exploitation et de supervision pour NordTransit Logistics
[2025-2026 ASRBD - Sujet MSPR TPRE511.pdf](https://github.com/user-attachments/files/24255750/2025-2026.ASRBD.-.Sujet.MSPR.TPRE511.pdf)

---

## À propos

**NTL-SysToolbox** est un outil en ligne de commande développé pour **NordTransit Logistics (NTL)** dans le cadre du projet MSPR - EPSI 2025-2026.

Cet utilitaire industrialise les vérifications d'exploitation, sécurise la gestion des sauvegardes de la base métier (WMS) et produit des audits d'obsolescence pour l'infrastructure informatique de NTL (siège à Lille + 3 entrepôts).

---

## Équipe Projet

**Promotion ASRBD 2025-2026 - EPSI**

| Membre          | Rôle                              |
|-----------------|-----------------------------------|
| **V. VERGULT**  | Chef de Projet / Développeur      |
| **C. REDOULES** | Développeur / Expert Réseau       |
| **M. BJAOUI**   | Développeur / Expert Base de Données |
| **S. TARSSE**   | Développeur / Expert Système      |

---

## Fonctionnalités

### Module 1 : Diagnostic
- ✓ Vérification des services AD/DNS
- ✓ Test de la base MySQL (WMS)
- ✓ Audit système Windows & Linux (OS, uptime, CPU, RAM, disques)

### Module 2 : Sauvegarde WMS
- ✓ Sauvegarde complète SQL
- ✓ Export de tables au format CSV

### Module 3 : Audit d'Obsolescence
- ✓ Scan réseau et détection d'OS
- ✓ Rapport des versions en fin de vie (EOL)
- ✓ Identification des composants obsolètes

---

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/votre-repo/NTL-SysToolbox.git
cd NTL-SysToolbox
```

**Aucune configuration requise !**

Les dépendances sont installées automatiquement au premier lancement.

---

## Utilisation

```bash
# Lancer l'application
start_ntl.bat
```

**C'est tout !** Le script batch s'occupe de :
- ✓ Vérifier et installer Python si nécessaire
- ✓ Installer automatiquement les dépendances
- ✓ Lancer le menu interactif

Les rapports sont générés dans le dossier `rapports/` au format JSON avec horodatage.

---

## Technologies

| Technologie                 | Usage                      |
|-----------------------------|----------------------------|
| Python 3.8+                 | Langage principal          |
| `pywinrm`                   | Connexion WinRM            |
| `mysql-connector-python`    | Connexion MySQL            |
| `python-nmap`               | Scan réseau                |

---

## Copyright

Projet développé dans le cadre de la formation **ASRBD 2025-2026** à l'**EPSI**.

**Développé avec ❤️ par l'équipe ASRBD 2025-2026**
© 2025 - Équipe NTL-SysToolbox

