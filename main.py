#### SECTION IMPORT DE LIBRAIRIES ####
import streamlit as st
import cdsapi
import xarray as xr
import folium
import numpy as np
import pandas as pd
import h3
import os
from datetime import datetime, timedelta

from streamlit import selectbox

#### SECTION INTRODUCITON ####

# Page introductive
st.title("API Copernicus ")


#### SECTION CHOIX DU PAYS #####

# Chargement de la base des pays
data_pays = pd.read_excel("Pays_grille.xlsx")

# Titre de la section
st.header("Choix du pays")

# Liste des pays disponibles
pays_list = data_pays["Pays"].tolist()

# Choix utilisateur
selected_country = st.selectbox("Choissisez un pays",pays_list)
st.write(f"Vous avez sélectionné : {selected_country}")
info_selected_country = data_pays[data_pays["Pays"] == selected_country].iloc[0]

# Informations relatives au pays choisi
code_ISO3A = info_selected_country["ISO3"]
lon_min = info_selected_country["Lon_min"]
lon_max = info_selected_country["Lon_max"]
lat_min = info_selected_country["Lat_min"]
lat_max = info_selected_country["Lat_max"]

### SELECTION CHOIX D UNE TEMPETE DE REFERENCE ####

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
    code_ISO3A_tempete = info_selected_tempete["ISO3A"]
    selected_date = info_selected_tempete["Date"]

    if code_ISO3A != code_ISO3A_tempete :
        st.warning(" Attention : Le pays choisi ne correspond pas au pays de la tempête sélectionnée")
