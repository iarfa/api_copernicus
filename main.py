#### SECTION IMPORT DE LIBRAIRIES ####
import os.path

import streamlit as st
import xarray as xr
import pandas as pd
from datetime import datetime, timedelta

from streamlit_folium import st_folium

from functions import *

#### SECTION INTRODUCITON ####

# Paramétrage
title_page_en_tete = "API Copernicus"
st.set_page_config(page_title=title_page_en_tete, page_icon=":tornado:", layout="wide", initial_sidebar_state="expanded")

# Page introductive
st.title("API données de vent Copernicus")
st.write("Bienvenue dans l'API de téléchargement Copernicus")
st.write("L'objectif est de télécharger des données provenenant de Copernicus et d'afficher des données de vent seln la date voulue ")

#### SECTION CHOIX DU PAYS #####

# Chargement de la base des pays
data_pays = pd.read_excel("Pays_grille.xlsx")

with st.sidebar:

    # Titre global
    st.title("Paramétrage")

    # Titre de la section
    st.header("Choix du pays")

    # Liste des pays disponibles
    pays_list = data_pays["Pays"].tolist()

    # Choix utilisateur
    selected_country = st.selectbox("Choissisez un pays",pays_list,index=pays_list.index("France")) # Par défaut France
    st.write(f"Vous avez sélectionné : {selected_country}")
    info_selected_country = data_pays[data_pays["Pays"] == selected_country].iloc[0]

    # Informations relatives au pays choisi
    country_selected = info_selected_country["ISO3"]

    # Grille du pays
    country_grid = grille_pays(data_pays,country_selected)

    ### SECTION CHOIX D UNE TEMPETE DE REFERENCE ####

    # Chargement de la base des tempêtes de références
    data_tempetes = pd.read_excel("Tempete_references.xlsx")
    data_tempetes['Date'] = pd.to_datetime(data_tempetes['Date']).dt.date

    # Titre de la section
    st.header("Choix de la date")

    # Choix utilisateur : Date d'une tempête de référence ou bien date choisie manuellement
    data_selection_method = st.radio("Méthode de sélection de la date :",("Date manuelle","Date à partir de tempêtes de références"))

    # Cas disponibles en fonction du choix de l'utilisateur (5 jours avant la date du jour max pour avoir les fichiers de réanalyse)

    # Sélection manuelle de la date
    if data_selection_method == "Date manuelle":
        selected_date = st.date_input('Sélectionne une date', min_value=datetime(1979, 1, 1), max_value=datetime.today() - timedelta(days=5))

    # Selection de la date à partir du fichier tempête
    else :

        # Plus de détail sur le dataframe
        if st.button("Plus de détails"):
            st.dataframe(data_tempetes.drop(columns=["ISO3A"]))

        # Liste de tempêtes
        tempete_list = data_tempetes["Nom de la Tempête"].tolist()
        selected_tempete = st.selectbox("Choissisez une tempête",tempete_list)
        st.write(f"Vous avez sélectionné : {selected_tempete}")
        info_selected_tempete = data_tempetes[data_tempetes["Nom de la Tempête"] == selected_tempete].iloc[0]

        # Informations extraites
        country_selected_tempete = info_selected_tempete["ISO3A"]
        selected_date = info_selected_tempete["Date"]

        if country_selected != country_selected_tempete :
            st.warning(" Attention : Le pays choisi ne correspond pas au pays de la tempête sélectionnée")
        else :
            st.success("Le pays sélectionné est compris dans la zone de la tempête")

    ### SECTION APPEL DE L'API ####

    # Titre de la section
    st.header("Appel de l'API Copernicus")

    # Choix de la variable vent
    wind_selected = st.radio("Choix de la variable de vent",("rafale","soutenu_10m","soutenu_100m"))

    # Extraction du jour, du mois et de l'année
    year_selected = [selected_date.year]
    month_selected = [selected_date.month]
    day_selected = [selected_date.day]

    # Extraction des heures
    hours = [
            "00:00", "01:00", "02:00",
            "03:00", "04:00", "05:00",
            "06:00", "07:00", "08:00",
            "09:00", "10:00", "11:00",
            "12:00", "13:00", "14:00",
            "15:00", "16:00", "17:00",
            "18:00", "19:00", "20:00",
            "21:00", "22:00", "23:00"]

    option_hours = st.radio("Choisissez une option :",("Selectionner toutes les heures","Selectionner des heures specifiques"))
    if option_hours == "Selectionner toutes les heures":
        time_selected = hours
    else:
        time_selected = st.multiselect("Choisissez des heures specifiques",hours)

    #### PARAMETRAGE HEXAGONE ####

    resolution_base = 15
    #resolution_parent = 4 # Fixé directement ou choix utilisateur

    # Titre de la section
    st.title("Selection de la résolution")
    st.write("Une résolution basse correspond à de grands hexagones (conseil : choisir la résolution 4 ou 5)")

    # Choix de la resolution parent
    resolution_parent = st.slider("Choisissez une résolution hexagonale",min_value=1,max_value=15,value=4)
    if resolution_parent > resolution_base:
        st.error(f"Erreur : La resolution doit être inférieure à {resolution_base}")
    else: # Affichage de la surface en km² ou m² en fonction de la résolution
        if resolution_parent <= 8:
            area_km2 = round(h3.cell_area(h3.latlng_to_cell(48.8566, 2.3522, resolution_parent),unit='km^2'))# surface d'un hexagone sur un pt aléatoire (Paris)
            st.success(f"Vous avez sélectionné la résolution {resolution_parent} d'une surface de {area_km2} km²")
        else :
            area_km2 = round(h3.cell_area(h3.latlng_to_cell(48.8566, 2.3522, resolution_parent),unit='m^2'))# surface d'un hexagone sur un pt aléatoire (Paris)
            st.success(f"Vous avez sélectionné la résolution {resolution_parent} d'une surface de {area_km2} m²")


