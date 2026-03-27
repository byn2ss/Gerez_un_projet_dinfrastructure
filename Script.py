import pandas as pd 
import numpy as np
from faker import Faker
import random
import sqlite3

# --- 1. INITIALISATION ---
fake = Faker('fr_FR')
fichier_rh = pd.read_excel('Donnees_RH.xlsx') 
ID_client = fichier_rh["ID salarié"].tolist()

commentaires_par_sport = {
    "Course à pied": ["Super running matinal !", "Record battu sur 10km", "Dur sur la fin...", "Belle sortie en ville"],
    "Vélo": ["Trajet domicile-travail au top", "Pas trop de vent aujourd'hui", "Cuisses en feu !", "Vive le vélotaf"],
    "Randonnée": ["Vue magnifique au sommet", "Sentier un peu boueux", "Bonne rando en famille", "St Guilhem le Désert, je conseille !"],
    "Escalade": ["Belle séance de grimpe", "Nouvelle voie validée", "Travail de la force", "Super ambiance à la salle"],
    "Marche": ["Petite marche pour s'aérer", "Objectif 10 000 pas atteint", "Tranquille ce matin", "Bon pour la santé"]
}

type_sport = list(commentaires_par_sport.keys())
historique_sport = []

# --- 2. GÉNÉRATION DU FLUX SPORTIF (SIMULATION) ---
for i in range(2500): 
    id_elu = random.choice(ID_client)
    sport = random.choice(type_sport)
    commentaire_elu = random.choice(commentaires_par_sport[sport])
    
    nouvelle_activite = {
        "ID": i + 1,
        "ID salarié": id_elu,
        "Date de début": fake.date_between(start_date='-1y', end_date='today'),
        "Type": sport,
        "Distance (m)": random.randint(1000, 20000) if sport != "Escalade" else 0,
        "Commentaire": commentaire_elu
    }
    historique_sport.append(nouvelle_activite)

df_final = pd.DataFrame(historique_sport)

# --- 3. CALCULS DE COHÉRENCE ET PRIMES ---
fichier_rh['Distance_siege'] = np.random.randint(1, 15, size=len(fichier_rh))

def verifier_coherence(ligne): 
    mode = str(ligne['Moyen de déplacement']).lower()
    dist = ligne['Distance_siege']
    if ("marche" in mode or "running" in mode) and dist <= 15:
        return True
    elif ("vélo" in mode or "trottinette" in mode) and dist <= 25:
        return True
    return False

fichier_rh['Eligible_Prime'] = fichier_rh.apply(verifier_coherence, axis=1)

# Calcul de la prime de 5%
fichier_rh['Montant_Prime_Reel'] = np.where(
    fichier_rh['Eligible_Prime'] == True, 
    fichier_rh['Salaire brut'] * 0.05, 
    0
)

# --- 4. CALCULS BIEN-ÊTRE (15 activités) ---
stats_sport = df_final['ID salarié'].value_counts().reset_index()
stats_sport.columns = ['ID salarié', 'Nombre_Activites']
fichier_rh = fichier_rh.merge(stats_sport, on='ID salarié', how='left')
fichier_rh['Jour Bien être'] = np.where(fichier_rh['Nombre_Activites'] >= 15, 5, 0)

# --- 5. FLUX SLACK ---
df_slack = df_final.merge(fichier_rh[['ID salarié', 'Nom', 'Prénom']], on='ID salarié', how='left')
def generer_publication(ligne):
    prenom = ligne['Prénom']
    nom = ligne['Nom']
    sport = ligne['Type']
    distance_km = round(ligne['Distance (m)'] / 1000, 1)
    return f" Bravo {prenom} {nom} ! Une séance de {sport} de {distance_km} km. Quelle énergie ! "

df_slack['Publication'] = df_slack.apply(generer_publication, axis=1)

# ==========================================================
# --- 6. ÉTAPE FINALE : NETTOYAGE, SQL ET EXPORT CSV ---
# ==========================================================

# A. Nettoyage des colonnes et doublons
fichier_rh = fichier_rh.loc[:, ~fichier_rh.columns.duplicated()]
if 'eligible_prime' in fichier_rh.columns:
    fichier_rh = fichier_rh.drop(columns=['eligible_prime'])

# B. Conversion numérique stricte pour Power BI
cols_numeriques = ['Salaire brut', 'Distance_siege', 'Montant_Prime_Reel', 'Nombre_Activites', 'Jour Bien être']
for col in cols_numeriques:
    fichier_rh[col] = pd.to_numeric(fichier_rh[col], errors='coerce').fillna(0)

# C. Statut texte pour les filtres Power BI
fichier_rh['Statut_Eligibilite'] = np.where(fichier_rh['Eligible_Prime'] == True, "✅ Éligible", "❌ Non Éligible")

# D. Sauvegarde SQLite (Architecture Cible)
conn = sqlite3.connect('SportData_POC.db')
fichier_rh.to_sql('Reporting_RH', conn, if_exists='replace', index=False)
df_final.to_sql('Flux_Activites', conn, if_exists='replace', index=False)
conn.close()

# E. Export CSV "Format Français" (Point-virgule et Virgule)
colonnes_kpi = [
    'ID salarié', 'Nom', 'Prénom', 'Moyen de déplacement', 
    'Distance_siege', 'Statut_Eligibilite', 'Montant_Prime_Reel', 
    'Nombre_Activites', 'Jour Bien être'
]

fichier_rh[colonnes_kpi].to_csv('Reporting_RH_Final.csv', 
                                index=False, 
                                sep=';', 
                                decimal=',', 
                                encoding='utf-8-sig')

print("\n" + "="*40)
print("🚀 PIPELINE TERMINÉ AVEC SUCCÈS !")
print("- Base SQLite générée : SportData_POC.db")
print("- Fichier Power BI : Reporting_RH_Final.csv")
print("="*40)