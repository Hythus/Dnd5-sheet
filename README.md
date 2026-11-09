# 🐉 Chronique du Héros — Fiche de Personnage D&D 5e Interactive

[![Ouvrir l'application Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dnd5-sheet.streamlit.app)
[![D&D 5e SRD](https://img.shields.io/badge/Règles-D%26D%205e%20Officiel%20FR-8b0000.svg)](https://dnd.wizards.com)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://python.org)

Application Web interactive motorisée par **Streamlit** et les règles officielles françaises de **Donjons & Dragons 5e (SRD & Extensions officielles)**.

---

## 🚀 Accès Direct à la Fiche en Ligne

N'importe quel joueur peut utiliser cette fiche directement dans son navigateur web, **sans rien installer, sans compte et sans exécuter de code** :

👉 **[Cliquez ici pour ouvrir la Fiche Interactive (dnd5-sheet.streamlit.app)](https://dnd5-sheet.streamlit.app)**

> 💡 **Prêt à l'emploi** : Le lien ouvre instantanément une fiche vierge interactive que vous pouvez remplir, sauvegarder en JSON, ou préremplir en important un PDF de personnage D&D 5e officiel.

<details>
<summary>🔧 <i>Pour les développeurs : Déployer votre propre instance sur Streamlit Cloud</i></summary>

Si vous avez forké ce dépôt et souhaitez héberger votre propre copie :
1. Rendez-vous sur [share.streamlit.io](https://share.streamlit.io) et connectez-vous avec GitHub.
2. Cliquez sur **« New app »**.
3. Renseignez :
   - **Repository** : `<votre-pseudo>/Dnd5-sheet`
   - **Branch** : `main`
   - **Main file path** : `app_dnd.py`
4. Cliquez sur **« Deploy! »**.
</details>

---

## ⚔️ Fonctionnalités Clés

- **🎨 Charte Graphique Thématique & Immersive** :
  - Design inspiré des grimoires anciens et parchemins officiels D&D 5e.
  - Palette et ambiance visuelle **dynamiques et adaptées selon la classe principale** (Barbare, Barde, Clerc, Druide, Ensorceleur, Guerrier, Magicien, Moine, Occultiste, Paladin, Rôdeur, Roublard, Artificier).

- **🛡️ Classes Officielles Françaises & Extensions** :
  - Les 13 classes avec terminologie officielle française (ex: *Occultiste* pour Warlock, *Artificier*...).
  - Sous-classes issues des manuels officiels et extensions (*Manuel des Joueurs / PHB*, *Guide des Monstres / XGtE*, *Chaudron Magique de Tasha / TCoE*, *Explorer's Guide to Wildemount / EGtW*).
  - Déblocage automatique des sous-classes à partir du **Niveau 3**.

- **🚀 Sorts à Plus Haut Niveau (Upcasting Dynamique)** :
  - Sélection de l'emplacement de sort utilisé pour l'incantation.
  - Calcul dynamique et automatique des dégâts, soins et cibles selon le niveau d'emplacement consommé.

- **📜 Aptitudes de Classe Évolutives & Cliquables** :
  - Chaque aptitude s'ouvre d'un clic pour révéler sa source, son type d'action et son **texte officiel complet**.
  - **Mise à l'échelle dynamique** selon les niveaux de classe (*Attaque Sournoise*, *Second Souffle*, *Rage*, *Points de Ki*, etc.).
  - Déblocage automatique des nouvelles aptitudes lors des montées de niveau.

- **❤️ Gestion des Points de Vie & PV Temporaires** :
  - PV Actuels et PV Max avec barre d'état dynamique.
  - **PV Temporaires (PV Temp)** : absorption automatique des dégâts en priorité selon les règles 5e.
  - Contrôles instantanés de dégâts et de soins.

- **💀 Jets de Sauvegarde contre la Mort (Death Saves)** :
  - Décompte visuel des 3 succès et 3 échecs.
  - Lancer de d20 interactif avec gestion des critiques (1 = 2 échecs, 20 = réveil à 1 PV !).

- **⛺ Repos Court & Repos Long** :
  - **Repos Court** : dépense de dés de vie par type (d12, d10, d8, d6) avec jet + modificateur de Constitution pour se soigner, et recharge automatique de la **Magie de Pacte de l'Occultiste** et des capacités courtes.
  - **Repos Long** : restauration intégrale des PV, suppression des PV temporaires, recharge de tous les emplacements de sorts, réinitialisation des jets de mort et récupération de la moitié des dés de vie dépensés.

- **🔮 Grimoire & Emplacements de Sorts Détaillés** :
  - Décompte dynamique des emplacements consommés et disponibles pour chaque niveau de sort.
  - Gestion spécifique de la **Magie de Pacte** (Occultiste).
  - Lancer de sort en un clic avec décompte automatique de l'emplacement.

- **📚 Compendium / Base de Données Intégrée** :
  - Ajout instantané d'armes, armures, sorts et compétences sans nécessiter de clé API externe.

- **📜 Import PDF & Import / Export JSON** :
  - **Import PDF** : analyse intelligente des formulaires AcroForm et du texte de votre feuille PDF pour préremplir automatiquement la fiche.
  - **JSON** : sauvegarde et restauration complète de votre personnage en un clic.

---

## 🚀 Utilisation en Local (Alternative)

### 1. Activer l'environnement virtuel
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Lancer l'application Web
```powershell
streamlit run app_dnd.py
```
L'application s'ouvrira à l'adresse : `http://localhost:8501`.

---

## 📁 Architecture du Projet

- `app_dnd.py` : Application principale Streamlit avec interface médiévale fantastique.
- `dnd_database.py` : Base de données des 13 classes, sous-classes, sorts, armes, armures, progression et aptitudes officielles en français.
- `dnd_importer.py` : Moteur d'importation PDF (AcroForm/texte) et JSON.
- `hythus_feuille_d_argent.json` : Fiche d'exemple complète de Hythus exportée en JSON.
- `requirements.txt` : Dépendances légères et optimisées pour le déploiement Cloud.