#### TELECHARGEMENT DONNEES CLIMATIQUES ####

# Selection des variables
variables_selected = choix_variable(wind_selected)

# Nom du fichier pour le téléchargement
filename = name_file(country_selected,year_selected,month_selected,day_selected,time_selected,wind_selected,version=1)
name_folder = "wind_api_copernicus"  # Sous dossier dans lequel les fichiers .nc sont enregistrés

if st.button("Commencer le téléchargement"):

    # Vérification de l'existence du fichier
    if os.path.exists(os.path.join(name_folder,filename)):
        st.write("Le fichier existe déjà : ")


    else :
        st.write("Télechargement des données : ")
        requete_api(filename,name_folder,variables_selected,year_selected,month_selected,day_selected,time_selected,country_grid)

#### VISUALISATION CARTOGRAPHIQUE ####

# Titre de la carte
title_carte = titre_carte(wind_selected, country_selected, day_selected, month_selected, year_selected)
st.markdown(title_carte, unsafe_allow_html=True)

# Centre de la carte
map_center_pt = map_center(country_grid)

# Initialisation de la carte si elle n'existe pas encore dans session_state
if "carte" not in st.session_state:
    st.session_state.carte = folium.Map(location=map_center_pt, zoom_start=5)

# Séparation côté légende et côté carte car problème de compatibilité html pour légende directement sur la carte
legend_side, carte_side = st.columns([1, 3])

with legend_side:
    # Crée de l'espace artificiellement
    st.write(""); st.write(""); st.write(""); st.write(""); st.write(""); st.write(""); st.write("")
    st.write(""); st.write(""); st.write(""); st.write(""); st.write(""); st.write(""); st.write("")

    # Affichage de la légende en tant qu'image
    legend_html = legende_carte(wind_selected)
    st.components.v1.html(legend_html, width=200, height=220)

with carte_side:
    # Vérification si les données ont déjà été extraites et stockées dans session_state
    if "dataset" not in st.session_state:
        # Ouverture du fichier et extraction des données uniquement si cela n'a pas été fait auparavant
        dataset = xr.open_dataset(os.path.join(name_folder, filename))

        # Extraction de la longitude, latitude et magnitude de vent
        longitudes, latitudes, wind_mag = traitement_data_wind(dataset, wind_selected)

        # Fermeture du fichier
        dataset.close()

        # Stocker les résultats dans session_state
        st.session_state.dataset = dataset
        st.session_state.longitudes = longitudes
        st.session_state.latitudes = latitudes
        st.session_state.wind_mag = wind_mag
    else:
        # Utiliser les données déjà extraites
        longitudes = st.session_state.longitudes
        latitudes = st.session_state.latitudes
        wind_mag = st.session_state.wind_mag

    # Vérification si les hexagones ont déjà été calculés et stockés dans session_state
    if "hexagones" not in st.session_state:
        # Calcul des hexagones uniquement si cela n'a pas été fait auparavant
        hexagones = calcul_hexagone(latitudes, longitudes, wind_mag, resolution_base, resolution_parent)
        st.session_state.hexagones = hexagones
    else:
        hexagones = st.session_state.hexagones

    # Vérifier si la carte a déjà été mise à jour avec les hexagones
    if "carte_with_hexagons" not in st.session_state:
        # Si la carte n'a pas encore été mise à jour avec les hexagones, on l'ajoute
        st.session_state.carte = affichage_hexagones(st.session_state.carte, hexagones, wind_selected)
        st.session_state.carte_with_hexagons = True  # Marquer que la carte a été mise à jour

    # Affichage de la carte
    st_folium(st.session_state.carte, width=600, height=550)
