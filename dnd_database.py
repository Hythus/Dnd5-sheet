"""
Catalogue Officiel D&D 5e (SRD + Extensions) en Français
=========================================================
Contient :
- Les 13 classes avec leurs noms français officiels (dont Artificier, Occultiste...)
- Les sous-classes officielles et d'extensions (PHB, Tasha, Xanathar)
- Les dés de vie, caractéristiques de lanceur de sort, aptitudes clés
- Catalogue complet d'armes, armures et sorts avec descriptions
"""

# ------------------------------------------------------------------------------
# 1. CLASSES ET SOUS-CLASSES OFFICIELLES (FR)
# ------------------------------------------------------------------------------

CLASSES_DND = {
    "Barbare": {
        "hit_die": 12,
        "saving_throws": ["STR", "CON"],
        "spellcasting": None,
        "icon": "🪓",
        "theme": {"primary": "#8b0000", "secondary": "#b22222", "accent": "#ff8c00"},
        "subclasses": [
            "Voie du Berserker (PHB)",
            "Voie du Guerrier Totémique (PHB)",
            "Voie du Zélote (XGtE)",
            "Voie du Gardien Ancestral (XGtE)",
            "Voie de la Tempête (XGtE)",
            "Voie de la Bête (TCoE)",
            "Voie de la Magie Sauvage (TCoE)"
        ]
    },
    "Barde": {
        "hit_die": 8,
        "saving_throws": ["DEX", "CHA"],
        "spellcasting": "CHA",
        "icon": "🎶",
        "theme": {"primary": "#82243b", "secondary": "#b03554", "accent": "#f39c12"},
        "subclasses": [
            "Collège du Savoir (PHB)",
            "Collège de la Vaillance (PHB)",
            "Collège de l'Épée (XGtE)",
            "Collège du Glamour (XGtE)",
            "Collège des Chuchotements (XGtE)",
            "Collège de la Création (TCoE)",
            "Collège de l'Éloquence (TCoE)"
        ]
    },
    "Clerc": {
        "hit_die": 8,
        "saving_throws": ["WIS", "CHA"],
        "spellcasting": "WIS",
        "icon": "✨",
        "theme": {"primary": "#997300", "secondary": "#c69500", "accent": "#ffffff"},
        "subclasses": [
            "Domaine de la Vie (PHB)",
            "Domaine de la Lumière (PHB)",
            "Domaine de la Guerre (PHB)",
            "Domaine de la Tempête (PHB)",
            "Domaine de la Ruse (PHB)",
            "Domaine de la Nature (PHB)",
            "Domaine du Savoir (PHB)",
            "Domaine de la Forge (XGtE)",
            "Domaine de la Tombe (XGtE)",
            "Domaine de l'Ordre (TCoE)",
            "Domaine de la Paix (TCoE)",
            "Domaine du Crépuscule (TCoE)"
        ]
    },
    "Druide": {
        "hit_die": 8,
        "saving_throws": ["INT", "WIS"],
        "spellcasting": "WIS",
        "icon": "🌿",
        "theme": {"primary": "#1f4a2c", "secondary": "#317445", "accent": "#a6d608"},
        "subclasses": [
            "Cercle de la Terre (PHB)",
            "Cercle de la Lune (PHB)",
            "Cercle des Rêves (XGtE)",
            "Cercle du Berger (XGtE)",
            "Cercle des Spores (GGtR/TCoE)",
            "Cercle des Étoiles (TCoE)",
            "Cercle du Feu Sauvage (TCoE)"
        ]
    },
    "Ensorceleur": {
        "hit_die": 6,
        "saving_throws": ["CON", "CHA"],
        "spellcasting": "CHA",
        "icon": "🔮",
        "theme": {"primary": "#5c1d68", "secondary": "#8c2a9e", "accent": "#ff70f5"},
        "subclasses": [
            "Lignée Draconique (PHB)",
            "Magie Sauvage (PHB)",
            "Âme Divine (XGtE)",
            "Ombre Sinistre (XGtE)",
            "Sorcellerie Tempétueuse (XGtE)",
            "Âme Mécanique (TCoE)",
            "Esprit Aberrant (TCoE)"
        ]
    },
    "Guerrier": {
        "hit_die": 10,
        "saving_throws": ["STR", "CON"],
        "spellcasting": None,  # Sauf Chevalier Occulte (1/3 INT)
        "icon": "⚔️",
        "theme": {"primary": "#7a1c1c", "secondary": "#a82d2d", "accent": "#e5a93c"},
        "subclasses": [
            "Champion (PHB)",
            "Maître de Guerre (PHB)",
            "Chevalier Occulte (PHB)",
            "Archer Arcanique (XGtE)",
            "Cavalier (XGtE)",
            "Samouraï (XGtE)",
            "Guerrier Psi (TCoE)",
            "Chevalier Runique (TCoE)",
            "Écho Guerrier (EGtW)"
        ]
    },
    "Magicien": {
        "hit_die": 6,
        "saving_throws": ["INT", "WIS"],
        "spellcasting": "INT",
        "icon": "📜",
        "theme": {"primary": "#2d2459", "secondary": "#4b3d8f", "accent": "#80d0ff"},
        "subclasses": [
            "École d'Évocation (PHB)",
            "École d'Abjuration (PHB)",
            "École de Divination (PHB)",
            "École d'Enchantement (PHB)",
            "École d'Illusion (PHB)",
            "École de Nécromancie (PHB)",
            "École de Transmutation (PHB)",
            "École d'Invocation (PHB)",
            "Chantelame (SCAG/TCoE)",
            "Ordre des Scribes (TCoE)",
            "Guerre Magique (XGtE)",
            "Chronomancie (EGtW)"
        ]
    },
    "Moine": {
        "hit_die": 8,
        "saving_throws": ["STR", "DEX"],
        "spellcasting": None,
        "icon": "🥋",
        "theme": {"primary": "#2b5876", "secondary": "#4e4376", "accent": "#00d2ff"},
        "subclasses": [
            "Voie de la Paume Ouverte (PHB)",
            "Voie de l'Ombre (PHB)",
            "Voie des Quatre Éléments (PHB)",
            "Voie du Kensei (XGtE)",
            "Voie du Maître Ivre (XGtE)",
            "Voie de l'Âme Solaire (XGtE)",
            "Voie de la Miséricorde (TCoE)",
            "Voie du Soi Astral (TCoE)"
        ]
    },
    "Occultiste": {  # Nom officiel français du Warlock
        "hit_die": 8,
        "saving_throws": ["WIS", "CHA"],
        "spellcasting": "CHA",
        "pact_magic": True,  # Magie de pacte (recharge sur repos court !)
        "icon": "👁️",
        "theme": {"primary": "#1e3d36", "secondary": "#2e5c52", "accent": "#00ffb3"},
        "subclasses": [
            "Le Fiélon (PHB)",
            "Le Grand Ancien (PHB)",
            "L'Archifée (PHB)",
            "L'Inanimé / Lame Maudite (XGtE)",
            "Le Céleste (XGtE)",
            "Le Génie (TCoE)",
            "L'Insondable (TCoE)",
            "L'Immortel (SCAG)"
        ]
    },
    "Paladin": {
        "hit_die": 10,
        "saving_throws": ["WIS", "CHA"],
        "spellcasting": "CHA",
        "icon": "🛡️",
        "theme": {"primary": "#856018", "secondary": "#b58728", "accent": "#ffd700"},
        "subclasses": [
            "Serment de Dévotion (PHB)",
            "Serment des Anciens (PHB)",
            "Serment de Vengeance (PHB)",
            "Serment de Conquête (XGtE)",
            "Serment de Rédemption (XGtE)",
            "Serment de Gloire (TCoE)",
            "Serment des Vigilants (TCoE)",
            "Briseur de Serment (DMG)"
        ]
    },
    "Rôdeur": {
        "hit_die": 10,
        "saving_throws": ["STR", "DEX"],
        "spellcasting": "WIS",
        "icon": "🏹",
        "theme": {"primary": "#2b5329", "secondary": "#3d733a", "accent": "#d4af37"},
        "subclasses": [
            "Chasseur (PHB)",
            "Maître des Bêtes (PHB)",
            "Tueur de Monstres (XGtE)",
            "Traqueur Ténébreux (XGtE)",
            "Arpenteur d'Horizons (XGtE)",
            "Fey Wanderer / Errant Féérique (TCoE)",
            "Essaim d'Épines (TCoE)",
            "Drake Warden / Gardien Draconique (FTD)"
        ]
    },
    "Roublard": {
        "hit_die": 8,
        "saving_throws": ["DEX", "INT"],
        "spellcasting": None,  # Sauf Mystificateur arcanique (1/3 INT)
        "icon": "🗡️",
        "theme": {"primary": "#2a2d34", "secondary": "#494e5a", "accent": "#c0c0c0"},
        "subclasses": [
            "Voleur (PHB)",
            "Assassin (PHB)",
            "Mystificateur Arcanique (PHB)",
            "Bretteur (XGtE)",
            "Éclaireur (XGtE)",
            "Inquisiteur (XGtE)",
            "Cerveau (XGtE)",
            "Lame Fantôme (TCoE)",
            "Affranchi (TCoE)"
        ]
    },
    "Artificier": {  # Classe d'extension officielle (Eberron / Tasha)
        "hit_die": 8,
        "saving_throws": ["CON", "INT"],
        "spellcasting": "INT",
        "icon": "⚙️",
        "theme": {"primary": "#795548", "secondary": "#a1887f", "accent": "#ffb74d"},
        "subclasses": [
            "Alchimiste (TCoE)",
            "Armurier (TCoE)",
            "Artilleur (TCoE)",
            "Forgeron de Bataille (TCoE)"
        ]
    }
}

