# Gerez_un_projet_dinfrastructure

README : POC Avantages Sportifs - Sport Data Solution
🎯 Objectif du Projet
Ce projet est un Proof of Concept (POC) visant à automatiser le système de récompenses sportives pour les salariés de Sport Data Solution. Il permet de :

Valider la cohérence des déclarations des salariés (trajets domicile-travail).

Calculer l'impact financier des primes de mobilité (5%).

Attribuer des jours de repos "Bien-être" basés sur l'activité réelle.

Automatiser la communication interne via des messages Slack.

🏗️ Architecture de la Solution
Le pipeline suit une logique ETL (Extract, Transform, Load) orchestrée par Kestra :

Extraction : Lecture du fichier RH (Donnees_RH.xlsx) et génération de données sportives via Faker.

Transformation : Nettoyage, tests de cohérence géographique et calculs des primes.

Chargement : Exportation vers une base de données SQLite et des fichiers CSV pour PowerBI.

🛠️ Installation et Utilisation
1. Prérequis

Python 3.11+

Pip (gestionnaire de paquets)

2. Configuration de l'environnement

Pour garantir la robustesse et l'isolation du projet :

Bash
# Création de l'environnement virtuel
python3 -m venv venv

# Activation
source venv/bin/activate  # Sur Mac/Linux

# Installation des dépendances
pip install -r requirements.txt
3. Exécution du pipeline

Bash
python Script.py
Tests de Cohérence et Qualité (Data Quality)
Le projet intègre des barrières de sécurité pour éviter les erreurs de déclaration :

Marche/Running : Distance maximale autorisée de 15 km.

Vélo/Trottinette : Distance maximale autorisée de 25 km.

Validation SQL : Nettoyage automatique des colonnes dupliquées avant l'injection en base.

📊 Monitoring et Restitution
Ordonnancement : Le flux est piloté par Kestra pour surveiller l'état d'exécution et la volumétrie.

Visualisation : Un rapport PowerBI est connecté à la base SQLite pour suivre les KPI financiers en temps réel.

📂 Structure des fichiers
Plaintext
.
├── Donnees_RH.xlsx          # Source de données RH
├── Script.py                # Pipeline Python principal
├── requirements.txt         # Liste des dépendances
├── SportData_POC.db         # Base de données SQLite générée
└── Resultats_RH_Final.csv   # Export pour PowerBI
