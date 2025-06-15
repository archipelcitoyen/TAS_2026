# 🎯 Tirage au sort géo-social pour constituer le Collège Citoyen — Archipel Citoyen — Municipales 2026

Ce dépôt contient les scripts Python permettant d’identifier, à l’échelle de Toulouse, **des micro-zones urbaines invisibilisées**, pour y organiser des actions de porte-à-porte dans le cadre de la **construction d’un Collège Citoyen** en vue des élections municipales de 2026.

Nous avons exécuter le notebook `TAS_INSEE.ipynb` en direct lors d'un Grand Cercle d'Archipel Citoyen, et avons établi comme officiel les 15 points tirés à ce moment là :

```bash
1353     POINT (1.40889 43.6122)
671      POINT (1.4019 43.58236)
580      POINT (1.39798 43.5782)
104     POINT (1.46576 43.55752)
624     POINT (1.40058 43.58004)
498     POINT (1.41068 43.57581)
1760     POINT (1.44983 43.6402)
83       POINT (1.49972 43.5572)
979     POINT (1.39958 43.59465)
1030     POINT (1.41622 43.5979)
247     POINT (1.40059 43.56295)
1735    POINT (1.46608 43.64071)
300     POINT (1.48119 43.57149)
499      POINT (1.4125 43.57684)
665     POINT (1.38785 43.58079)
```

Vous pouvez les retrouver [sur la carte suivante](https://archipelcitoyen.github.io/TAS_2026/carte_invisibilisation_toulouse.html).

## 💡 Fondement théorique

Ce travail s’inspire (en le déformant à une maille beaucoup plus locale) du concept de **classe géo-sociale**, développé par Julia Cagé et Thomas Piketty ([2023](https://www.unehistoireduconflitpolitique.fr/glossaire.html)).  
L’idée : **ce que l’on vit est fortement lié à où l’on vit**. Le lieu de résidence concentre et cristallise des déterminants sociaux, économiques et politiques. Un carreau urbain peut donc porter en lui des inégalités invisibles aux échelles habituelles, et surtout permet de sortir des clichés que l'on peut avoir sur tel ou tel quartier, de la politique de la ville ou pas, pour s'ancrer dans une réalité statistique.

Nous avons donc croisé des données carroyées de l’INSEE à 200 m × 200 m (soit à peine 4 terrains de foot) pour créer un **indicateur d’invisibilisation**, que nous utilisons ensuite pour tirer au sort les zones d’investigation.

## 📊 Données sources

- **INSEE - Filosofi 2019**  
  [Données carroyées sur les revenus et la pauvreté](https://www.insee.fr/fr/statistiques/7655475?sommaire=7655515)  
  Dispositif : *Fichier localisé social et fiscal (Filosofi)*.

> 🕒 Ces données ne sont pas récentes (2019), mais les variables observés évoluent lentement, ce qui rend ces statistiques encore largement pertinentes pour une action en 2025.

## 🧩 Indicateurs utilisés et pondérations

À chaque carreau INSEE, nous attribuons un score composite construit à partir des variables suivantes, normalisées entre 0 et 1, puis pondérées :

| Indicateur                                 | Variable INSEE | Pondération |
|--------------------------------------------|----------------|-------------|
| % de ménages pauvres                       | `men_pauv`     | 3           |
| % de familles monoparentales               | `men_fmp`      | 2           |
| % de jeunes adultes (18–24 ans)            | `ind_18_24`    | 1           |
| % de logements sociaux                     | `log_soc`      | 2           |
| % de ménages en habitat collectif          | `men_coll`     | 1           |

Le score final (indicateur d'invisibilisation) est ensuite **filtré** : nous ne gardons que les carreaux ayant un score ≥ **0.5**, pour y tirer au sort des points d’action.

## ⚙️ Étapes du processus automatisé

1. **Téléchargement et extraction** des données carroyées
2. **Filtrage géographique** (commune de Toulouse : code `31555`)
3. **Calcul des indicateurs** normalisés
4. **Agrégation pondérée** en un score d’invisibilisation
5. **Filtrage** des carreaux ayant un score ≥ 0.5
6. **Tirage au sort** de `n=15` points dans ces carreaux
7. **Génération d'une carte interactive** (`carte_invisibilisation_toulouse.html`)

```

## 📦 Lancer le script

1. `pip install geopandas folium branca`
2. Executer le notebook `TAS_INSEE.ipynb`.