# ------------------------------------------------------------------------------
# 2. DICTIONNAIRE DÉTAILLÉ DES APTITUDES DE CLASSE & SOUS-CLASSE
# ------------------------------------------------------------------------------

FEATURES_DB = {
    "Attaque Sournoise (Sneak Attack)": {
        "source": "Roublard Niv 1",
        "type": "Attaque / Dégâts",
        "desc": "Une fois par tour, vous pouvez infliger des dégâts supplémentaires (1d6 au niv 1, +1d6 tous les 2 niveaux) à une créature touchée avec une arme de finesse ou à distance si vous avez l'avantage au jet d'attaque, ou si un allié se trouve à 1,5m de la cible et que vous n'avez pas de désavantage."
    },
    "Ruse (Cunning Action)": {
        "source": "Roublard Niv 2",
        "type": "Action Bonus",
        "desc": "Vous pouvez utiliser une action bonus à chacun de vos tours en combat pour Foncer (Dash), Se désengager (Disengage) ou Se cacher (Hide)."
    },
    "Sens du Danger (Danger Sense)": {
        "source": "Barbare Niv 2",
        "type": "Passif",
        "desc": "Vous avez un avantage aux jets de sauvegarde de Dextérité contre les effets que vous pouvez voir (pièges, sorts...)."
    },
    "Rage Barbare": {
        "source": "Barbare Niv 1",
        "type": "Action Bonus",
        "desc": "En combat, vous entrez dans une rage dévastatrice. Vous avez l'avantage aux tests et jets de sauvegarde de Force, un bonus aux dégâts de mêlée avec la Force (+2 à +4), et la résistance aux dégâts contondants, perforants et tranchants."
    },
    "Second Souffle (Second Wind)": {
        "source": "Guerrier Niv 1",
        "type": "Action Bonus (Repos court)",
        "desc": "Vous possédez une réserve d'endurance mobilisable pour vous protéger. À votre tour, vous pouvez utiliser une action bonus pour récupérer un nombre de PV égal à 1d10 + votre niveau de guerrier. Utilisable 1 fois par repos court ou long."
    },
    "Sursaut d'Activité (Action Surge)": {
        "source": "Guerrier Niv 2",
        "type": "Spécial (Repos court)",
        "desc": "Vous pouvez repousser vos limites pendant un instant. À votre tour, vous pouvez faire une action supplémentaire en plus de votre action normale et de votre éventuelle action bonus. Utilisable 1 fois par repos court ou long."
    },
    "Ennemi Juré (Favored Enemy)": {
        "source": "Rôdeur Niv 1",
        "type": "Exploration / RP",
        "desc": "Vous bénéficiez d'un avantage aux tests de Sagesse (Survie) pour pister vos ennemis jurés (ex: Fiélons, Humanoïdes...), ainsi qu'aux tests d'Intelligence pour vous remémorer des informations à leur sujet. Vous apprenez également une langue parlée par vos ennemis jurés."
    },
    "Vigilance Primitive (Primeval Awareness)": {
        "source": "Rôdeur Niv 3",
        "type": "Action",
        "desc": "Vous pouvez dépenser un emplacement de sort de rôdeur pour concentrer vos sens sur la région environnante. Pendant 1 minute par niveau d'emplacement dépensé, vous détectez si des aberrations, célestes, dragons, élémentaires, fées, fiélons ou morts-vivants se trouvent dans un rayon de 1,5 km."
    },
    "Sens du Chasseur (Hunter's Sense)": {
        "source": "Rôdeur (Tueur de Monstres)",
        "type": "Action Bonus",
        "desc": "Par une action bonus, examinez une créature à 18m. Vous apprenez immédiatement si elle a des immunités, résistances ou vulnérabilités aux dégâts, et lesquelles. Utilisable SAG fois par repos long."
    },
    "Proie du Tueur (Slayer's Prey)": {
        "source": "Rôdeur (Tueur de Monstres)",
        "type": "Action Bonus",
        "desc": "Par une action bonus, désignez une cible à 18m. La première fois à chaque tour où vous la touchez avec une attaque d'arme, elle subit 1d6 dégâts supplémentaires du type de l'arme."
    },
    "Inspiration Bardique": {
        "source": "Barde Niv 1",
        "type": "Action Bonus",
        "desc": "Vous pouvez inspirer autrui par vos mots ou votre musique. Une créature à 18m reçoit un dé d'inspiration (d6 à d12). Pendant 10 minutes, elle peut l'ajouter à un test de caractéristique, jet d'attaque ou jet de sauvegarde. Utilisable CHA fois par repos long (ou court dès le niveau 5)."
    },
    "Imposition des Mains (Lay on Hands)": {
        "source": "Paladin Niv 1",
        "type": "Action",
        "desc": "Votre toucher béni peut guérir les blessures. Vous disposez d'une réserve de soins égale à votre niveau de paladin x 5. Vous pouvez aussi dépenser 5 points pour guérir une maladie ou neutraliser un poison."
    },
    "Châtiment Divin (Divine Smite)": {
        "source": "Paladin Niv 2",
        "type": "Frappe en mêlée",
        "desc": "Quand vous touchez une créature avec une arme de corps à corps, vous pouvez dépenser un emplacement de sort pour infliger 2d8 dégâts radiants supplémentaires (sort niv 1) + 1d8 par niveau de sort supérieur (max 5d8), plus 1d8 additionnel contre morts-vivants ou fiélons."
    },
    "Restauration Arcanique (Arcane Recovery)": {
        "source": "Magicien Niv 1",
        "type": "Repos Court",
        "desc": "Une fois par jour lors d'un repos court, vous pouvez récupérer des emplacements de sorts dépensés dont le niveau combiné est égal ou inférieur à la moitié de votre niveau de magicien (arrondi au supérieur), aucun sort ne pouvant être de niveau 6 ou plus."
    },
    "Magie de Pacte (Pact Magic)": {
        "source": "Occultiste",
        "type": "Spécial",
        "desc": "Vos emplacements de sorts sont tous lancés au niveau le plus haut possible selon votre niveau d'occultiste, et ils se rechargent entièrement après un **Repos Court** (ou long) !"
    },
    "Infusions d'Artificier": {
        "source": "Artificier Niv 2",
        "type": "Artisanat magique",
        "desc": "Vous apprenez à imprégner des objets ordinaires d'effets magiques puissants (Arme améliorée +1, Défense améliorée +1, Sac sans fond, Répulseur de bouclier...). Rechargé après chaque repos long."
    },
    "Transe & Ascendance Féérique": {
        "source": "Elfe (Race)",
        "type": "Racial",
        "desc": "Vous avez l'avantage aux sauvegardes contre les effets de charme et la magie ne peut pas vous endormir. Vous ne dormez pas : 4 heures de méditation profonde remplacent 8 heures de sommeil humain."
    },
    "Vision dans le Noir (18m)": {
        "source": "Racial / Classe",
        "type": "Sens",
        "desc": "Vous voyez dans l'obscurité comme si vous étiez dans une lumière faible, et dans une lumière faible comme en plein jour, jusqu'à 18 mètres (nuances de gris uniquement)."
    },
    "Forme Sauvage (Wild Shape)": {
        "source": "Druide Niv 2",
        "type": "Action / Repos court",
        "desc": "Par une action magique, vous prenez la forme d'un animal que vous avez déjà vu. Utilisable 2 fois par repos court ou long. Vos PV sont temporairement remplacés par ceux de la bête."
    },
    "Canalisation d'Énergie Divine": {
        "source": "Clerc / Paladin Niv 2",
        "type": "Action / Repos court",
        "desc": "Vous canalisez l'énergie divine pour déclencher des effets sacrés (Renvoi des morts-vivants, Préservation de la vie, etc.). Utilisable 1 à 3 fois par repos court ou long."
    },
    "Points de Ki & Arts Martiaux": {
        "source": "Moine Niv 2",
        "type": "Ressource / Repos court",
        "desc": "Votre entraînement vous permet d'exploiter l'énergie mystique du Ki (nombre de points égal à votre niveau de moine). Dépensez des points pour Déluge de coups, Défense patiente ou Dérobade. Récupérés après un repos court !"
    },
    "Métamagie & Points de Sorcellerie": {
        "source": "Ensorceleur Niv 3",
        "type": "Magie spontanée",
        "desc": "Vous pouvez plier la trame de la magie à votre volonté grâce à vos points de sorcellerie (Sort subtil, Sort jumeau, Sort accéléré, Sort puissant...). Récupérés après un repos long."
    },
    "Échappatoire (Uncanny Dodge)": {
        "source": "Roublard Niv 5",
        "type": "Réaction",
        "desc": "Quand un attaquant que vous pouvez voir vous touche avec une attaque, vous pouvez utiliser votre réaction pour diviser par deux les dégâts infligés par cette attaque."
    },
    "Style de Combat": {
        "source": "Guerrier / Paladin / Rôdeur",
        "type": "Passif",
        "desc": "Vous adoptez un style de combat particulier : Archerie (+2 aux jets d'attaque à distance), Défense (+1 CA quand vous portez une armure), Duelliste (+2 aux dégâts avec une arme à 1 main), ou Armes à deux mains (relance les 1 et 2 aux dés de dégâts)."
    }
}

