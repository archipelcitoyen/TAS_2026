import geopandas as gpd
import pandas as pd
import numpy as np
import zipfile
import os
import fiona
import random
from urllib.request import urlretrieve
from shapely.geometry import Point
import geopandas as gpd


def telecharger_donnees_insee(DATA_DIR):
    """Télécharge les données carroyées de l'INSEE à 200m"""
    
    print("Téléchargement des données carroyées INSEE 200m...")
    
    # URL de téléchargement des données carroyées 200m les plus récentes (2019)
    url_carreaux = "https://www.insee.fr/fr/statistiques/fichier/7655475/Filosofi2019_carreaux_200m_gpkg.zip"

    # Chemin local pour sauvegarder le fichier zip
    zip_path = os.path.join(DATA_DIR, "Filosofi2019_carreaux_200m_gpkg.zip")
    
    # Télécharger le fichier
    urlretrieve(url_carreaux, zip_path)
    
    # Extraire le contenu du zip
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)
    
    print("Téléchargement et extraction terminés.")

def charger_donnees_insee_local(chemin_geopackage):
    """Charge les données carroyées de l'INSEE à partir d'un fichier geopackage local"""
    
    print(f"Chargement des données carroyées INSEE 200m depuis le fichier local : {chemin_geopackage}")
    
    # Vérification que le fichier existe
    if not os.path.exists(chemin_geopackage):
        raise FileNotFoundError(f"Le fichier {chemin_geopackage} n'existe pas.")
    
    # Chargement du geopackage
    try:
        # Lister les couches disponibles dans le geopackage
        layers = fiona.listlayers(chemin_geopackage)
        print(f"Couches disponibles dans le geopackage : {layers}")
        
        # Charger la première couche (ou spécifier le nom si connu)
        layer_name = layers[0]
        carreaux_gdf = gpd.read_file(chemin_geopackage, layer=layer_name)
        
        print(f"Données chargées avec succès. {len(carreaux_gdf)} carreaux trouvés.")
        print(f"CRS des données : {carreaux_gdf.crs}")
        print(f"Colonnes disponibles : {carreaux_gdf.columns.tolist()}")
        
        return carreaux_gdf
    
    except Exception as e:
        print(f"Erreur lors du chargement du geopackage : {e}")
        raise


def calculer_indicateurs(carreaux):
    """
    Calcule les indicateurs de précarité pour chaque carreau.
    """

    # Pourcentage de ménages pauvres
    if 'men_pauv' in carreaux.columns and 'men' in carreaux.columns:
        carreaux['pct_men_pauvres'] = (carreaux['men_pauv'] / carreaux['men']) * 100
    else:
        carreaux['pct_men_pauvres'] = np.nan

    # Pourcentage de familles monoparentales
    if 'men_fmp' in carreaux.columns and 'men' in carreaux.columns:
        carreaux['pct_men_monoparentales'] = (carreaux['men_fmp'] / carreaux['men']) * 100
    else:
        carreaux['pct_men_monoparentales'] = np.nan

    # Pourcentage de jeunes adultes
    if 'ind_18_24' in carreaux.columns and 'ind' in carreaux.columns:
        carreaux['pct_ind_18_24'] = (carreaux['ind_18_24'] / carreaux['ind']) * 100
    else:
        carreaux['pct_ind_18_24'] = np.nan

    # Pourcentage de logement social
    if 'log_soc' in carreaux.columns and 'men' in carreaux.columns:
        carreaux['pct_log_soc'] = (carreaux['log_soc'] / (carreaux['log_av45'] + carreaux['log_45_70'] + carreaux['log_70_90'] + carreaux['log_ap90'] + carreaux['log_inc'])) * 100
    else:
        carreaux['pct_log_soc'] = np.nan

    # Pourcentage de ménages en logements collectifs
    if 'men_coll' in carreaux.columns and 'men' in carreaux.columns:
        carreaux['pct_men_coll'] = (carreaux['men_coll'] / carreaux['men']) * 100
    else:
        carreaux['pct_men_coll'] = np.nan

    # Pourcentage de locataires
    if 'men_prop' in carreaux.columns and 'men' in carreaux.columns:
        carreaux['pct_locataires'] = (1 - carreaux['men_prop'] / carreaux['men']) * 100
    else:
        carreaux['pct_locataires'] = np.nan

    return carreaux

def normaliser_indicateurs(carreaux):
    """
    Normalise les indicateurs de précarité pour chaque carreau.
    """
    def normaliser(serie):
        min_val = serie.min()
        max_val = serie.max()
        if pd.notnull(min_val) and pd.notnull(max_val) and max_val > min_val:
            return (serie - min_val) / (max_val - min_val)
        else:
            return pd.Series([0] * len(serie), index=serie.index)

    # Normalisation
    carreaux['norm_pct_men_pauvres'] = normaliser(carreaux['pct_men_pauvres'])
    carreaux['norm_pct_men_monoparentales'] = normaliser(carreaux['pct_men_monoparentales'])
    carreaux['norm_pct_ind_18_24'] = normaliser(carreaux['pct_ind_18_24'])
    carreaux['norm_pct_log_soc'] = normaliser(carreaux['pct_log_soc'])
    carreaux['norm_pct_men_coll'] = normaliser(carreaux['pct_men_coll'])
    carreaux['norm_pct_locataires'] = normaliser(carreaux['pct_locataires'])
    #carreaux['norm_revenu_moyen'] = 1 - normaliser(carreaux['revenu_moyen'])  # Inversion car revenu élevé = moins de précarité
    #carreaux['norm_pct_bas_revenus'] = normaliser(carreaux['pct_bas_revenus'])
    return carreaux


def calculer_indicateur_composite(carreaux):
    """
    Calcule l'indicateur composite d'invisibilisation pour chaque carreau.
    """
    # Pondérations
    poids_bruts = {
        'norm_pct_men_pauvres': 3,
        'norm_pct_men_monoparentales': 2,
        'norm_pct_ind_18_24': 1,
        'norm_pct_log_soc': 1,
        'norm_pct_men_coll': 1,
        'norm_pct_locataires': 1
    }
    somme_poids = sum(poids_bruts.values())
    poids = {variable: poids / somme_poids for variable, poids in poids_bruts.items()}

    # Calcul de l'indicateur composite
    indicateur = pd.Series(0, index=carreaux.index, dtype=float)
    poids_total = 0

    for indicateur_nom, p in poids.items():
        if indicateur_nom in carreaux.columns and not carreaux[indicateur_nom].isnull().all():
            indicateur += p * carreaux[indicateur_nom]
            poids_total += p

    if poids_total > 0:
        carreaux['indicateur_invisibilisation'] = indicateur / poids_total
    else:
        carreaux['indicateur_invisibilisation'] = 0

    return carreaux

def filtrer_carreaux(carreaux, seuil_population=20):
    """
    Filtre les carreaux ayant une population inférieure au seuil spécifié.
    """
    if 'ind' in carreaux.columns:
        return carreaux[carreaux['ind'] >= seuil_population]
    else:
        return carreaux

def random_point_in_polygon(polygon):
    min_x, min_y, max_x, max_y = polygon.bounds
    while True:
        point = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
        if polygon.contains(point):
            return point
        