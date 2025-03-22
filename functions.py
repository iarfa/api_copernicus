"""
Fonctions utilisées dans le main
"""

import os

# Import de librairies
import cdsapi
import folium
import h3
import numpy as np

# Liste de fonctions


def grille_pays(data_pays, code_iso3a):
    """
    Objectif:
        Définir les coordonées d'un rectangle contenant le pays selectionné

    Paramètres :
        data_pays : Fichier contenant tous les pays, leur code d'identification et les coordonnées du rectangle
        code_iso3a : Code d'identification du pays
    """

    # Extraction des coordonnées
    lon_min = data_pays.loc[data_pays["ISO3"] == code_iso3a, "Lon_min"].values[0]
    lon_max = data_pays.loc[data_pays["ISO3"] == code_iso3a, "Lon_max"].values[0]
    lat_min = data_pays.loc[data_pays["ISO3"] == code_iso3a, "Lat_min"].values[0]
    lat_max = data_pays.loc[data_pays["ISO3"] == code_iso3a, "Lat_max"].values[0]

    # Renvoi de l'array dans l'ordre demandé par l'API Copernicus
    return [lat_max, lon_min, lat_min, lon_max]


def name_file(
    country_selected,
    year_selected,
    month_selected,
    day_selected,
    time_selected,
    choix,
    version=1,
):
    """
    Objectif :
        Créer un nom automatique lors de la création d'un fichier de téléchargement

    Paramètres :
        country_selected : pays selectionné
        year_selected : années sélectionnée
        month_selected : mois sélectionné
        day_selected : jour selectioné
        time_selected : intervalle de temps selectionné
        version : Si il y a plusieurs version du fichier (en particulier pour l'option part day)

    Attention : Si plusieurs jours, mois ou années sont sélectionnées, le fichier prend le nom du premier élément à chaque fois
    """

    # Le fichier prend en compte toute la jounrée ou seulement quelques heures
    if (
        len(set(time_selected)) == 24
    ):  # Si il y a 24 valeurs différentes sur 24 possibles, alors toute la journée est sélectionnée
        type_day = "all_day"
    else:
        type_day = "part_day_v" + str(version)

    # Nom du fichier
    final_name = (
        "era_data_"
        + str(country_selected)
        + "_"
        + str(year_selected[0])
        + "_"
        + str(month_selected[0])
        + "_"
        + str(day_selected[0])
        + "_"
        + type_day
        + "_"
        + str(choix)
        + ".nc"
    )

    return final_name


def choix_variable(choix):
    """
    Objectif : Sélectionner les variables de l'API en fonction du choix utilisateur

    Paramètrs:
        choix : Choix de l'utilisateur entre soutenu_10m, soutenu_100m, rafale
    """

    if choix == "soutenu_10m":
        variables_selected = ["10m_u_component_of_wind", "10m_v_component_of_wind"]
    elif choix == "soutenu_100m":
        variables_selected = ["100m_u_component_of_wind", "100m_v_component_of_wind"]
    elif choix == "rafale":
        variables_selected = ["instantaneous_10m_wind_gust"]
    else:
        raise ValueError(
            "Erreur : choix non reconnu. Utilisez 'rafale', 'soutenu_10m' ou 'soutenu_100m'."
        )

    return variables_selected


def requete_api(
    cdsapi_url,
    cdsapi_key,
    filename,
    name_folder,
    variables_selected,
    year_selected,
    month_selected,
    day_selected,
    time_selected,
    country_grid,
):
    """
    Objectif : Requeter l'API Copernicus en fonction des choix faits par l'utilisateur
    """
    # Nom du dataset de ré-analyse
    dataset = "reanalysis-era5-single-levels"

    # Appel de l'API
    client = cdsapi.Client(url=cdsapi_url,key=cdsapi_key)

    # Requête d'extraction (Show API request)
    request = {
        "product_type": ["reanalysis"],
        "variable": variables_selected,
        "year": year_selected,
        "month": month_selected,
        "day": day_selected,
        "time": time_selected,
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": country_grid,
    }

    # Sous dossier pour enregistrer les fichiers .nc
    folder = name_folder

    # Création du sous dossier si il n'existe pas
    os.makedirs(folder, exist_ok=True)
    full_path = os.path.join(folder, filename)

    # Récupération des données et téléchargement
    if filename in os.listdir():
        return f"Fichier {filename} déjà existant"
    else:
        client.retrieve(dataset, request).download(target=full_path)
        return f"Fichier {filename} a été téléchargé avec succès"