# ------------------------------------------------------------------------------
# 3. BASE DE DONNÉES DES ARMES OFFICIELLES (FR)
# ------------------------------------------------------------------------------

WEAPONS_DB = {
    "Dague": {"damage": "1d4", "type": "perforant", "finesse": True, "ranged": False, "weight": 0.5},
    "Rapière": {"damage": "1d8", "type": "perforant", "finesse": True, "ranged": False, "weight": 1.0},
    "Cimeterre": {"damage": "1d6", "type": "tranchant", "finesse": True, "ranged": False, "weight": 1.5},
    "Épée courte": {"damage": "1d6", "type": "perforant", "finesse": True, "ranged": False, "weight": 1.0},
    "Épée longue": {"damage": "1d8", "type": "tranchant", "finesse": False, "ranged": False, "weight": 1.5},
    "Espadon (2 mains)": {"damage": "2d6", "type": "tranchant", "finesse": False, "ranged": False, "weight": 3.0},
    "Hache d'armes": {"damage": "1d8", "type": "tranchant", "finesse": False, "ranged": False, "weight": 2.0},
    "Grande hache": {"damage": "1d12", "type": "tranchant", "finesse": False, "ranged": False, "weight": 3.5},
    "Coutille": {"damage": "1d10", "type": "tranchant", "finesse": False, "ranged": False, "weight": 3.0},
    "Masse d'armes": {"damage": "1d6", "type": "contondant", "finesse": False, "ranged": False, "weight": 2.0},
    "Marteau de guerre": {"damage": "1d8", "type": "contondant", "finesse": False, "ranged": False, "weight": 2.0},
    "Bâton": {"damage": "1d6", "type": "contondant", "finesse": False, "ranged": False, "weight": 2.0},
    "Arc court": {"damage": "1d6", "type": "perforant", "finesse": False, "ranged": True, "weight": 1.0},
    "Arc long": {"damage": "1d8", "type": "perforant", "finesse": False, "ranged": True, "weight": 1.5},
    "Arbalète légère": {"damage": "1d8", "type": "perforant", "finesse": False, "ranged": True, "weight": 2.5},
    "Arbalète lourde": {"damage": "1d10", "type": "perforant", "finesse": False, "ranged": True, "weight": 4.5},
    "Arbalète de poing": {"damage": "1d6", "type": "perforant", "finesse": False, "ranged": True, "weight": 1.5},
}

