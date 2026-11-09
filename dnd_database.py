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
    },
    "Attaque Supplémentaire": {
        "source": "Guerrier / Rôdeur / Paladin / Barbare / Moine Niv 5",
        "type": "Passif de combat",
        "desc": "Vous pouvez attaquer deux fois au lieu d'une lorsque vous choisissez l'action Attaquer durant votre tour (trois fois au niveau 11 de Guerrier, quatre fois au niveau 20)."
    },
    "Dérobade (Evasion)": {
        "source": "Roublard / Moine Niv 7",
        "type": "Passif de défense",
        "desc": "Votre agilité instinctive vous permet d'esquiver certains effets de zone. Lorsque vous subissez un effet qui vous permet de faire un jet de sauvegarde de Dextérité pour ne subir que la moitié des dégâts (comme une boule de feu), vous ne subissez aucun dégât si vous réussissez votre jet, et seulement la moitié si vous échouez."
    },
    "Talent Fiable": {
        "source": "Roublard Niv 11",
        "type": "Passif d'expertise",
        "desc": "Vous avez tellement affiné vos compétences que vous pouvez compter sur votre régularité. Dès que vous faites un test de caractéristique qui intègre votre bonus de maîtrise, vous pouvez traiter tout résultat de 9 ou moins au d20 comme étant un 10."
    },
    "Défense sans armure (Barbare)": {
        "source": "Barbare Niv 1",
        "type": "Passif",
        "desc": "Tant que vous ne portez pas d'armure, votre classe d'armure est égale à 10 + modificateur de Dextérité + modificateur de Constitution. Vous pouvez utiliser un bouclier et continuer de bénéficier de cette aptitude."
    },
    "Attaque Téméraire (Reckless Attack)": {
        "source": "Barbare Niv 2",
        "type": "Attaque spéciale",
        "desc": "À votre tour, quand vous faites votre première attaque, vous pouvez décider d'attaquer avec témérité. Vous bénéficiez d'un avantage sur tous vos jets d'attaque au corps à corps utilisant la Force durant ce tour, mais les jets d'attaque contre vous bénéficient également d'un avantage jusqu'au début de votre prochain tour."
    },
    "Touche-à-tout (Jack of all Trades)": {
        "source": "Barde Niv 2",
        "type": "Passif",
        "desc": "Vous pouvez ajouter la moitié de votre bonus de maîtrise (arrondi à l'inférieur) à n'importe quel test de caractéristique qui n'inclut pas déjà votre bonus de maîtrise."
    },
    "Chant de Repos": {
        "source": "Barde Niv 2",
        "type": "Repos court",
        "desc": "Vous pouvez utiliser une musique ou des paroles apaisantes durant un repos court. Tout allié dépensant au moins un dé de vie pour récupérer des PV récupère 1d6 PV supplémentaires (1d8 au niv 9, 1d10 au niv 13, 1d12 au niv 17)."
    },
    "Source d'Inspiration": {
        "source": "Barde Niv 5",
        "type": "Recharge",
        "desc": "Vous récupérez désormais toutes vos utilisations d'Inspiration Bardique après avoir terminé un repos court OU un repos long !"
    },
    "Destruction des Morts-Vivants": {
        "source": "Clerc Niv 5",
        "type": "Spécial",
        "desc": "Quand un mort-vivant rate son jet de sauvegarde contre votre Renvoi des morts-vivants, la créature est instantanément détruite si son facteur de puissance (FP) est inférieur ou égal à 1/2 (FP 1 au niv 8, FP 2 au niv 11...)."
    },
    "Indomptable": {
        "source": "Guerrier Niv 9",
        "type": "Jet de sauvegarde (Repos long)",
        "desc": "Vous pouvez relancer un jet de sauvegarde que vous venez d'échouer. Vous devez utiliser le nouveau résultat. Utilisable 1 fois par repos long (2 fois au niv 13, 3 fois au niv 17)."
    },
    "Parade de Projectiles": {
        "source": "Moine Niv 3",
        "type": "Réaction",
        "desc": "Vous pouvez utiliser votre réaction pour dévier ou intercepter un projectile quand vous êtes touché par une attaque d'arme à distance. Les dégâts subis sont réduits de 1d10 + modificateur de Dextérité + votre niveau de moine. Si les dégâts tombent à 0, vous pouvez attraper le projectile et le renvoyer !"
    },
    "Chute Ralentie": {
        "source": "Moine Niv 4",
        "type": "Réaction",
        "desc": "Vous pouvez utiliser votre réaction quand vous tombez pour réduire les dégâts de chute que vous subissez d'une valeur égale à 5 fois votre niveau de moine."
    },
    "Frappe Étourdissante": {
        "source": "Moine Niv 5",
        "type": "Frappe martiale",
        "desc": "Quand vous touchez une créature avec une attaque d'arme au corps à corps, vous pouvez dépenser 1 point de Ki pour tenter d'étourdir la cible. Elle doit réussir une sauvegarde de Constitution ou être étourdie jusqu'à la fin de votre prochain tour."
    },
    "Invocations Occultes": {
        "source": "Occultiste Niv 2",
        "type": "Magie occulte",
        "desc": "Dans vos études des connaissances occultes, vous avez déterré des invocations mystiques qui vous confèrent des capacités magiques permanentes (Armure d'ombres, Décharge déchirante, Yeux du gardien runique...)."
    },
    "Don du Pacte": {
        "source": "Occultiste Niv 3",
        "type": "Pacte de classe",
        "desc": "Votre patron céleste, féerique ou démoniaque vous octroie une faveur : le Pacte de la Lame (arme magique invocable), le Pacte du Tome (grimoire d'ombres) ou le Pacte de la Chaîne (familier supérieur)."
    },
    "Aura de Protection": {
        "source": "Paladin Niv 6",
        "type": "Aura de soutien",
        "desc": "Dès qu'un jet de sauvegarde est nécessaire pour vous ou pour une créature amicale située à 3 mètres de vous, la créature gagne un bonus au jet de sauvegarde égal à votre modificateur de Charisme (minimum +1)."
    },
    "Explorateur-Né": {
        "source": "Rôdeur Niv 1",
        "type": "Exploration",
        "desc": "Vous êtes particulièrement familier avec un type d'environnement naturel (Forêt, Marais, Montagne...). Vous ignorez le terrain difficile pour votre groupe, ne pouvez vous perdre que par magie et restez alerte même en cueillant ou pistant."
    },
    "Foulée Terrestre": {
        "source": "Rôdeur Niv 8",
        "type": "Déplacement",
        "desc": "Se déplacer sur un terrain difficile non magique ne vous coûte aucun mouvement supplémentaire. Vous traversez également les plantes non magiques sans subir de ralentissement ni de dégâts."
    },
    "Jargon des Voleurs": {
        "source": "Roublard Niv 1",
        "type": "Secret / RP",
        "desc": "Mélange de dialecte, d'argot et de signes secrets qui vous permet de cacher des messages dans une conversation apparemment normale."
    },
    "Expertise": {
        "source": "Roublard / Barde",
        "type": "Maîtrise améliorée",
        "desc": "Votre bonus de maîtrise est doublé pour tout test de caractéristique qui fait appel aux compétences ou outils choisis (ex: Discrétion, Perception, Escamotage)."
    },
    "Bricolage Magique": {
        "source": "Artificier Niv 1",
        "type": "Artisanat",
        "desc": "Vous apprenez comment investir une étincelle de magie dans des objets ordinaires pour leur faire émettre de la lumière, un son enregistré, une odeur ou un message visuel."
    },
    "Outilleur Polyvalent": {
        "source": "Artificier Niv 3",
        "type": "Artisanat",
        "desc": "Vous pouvez créer par magie n'importe quel type d'outils d'artisan en 1 heure de travail ininterrompu."
    },
    "Trait de Génie": {
        "source": "Artificier Niv 7",
        "type": "Réaction",
        "desc": "Quand vous ou une autre créature visible à 9m fait un test de caractéristique ou un jet de sauvegarde, vous pouvez utiliser votre réaction pour ajouter votre modificateur d'Intelligence au résultat."
    },
    # Sous-classes
    "Mains Lestes (Fast Hands)": {
        "source": "Roublard (Voleur Niv 3)",
        "type": "Action bonus",
        "desc": "Vous pouvez utiliser l'action bonus accordée par votre Ruse pour faire un test de Dextérité (Escamotage), utiliser vos outils de voleur pour désamorcer un piège ou crocheter une serrure, ou réaliser l'action Utiliser un objet."
    },
    "Cambrioleur (Second-Story Work)": {
        "source": "Roublard (Voleur Niv 3)",
        "type": "Mouvement",
        "desc": "Vous gagnez la capacité d'escalader plus rapidement que la normale : grimper ne vous coûte plus de mouvement supplémentaire. De plus, lorsque vous faites un saut en longueur avec élan, la distance que vous couvrez augmente d'un nombre de mètres égal à votre modificateur de Dextérité."
    },
    "Assassinat (Avantage & Critique surprise)": {
        "source": "Roublard (Assassin Niv 3)",
        "type": "Embuscade fatale",
        "desc": "Vous avez l'avantage sur les jets d'attaque contre toute créature qui n'a pas encore agi durant le combat. De plus, tout coup qui touche une créature que vous surprenez est automatiquement un coup critique !"
    },
    "Critique Amélioré (19-20)": {
        "source": "Guerrier (Champion Niv 3)",
        "type": "Combat",
        "desc": "Vos attaques avec une arme obtiennent un coup critique sur un résultat de 19 ou 20 au dé à 20 faces."
    },
    "Supériorité Martiale": {
        "source": "Guerrier (Maître de Guerre Niv 3)",
        "type": "Manœuvres",
        "desc": "Vous disposez de 4 dés de supériorité (d8) pour exécuter des manœuvres martiales spéciales (Riposte, Feinte, Balayage, Désarmement...). Rechargés après un repos court !"
    },
    "Frénésie": {
        "source": "Barbare (Berserker Niv 3)",
        "type": "Rage sauvage",
        "desc": "Durant votre rage, vous pouvez entrer dans une frénésie sanguinaire. Vous pouvez effectuer une unique attaque d'arme au corps à corps par une action bonus à chacun de vos tours. Vous subissez 1 niveau d'épuisement à la fin de la rage."
    },
    "Esprit Totémique (Ours, Aigle ou Loup)": {
        "source": "Barbare (Guerrier Totémique Niv 3)",
        "type": "Totem",
        "desc": "L'Ours vous confère la résistance à TOUS les dégâts sauf les dégâts psychiques durant votre rage. L'Aigle vous permet de foncer en action bonus et désavantage les attaques d'opportunité contre vous. Le Loup donne l'avantage aux attaques de mêlée de vos alliés."
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
    "Illusion mineure": {"level": 0, "school": "Illusion", "time": "1 action", "range": "9 m", "conc": False, "desc": "Crée un son (du chuchotement au cri) ou l'image d'un objet (max cube de 1,5m) à portée pendant 1 minute."},
    
    # Niveau 1
    "Marque du Chasseur": {"level": 1, "school": "Divination", "time": "1 action bonus", "range": "27 m", "conc": True, "desc": "+1d6 dégâts sur chaque frappe contre la cible et avantage pour la pister."},
    "Baie nourricière (Goodberry)": {"level": 1, "school": "Transmutation", "time": "1 action", "range": "Contact", "conc": False, "desc": "Crée jusqu'à 10 baies magiques. Manger une baie rend 1 PV et nourrit pour la journée."},
    "Protection contre le mal et le bien": {"level": 1, "school": "Abjuration", "time": "1 action", "range": "Contact", "conc": True, "desc": "Protège une créature contre les aberrations, célestes, élémentaires, fées, fiélons et morts-vivants (désavantage aux attaques contre la cible, immunité charme/peur/possession)."},
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
# 5b. BASE DE DONNÉES DES OBJETS & ÉQUIPEMENTS STANDARDS (FR)
# ------------------------------------------------------------------------------

ITEMS_DB = {
    # Équipement d'aventurier
    "Sac à dos d'aventurier": {"category": "Aventurier", "weight": 2.5, "desc": "Sac spacieux permettant de ranger jusqu'à 15 kg ou 0,04 m³ d'équipement."},
    "Paillasse (sac de couchage)": {"category": "Aventurier", "weight": 3.0, "desc": "Lit pliable et chaud indispensable pour les repos longs."},
    "Corde en chanvre (15 m)": {"category": "Aventurier", "weight": 5.0, "desc": "Corde solide de 15m. Possède 2 points de vie et DC 17 FOR."},
    "Corde en soie (15 m)": {"category": "Aventurier", "weight": 2.5, "desc": "Corde légère en soie de 15m. Possède 2 points de vie et DC 17 FOR."},
    "Lanterne sourde": {"category": "Aventurier", "weight": 1.0, "desc": "Projette une lumière vive sur 18m et faible sur 18m supplémentaires. Un volet permet d'occulter la flamme."},
    "Torche (lot de 5)": {"category": "Aventurier", "weight": 2.5, "desc": "Brûle pendant 1 heure en produisant une lumière vive sur un rayon de 6m."},
    "Rations de voyage (1 jour)": {"category": "Aventurier", "weight": 1.0, "desc": "Nourriture sèche compacte suffisante pour un aventurier pendant un jour."},
    "Outre d'eau": {"category": "Aventurier", "weight": 2.5, "desc": "Gourde en cuir étanche pouvant contenir jusqu'à 2 litres d'eau."},
    "Boîte d'amadou": {"category": "Aventurier", "weight": 0.5, "desc": "Silex, briquet d'acier et amadou pour allumer un feu."},
    "Grappin": {"category": "Aventurier", "weight": 2.0, "desc": "Crochet d'acier à 4 dents permettant d'ancrer une corde."},
    "Pied-de-biche": {"category": "Aventurier", "weight": 2.5, "desc": "Donne l'avantage aux tests de Force lorsqu'on cherche à faire levier."},
    "Huile (flacon)": {"category": "Aventurier", "weight": 0.5, "desc": "Alimente une lanterne pendant 6h ou s'enflamme pour 5 dégâts."},
    "Menottes en fer": {"category": "Aventurier", "weight": 3.0, "desc": "Entraves métalliques robustes (DC 20 DEX pour s'échapper, DC 20 FOR pour briser)."},
    "Craie (morceau)": {"category": "Aventurier", "weight": 0.05, "desc": "Utile pour marquer les portes et repérer son chemin."},
    "Gamelle en métal": {"category": "Aventurier", "weight": 0.5, "desc": "Casserole en étain et couverts pour cuisiner au campement."},
    
    # Objets magiques & vêtements
    "Cape de protection (+1 CA & Sauvegardes)": {"category": "Objet magique", "weight": 0.5, "desc": "Harmonisation requise. Confère un bonus de +1 à la CA et à tous les jets de sauvegarde."},
    "Cape elfique (Avantage Discrétion)": {"category": "Objet magique", "weight": 0.5, "desc": "Harmonisation requise. Les créatures ont un désavantage aux tests de Perception pour vous voir et vous avez l'avantage en Discrétion."},
    "Anneau de protection (+1 CA & Sauvegardes)": {"category": "Objet magique", "weight": 0.05, "desc": "Harmonisation requise. Confère un bonus de +1 à la CA et aux jets de sauvegarde."},
    "Anneau d'action libre": {"category": "Objet magique", "weight": 0.05, "desc": "Harmonisation requise. Vous ignorez les terrains difficiles et ne pouvez être paralysé ni entravé par la magie."},
    "Bottes elfiques": {"category": "Objet magique", "weight": 0.5, "desc": "Vos bruits de pas sont étouffés. Vous bénéficiez de l'avantage aux tests de Dextérité (Discrétion)."},
    "Sac sans fond (Bag of Holding)": {"category": "Objet magique", "weight": 7.0, "desc": "Pèse toujours 7 kg mais peut contenir jusqu'à 250 kg et 1,8 m³ à l'intérieur."},
    "Vêtements fins de noble": {"category": "Vêtements", "weight": 3.0, "desc": "Habits soignés en soie et broderies."},
    "Vêtements de voyageur": {"category": "Vêtements", "weight": 2.0, "desc": "Bottes renforcées, cape chaude et pourpoint résistant."},
    
    # Potions & Consommables
    "Potion de soins (2d4+2)": {"category": "Potion", "weight": 0.2, "desc": "Action pour boire. Restaure 2d4 + 2 points de vie immédiatement."},
    "Potion de soins supérieure (4d4+4)": {"category": "Potion", "weight": 0.2, "desc": "Action pour boire. Restaure 4d4 + 4 points de vie immédiatement."},
    "Potion d'invisibilité": {"category": "Potion", "weight": 0.2, "desc": "Confère l'invisibilité pendant 1 heure ou jusqu'à attaque."},
    "Antidote (fiole)": {"category": "Potion", "weight": 0.1, "desc": "Boire confère l'avantage aux jets de sauvegarde contre le poison pendant 1 heure."},

    # Outils & Instruments
    "Outils de voleur": {"category": "Outils", "weight": 0.5, "desc": "Pieds-de-biche miniatures, crochets, limes et miroirs pour crocheter et désamorcer."},
    "Outils d'herboristerie": {"category": "Outils", "weight": 1.5, "desc": "Nécessaire pour récolter des herbes et confectionner des potions de soins et antidotes."},
    "Matériel d'alchimiste": {"category": "Outils", "weight": 4.0, "desc": "Alambics, cornues et réactifs pour produire de l'acide ou du feu grégeois."},
    "Luth ouvragé": {"category": "Instrument", "weight": 1.0, "desc": "Instrument de musique de barde servant de focaliseur d'incantation."}
}

def calculate_currency_total_po(curr: dict) -> float:
    """Calcule la valeur totale d'une bourse en Pièces d'Or (PO)."""
    po = float(curr.get("po", 0))
    pp = float(curr.get("pp", 0))
    pe = float(curr.get("pe", 0))
    pa = float(curr.get("pa", 0))
    pc = float(curr.get("pc", 0))
    return round(pp * 10.0 + po + pe * 0.5 + pa * 0.1 + pc * 0.01, 2)

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
    Calcule les emplacements de sorts du personnage selon les règles de D&D 5e.
    Gère les lanceurs complets, demi-lanceurs (Paladin, Rôdeur), Artificier et multiclassage.
    Retourne un dictionnaire {niveau_sort: nombre_emplacements}.
    """
    full_casters = ["Barde", "Clerc", "Druide", "Ensorceleur", "Magicien"]
    half_casters = ["Paladin", "Rôdeur"]
    
    # Table spécifique demi-lanceur (Rôdeur / Paladin)
    half_caster_table = {
        2: {1: 2},
        3: {1: 3},
        4: {1: 3},
        5: {1: 4, 2: 2},
        6: {1: 4, 2: 2},
        7: {1: 4, 2: 3},
        8: {1: 4, 2: 3},
        9: {1: 4, 2: 3, 3: 2},
        10: {1: 4, 2: 3, 3: 2},
        11: {1: 4, 2: 3, 3: 3},
        12: {1: 4, 2: 3, 3: 3},
        13: {1: 4, 2: 3, 3: 3, 4: 1},
        14: {1: 4, 2: 3, 3: 3, 4: 1},
        15: {1: 4, 2: 3, 3: 3, 4: 2},
        16: {1: 4, 2: 3, 3: 3, 4: 2},
        17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
        18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
        19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
        20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
    }

    # Si le personnage n'a qu'une seule classe de lanceur et que c'est un demi-lanceur
    active_half = [c for c in classes.keys() if c in half_casters]
    active_full = [c for c in classes.keys() if c in full_casters]

    if active_half and not active_full and "Artificier" not in classes:
        # Cas pur demi-lanceur (ex: Rôdeur 5 / Roublard 2)
        total_half_lvl = sum(classes[c] for c in active_half)
        return half_caster_table.get(total_half_lvl, {1: 2} if total_half_lvl >= 2 else {})

    # Sinon : calcul multiclasse standard
    caster_level = 0
    for cls, lvl in classes.items():
        if cls in full_casters:
            caster_level += lvl
        elif cls in half_casters:
            caster_level += lvl // 2
        elif cls == "Artificier":
            caster_level += (lvl + 1) // 2

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

# ------------------------------------------------------------------------------
# 7. RÈGLES DE LANCER DE SORTS À PLUS HAUT NIVEAU (UPCASTING DYNAMIQUE)
# ------------------------------------------------------------------------------

SPELL_UPCAST_RULES = {
    "Soin des blessures": {
        "base_level": 1,
        "format": lambda lvl: f"Restaure {lvl}d8 + Modificateur de sort PV à la créature touchée. (Lancé au Niveau {lvl} : +{lvl-1}d8)",
    },
    "Mot de guérison": {
        "base_level": 1,
        "format": lambda lvl: f"Restaure {lvl}d4 + Modificateur de sort PV à distance par action bonus. (Lancé au Niveau {lvl} : +{lvl-1}d4)",
    },
    "Projectile magique": {
        "base_level": 1,
        "format": lambda lvl: f"Crée {lvl + 2} fléchettes d'énergie touchant automatiquement pour {lvl + 2}d4+{lvl + 2} dégâts de force (1d4+1 chacune). (Lancé au Niveau {lvl} : +{lvl-1} fléchette(s))",
    },
    "Grêle d'Épines": {
        "base_level": 1,
        "format": lambda lvl: f"La prochaine attaque à distance déclenche une pluie d'épines infligeant {min(6, lvl)}d10 dégâts perforants en zone. (Lancé au Niveau {lvl})",
    },
    "Fracassement (Shatter)": {
        "base_level": 2,
        "format": lambda lvl: f"Bruit assourdissant infligeant {3 + (lvl - 2)}d8 dégâts de tonnerre en zone (sauvegarde CON pour moitié). (Lancé au Niveau {lvl} : +{lvl-2}d8)",
    },
    "Rayon ardent (Scorching Ray)": {
        "base_level": 2,
        "format": lambda lvl: f"Lance {3 + (lvl - 2)} rayons de feu distincts infligeant chacun 2d6 dégâts de feu (soit {(3 + (lvl - 2)) * 2}d6 au total). (Lancé au Niveau {lvl} : +{lvl-2} rayon(s))",
    },
    "Esprit Guérisseur (Healing Spirit)": {
        "base_level": 2,
        "format": lambda lvl: f"Invoque un esprit féerique. Chaque passage soigne {1 + (lvl - 2)}d6 PV. (Lancé au Niveau {lvl} : +{lvl-2}d6 de soin)",
    },
    "Boule de feu (Fireball)": {
        "base_level": 3,
        "format": lambda lvl: f"Explosion ardente dans un rayon de 6m infligeant {8 + (lvl - 3)}d6 dégâts de feu (sauvegarde DEX pour moitié). (Lancé au Niveau {lvl} : +{lvl-3}d6)",
    },
    "Éclair (Lightning Bolt)": {
        "base_level": 3,
        "format": lambda lvl: f"Ligne de foudre de 30m infligeant {8 + (lvl - 3)}d6 dégâts de foudre (sauvegarde DEX pour moitié). (Lancé au Niveau {lvl} : +{lvl-3}d6)",
    },
    "Esprits Gardiens": {
        "base_level": 3,
        "format": lambda lvl: f"Esprits protecteurs infligeant {3 + (lvl - 3)}d8 dégâts radiants ou nécrotiques et réduisant la vitesse de moitié. (Lancé au Niveau {lvl} : +{lvl-3}d8)",
    },
    "Cône de froid": {
        "base_level": 5,
        "format": lambda lvl: f"Souffle glacial infligeant {8 + (lvl - 5)}d8 dégâts de froid dans un cône de 18m. (Lancé au Niveau {lvl} : +{lvl-5}d8)",
    },
    "Soins de masse": {
        "base_level": 5,
        "format": lambda lvl: f"Restaure {3 + (lvl - 5)}d8 + Modificateur de sort à un maximum de six créatures. (Lancé au Niveau {lvl} : +{lvl-5}d8)",
    }
}

def get_dynamic_spell_description(spell_name: str, cast_level: int) -> tuple[str, bool]:
    """Retourne la description adaptée au niveau d'emplacement utilisé et un booléen indiquant si le sort est amplifié."""
    meta = SPELLS_DB.get(spell_name, {})
    base_level = meta.get("level", 1)
    base_desc = meta.get("desc", "")
    
    rule = SPELL_UPCAST_RULES.get(spell_name)
    if rule and cast_level > rule["base_level"]:
        return rule["format"](cast_level), True
    return base_desc, False

# ------------------------------------------------------------------------------
# 8. APTITUDES DYNAMIQUES & PROGRESSION SELON LE NIVEAU DE CLASSE
# ------------------------------------------------------------------------------

def get_dynamic_feature_info(feature_name: str, classes: dict) -> dict:
    """
    Calcule dynamiquement les dés de dégâts, soins, utilisations et bonus
    d'une aptitude en fonction du niveau du personnage dans sa classe.
    """
    import math
    base_feat = FEATURES_DB.get(feature_name, {
        "source": "Aptitude",
        "type": "Spécial",
        "desc": f"Capacité : {feature_name}."
    })
    
    # 1. Attaque Sournoise (Roublard)
    if "attaque sournoise" in feature_name.lower():
        rogue_lvl = classes.get("Roublard", 0)
        dice_count = max(1, math.ceil(rogue_lvl / 2)) if rogue_lvl > 0 else 1
        return {
            "title": f"Attaque Sournoise (+{dice_count}d6)",
            "source": f"Roublard Niv {rogue_lvl or 1}",
            "type": "Attaque / Dégâts",
            "desc": f"Une fois par tour, vous pouvez infliger **+{dice_count}d6** dégâts supplémentaires à une créature touchée avec une arme de finesse ou à distance si vous avez l'avantage au jet d'attaque (ou un allié à 1,5m sans désavantage). *(Calculé selon votre niveau {rogue_lvl} de Roublard)*."
        }
        
    # 2. Second Souffle (Guerrier)
    if "second souffle" in feature_name.lower():
        fighter_lvl = classes.get("Guerrier", 0)
        return {
            "title": f"Second Souffle (1d10 + {fighter_lvl} PV)",
            "source": f"Guerrier Niv {fighter_lvl or 1}",
            "type": "Action Bonus (Repos court)",
            "desc": f"Par une action bonus à votre tour, récupérez **1d10 + {fighter_lvl}** PV. Utilisable 1 fois par repos court ou long."
        }
        
    # 3. Sursaut d'Activité (Guerrier)
    if "sursaut" in feature_name.lower():
        fighter_lvl = classes.get("Guerrier", 0)
        uses = 2 if fighter_lvl >= 17 else 1
        return {
            "title": f"Sursaut d'Activité ({uses} util./repos court)",
            "source": f"Guerrier Niv {fighter_lvl or 1}",
            "type": "Spécial (Repos court)",
            "desc": f"Effectuez 1 action supplémentaire durant votre tour. Utilisable **{uses} fois** par repos court ou long."
        }

    # 4. Rage Barbare
    if "rage" in feature_name.lower():
        barb_lvl = classes.get("Barbare", 0)
        bonus = 4 if barb_lvl >= 16 else (3 if barb_lvl >= 9 else 2)
        rages = "Illimité" if barb_lvl >= 20 else (6 if barb_lvl >= 17 else (5 if barb_lvl >= 12 else (4 if barb_lvl >= 6 else (3 if barb_lvl >= 3 else 2))))
        return {
            "title": f"Rage Barbare (+{bonus} dégâts • {rages} rages/jour)",
            "source": f"Barbare Niv {barb_lvl or 1}",
            "type": "Action Bonus",
            "desc": f"En combat, vous entrez dans une rage dévastatrice : avantage aux jets et sauvegardes de Force, **+{bonus}** aux dégâts au corps à corps avec la Force, et résistance aux dégâts contondants, perforants et tranchants. Nombre d'utilisations : **{rages} par jour**."
        }

    # 5. Imposition des Mains (Paladin)
    if "imposition des mains" in feature_name.lower():
        pal_lvl = classes.get("Paladin", 0)
        pool = pal_lvl * 5
        return {
            "title": f"Imposition des Mains (Réserve : {pool} PV)",
            "source": f"Paladin Niv {pal_lvl or 1}",
            "type": "Action de soin",
            "desc": f"Vous disposez d'une réserve de soins magiques égale à **{pool} PV** (Paladin Niv {pal_lvl} x 5). Vous pouvez également dépenser 5 PV de la réserve pour soigner une maladie ou neutraliser un poison."
        }

    # 6. Inspiration Bardique
    if "inspiration bardique" in feature_name.lower():
        bard_lvl = classes.get("Barde", 0)
        die = "d12" if bard_lvl >= 15 else ("d10" if bard_lvl >= 10 else ("d8" if bard_lvl >= 5 else "d6"))
        rest_recharge = "repos court ou long" if bard_lvl >= 5 else "repos long"
        return {
            "title": f"Inspiration Bardique (Dé : {die})",
            "source": f"Barde Niv {bard_lvl or 1}",
            "type": "Action Bonus",
            "desc": f"Par une action bonus, donnez un dé d'inspiration **{die}** à un allié à 18m. Il pourra l'ajouter à un jet d'attaque, test de carac ou jet de sauvegarde dans les 10 min. Rechargeable par **{rest_recharge}**."
        }

    # 7. Points de Ki & Arts Martiaux (Moine)
    if "points de ki" in feature_name.lower() or "arts martiaux" in feature_name.lower():
        monk_lvl = classes.get("Moine", 0)
        die = "1d10" if monk_lvl >= 17 else ("1d8" if monk_lvl >= 11 else ("1d6" if monk_lvl >= 5 else "1d4"))
        return {
            "title": f"Points de Ki ({monk_lvl} pts) & Arts Martiaux ({die})",
            "source": f"Moine Niv {monk_lvl or 1}",
            "type": "Ressource martiale",
            "desc": f"Vous disposez de **{monk_lvl} points de Ki** (rechargeables sur repos court). Vos attaques à mains nues infligent **{die}** et vous pouvez attaquer en action bonus."
        }

    # 8. Restauration Arcanique (Magicien)
    if "restauration arcanique" in feature_name.lower():
        wiz_lvl = classes.get("Magicien", 0)
        max_slots = max(1, math.ceil(wiz_lvl / 2))
        return {
            "title": f"Restauration Arcanique (Max combiné : Niv {max_slots})",
            "source": f"Magicien Niv {wiz_lvl or 1}",
            "type": "Repos court (1/jour)",
            "desc": f"Lors d'un repos court une fois par jour, récupérez des emplacements de sorts dépensés dont la somme des niveaux est inférieure ou égale à **{max_slots}** (aucun emplacement de niveau 6+)."
        }

    # 9. Infusions d'Artificier
    if "infusions" in feature_name.lower():
        art_lvl = classes.get("Artificier", 0)
        known = 8 if art_lvl >= 18 else (7 if art_lvl >= 14 else (6 if art_lvl >= 10 else (5 if art_lvl >= 6 else 4)))
        active = 6 if art_lvl >= 18 else (5 if art_lvl >= 14 else (4 if art_lvl >= 10 else (3 if art_lvl >= 6 else 2)))
        return {
            "title": f"Infusions d'Artificier ({active} actives / {known} connues)",
            "source": f"Artificier Niv {art_lvl or 1}",
            "type": "Artisanat magique",
            "desc": f"Vous connaissez **{known}** formules d'infusions et pouvez maintenir **{active}** objets infusés simultanément."
        }

    return {
        "title": feature_name,
        "source": base_feat["source"],
        "type": base_feat["type"],
        "desc": base_feat["desc"]
    }

# ------------------------------------------------------------------------------
# 9. PROGRESSION OFFICIELLE DES APTITUDES PAR CLASSE ET SOUS-CLASSE
# ------------------------------------------------------------------------------

CLASS_LEVEL_PROGRESSION = {
    "Barbare": {
        1: ["Rage Barbare", "Défense sans armure (Barbare)"],
        2: ["Sens du Danger (Danger Sense)", "Attaque Téméraire (Reckless Attack)"],
        5: ["Attaque Supplémentaire"],
    },
    "Barde": {
        1: ["Inspiration Bardique"],
        2: ["Touche-à-tout (Jack of all Trades)", "Chant de Repos"],
        3: ["Expertise"],
        5: ["Source d'Inspiration"],
    },
    "Clerc": {
        2: ["Canalisation d'Énergie Divine"],
        5: ["Destruction des Morts-Vivants"],
    },
    "Druide": {
        2: ["Forme Sauvage (Wild Shape)"],
    },
    "Ensorceleur": {
        3: ["Métamagie & Points de Sorcellerie"],
    },
    "Guerrier": {
        1: ["Second Souffle (Second Wind)", "Style de Combat"],
        2: ["Sursaut d'Activité (Action Surge)"],
        5: ["Attaque Supplémentaire"],
        9: ["Indomptable"],
    },
    "Magicien": {
        1: ["Restauration Arcanique (Arcane Recovery)"],
    },
    "Moine": {
        2: ["Points de Ki & Arts Martiaux"],
        3: ["Parade de Projectiles"],
        4: ["Chute Ralentie"],
        5: ["Attaque Supplémentaire", "Frappe Étourdissante"],
        7: ["Dérobade (Evasion)"],
    },
    "Occultiste": {
        1: ["Magie de Pacte (Pact Magic)"],
        2: ["Invocations Occultes"],
        3: ["Don du Pacte"],
    },
    "Paladin": {
        1: ["Imposition des Mains (Lay on Hands)"],
        2: ["Style de Combat", "Châtiment Divin (Divine Smite)"],
        3: ["Canalisation d'Énergie Divine"],
        5: ["Attaque Supplémentaire"],
        6: ["Aura de Protection"],
    },
    "Rôdeur": {
        1: ["Ennemi Juré (Favored Enemy)", "Explorateur-Né"],
        2: ["Style de Combat"],
        3: ["Vigilance Primitive (Primeval Awareness)"],
        5: ["Attaque Supplémentaire"],
        8: ["Foulée Terrestre"],
    },
    "Roublard": {
        1: ["Attaque Sournoise (Sneak Attack)", "Jargon des Voleurs", "Expertise"],
        2: ["Ruse (Cunning Action)"],
        5: ["Échappatoire (Uncanny Dodge)"],
        7: ["Dérobade (Evasion)"],
        11: ["Talent Fiable"],
    },
    "Artificier": {
        1: ["Bricolage Magique"],
        2: ["Infusions d'Artificier"],
        3: ["Outilleur Polyvalent"],
        7: ["Trait de Génie"],
    }
}

SUBCLASS_LEVEL_PROGRESSION = {
    # Rôdeur
    "Tueur de Monstres": {
        3: ["Sens du Chasseur (Hunter's Sense)", "Proie du Tueur (Slayer's Prey)"],
    },
    # Roublard
    "Voleur": {
        3: ["Mains Lestes (Fast Hands)", "Cambrioleur (Second-Story Work)"],
    },
    "Assassin": {
        3: ["Assassinat (Avantage & Critique surprise)"],
    },
    # Guerrier
    "Champion": {
        3: ["Critique Amélioré (19-20)"],
    },
    "Maître de Guerre": {
        3: ["Supériorité Martiale"],
    },
    # Barbare
    "Berserker": {
        3: ["Frénésie"],
    },
    "Guerrier Totémique": {
        3: ["Esprit Totémique (Ours, Aigle ou Loup)"],
    }
}

def sync_character_features(classes: dict, subclasses: dict, current_features: list) -> tuple[list, list]:
    """
    Synchronise les aptitudes officielles débloquées selon les niveaux et sous-classes du personnage.
    Retourne (liste_mise_à_jour, liste_nouvelles_aptitudes).
    """
    updated = list(current_features)
    added = []

    for cls_name, lvl in classes.items():
        # Aptitudes de classe
        prog = CLASS_LEVEL_PROGRESSION.get(cls_name, {})
        for req_lvl, feats in prog.items():
            if lvl >= req_lvl:
                for f in feats:
                    if f and not any(f.lower() in ex.lower() or ex.lower() in f.lower() for ex in updated):
                        updated.append(f)
                        added.append(f)

        # Aptitudes de sous-classe (uniquement si niveau >= 3)
        if lvl >= 3:
            sub_name = subclasses.get(cls_name, "")
            if sub_name:
                for sub_key, sub_prog in SUBCLASS_LEVEL_PROGRESSION.items():
                    if sub_key.lower() in sub_name.lower():
                        for req_lvl, feats in sub_prog.items():
                            if lvl >= req_lvl:
                                for f in feats:
                                    if f and not any(f.lower() in ex.lower() or ex.lower() in f.lower() for ex in updated):
                                        updated.append(f)
                                        added.append(f)
                        break

    return updated, added


