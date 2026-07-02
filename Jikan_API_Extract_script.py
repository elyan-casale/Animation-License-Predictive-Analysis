import requests
import pandas as pd
import time
import re

anime_data = []
base_url = "https://api.jikan.moe/v4/anime"

page = 1
has_next_page = True # Variable qui va contrôler notre boucle

print("Début de l'extraction massive... Cela va prendre quelques minutes.")

while has_next_page:
    params = {
        'page': page,
        'type': 'tv',
        'order_by': 'popularity',
        'sort': 'asc'
    }
    
    response = requests.get(base_url, params=params)
    
    # Code 200 = Tout va bien
    if response.status_code == 200:
        json_data = response.json()
        data = json_data.get('data', [])
        
        for anime in data:
            titre = anime.get('title', '')
            
            # FILTRE FRANCHISE : On ignore les suites
            if re.search(r'(season \d|part \d|2nd season|3rd season|4th season|the movie|ova)', titre, re.IGNORECASE):
                continue 
            
            # APLATISSEMENT
            studios = anime.get('studios', [])
            studio_principal = studios[0]['name'] if len(studios) > 0 else 'Unknown'
            
            genres = anime.get('genres', [])
            genre_principal = genres[0]['name'] if len(genres) > 0 else 'Unknown'
            
            aired_from = anime.get('aired', {}).get('from', 'Unknown')
            
            anime_data.append({
                'Anime_ID': anime.get('mal_id'),
                'Titre': titre,
                'Score': anime.get('score'),
                'Nombre_Votants': anime.get('scored_by'),
                'Nombre_Membres': anime.get('members'),
                'Favoris': anime.get('favorites'),
                'Nombre_Episodes': anime.get('episodes'),
                'Duree_Brute': anime.get('duration'),
                'Source': anime.get('source'),
                'Status': anime.get('status'),
                'Rating': anime.get('rating'),
                'Date_Sortie': aired_from,
                'Saison': anime.get('season'),
                'Studio_Principal': studio_principal,
                'Genre_Principal': genre_principal
            })
            
        # VÉRIFICATION DE LA PAGINATION
        pagination = json_data.get('pagination', {})
        has_next_page = pagination.get('has_next_page', False)
        
        print(f"Page {page} traitée. Franchises conservées jusqu'à présent : {len(anime_data)}")
        page += 1
        
    # Code 429 = On va trop vite (Rate Limit de l'API)
    elif response.status_code == 429:
        print(f"Oups, on va trop vite ! Pause de 5 secondes...")
        time.sleep(5)
        # On ne change pas de page, la boucle va réessayer la même page
        
    else:
        print(f"Erreur inattendue sur la page {page} - Code: {response.status_code}")
        break
    
    # Règle d'or de courtoisie envers l'API (1.5 sec est plus sûr pour Jikan)
    time.sleep(1)

# Transformation et Sauvegarde
df = pd.DataFrame(anime_data)
fichier_sortie = r"C:\EPHEC\TFE\Travail\Shinpan_v2\jikan_donnees_brutes_franchises.csv"
df.to_csv(fichier_sortie, index=False, encoding='utf-8')

print(f"\nTerminé ! {len(df)} franchises uniques extraites et sauvegardées dans {fichier_sortie}.")