# ------------------------------------------------------------------------------
# 4. BASE DE DONNÉES DES ARMURES (FR)
# ------------------------------------------------------------------------------

ARMORS_DB = {
    "Tissu / Vêtements": {"type": "Aucune", "base_ac": 10, "max_dex": None, "weight": 1.5},
    "Armure de cuir": {"type": "Légère", "base_ac": 11, "max_dex": None, "weight": 5.0},
    "Armure de cuir clouté": {"type": "Légère", "base_ac": 12, "max_dex": None, "weight": 6.5},
    "Chemise de mailles": {"type": "Intermédiaire", "base_ac": 13, "max_dex": 2, "weight": 10.0},
    "Cuirasse": {"type": "Intermédiaire", "base_ac": 14, "max_dex": 2, "weight": 12.0},
    "Demi-plaque": {"type": "Intermédiaire", "base_ac": 15, "max_dex": 2, "weight": 20.0},
    "Cotte de mailles": {"type": "Lourde", "base_ac": 16, "max_dex": 0, "weight": 25.0},
    "Harnois / Plaques complètes": {"type": "Lourde", "base_ac": 18, "max_dex": 0, "weight": 30.0},
}

# ------------------------------------------------------------------------------
# 5. BASE DE DONNÉES DES SORTS OFFICIELS (FR)
# ------------------------------------------------------------------------------

