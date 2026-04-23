# 🔗 Shortcut Creator Pro v3.0

Créateur, gestionnaire et éditeur de raccourcis Windows – PySide6 + pywin32.

## Fonctionnalités

- ✨ Création de raccourcis (fichiers, dossiers, URLs, commandes système)
- 📦 Création batch avec drag & drop (threadé)
- 🔍 Gestionnaire de raccourcis (scan, édition, suppression)
- 📋 Modèles et historique persistants (JSON atomique)
- 🧹 Nettoyeur de raccourcis cassés
- 🛠️ Outils système (chemins, vidage corbeille)
- 🎨 Thème clair/sombre (Catppuccin)
- 📌 Icône dans la barre des tâches
- 🛡️ Sécurité renforcée (validation URLs, flag admin, extensions dangereuses)

## Prérequis

- Python 3.10 ou supérieur
- Windows (les raccourcis .lnk et .url sont spécifiques)

## Installation

```bash
git clone https://github.com/votre-nom/ShortcutCreatorPro.git
cd ShortcutCreatorPro
pip install -r requirements.txt
python main.py
```

## Dépendances

- PySide6
- pywin32
- winshell (optionnel pour la corbeille et certains chemins)
