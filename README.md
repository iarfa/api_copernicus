# API Copernicus - Téléchargement et Visualisation de Données de Vent

## Introduction
Bienvenue dans l'API de téléchargement Copernicus. L'objectif de ce projet est de télécharger des données de vent provenant de Copernicus et de les afficher selon la date souhaitée.

## Prérequis
Avant de commencer, assurez-vous d'avoir installé les bibliothèques suivantes :

- `os`
- `cdsapi`
- `folium`
- `h3`
- `numpy`
- `pandas`
- `streamlit`
- `xarray`

Vous pouvez les installer en utilisant `pip` :

```bash
pip install cdsapi folium h3 numpy pandas streamlit xarray
```

## Fonctionnement de l'API Copernicus
L'API Copernicus permet d'accéder à des données climatiques, notamment des données de vent, provenant de la base de données ERA5. Voici les étapes principales de son fonctionnement :

### 1. Sélection du Pays et de la Date
L'utilisateur choisit un pays et une date pour laquelle il souhaite obtenir des données de vent. Le pays est identifié par son code ISO3, et la date peut être sélectionnée manuellement ou à partir d'une liste de tempêtes de référence.

### 2. Définition des Coordonnées du Pays
Les coordonnées géographiques du pays sélectionné sont extraites d'un fichier contenant les informations de tous les pays. Ces coordonnées définissent un rectangle englobant le pays.

### 3. Choix des Variables de Vent
L'utilisateur choisit le type de données de vent qu'il souhaite obtenir :
- Vent soutenu à 10m
- Vent soutenu à 100m
- Rafales de vent

En fonction de ce choix, les variables correspondantes sont sélectionnées pour la requête.

### 4. Requête à l'API Copernicus
Une requête est envoyée à l'API Copernicus pour télécharger les données de vent. La requête inclut :
- Les variables sélectionnées
- Les coordonnées du pays
- La période de temps souhaitée

Les données sont téléchargées au format NetCDF.

### 5. Traitement des Données
Les données téléchargées sont traitées pour extraire les valeurs de vent maximales selon les directions `u` et `v`. La magnitude du vent est calculée à partir de ces valeurs.

### 6. Visualisation des Données
Les données de vent sont visualisées sur une carte en utilisant des hexagones H3. Chaque hexagone représente une zone géographique et est coloré en fonction de l'intensité du vent. La carte est centrée sur le pays sélectionné et affiche une légende indiquant les différentes intensités de vent.

## Exemple d'Utilisation

### 1. Sélection du Pays et de la Date
Vous choisissez **"France"** et une date spécifique, par exemple **le 15 mars 2023**.

### 2. Définition des Coordonnées du Pays
Les coordonnées de la France sont extraites : `[lat_max, lon_min, lat_min, lon_max]`.

### 3. Choix des Variables de Vent
Vous choisissez **"rafale"** pour obtenir les données de rafales de vent.

### 4. Requête à l'API Copernicus
Une requête est envoyée à l'API avec les paramètres sélectionnés. Les données sont téléchargées et enregistrées dans un fichier **NetCDF**.

### 5. Traitement des Données
Les données de vent sont traitées pour calculer la magnitude des rafales de vent.

### 6. Visualisation des Données
Les données sont affichées sur une carte avec des hexagones colorés en fonction de l'intensité des rafales de vent.

## Conclusion
L'API Copernicus est un outil permettant d'accéder et de visualiser des données climatiques. En suivant ces étapes, vous pouvez obtenir des informations détaillées sur les conditions de vent pour n'importe quel pays et date sélectionnés.