SPELLS_DB = {
    # Niveau 0 (Tours de magie)
    "Rayon de givre": {"level": 0, "school": "Évocation", "time": "1 action", "range": "18 m", "conc": False, "desc": "Attaque à distance de sort : 1d8 dégâts de froid et réduit la vitesse de 3m."},
    "Trait de feu": {"level": 0, "school": "Évocation", "time": "1 action", "range": "36 m", "conc": False, "desc": "Attaque de sort à distance infligeant 1d10 dégâts de feu."},
    "Décharge occulte (Eldritch Blast)": {"level": 0, "school": "Évocation", "time": "1 action", "range": "36 m", "conc": False, "desc": "Rayon d'énergie crépitante infligeant 1d10 dégâts de force (lance plusieurs rayons à plus haut niveau)."},
    "Lumière": {"level": 0, "school": "Évocation", "time": "1 action", "range": "Contact", "conc": False, "desc": "Fait luire un objet comme une torche pendant 1 heure."},
    "Assistance (Guidance)": {"level": 0, "school": "Divination", "time": "1 action", "range": "Contact", "conc": True, "desc": "La cible ajoute 1d4 à un test de caractéristique de son choix."},
    
    # Niveau 1
    "Marque du Chasseur": {"level": 1, "school": "Divination", "time": "1 action bonus", "range": "27 m", "conc": True, "desc": "+1d6 dégâts sur chaque frappe contre la cible et avantage pour la pister."},
    "Baie nourricière (Goodberry)": {"level": 1, "school": "Transmutation", "time": "1 action", "range": "Contact", "conc": False, "desc": "Crée jusqu'à 10 baies magiques. Manger une baie restaure 1 PV et nourrit pour la journée."},
    "Grêle d'Épines": {"level": 1, "school": "Invocation", "time": "1 action bonus", "range": "Soi-même", "conc": True, "desc": "La prochaine attaque à distance déclenche une pluie d'épines infligeant 1d10 dégâts perforants en zone."},
    "Soin des blessures": {"level": 1, "school": "Évocation", "time": "1 action", "range": "Contact", "conc": False, "desc": "Restaure 1d8 + Modificateur de caractéristique magique PV à une créature touchée."},
    "Mot de guérison": {"level": 1, "school": "Évocation", "time": "1 action bonus", "range": "18 m", "conc": False, "desc": "Restaure 1d4 + Modificateur PV à distance par une action bonus."},
    "Projectile magique": {"level": 1, "school": "Évocation", "time": "1 action", "range": "36 m", "conc": False, "desc": "Crée 3 fléchettes d'énergie touchant automatiquement leurs cibles pour 1d4+1 dégâts de force chacune."},
    "Bouclier (Shield)": {"level": 1, "school": "Abjuration", "time": "1 réaction", "range": "Soi-même", "conc": False, "desc": "+5 à la CA jusqu'au début de votre prochain tour et bloque le sort Projectile magique."},

    # Niveau 2
    "Esprit Guérisseur (Healing Spirit)": {"level": 2, "school": "Invocation", "time": "1 action bonus", "range": "18 m", "conc": True, "desc": "Invoque un esprit féerique. Une créature entrant dans son espace récupère 1d6 PV (jusqu'à 1 + Modificateur de SAG fois)."},
    "Zone de vérité": {"level": 2, "school": "Enchantement", "time": "1 action", "range": "18 m", "conc": False, "desc": "Crée une zone de 4,5m de rayon dans laquelle nul ne peut prononcer un mensonge délibéré."},
    "Passage sans trace": {"level": 2, "school": "Abjuration", "time": "1 action", "range": "Soi-même", "conc": True, "desc": "Un voile d'ombres confère +10 aux tests de Dextérité (Discrétion) à tout le groupe à 9m."},
    "Fracassement (Shatter)": {"level": 2, "school": "Évocation", "time": "1 action", "range": "18 m", "conc": False, "desc": "Bruit assourdissant infligeant 3d8 dégâts de tonnerre en zone (sauvegarde CON pour moitié)."},
    "Rayon ardent (Scorching Ray)": {"level": 2, "school": "Évocation", "time": "1 action", "range": "36 m", "conc": False, "desc": "Lance 3 rayons de feu distincts infligeant chacun 2d6 dégâts de feu sur une attaque de sort."},
    "Invisibilité": {"level": 2, "school": "Illusion", "time": "1 action", "range": "Contact", "conc": True, "desc": "Une créature touchée devient invisible pendant 1 heure (prend fin si elle attaque ou lance un sort)."},
    
    # Niveau 3
    "Boule de feu (Fireball)": {"level": 3, "school": "Évocation", "time": "1 action", "range": "45 m", "conc": False, "desc": "Une explosion ardente déflagre dans un rayon de 6m infligeant 8d6 dégâts de feu (sauvegarde DEX pour moitié)."},
    "Hâte (Haste)": {"level": 3, "school": "Transmutation", "time": "1 action", "range": "9 m", "conc": True, "desc": "Double la vitesse de déplacement, confère +2 à la CA, avantage aux jets de DEX et une action supplémentaire par tour."},
    "Contresort (Counterspell)": {"level": 3, "school": "Abjuration", "time": "1 réaction", "range": "18 m", "conc": False, "desc": "Interrompt une créature en train de lancer un sort de niveau 3 ou inférieur (test de carac si niveau supérieur)."},
    "Esprits Gardiens": {"level": 3, "school": "Invocation", "time": "1 action", "range": "Soi-même (4,5m)", "conc": True, "desc": "Des esprits protecteurs tourbillonnent autour de vous. Les ennemis voient leur vitesse réduite de moitié et subissent 3d8 dégâts radiants ou nécrotiques."},
    "Éclair (Lightning Bolt)": {"level": 3, "school": "Évocation", "time": "1 action", "range": "Ligne de 30m", "conc": False, "desc": "Une ligne de foudre pure frappe toutes les créatures traversées pour 8d6 dégâts de foudre (sauvegarde DEX pour moitié)."},

    # Niveau 4
    "Porte dimensionnelle": {"level": 4, "school": "Invocation", "time": "1 action", "range": "150 m", "conc": False, "desc": "Vous vous téléportez instantanément jusqu'à 150m, en emmenant éventuellement un allié de votre taille consentant."},
    "Métamorphose (Polymorph)": {"level": 4, "school": "Transmutation", "time": "1 action", "range": "18 m", "conc": True, "desc": "Transforme une créature en bête dont le FP est inférieur ou égal au niveau de la cible (ex: Tyranosaure, Mammouth...)."},

    # Niveau 5
    "Cône de froid": {"level": 5, "school": "Évocation", "time": "1 action", "range": "Cône de 18m", "conc": False, "desc": "Un souffle glacial infligeant 8d8 dégâts de froid aux cibles dans la zone (sauvegarde CON pour moitié)."},
    "Soins de masse": {"level": 5, "school": "Évocation", "time": "1 action", "range": "18 m", "conc": False, "desc": "Restaure 3d8 + modificateur de sort à un maximum de six créatures visibles dans la portée."}
}

