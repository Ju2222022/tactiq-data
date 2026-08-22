import pandas as pd
import json
import uuid
import kagglehub
import os
import glob # NOUVEAU: Pour chercher les fichiers dynamiquement

# 1. CONFIGURATION
TOP_PLAYERS_COUNT = 500 # On garde les 500 meilleurs joueurs du monde pour commencer

def process_positions(pos_string):
    # Sécurité anti-crash si la position est vide (NaN)
    if not isinstance(pos_string, str) or pd.isna(pos_string): 
        return ["CM"]
    
    positions = [p.strip().upper() for p in pos_string.split(',')]
    return positions

# Helpers de sécurité pour éviter les crashs sur les cellules vides (NaN)
def safe_int(val, default=50):
    if pd.isna(val): 
        return default
    try:
        return int(float(val))
    except:
        return default

def safe_str(val, default="Unknown"):
    if pd.isna(val): 
        return default
    return str(val)

def build_database():
    print("⚽️ Téléchargement des données depuis Kaggle (EA FC)...")
    
    # Utilisation du dataset de référence
    path = kagglehub.dataset_download("rovnez/fc-26-fifa-26-player-data")
    
    # NOUVEAU: Recherche dynamique du fichier CSV
    # On cherche tous les fichiers .csv dans le dossier téléchargé
    csv_files = glob.glob(os.path.join(path, "**/*.csv"), recursive=True)
    
    if not csv_files:
        raise FileNotFoundError(f"❌ ERREUR : Aucun fichier CSV trouvé dans {path}")
        
    # S'il y a plusieurs fichiers, on prend le plus lourd (la vraie DB des joueurs)
    csv_path = max(csv_files, key=os.path.getsize)
    
    print(f"📊 Fichier trouvé : {csv_path}. Début du traitement...")
    df = pd.read_csv(csv_path, low_memory=False)
    
    # Force toutes les colonnes en minuscules pour la sécurité
    df.columns = df.columns.str.lower()
    
    # 2. FILTRAGE
    # On trie par note globale (overall) et on prend les meilleurs
    df = df.sort_values('overall', ascending=False).head(TOP_PLAYERS_COUNT)
    
    # 3. CONSTRUCTION DU JSON
    players_list = []
    
    for index, row in df.iterrows():
        # Extraction des positions
        positions = process_positions(row.get('player_positions'))
        primary_pos = positions[0]
        secondary_pos = positions[1:] if len(positions) > 1 else []
        
        # Création du dictionnaire joueur avec nettoyage sécurisé
        player = {
            "id": str(uuid.uuid4()),
            "name": safe_str(row.get('short_name'), 'Unknown'),
            "rating": safe_int(row.get('overall'), 70),
            "position": primary_pos,
            "secondaryPositions": secondary_pos,
            "nationality": safe_str(row.get('nationality_name'), 'Unknown'),
            "club": safe_str(row.get('club_name'), 'Free Agent'),
            "league": safe_str(row.get('league_name'), 'Unknown'),
            "marketValue": safe_int(row.get('value_eur'), 0),
            "stats": {
                "pace": safe_int(row.get('pace'), 50),
                "shooting": safe_int(row.get('shooting'), 50),
                "passing": safe_int(row.get('passing'), 50),
                "dribbling": safe_int(row.get('dribbling'), 50),
                "defending": safe_int(row.get('defending'), 50),
                "physical": safe_int(row.get('physic'), 50) 
            }
        }
        players_list.append(player)
    
    # 4. SAUVEGARDE
    with open('players.json', 'w', encoding='utf-8') as f:
        json.dump(players_list, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Terminé ! {len(players_list)} joueurs exportés pour TactIQ Eleven.")

if __name__ == "__main__":
    build_database()
