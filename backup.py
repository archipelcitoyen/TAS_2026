gdf = gpd.read_file(chemin_fichier)

# Vérifier et définir la projection si nécessaire
if gdf.crs is None:
    gdf.set_crs(epsg=2154, inplace=True)  # Lambert-93, projection courante en France

# Définir la palette de couleurs
#cmap = 'OrRd'  # Orange-Red, adaptée pour représenter des intensités

m = folium.Map(location=[43.6045, 1.4442], zoom_start=12, tiles=None)
folium.TileLayer(
    tiles='CartoDB positron',
    name='Fond de carte',
    control=False
).add_to(m)

colormap = cm.linear.YlOrRd_09.scale(0, 1)
colormap.caption = 'Valeur normalisée'
colormap.add_to(m)

# Chargement des données
gdf = gpd.read_file(chemin_fichier) #gpd.read_file("carreaux_toulouse_precarite.gpkg")

# Liste des variables à visualiser
variables = {
    "Indicateur d'invisibilisation": "indicateur_invisibilisation",
    "Ménages pauvres": 'norm_pct_men_pauvres',
    "Familles monoparentales": 'norm_pct_men_monoparentales',
    "Individus entre 18 et 24 ans": 'norm_pct_ind_18_24',
    "Logements sociaux": 'norm_pct_log_soc',
    "Ménages en logements collectifs": 'norm_pct_men_coll',
    "Taux de locataires": 'norm_pct_locataires'
}

for nom_couche, colonne in variables.items():
    fg = folium.FeatureGroup(name=nom_couche, show=(colonne == "indicateur_invisibilisation"))
    folium.GeoJson(
        gdf,
        style_function=lambda feature, col=colonne: {
            'fillColor': colormap(feature['properties'][col]) if feature['properties'][col] is not None else '#gray',
            'color': 'black',
            'weight': 0.5,
            'fillOpacity': 0.7
        },
        tooltip=folium.GeoJsonTooltip(fields=[colonne], aliases=[nom_couche])
    ).add_to(fg)
    fg.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)
m.save("carte_invisibilisation_toulouse.html")