# ------------------------------------------------------------------------------
# 6. CALCULATEURS DE DÉS DE VIE & EMPLACEMENTS DE SORTS OFFICIELS
# ------------------------------------------------------------------------------

def get_class_hit_die(class_name: str) -> str:
    """Retourne la désignation du dé de vie pour une classe donnée."""
    data = CLASSES_DND.get(class_name)
    if data:
        return f"d{data['hit_die']}"
    return "d8"

def get_total_hit_dice(classes: dict) -> dict:
    """Retourne la réserve totale de dés de vie par type de dé (ex: {'d10': 5, 'd8': 2})."""
    pool = {}
    for cls, lvl in classes.items():
        hd = get_class_hit_die(cls)
        pool[hd] = pool.get(hd, 0) + lvl
    return pool

def calculate_spell_slots(classes: dict) -> dict:
    """
    Calcule les emplacements de sorts du personnage selon les règles multi-classes de D&D 5e.
    Retourne un dictionnaire {niveau_sort: nombre_emplacements}.
    """
    # 1. Calcul du niveau de lanceur de sort combiné
    full_casters = ["Barde", "Clerc", "Druide", "Ensorceleur", "Magicien"]
    half_casters = ["Paladin", "Rôdeur"]
    
    caster_level = 0
    for cls, lvl in classes.items():
        if cls in full_casters:
            caster_level += lvl
        elif cls in half_casters:
            caster_level += lvl // 2
        elif cls == "Artificier":
            caster_level += (lvl + 1) // 2

    # Table officielle multiclasse D&D 5e
    multiclass_table = {
        1: {1: 2},
        2: {1: 3},
        3: {1: 4, 2: 2},
        4: {1: 4, 2: 3},
        5: {1: 4, 2: 3, 3: 2},
        6: {1: 4, 2: 3, 3: 3},
        7: {1: 4, 2: 3, 3: 3, 4: 1},
        8: {1: 4, 2: 3, 3: 3, 4: 2},
        9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
        10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
        11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
        12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
        13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
        14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
        15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
        16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
        17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
        18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 1},
        19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 1, 8: 1, 9: 1},
        20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 3, 6: 2, 7: 2, 8: 1, 9: 1},
    }
    
    return multiclass_table.get(caster_level, {})

def calculate_pact_slots(classes: dict) -> tuple[int, int]:
    """
    Calcule les emplacements de Magie de Pacte (Occultiste).
    Retourne (nombre_emplacements, niveau_des_emplacements).
    """
    warlock_lvl = classes.get("Occultiste", 0)
    if warlock_lvl <= 0:
        return (0, 0)
    
    if warlock_lvl == 1:
        return (1, 1)
    elif warlock_lvl == 2:
        return (2, 1)
    elif warlock_lvl in [3, 4]:
        return (2, 2)
    elif warlock_lvl in [5, 6]:
        return (2, 3)
    elif warlock_lvl in [7, 8]:
        return (2, 4)
    elif warlock_lvl in range(9, 11):
        return (2, 5)
    elif warlock_lvl in range(11, 17):
        return (3, 5)
    else:
        return (4, 5)