def traitement_data_wind(dataset, choix):
    """
    Objectif : Réaliser du traitement de données sur un dataset de vent (soutenu ou rafale)

    Paramètres :
        dataset : Fichier .nc téléchargé par l'API Copernicus
        choix : Choix de l'utilisateur afin de personnaliser le calcul de la magnitude de vent : w_mag
    """

    # Extraction des longitudes et latitudes: même si on prend plusieurs variables la grille reste identiques -> coordonnées de la 1ère variable
    longitudes = dataset[list(dataset.keys())[0]]["longitude"].values
    latitudes = dataset[list(dataset.keys())[0]]["latitude"].values

    # Pour un vent soutenu 10 m
    if choix == "soutenu_10m":

        # Valeurs de vent maximale à la journée selon la direction u -> format numpy.ndarray
        u_wind_time_value_ex = dataset["u10"].max(dim="valid_time").values

        # Valeurs de vent maximale à la journée selon la direction v -> format numpy.ndarray
        v_wind_time_value_ex = dataset["v10"].max(dim="valid_time").values

        # Magnitude du vent , w_mag = sqrt(u² +v²) et en km/H -> *3.6
        wind_mag = 3.6 * np.sqrt(u_wind_time_value_ex**2 + v_wind_time_value_ex**2)

    # Pour un vent soutenu 100 m
    elif choix == "soutenu_100m":

        # Valeurs de vent maximale à la journée selon la direction u -> format numpy.ndarray
        u_wind_time_value_ex = dataset["u100"].max(dim="valid_time").values

        # Valeurs de vent maximale à la journée selon la direction v -> format numpy.ndarray
        v_wind_time_value_ex = dataset["v100"].max(dim="valid_time").values

        # Magnitude du vent , w_mag = sqrt(u² +v²) et en km/H -> *3.6
        wind_mag = 3.6 * np.sqrt(u_wind_time_value_ex**2 + v_wind_time_value_ex**2)

    # Pour des rafales de vent
    elif choix == "rafale":

        # Magnitude du vent
        wind_mag = 3.6 * dataset["i10fg"].max(dim="valid_time").values

    else:
        raise ValueError(
            "Erreur : choix non reconnu. Utilisez 'rafale', 'soutenu_10m' ou 'soutenu_100m'."
        )

    return longitudes, latitudes, wind_mag


def map_center(country_grid):
    """
    Objectif : Initaliser la carte sur le centre du rectangle correspondant au pays

    Paramètres :
        country_grid : Grille lon_min, lon_max, lat_min, lat_max
    """
    # Centre
    lat_mid = (country_grid[0] + country_grid[2]) / 2  # Latitude centrale
    lon_mid = (country_grid[1] + country_grid[3]) / 2  # Longitude centrale
    map_center_pt = [lat_mid, lon_mid]

    return map_center_pt


def calcul_hexagone(latitudes, longitudes, wind, resolution_base, resolution_parent):
    """
    Objectif :
        Calcul les hexagones h3 à partir de la grille de longitude | latitude et associe à chaque hexagone le maximum de la valeur du vent

    Paramètres :
        latitudes : Liste de latitudes
        longitudes : Liste de longitudes
        wind : Matrice où chaque valeur i,j de vent correspond à une longitude i et une latitude j
    """

    # Dictionnaire pour stocker les hexagones de niveau 4 et leurs valeurs de vent agrégées
    parent_hex_values = {}

    # Ajout des hexagones (boucle longitude | latitude)
    for i in range(len(latitudes)):
        for j in range(len(longitudes)):

            # Pour chaque latitude et longitude -> Magnitude du vent
            lat = latitudes[i]
            lon = longitudes[j]
            wind_value = wind[i, j]

            # Conversion de la latitude et de la longitude en indice H3 (base)
            hex_index_base = h3.latlng_to_cell(lat, lon, resolution_base)

            # Calculer l'hexagone parent de niveau 4
            hex_index_parent = h3.cell_to_parent(hex_index_base, resolution_parent)

            # Ajouter ou mettre à jour la valeur maximale pour l'hexagone parent de niveau 4
            if hex_index_parent not in parent_hex_values:
                parent_hex_values[hex_index_parent] = wind_value
            else:
                parent_hex_values[hex_index_parent] = max(
                    parent_hex_values[hex_index_parent], wind_value
                )

    return parent_hex_values


def get_wind_color(wind_value, choix):
    """
    Objectif :
        Créer une légende et associer une couleur a une intensité de vent

    Paramètres :
        wind_value : Valeur du vent en km/h
        choix : Choix de l'utilisateur pour la variable a utiliser
    """

    if choix == "rafale":
        if wind_value < 31:
            return "green"
        elif wind_value < 71:
            return "yellow"
        elif wind_value < 101:
            return "orange"
        elif wind_value < 131:
            return "#FF8C00"  # Orange foncé
        else:
            return "red"

    elif choix == "soutenu_10m":
        if wind_value < 31:
            return "green"
        elif wind_value < 71:
            return "yellow"
        elif wind_value < 101:
            return "orange"
        elif wind_value < 131:
            return "#FF8C00"  # Orange foncé
        else:
            return "red"

    elif choix == "soutenu_100m":
        if wind_value < 31:
            return "green"
        elif wind_value < 71:
            return "yellow"
        elif wind_value < 131:
            return "orange"
        elif wind_value < 171:
            return "#FF8C00"  # Orange foncé
        else:
            return "red"

    else:
        raise ValueError(
            "Erreur : choix non reconnu. Utilisez 'rafale', 'soutenu_10m' ou 'soutenu_100m'."
        )


