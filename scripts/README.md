# Visuels du profil

La bannière et les boutons sont des SVG locaux. Les icônes de technologies proviennent de [Devicon](https://github.com/devicons/devicon), sous licence MIT, conservée dans `assets/icons/LICENSE`.

`profile_assets.py` lit le nombre de dépôts publics et le calendrier de contributions affiché par GitHub. Le relevé est enregistré dans `assets/activity.json`, avec sa date. Si GitHub renvoie une page incomplète ou change le format de ses données, le script échoue et conserve le relevé précédent ; il ne remplace pas une valeur inconnue par zéro.

Pour actualiser les données :

```sh
python3 scripts/profile_assets.py
```

Pour régénérer les visuels sans requête réseau :

```sh
python3 scripts/profile_assets.py --offline
```

Pour vérifier le lecteur de calendrier et les SVG :

```sh
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Le workflow `Refresh profile activity` exécute la mise à jour chaque jour et peut être lancé manuellement. Il utilise le jeton intégré de GitHub Actions, sans clé externe. Les captures des applications utilisent des données de démonstration fictives.
