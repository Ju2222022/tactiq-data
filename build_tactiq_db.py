import pandas as pd
import json
import uuid
import kagglehub
import os

# 1. CONFIGURATION
TOP_PLAYERS_COUNT = 500 # On garde les 500 meilleurs joueurs du monde pour commencer

def process_positions(pos_string):
    if not isinstance(pos_string, str): return ["CM"]
    # Les positions dans FIFA sont séparées par des virgules (ex: "ST, LW")
    positions = [p.strip().upper() for p in pos_string.split(',')]
    return positions

def build_database():
    print("⚽️ Téléchargement des données depuis Kaggle (EA FC 24)...")
    
    # Utilisation du dataset de référence
    path = kagglehub.dataset_download("rovnez/fc-26-fifa-26-player-data")
    csv_path = os.path.join(path, "male_players.csv") # ou le nom exact du fichier principal
    
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
        positions = process_positions(row.get('player_positions', 'CM'))
        primary_pos = positions[0]
        secondary_pos = positions[1:] if len(positions) > 1 else []
        
        # Création du dictionnaire joueur (Structure en Anglais)
        player = {
            "id": str(uuid.uuid4()),
            "name": str(row.get('short_name', 'Unknown')),
            "rating": int(row.get('overall', 70)),
            "position": primary_pos,
            "secondaryPositions": secondary_pos,
            "nationality": str(row.get('nationality_name', 'Unknown')),
            "club": str(row.get('club_name', 'Free Agent')),
            "league": str(row.get('league_name', 'Unknown')),
            "marketValue": int(row.get('value_eur', 0)),
            "stats": {
                "pace": int(row.get('pace', 50)),
                "shooting": int(row.get('shooting', 50)),
                "passing": int(row.get('passing', 50)),
                "dribbling": int(row.get('dribbling', 50)),
                "defending": int(row.get('defending', 50)),
                "physical": int(row.get('physic', 50)) # Note: c'est souvent 'physic' dans les CSV Kaggle
            }
        }
        players_list.append(player)
    
    # 4. SAUVEGARDE
    with open('players.json', 'w', encoding='utf-8') as f:
        json.dump(players_list, f, ensure_ascii=False, indent=4)
        
    print(f"✅ Terminé ! {len(players_list)} joueurs exportés pour TactIQ Eleven.")

if __name__ == "__main__":
    build_database()