def affichage_hexagones(carte, hexagones, choix):
    """
    Objectif :
        Afficher les hexagones calculés sur une carte

    Paramètres :
        carte : Objet carte follium sur lesquels les hexagones seront affichés
        hexagones : Liste d'hexagones contenant la valeur du vent à afficher
        choix : Choix de l'utilisateur pour la variable a utiliser
    """

    for hex_index, max_wind_value in hexagones.items():
        # Coordonées de l'hexagone
        hex_boundary = h3.cell_to_boundary(hex_index)

        # Couleur de l'hexagone en fonction de la légende
        color = get_wind_color(max_wind_value, choix)

        # Création du polygone
        folium.Polygon(
            locations=hex_boundary,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.2,
            popup=f"Vent soutenu: {max_wind_value:.2f} km/h",
        ).add_to(carte)

    return carte


def legende_carte(choix):
    """
    Objectif : Adapter la légende à la variable utilisée (cf fichier Echelle_vent.xlsx)

    Paramètres :
        choix : choix de la variable de l'utilisateur
    """

    if choix == "rafale":
        legend_html = """
            <div style="position: fixed; 
                        bottom: 20px; left: 20px; width: 140x; height: 150px; 
                        background-color: white; border:2px solid grey; 
                        z-index:9999; font-size:14px;
                         padding: 10px;">
                <b style="display: inline-block; margin-bottom: 8px;">Légende Rafale</b><br>
                <i style="background:green; width: 20px; height: 20px; display: inline-block;"></i> < 30 km/h<br>
                <i style="background:yellow; width: 20px; height: 20px; display: inline-block;"></i> 31 - 70 km/h<br>
                <i style="background:orange; width: 20px; height: 20px; display: inline-block;"></i> 71 - 100 km/h<br>
                <i style="background:#FF8C00; width: 20px; height: 20px; display: inline-block;"></i> 101 - 130 km/h<br>
                <i style="background:red; width: 20px; height: 20px; display: inline-block;"></i> > 130 km/h
            </div>
        """

    elif choix == "soutenu_10m":
        legend_html = """
            <div style="position: fixed; 
                        bottom: 20px; left: 20px; width: 140px; height: 150px;
                        background-color: white; border:2px solid grey; 
                        z-index:9999; font-size:14px;
                        padding: 10px;">
                <b style="display: inline-block; margin-bottom: 8px;">Légende Vent soutenu 10m</b><br>
                <i style="background:green; width: 20px; height: 20px; display: inline-block;"></i> < 30 km/h<br>
                <i style="background:yellow; width: 20px; height: 20px; display: inline-block;"></i> 31 - 70 km/h<br>
                <i style="background:orange; width: 20px; height: 20px; display: inline-block;"></i> 71 - 100 km/h<br>
                <i style="background:#FF8C00; width: 20px; height: 20px; display: inline-block;"></i> 101 - 130 km/h<br>
                <i style="background:red; width: 20px; height: 20px; display: inline-block;"></i> > 130 km/h
            </div>
        """

    elif choix == "soutenu_100m":
        legend_html = """
            <div style="position: fixed; 
                        bottom: 20px; left: 20px; width: 140px; height: 150px;
                        background-color: white; border:2px solid grey; 
                        z-index:9999; font-size:14px;
                        padding: 10px;">
                <b style="display: inline-block; margin-bottom: 8px;">Légende Vent soutenu 100m</b><br>
                <i style="background:green; width: 20px; height: 20px; display: inline-block;"></i> < 30 km/h<br>
                <i style="background:yellow; width: 20px; height: 20px; display: inline-block;"></i> 31 - 70 km/h<br>
                <i style="background:orange; width: 20px; height: 20px; display: inline-block;"></i> 71 - 130 km/h<br>
                <i style="background:#FF8C00; width: 20px; height: 20px; display: inline-block;"></i> 131 - 170 km/h<br>
                <i style="background:red; width: 20px; height: 20px; display: inline-block;"></i> > 170 km/h
            </div>
        """

    else:
        raise ValueError(
            "Erreur : choix non reconnu. Utilisez 'rafale', 'soutenu_10m' ou 'soutenu_100m'."
        )

    return legend_html


def titre_carte(choix, country_selected, day_selected, month_selected, year_selected):
    """
    Objectif : Adapter la légende à la variable utilisée (cf fichier Echelle_vent.xlsx)

    Paramètres :
        choix : choix de la variable de l'utilisateur
    """

    # Titre
    titre = (
        "Carte "
        + str(choix)
        + " "
        + str(country_selected)
        + " "
        + str(day_selected[0])
        + "-"
        + str(month_selected[0])
        + "-"
        + str(year_selected[0])
    )

    # En HTML
    titre_html = f"""
     <h1 style='margin-left: 150px; text-align: left; font-size: 24px;'>{titre}</h1>
     """

    return titre_html
