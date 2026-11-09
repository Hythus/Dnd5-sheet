"""
Application Web D&D 5e - Fiche de Personnage Interactive & Grimoire de Maître
=============================================================================
Auteur : Hythus / Antigravity
Framework : Streamlit (Python 3.13)
Style : Parchemin médiéval fantastique, ornementations dorées, adaptabilité dynamique par classe.

Fonctionnalités majeures :
- Gestion complète des 13 classes officielles françaises (dont Occultiste, Artificier...)
- Sous-classes avec extensions (PHB, Xanathar, Tasha, Wildemount...)
- Aptitudes de classe interactives & cliquables avec descriptif complet officiel
- Gestion fine des points de vie (PV actuels, PV max, PV temporaires avec absorption)
- Jets de sauvegarde contre la mort (Death Saves) interactifs
- Repos Long (remise à zéro des PV, emplacements de sorts, moitié des dés de vie)
- Repos Court (dépense de dés de vie avec jet + CON, recharge Magie de Pacte / capacités)
- Suivi dynamique des emplacements de sorts consommés / disponibles
- Compendium / Base de données intégrée pour armes, armures, sorts et aptitudes
- Import PDF intelligent (AcroForm + analyse heuristique) & Import/Export JSON
"""

import streamlit as st
import pandas as pd
import random
import json
import math
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

import dnd_database as db
from dnd_importer import parse_pdf_character, parse_json_character

# ==============================================================================
# 1. CONFIGURATION DE LA PAGE STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Chronique du Héros - Fiche D&D 5e",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. MODÈLES DE DONNÉES & RÈGLES OFFICIELLES D&D 5e
# ==============================================================================

class Ability(str, Enum):
    STR = "Force"
    DEX = "Dextérité"
    CON = "Constitution"
    INT = "Intelligence"
    WIS = "Sagesse"
    CHA = "Charisme"

class ArmorType(str, Enum):
    LIGHT = "Légère"
    MEDIUM = "Intermédiaire"
    HEAVY = "Lourde"
    SHIELD = "Bouclier"
    NONE = "Aucune"

SKILL_ABILITY_MAP = {
    "Acrobaties": Ability.DEX,
    "Arcanes": Ability.INT,
    "Athlétisme": Ability.STR,
    "Discrétion": Ability.DEX,
    "Dressage": Ability.WIS,
    "Escamotage": Ability.DEX,
    "Histoire": Ability.INT,
    "Intimidation": Ability.CHA,
    "Intuition": Ability.WIS,
    "Investigation": Ability.INT,
    "Médecine": Ability.WIS,
    "Nature": Ability.INT,
    "Perception": Ability.WIS,
    "Persuasion": Ability.CHA,
    "Religion": Ability.INT,
    "Représentation": Ability.CHA,
    "Survie": Ability.WIS,
    "Tromperie": Ability.CHA,
}

@dataclass
class Weapon:
    name: str
    damage_dice: str
    damage_type: str
    is_finesse: bool = False
    is_ranged: bool = False
    magic_bonus: int = 0
    attack_bonus_override: Optional[int] = None
    extra_damage_desc: str = ""

@dataclass
class Armor:
    name: str
    armor_type: ArmorType
    base_ac: int
    max_dex_bonus: Optional[int] = None
    magic_bonus: int = 0

@dataclass
class Spell:
    name: str
    level: int
    school: str = "Évocation"
    casting_time: str = "1 action"
    range_area: str = "18 m"
    duration: str = "Instantanée"
    concentration: bool = False
    description: str = ""

@dataclass
class CharacterSheet:
    name: str
    race: str
    background: str
    alignment: str
    raw_abilities: Dict[Ability, int]
    classes: Dict[str, int] = field(default_factory=dict)
    subclasses: Dict[str, str] = field(default_factory=dict)
    saving_throw_proficiencies: List[Ability] = field(default_factory=list)
    skill_proficiencies: List[str] = field(default_factory=list)
    skill_expertises: List[str] = field(default_factory=list)
    equipped_armor: Optional[Armor] = None
    equipped_shield: Optional[Armor] = None
    weapons: List[Weapon] = field(default_factory=list)
    known_spells: List[Spell] = field(default_factory=list)
    traits_and_features: List[str] = field(default_factory=list)
    
    # Points de vie & survie
    pv_max: int = 52
    pv_current: int = 52
    pv_temp: int = 0
    speed: int = 9
    
    # Gestion des ressources (Consommables)
    death_saves: Dict[str, int] = field(default_factory=lambda: {"successes": 0, "failures": 0})
    spell_slots_used: Dict[int, int] = field(default_factory=dict)
    pact_slots_used: int = 0
    hit_dice_used: Dict[str, int] = field(default_factory=dict)

    @property
    def total_level(self) -> int:
        return sum(self.classes.values()) if self.classes else 1

    @property
    def proficiency_bonus(self) -> int:
        return math.floor((self.total_level - 1) / 4) + 2

    def get_ability_modifier(self, ability: Ability) -> int:
        score = self.raw_abilities.get(ability, 10)
        return math.floor((score - 10) / 2)

    def get_saving_throw(self, ability: Ability) -> int:
        mod = self.get_ability_modifier(ability)
        if ability in self.saving_throw_proficiencies:
            mod += self.proficiency_bonus
        return mod

    def get_skill_modifier(self, skill_name: str) -> int:
        ability = SKILL_ABILITY_MAP.get(skill_name)
        if not ability:
            return 0
        mod = self.get_ability_modifier(ability)
        if skill_name in self.skill_expertises:
            mod += self.proficiency_bonus * 2
        elif skill_name in self.skill_proficiencies:
            mod += self.proficiency_bonus
        return mod

    @property
    def passive_perception(self) -> int:
        return 10 + self.get_skill_modifier("Perception")

    @property
    def armor_class(self) -> int:
        dex_mod = self.get_ability_modifier(Ability.DEX)
        if not self.equipped_armor or self.equipped_armor.armor_type == ArmorType.NONE:
            ac = 10 + dex_mod
        elif self.equipped_armor.armor_type == ArmorType.LIGHT:
            ac = self.equipped_armor.base_ac + dex_mod + self.equipped_armor.magic_bonus
        elif self.equipped_armor.armor_type == ArmorType.MEDIUM:
            allowed_dex = min(dex_mod, 2) if self.equipped_armor.max_dex_bonus is None else min(dex_mod, self.equipped_armor.max_dex_bonus)
            ac = self.equipped_armor.base_ac + allowed_dex + self.equipped_armor.magic_bonus
        elif self.equipped_armor.armor_type == ArmorType.HEAVY:
            ac = self.equipped_armor.base_ac + self.equipped_armor.magic_bonus
        else:
            ac = 10 + dex_mod

        if self.equipped_shield and self.equipped_shield.armor_type == ArmorType.SHIELD:
            ac += self.equipped_shield.base_ac + self.equipped_shield.magic_bonus
        return ac

    def calculate_weapon_attack(self, weapon: Weapon) -> tuple[int, str]:
        dex_mod = self.get_ability_modifier(Ability.DEX)
        str_mod = self.get_ability_modifier(Ability.STR)
        if weapon.is_ranged:
            stat_mod = dex_mod
        elif weapon.is_finesse:
            stat_mod = max(dex_mod, str_mod)
        else:
            stat_mod = str_mod

        attack_bonus = stat_mod + self.proficiency_bonus + weapon.magic_bonus
        if weapon.attack_bonus_override is not None:
            attack_bonus += weapon.attack_bonus_override

        damage_bonus = stat_mod + weapon.magic_bonus
        sign = f"+{damage_bonus}" if damage_bonus >= 0 else f"{damage_bonus}"
        dmg_formula = f"{weapon.damage_dice}{sign} {weapon.damage_type}"
        if weapon.extra_damage_desc:
            dmg_formula += f" ({weapon.extra_damage_desc})"
        return attack_bonus, dmg_formula

    def to_dict(self) -> Dict[str, Any]:
        """Convertit la fiche complète en dictionnaire sérialisable JSON."""
        return {
            "name": self.name,
            "race": self.race,
            "background": self.background,
            "alignment": self.alignment,
            "raw_abilities": {ab.name: val for ab, val in self.raw_abilities.items()},
            "classes": self.classes,
            "subclasses": self.subclasses,
            "saving_throw_proficiencies": [ab.name for ab in self.saving_throw_proficiencies],
            "skill_proficiencies": self.skill_proficiencies,
            "skill_expertises": self.skill_expertises,
            "pv_max": self.pv_max,
            "pv_current": self.pv_current,
            "pv_temp": self.pv_temp,
            "speed": self.speed,
            "death_saves": self.death_saves,
            "spell_slots_used": {str(k): v for k, v in self.spell_slots_used.items()},
            "pact_slots_used": self.pact_slots_used,
            "hit_dice_used": self.hit_dice_used,
            "traits_and_features": self.traits_and_features,
            "equipped_armor": {
                "name": self.equipped_armor.name,
                "armor_type": self.equipped_armor.armor_type.value,
                "base_ac": self.equipped_armor.base_ac,
                "magic_bonus": self.equipped_armor.magic_bonus,
            } if self.equipped_armor else None,
            "equipped_shield": {
                "name": self.equipped_shield.name,
                "base_ac": self.equipped_shield.base_ac,
            } if self.equipped_shield else None,
            "weapons": [asdict(w) for w in self.weapons],
            "known_spells": [asdict(s) for s in self.known_spells],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CharacterSheet":
        """Reconstruit un objet CharacterSheet à partir d'un dictionnaire sérialisé."""
        abilities = {}
        for k, v in data.get("raw_abilities", {}).items():
            try:
                abilities[Ability[k]] = int(v)
            except KeyError:
                pass
        for ab in Ability:
            if ab not in abilities:
                abilities[ab] = 10

        saving_throws = []
        for ab_code in data.get("saving_throw_proficiencies", []):
            try:
                saving_throws.append(Ability[ab_code])
            except KeyError:
                pass

        weapons = [
            Weapon(
                name=w.get("name", "Arme"),
                damage_dice=w.get("damage_dice", "1d6"),
                damage_type=w.get("damage_type", "tranchant"),
                is_finesse=w.get("is_finesse", False),
                is_ranged=w.get("is_ranged", False),
                magic_bonus=w.get("magic_bonus", 0),
                extra_damage_desc=w.get("extra_damage_desc", "")
            )
            for w in data.get("weapons", [])
        ]

        spells = [
            Spell(
                name=s.get("name", "Sort"),
                level=int(s.get("level", 0)),
                school=s.get("school", "Évocation"),
                casting_time=s.get("casting_time", "1 action"),
                range_area=s.get("range_area", "18 m"),
                duration=s.get("duration", "Instantanée"),
                concentration=s.get("concentration", False),
                description=s.get("description", "")
            )
            for s in data.get("known_spells", [])
        ]

        armor_data = data.get("equipped_armor")
        equipped_armor = None
        if armor_data:
            a_type = ArmorType.LIGHT
            for t in ArmorType:
                if t.value == armor_data.get("armor_type"):
                    a_type = t
                    break
            equipped_armor = Armor(
                name=armor_data.get("name", "Armure"),
                armor_type=a_type,
                base_ac=armor_data.get("base_ac", 11),
                magic_bonus=armor_data.get("magic_bonus", 0)
            )

        shield_data = data.get("equipped_shield")
        equipped_shield = Armor(name="Bouclier", armor_type=ArmorType.SHIELD, base_ac=2) if shield_data else None

        # Conversion emplacements de sorts
        slots_used = {}
        for k, v in data.get("spell_slots_used", {}).items():
            try:
                slots_used[int(k)] = int(v)
            except ValueError:
                pass

        return cls(
            name=data.get("name", "Héros Sans Nom"),
            race=data.get("race", "Humain"),
            background=data.get("background", "Aventurier"),
            alignment=data.get("alignment", "Neutre"),
            raw_abilities=abilities,
            classes=data.get("classes", {"Guerrier": 1}),
            subclasses=data.get("subclasses", {}),
            saving_throw_proficiencies=saving_throws,
            skill_proficiencies=data.get("skill_proficiencies", []),
            skill_expertises=data.get("skill_expertises", []),
            equipped_armor=equipped_armor,
            equipped_shield=equipped_shield,
            weapons=weapons,
            known_spells=spells,
            traits_and_features=data.get("traits_and_features", []),
            pv_max=int(data.get("pv_max", 50)),
            pv_current=int(data.get("pv_current", 50)),
            pv_temp=int(data.get("pv_temp", 0)),
            speed=int(data.get("speed", 9)),
            death_saves=data.get("death_saves", {"successes": 0, "failures": 0}),
            spell_slots_used=slots_used,
            pact_slots_used=int(data.get("pact_slots_used", 0)),
            hit_dice_used=data.get("hit_dice_used", {})
        )

# ==============================================================================
# 3. INITIALISATION DU PERSONNAGE PAR DÉFAUT (HYTHUS)
# ==============================================================================

def get_default_character() -> CharacterSheet:
    char = CharacterSheet(
        name="Hythus Feuille d'Argent",
        race="Haut elfe",
        background="Grand Voyageur",
        alignment="Chaotique Neutre",
        raw_abilities={
            Ability.STR: 15,
            Ability.DEX: 17,
            Ability.CON: 12,
            Ability.INT: 14,
            Ability.WIS: 18,
            Ability.CHA: 11,
        },
        classes={"Rôdeur": 5, "Roublard": 2},
        # Rôdeur Niv 5 >= 3 (Sous-classe débloquée). Roublard Niv 2 < 3 (Sous-classe bloquée jusqu'au niveau 3).
        subclasses={"Rôdeur": "Tueur de Monstres (XGtE)"},
        saving_throw_proficiencies=[Ability.STR, Ability.DEX],
        skill_proficiencies=[
            "Acrobaties", "Athlétisme", "Discrétion", "Histoire",
            "Intuition", "Investigation", "Nature", "Perception", "Survie"
        ],
        skill_expertises=["Discrétion", "Perception"],
        traits_and_features=[
            "Ennemi Juré (Favored Enemy)",
            "Vigilance Primitive (Primeval Awareness)",
            "Sens du Chasseur (Hunter's Sense)",
            "Proie du Tueur (Slayer's Prey)",
            "Attaque Sournoise (Sneak Attack)",
            "Ruse (Cunning Action)",
            "Transe & Ascendance Féérique",
            "Vision dans le Noir (18m)"
        ],
        pv_max=52,
        pv_current=52,
        pv_temp=0,
        speed=9
    )
    char.equipped_armor = Armor(
        name="Armure de cuir clouté",
        armor_type=ArmorType.LIGHT,
        base_ac=12,
        magic_bonus=0,
    )
    char.weapons = [
        Weapon(name="Arc long +1", damage_dice="1d8", damage_type="perforant", is_ranged=True, magic_bonus=1),
        Weapon(name="Cimeterre", damage_dice="1d6", damage_type="tranchant", is_finesse=True),
        Weapon(name="Coutille vicieuse", damage_dice="1d10", damage_type="tranchant", is_finesse=False, extra_damage_desc="+7 si critique"),
    ]
    char.known_spells = [
        Spell(name="Marque du Chasseur", level=1, casting_time="1 action bonus", duration="1 heure", concentration=True, description="+1d6 dégâts sur chaque frappe contre la cible et avantage pour la pister."),
        Spell(name="Baie nourricière (Goodberry)", level=1, casting_time="1 action", duration="24 heures", description="Crée 10 baies restaurant 1 PV chacune."),
        Spell(name="Grêle d'Épines", level=1, casting_time="1 action bonus", concentration=True, description="Explosion d'épines sur la prochaine attaque à distance (1d10 perforant)."),
        Spell(name="Esprit Guérisseur (Healing Spirit)", level=2, casting_time="1 action bonus", concentration=True, duration="1 min", description="Invoque un esprit qui soigne 1d6 PV par passage."),
        Spell(name="Zone de vérité", level=2, casting_time="1 action", duration="10 min", description="Les créatures ne peuvent proférer de mensonges délibérés."),
    ]
    return char

if "char" not in st.session_state:
    st.session_state.char = get_default_character()

char: CharacterSheet = st.session_state.char

# Thème actif selon la classe principale
primary_class = max(char.classes.items(), key=lambda x: x[1])[0] if char.classes else "Rôdeur"
class_meta = db.CLASSES_DND.get(primary_class, db.CLASSES_DND["Rôdeur"])
theme = class_meta["theme"]
theme_icon = class_meta["icon"]

# ==============================================================================
# 4. INJECTION CSS - THÈME GRIMOIRE MÉDIÉVAL FANTASTIQUE D&D
# ==============================================================================

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700&family=Cinzel:wght@600;700&family=Alegreya:ital,wght@0,400;0,700;1,400&display=swap');

    .stApp {{
        background: radial-gradient(circle at 50% 10%, #202328 0%, #131518 100%);
        color: #e8dcc6;
        font-family: 'Alegreya', Georgia, serif;
        font-size: 1.08rem;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #17191d !important;
        border-right: 2px solid {theme['primary']};
        box-shadow: 4px 0px 20px rgba(0,0,0,0.7);
    }}

    h1, h2, h3, h4 {{
        font-family: 'Cinzel', serif !important;
        color: {theme['accent']} !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
        letter-spacing: 0.8px;
    }}

    /* Cadre héroïque façon parchemin officiel */
    .hero-banner {{
        background: linear-gradient(135deg, rgba(32,36,42,0.95), rgba(18,20,24,0.95));
        border: 2px solid {theme['primary']};
        border-radius: 8px;
        padding: 22px 26px;
        box-shadow: 0 4px 25px rgba(0,0,0,0.6);
        margin-bottom: 22px;
    }}
    .hero-title {{
        font-family: 'Cinzel Decorative', serif;
        font-size: 2.3rem;
        color: {theme['accent']};
        margin: 0;
    }}
    .hero-sub {{
        color: #b3a693;
        font-size: 1.15rem;
        font-style: italic;
    }}

    /* Blasons de caractéristiques (FOR, DEX, CON...) */
    .stat-badge {{
        background: linear-gradient(180deg, #282c33 0%, #191c20 100%);
        border: 2px solid {theme['secondary']};
        border-radius: 8px;
        text-align: center;
        padding: 10px 4px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .stat-badge:hover {{
        transform: translateY(-3px);
        border-color: {theme['accent']};
    }}
    .stat-name {{
        font-family: 'Cinzel', serif;
        font-size: 0.82rem;
        color: #d1c5b0;
        text-transform: uppercase;
        font-weight: 700;
    }}
    .stat-mod {{
        font-family: 'Cinzel', serif;
        font-size: 1.85rem;
        font-weight: 700;
        color: {theme['accent']};
        line-height: 1.15;
    }}
    .stat-score {{
        font-size: 0.9rem;
        color: #8c8273;
        border-top: 1px solid rgba(255,255,255,0.1);
        display: inline-block;
        padding-top: 2px;
        width: 60%;
    }}

    /* Cartes de métriques clés */
    .metric-shield {{
        background: rgba(28, 31, 36, 0.92);
        border: 1px solid {theme['primary']};
        border-radius: 6px;
        padding: 12px 8px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    }}
    .metric-value {{
        font-family: 'Cinzel', serif;
        font-size: 1.8rem;
        color: {theme['accent']};
        font-weight: bold;
    }}
    .metric-label {{
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #baa992;
    }}

    /* Boîte de gestion des points de vie */
    .hp-container {{
        background: rgba(22, 25, 30, 0.95);
        border: 2px solid {theme['primary']};
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 20px;
    }}

    /* Cartes d'armes et de sorts */
    .card-combat {{
        background: #1c1f24;
        border-left: 4px solid {theme['primary']};
        border-radius: 4px;
        padding: 12px 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }}

    /* Pastilles d'emplacements de sorts */
    .slot-pill {{
        display: inline-block;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-right: 4px;
    }}
    .slot-available {{
        background-color: #2ecc71;
        box-shadow: 0 0 6px #2ecc71;
    }}
    .slot-used {{
        background-color: #555;
        border: 1px solid #777;
    }}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 5. SIDEBAR : LE GRIMOIRE D'ÉDITION, IMPORT & EXPORT
# ==============================================================================

with st.sidebar:
    st.markdown(f"### {theme_icon} Grimoire du Héros")
    st.caption(f"Classe majeure active : **{primary_class}**")

    tab_bio, tab_stats, tab_import = st.tabs(["Identité", "Caractéristiques", "Fichiers & Import"])

    with tab_bio:
        st.subheader("État Civil")
        char.name = st.text_input("Nom du Héros", value=char.name)
        char.race = st.text_input("Peuple / Race", value=char.race)
        char.background = st.text_input("Historique", value=char.background)
        
        aligns = ["Loyal Bon", "Neutre Bon", "Chaotique Bon", "Loyal Neutre", "Neutre Pur", "Chaotique Neutre", "Loyal Mauvais", "Neutre Mauvais", "Chaotique Mauvais"]
        char.alignment = st.selectbox("Alignement", aligns, index=aligns.index(char.alignment) if char.alignment in aligns else 5)

        st.divider()
        st.subheader("Classes & Sous-Classes")
        level_changed = False
        for cls_name in list(char.classes.keys()):
            col_c1, col_c2, col_c3 = st.columns([3, 2, 1])
            with col_c1:
                st.write(f"**{cls_name}**")
            with col_c2:
                old_lvl = char.classes[cls_name]
                new_lvl = st.number_input(f"Niv {cls_name}", min_value=1, max_value=20, value=old_lvl, key=f"lvl_{cls_name}", label_visibility="collapsed")
                if new_lvl != old_lvl:
                    char.classes[cls_name] = new_lvl
                    level_changed = True
            with col_c3:
                if len(char.classes) > 1:
                    if st.button("❌", key=f"del_{cls_name}", help=f"Retirer la classe {cls_name}"):
                        del char.classes[cls_name]
                        if cls_name in char.subclasses:
                            del char.subclasses[cls_name]
                        level_changed = True
                        st.rerun()

            # Règle officielle D&D 5e : Sous-classe débloquée au niveau 3
            cls_level = char.classes.get(cls_name, 1)
            available_subs = db.CLASSES_DND.get(cls_name, {}).get("subclasses", [])
            if cls_level < 3:
                st.info(f"🔒 **Sous-classe {cls_name}** : Accessible au **Niveau 3** (Actuel: Niv {cls_level})")
                if cls_name in char.subclasses:
                    del char.subclasses[cls_name]
            else:
                current_sub = char.subclasses.get(cls_name, available_subs[0] if available_subs else "Aucune")
                sub_idx = available_subs.index(current_sub) if current_sub in available_subs else 0
                selected_sub = st.selectbox(f"Sous-classe ({cls_name})", available_subs, index=sub_idx, key=f"sub_{cls_name}")
                if selected_sub != current_sub:
                    char.subclasses[cls_name] = selected_sub
                    level_changed = True

        # Synchronisation automatique des aptitudes lors de gains de niveau ou changement de sous-classe
        if level_changed:
            updated_feats, added_feats = db.sync_character_features(char.classes, char.subclasses, char.traits_and_features)
            char.traits_and_features = updated_feats
            if added_feats:
                st.session_state["toast_msg"] = f"🎉 Niveau supérieur ! Nouvelles aptitudes débloquées : {', '.join(added_feats)}"
            st.rerun()

        # Affichage de la notification si présente
        if "toast_msg" in st.session_state:
            st.toast(st.session_state.pop("toast_msg"))

        # Ajouter une nouvelle classe
        new_classes_avail = [c for c in db.CLASSES_DND.keys() if c not in char.classes]
        if new_classes_avail:
            new_cls = st.selectbox("Ajouter une classe", ["-- Sélectionner --"] + new_classes_avail)
            if new_cls != "-- Sélectionner --":
                if st.button(f"Emprunter la voie du {new_cls}"):
                    char.classes[new_cls] = 1
                    # Au niveau 1, pas de sous-classe (débloquée au niveau 3)
                    if new_cls in char.subclasses:
                        del char.subclasses[new_cls]
                    updated_feats, _ = db.sync_character_features(char.classes, char.subclasses, char.traits_and_features)
                    char.traits_and_features = updated_feats
                    st.rerun()

        st.write("")
        if st.button("🔄 Réinitialiser la fiche (Défaut Hythus)", use_container_width=True):
            st.session_state.char = get_default_character()
            st.rerun()

    with tab_stats:
        st.subheader("Caractéristiques Brutes")
        for ab in Ability:
            char.raw_abilities[ab] = st.slider(
                f"{ab.value} ({ab.name})",
                min_value=1,
                max_value=30,
                value=char.raw_abilities.get(ab, 10),
                key=f"slider_{ab.name}"
            )
        st.divider()
        st.subheader("Vitesse & Équipement")
        char.speed = st.number_input("Vitesse (mètres)", min_value=1, max_value=30, value=char.speed)
        
        # Armure équipée
        armors_keys = list(db.ARMORS_DB.keys())
        current_armor_name = char.equipped_armor.name if char.equipped_armor else armors_keys[0]
        arm_idx = armors_keys.index(current_armor_name) if current_armor_name in armors_keys else 0
        chosen_armor_name = st.selectbox("Armure équipée", armors_keys, index=arm_idx)
        arm_info = db.ARMORS_DB[chosen_armor_name]
        
        # Mapping ArmorType
        type_mapping = {
            "Légère": ArmorType.LIGHT,
            "Intermédiaire": ArmorType.MEDIUM,
            "Lourde": ArmorType.HEAVY,
            "Aucune": ArmorType.NONE
        }
        char.equipped_armor = Armor(
            name=chosen_armor_name,
            armor_type=type_mapping.get(arm_info["type"], ArmorType.NONE),
            base_ac=arm_info["base_ac"],
            max_dex_bonus=arm_info["max_dex"]
        )

        porte_bouclier = st.checkbox("Porter un Bouclier (+2 CA)", value=(char.equipped_shield is not None))
        char.equipped_shield = Armor(name="Bouclier", armor_type=ArmorType.SHIELD, base_ac=2) if porte_bouclier else None

    with tab_import:
        st.subheader("📜 Importer une Feuille")
        st.caption("Chargez un PDF (feuille D&D officielle) ou un fichier JSON sauvegardé.")
        
        uploaded_file = st.file_uploader("Fichier PDF ou JSON", type=["pdf", "json"])
        if uploaded_file is not None:
            bytes_data = uploaded_file.read()
            if uploaded_file.name.endswith(".json"):
                try:
                    data = parse_json_character(bytes_data)
                    st.success("Fichier JSON valide !")
                    if st.button("Restaurer ce Héros depuis JSON"):
                        st.session_state.char = CharacterSheet.from_dict(data)
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur de lecture du JSON : {e}")
            elif uploaded_file.name.endswith(".pdf"):
                try:
                    extracted_data, summary = parse_pdf_character(bytes_data)
                    st.info(summary)
                    if st.button("Appliquer les données du PDF à la fiche"):
                        char.name = extracted_data["name"]
                        char.race = extracted_data["race"]
                        if extracted_data.get("classes"):
                            char.classes = extracted_data["classes"]
                        for ab_code, val in extracted_data.get("raw_abilities", {}).items():
                            try:
                                char.raw_abilities[Ability[ab_code]] = val
                            except KeyError:
                                pass
                        char.pv_max = extracted_data["pv_max"]
                        char.pv_current = extracted_data["pv_current"]
                        char.speed = extracted_data["speed"]
                        st.success("Données du PDF injectées avec succès !")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur d'analyse du PDF : {e}")

        st.divider()
        st.subheader("💾 Exporter la Fiche")
        json_export = json.dumps(char.to_dict(), indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Télécharger la Fiche (JSON)",
            data=json_export,
            file_name=f"{char.name.replace(' ', '_')}_DnD5e.json",
            mime="application/json"
        )

# ==============================================================================
# 6. BANNIÈRE PRINCIPALE HÉROÏQUE
# ==============================================================================

class_items = []
for cls, lvl in char.classes.items():
    if lvl >= 3 and cls in char.subclasses and char.subclasses[cls]:
        class_items.append(f"{cls} ({char.subclasses[cls]}) Niv {lvl}")
    else:
        class_items.append(f"{cls} Niv {lvl}")
class_summary_str = " / ".join(class_items)
st.markdown(f"""
<div class="hero-banner">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 class="hero-title">{theme_icon} {char.name}</h1>
            <div class="hero-sub">{char.race} • {class_summary_str} • {char.alignment} (Niveau Total {char.total_level})</div>
        </div>
        <div style="text-align: right; margin-top: 10px;">
            <span style="font-size: 1.1rem; color: {theme['accent']}; font-style: italic;">{class_meta.get('theme', {}).get('quote', '« Que les dés soient favorables à ton destin. »')}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# 7. LES 6 CARACTÉRISTIQUES D&D (BADGES BLASONS)
# ==============================================================================

cols_stats = st.columns(6)
for i, ab in enumerate(Ability):
    score = char.raw_abilities.get(ab, 10)
    mod = char.get_ability_modifier(ab)
    sign = f"+{mod}" if mod >= 0 else f"{mod}"
    with cols_stats[i]:
        st.markdown(f"""
        <div class="stat-badge">
            <div class="stat-name">{ab.value[:4]}</div>
            <div class="stat-mod">{sign}</div>
            <div class="stat-score">{score}</div>
        </div>
        """, unsafe_allow_html=True)

st.write("")

# ==============================================================================
# 8. STATISTIQUES COMBAT & GESTION DES POINTS DE VIE, REPOS & MORTS
# ==============================================================================

# Métriques rapides
col_m1, col_m2, col_m3, col_m4, col_m5, col_m6 = st.columns(6)
dex_mod = char.get_ability_modifier(Ability.DEX)
init_sign = f"+{dex_mod}" if dex_mod >= 0 else f"{dex_mod}"

with col_m1:
    st.markdown(f"""<div class="metric-shield"><div class="metric-value">🛡️ {char.armor_class}</div><div class="metric-label">Classe d'Armure</div></div>""", unsafe_allow_html=True)
with col_m2:
    st.markdown(f"""<div class="metric-shield"><div class="metric-value">⚡ {init_sign}</div><div class="metric-label">Initiative</div></div>""", unsafe_allow_html=True)
with col_m3:
    st.markdown(f"""<div class="metric-shield"><div class="metric-value">👣 {char.speed} m</div><div class="metric-label">Vitesse</div></div>""", unsafe_allow_html=True)
with col_m4:
    st.markdown(f"""<div class="metric-shield"><div class="metric-value">🎯 +{char.proficiency_bonus}</div><div class="metric-label">Bonus Maîtrise</div></div>""", unsafe_allow_html=True)
with col_m5:
    st.markdown(f"""<div class="metric-shield"><div class="metric-value">👁️ {char.passive_perception}</div><div class="metric-label">Perception Pass.</div></div>""", unsafe_allow_html=True)
with col_m6:
    pv_ratio = max(0.0, min(1.0, char.pv_current / max(1, char.pv_max)))
    pv_color = "#4caf50" if pv_ratio > 0.5 else ("#ff9800" if pv_ratio > 0.25 else "#f44336")
    temp_badge = f" (+{char.pv_temp} Temp)" if char.pv_temp > 0 else ""
    st.markdown(f"""<div class="metric-shield"><div class="metric-value" style="color: {pv_color};">❤️ {char.pv_current}/{char.pv_max}</div><div class="metric-label">PV{temp_badge}</div></div>""", unsafe_allow_html=True)

st.write("")

# Panneau Vital : PV, Dégâts, Soins, Repos Long & Court
with st.container():
    st.markdown("""<div class="hp-container">""", unsafe_allow_html=True)
    
    col_hp_actions, col_rests, col_death = st.columns([4, 4, 3])

    # 1. Action sur les PV (Dégâts / Soins / PV Temporaires)
    with col_hp_actions:
        st.markdown("#### ❤️ Gestion des Points de Vie")
        
        # Barre de progression de vie
        progress_val = max(0.0, min(1.0, char.pv_current / max(1, char.pv_max)))
        st.progress(progress_val)
        
        col_dmg, col_heal = st.columns(2)
        with col_dmg:
            dmg_amount = st.number_input("Subir Dégâts", min_value=1, max_value=200, value=5, key="input_dmg")
            if st.button("💥 Appliquer Dégâts", use_container_width=True):
                # Absorption des PV temporaires d'abord
                remaining_dmg = dmg_amount
                if char.pv_temp > 0:
                    if remaining_dmg <= char.pv_temp:
                        char.pv_temp -= remaining_dmg
                        remaining_dmg = 0
                    else:
                        remaining_dmg -= char.pv_temp
                        char.pv_temp = 0
                
                char.pv_current = max(0, char.pv_current - remaining_dmg)
                st.rerun()

        with col_heal:
            heal_amount = st.number_input("Soigner", min_value=1, max_value=200, value=5, key="input_heal")
            if st.button("✨ Appliquer Soins", use_container_width=True):
                char.pv_current = min(char.pv_max, char.pv_current + heal_amount)
                # Si on est soigné au-dessus de 0, réinitialise les jets de mort
                if char.pv_current > 0:
                    char.death_saves = {"successes": 0, "failures": 0}
                st.rerun()

        # PV Temporaires
        col_t1, col_t2 = st.columns([3, 2])
        with col_t1:
            temp_in = st.number_input("Ajouter PV Temporaires", min_value=1, max_value=100, value=5, key="input_temp")
        with col_t2:
            st.write("")
            st.write("")
            if st.button("🛡️ Définir Temp", use_container_width=True):
                # Règle D&D 5e : les PV temporaires ne se cumulent pas, on prend le plus haut
                char.pv_temp = max(char.pv_temp, temp_in)
                st.rerun()

    # 2. Gestion des Repos (Court & Long)
    with col_rests:
        st.markdown("#### ⛺ Repos & Récupération")
        
        # Affichage des dés de vie
        total_hit_dice = db.get_total_hit_dice(char.classes)
        hd_display = []
        for hd_type, total_cnt in total_hit_dice.items():
            used = char.hit_dice_used.get(hd_type, 0)
            avail = max(0, total_cnt - used)
            hd_display.append(f"**{hd_type}** : {avail}/{total_cnt} dispo")
        st.caption("Dés de vie : " + " | ".join(hd_display))

        # Repos Long
        if st.button("🌙 Repos Long (8 heures)", use_container_width=True):
            char.pv_current = char.pv_max
            char.pv_temp = 0
            char.death_saves = {"successes": 0, "failures": 0}
            char.spell_slots_used = {}
            char.pact_slots_used = 0
            
            # Récupère la moitié des dés de vie totaux
            total_dice_count = sum(total_hit_dice.values())
            recovered_allowance = max(1, math.ceil(total_dice_count / 2))
            
            for hd_type in char.hit_dice_used:
                used = char.hit_dice_used[hd_type]
                to_recover = min(used, recovered_allowance)
                char.hit_dice_used[hd_type] -= to_recover
                recovered_allowance -= to_recover
                if recovered_allowance <= 0:
                    break
            
            st.success("Repos long achevé ! PV restaurés au maximum, emplacements de sorts rechargés et dés de vie récupérés.")
            st.rerun()

        # Repos Court avec dépense de dés de vie
        with st.expander("⏳ Prendre un Repos Court (1 heure)"):
            con_mod = char.get_ability_modifier(Ability.CON)
            avail_dice = {}
            for hd_t, total_c in total_hit_dice.items():
                u = char.hit_dice_used.get(hd_t, 0)
                if total_c - u > 0:
                    avail_dice[hd_t] = total_c - u

            if avail_dice:
                chosen_hd = st.selectbox("Type de dé à dépenser", list(avail_dice.keys()), key="rest_hd_type")
                max_rollable = avail_dice[chosen_hd]
                num_dice = st.number_input("Nombre de dés", min_value=1, max_value=max_rollable, value=1, key="rest_hd_count")
                
                if st.button("🎲 Dépenser ces dés et récupérer des PV"):
                    sides = int(chosen_hd.replace("d", ""))
                    total_healed = 0
                    rolls = []
                    for _ in range(num_dice):
                        r = random.randint(1, sides)
                        rolls.append(r)
                        total_healed += max(0, r + con_mod)
                    
                    char.hit_dice_used[chosen_hd] = char.hit_dice_used.get(chosen_hd, 0) + num_dice
                    char.pv_current = min(char.pv_max, char.pv_current + total_healed)
                    
                    # Récupération spécifique Occultiste (Magie de Pacte)
                    if "Occultiste" in char.classes:
                        char.pact_slots_used = 0
                        st.info("👁️ Occultiste : Tous vos emplacements de Magie de Pacte ont été réinitialisés !")

                    st.success(f"Repos court : Jets de {chosen_hd} = {rolls} + {con_mod} CON. Vous récupérez **{total_healed} PV** !")
                    st.rerun()
            else:
                st.warning("Aucun dé de vie disponible pour se soigner pendant ce repos court.")
                if "Occultiste" in char.classes and st.button("Recharger la Magie de Pacte sans dés"):
                    char.pact_slots_used = 0
                    st.success("Magie de Pacte rechargée !")
                    st.rerun()

    # 3. Jets de Sauvegarde contre la mort
    with col_death:
        st.markdown("#### 💀 Sauvegardes contre la Mort")
        if char.pv_current == 0:
            st.error("⚠️ LE HÉROS EST À TERRE ET INCONSCIENT !")
        
        suc = char.death_saves.get("successes", 0)
        fai = char.death_saves.get("failures", 0)

        # Affichage visuel des succès et échecs
        st.write(f"**Succès** ({suc}/3) : {'🟢 ' * suc}{'⚪ ' * (3 - suc)}")
        st.write(f"**Échecs** ({fai}/3) : {'🔴 ' * fai}{'⚪ ' * (3 - fai)}")

        if st.button("🎲 Lancer un Jet contre la Mort", disabled=(char.pv_current > 0 or suc >= 3 or fai >= 3)):
            roll = random.randint(1, 20)
            if roll == 20:
                char.pv_current = 1
                char.death_saves = {"successes": 0, "failures": 0}
                st.balloons()
                st.success("🔥 20 NATUREL ! Le héros reprend conscience avec 1 PV !")
            elif roll >= 10:
                char.death_saves["successes"] = suc + 1
                st.success(f"Succès ({roll}) !")
            elif roll == 1:
                char.death_saves["failures"] = min(3, fai + 2)
                st.error("💀 1 NATUREL ! 2 Échecs critiques !")
            else:
                char.death_saves["failures"] = fai + 1
                st.warning(f"Échec ({roll}) !")
            st.rerun()

        if suc >= 3:
            st.info("🛡️ Stabilisé ! Le héros est inconscient mais hors de danger mortel.")
        elif fai >= 3:
            st.error("⚰️ Mort... Que son âme repose dans les Terres Extérieures.")

        if st.button("Réinitialiser les jets de mort", key="reset_death"):
            char.death_saves = {"successes": 0, "failures": 0}
            st.rerun()

    st.markdown("""</div>""", unsafe_allow_html=True)

st.divider()

# ==============================================================================
# 9. CORPS PRINCIPAL : ONGLETS DÉDIÉS EN PLEINE LARGEUR
# ==============================================================================

tab_arsenal, tab_grimoire, tab_traits, tab_skills = st.tabs([
    "⚔️ Arsenal & Combat",
    "🔮 Grimoire & Sorts",
    "✨ Aptitudes de Classe & Dons",
    "📜 Compétences & Sauvegardes"
])

# ------------------------------------------------------------------------------
# ONGLET 1 : ARSENAL & COMBAT
# ------------------------------------------------------------------------------
with tab_arsenal:
    st.markdown("### ⚔️ Arsenal & Attaques Équipées")
    
    if char.weapons:
        for idx_w, w in enumerate(char.weapons):
            att_bonus, dmg_formula = char.calculate_weapon_attack(w)
            att_str = f"+{att_bonus}" if att_bonus >= 0 else f"{att_bonus}"
            
            col_w_card, col_w_del = st.columns([8, 1])
            with col_w_card:
                st.markdown(f"""
                <div class="card-combat">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.2rem; font-weight: bold; color: #fff;">{w.name}</span>
                        <span style="background: {theme['primary']}; padding: 4px 10px; border-radius: 4px; font-weight: bold; color: #fff;">Toucher : {att_str}</span>
                    </div>
                    <div style="color: #c9baa2; margin-top: 6px; font-size: 1rem;">
                        🎲 <b>Dégâts :</b> {dmg_formula} | <i>{'Distance' if w.is_ranged else ('Finesse' if w.is_finesse else 'Corps-à-corps')}</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_w_del:
                st.write("")
                if st.button("🗑️", key=f"del_w_{idx_w}", help="Retirer cette arme"):
                    char.weapons.pop(idx_w)
                    st.rerun()
    else:
        st.info("Aucune arme équipée pour le moment.")

    st.divider()
    st.markdown("#### ➕ Ajouter une Arme depuis la Base Officielle")
    col_aw1, col_aw2, col_aw3 = st.columns([3, 2, 3])
    with col_aw1:
        weapon_keys = list(db.WEAPONS_DB.keys())
        chosen_w_name = st.selectbox("Choisir l'arme de base", weapon_keys, key="add_weapon_select")
        w_data = db.WEAPONS_DB[chosen_w_name]
        st.caption(f"Dégâts : {w_data['damage']} {w_data['type']} | Finesse : {w_data['finesse']} | Distance : {w_data['ranged']}")
    with col_aw2:
        magic_mod = st.number_input("Bonus magique (+1, +2...)", min_value=0, max_value=5, value=0, key="add_w_magic")
    with col_aw3:
        custom_suffix = st.text_input("Effet spécial additionnel", value="", placeholder="ex: +1d6 feu si critique", key="add_w_desc")

    if st.button("⚔️ Équiper cette arme", use_container_width=False):
        final_name = f"{chosen_w_name} +{magic_mod}" if magic_mod > 0 else chosen_w_name
        char.weapons.append(Weapon(
            name=final_name,
            damage_dice=w_data["damage"],
            damage_type=w_data["type"],
            is_finesse=w_data["finesse"],
            is_ranged=w_data["ranged"],
            magic_bonus=magic_mod,
            extra_damage_desc=custom_suffix
        ))
        st.success(f"{final_name} ajoutée à votre arsenal !")
        st.rerun()


# ------------------------------------------------------------------------------
# ONGLET 2 : GRIMOIRE & SORTS
# ------------------------------------------------------------------------------
with tab_grimoire:
    st.markdown("### 🔮 Grimoire & Magie")

    # 1. Emplacements de sorts
    slots_max = db.calculate_spell_slots(char.classes)
    pact_slots_cnt, pact_slots_lvl = db.calculate_pact_slots(char.classes)

    st.markdown("#### 🌟 Emplacements de Sorts Disponibles")
    if slots_max or pact_slots_cnt > 0:
        if slots_max:
            for lvl, total_slots in slots_max.items():
                used_slots = char.spell_slots_used.get(lvl, 0)
                avail = max(0, total_slots - used_slots)
                
                col_sl1, col_sl2, col_sl3 = st.columns([3, 4, 3])
                with col_sl1:
                    st.write(f"**Niveau {lvl}** : `{avail} / {total_slots} disponibles`")
                with col_sl2:
                    pills = "🟢 " * avail + "🔴 " * used_slots
                    st.write(pills)
                with col_sl3:
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        if st.button("−1 Dépenser", key=f"use_slot_{lvl}", disabled=(avail <= 0)):
                            char.spell_slots_used[lvl] = used_slots + 1
                            st.rerun()
                    with c_btn2:
                        if st.button("+1 Rendre", key=f"rest_slot_{lvl}", disabled=(used_slots <= 0)):
                            char.spell_slots_used[lvl] = max(0, used_slots - 1)
                            st.rerun()

        if pact_slots_cnt > 0:
            st.divider()
            st.markdown(f"##### 👁️ Magie de Pacte (Occultiste - Niveau {pact_slots_lvl})")
            avail_pact = max(0, pact_slots_cnt - char.pact_slots_used)
            col_p1, col_p2, col_p3 = st.columns([3, 4, 3])
            with col_p1:
                st.write(f"**Slots de Pacte** : `{avail_pact} / {pact_slots_cnt} disponibles`")
            with col_p2:
                st.write("🟢 " * avail_pact + "🔴 " * char.pact_slots_used)
            with col_p3:
                p_c1, p_c2 = st.columns(2)
                with p_c1:
                    if st.button("−1 Slot Pacte", key="use_pact_slot", disabled=(avail_pact <= 0)):
                        char.pact_slots_used += 1
                        st.rerun()
                with p_c2:
                    if st.button("+1 Slot Pacte", key="rest_pact_slot", disabled=(char.pact_slots_used <= 0)):
                        char.pact_slots_used = max(0, char.pact_slots_used - 1)
                        st.rerun()
    else:
        st.info("Ce personnage ne dispose pas d'emplacements de sorts de classe.")

    st.divider()

    # 2. Sorts connus dans le grimoire
    st.markdown("#### 📖 Sorts Connus dans votre Grimoire")
    if char.known_spells:
        for s_idx, sp in enumerate(char.known_spells):
            col_sp_card, col_sp_act = st.columns([7, 3])
            
            # Détermination des niveaux d'emplacements utilisables
            available_cast_levels = []
            if sp.level > 0:
                # Niveaux d'emplacements standards disponibles
                for lvl_cand in sorted(slots_max.keys()):
                    if lvl_cand >= sp.level:
                        avail_cnt = slots_max[lvl_cand] - char.spell_slots_used.get(lvl_cand, 0)
                        available_cast_levels.append((lvl_cand, "standard", avail_cnt))
                # Magie de Pacte (Occultiste)
                if pact_slots_cnt > 0 and pact_slots_lvl >= sp.level:
                    avail_pact_cnt = pact_slots_cnt - char.pact_slots_used
                    available_cast_levels.append((pact_slots_lvl, "pacte", avail_pact_cnt))

            with col_sp_act:
                st.write("")
                selected_cast_lvl = sp.level
                selected_slot_type = "standard"
                can_cast = False

                if sp.level == 0:
                    st.caption("✨ Tour de magie (Illimité)")
                    if st.button(f"✨ Lancer {sp.name}", key=f"cast_{s_idx}", use_container_width=True):
                        st.success(f"Tour de magie {sp.name} incanté !")
                else:
                    if available_cast_levels:
                        # Sélecteur de niveau d'emplacement pour le lancer (Upcasting)
                        slot_options = []
                        for lvl_c, s_type, cnt in available_cast_levels:
                            type_label = "Pacte" if s_type == "pacte" else "Standard"
                            slot_options.append((lvl_c, s_type, f"Niveau {lvl_c} ({type_label} : {cnt} dispo)"))

                        chosen_tuple = st.selectbox(
                            "Emplacement utilisé :",
                            slot_options,
                            format_func=lambda x: x[2],
                            key=f"slot_choice_{s_idx}"
                        )
                        selected_cast_lvl = chosen_tuple[0]
                        selected_slot_type = chosen_tuple[1]
                        
                        # Vérifier s'il reste des emplacements de ce type
                        if selected_slot_type == "standard":
                            avail_slots_now = slots_max.get(selected_cast_lvl, 0) - char.spell_slots_used.get(selected_cast_lvl, 0)
                        else:
                            avail_slots_now = pact_slots_cnt - char.pact_slots_used
                        can_cast = (avail_slots_now > 0)

                        if st.button(f"✨ Lancer (Niv {selected_cast_lvl})", key=f"cast_{s_idx}", disabled=not can_cast, use_container_width=True):
                            if selected_slot_type == "standard":
                                char.spell_slots_used[selected_cast_lvl] = char.spell_slots_used.get(selected_cast_lvl, 0) + 1
                            else:
                                char.pact_slots_used += 1
                            st.success(f"Sort {sp.name} lancé avec succès avec un emplacement de Niveau {selected_cast_lvl} !")
                            st.rerun()
                    else:
                        st.caption("🔒 Aucun emplacement de niveau suffisant")

                if st.button("🗑️ Oublier ce sort", key=f"del_spell_{s_idx}", use_container_width=True):
                    char.known_spells.pop(s_idx)
                    st.rerun()

            with col_sp_card:
                # Description dynamique avec upcasting selon l'emplacement sélectionné
                dyn_desc, is_upcast = db.get_dynamic_spell_description(sp.name, selected_cast_lvl)
                conc_badge = "🧠 [Concentration]" if sp.concentration else ""
                upcast_badge = f"<span style='background: #e67e22; color: #fff; padding: 2px 6px; border-radius: 4px; font-size: 0.82rem; font-weight: bold;'>🚀 Amplifié au Niveau {selected_cast_lvl}</span>" if is_upcast else ""

                st.markdown(f"""
                <div class="card-combat">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 1.15rem; font-weight: bold; color: {theme['accent']};">{sp.name} {upcast_badge}</span>
                        <span style="font-size: 0.9rem; color: #d4af37;">Base : Niv {sp.level} • {sp.school} {conc_badge}</span>
                    </div>
                    <div style="color: #b5a895; font-size: 0.95rem; margin-top: 4px;">
                        ⏱️ <b>Incantation :</b> {sp.casting_time} | 📏 <b>Portée :</b> {sp.range_area} | ⏳ <b>Durée :</b> {sp.duration}
                    </div>
                    <div style="color: #e0d5c1; margin-top: 6px; font-size: 1.02rem; line-height: 1.45;">
                        {dyn_desc}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.info("Aucun sort dans votre grimoire pour le moment.")

    st.divider()

    # 3. Ajouter un sort depuis le catalogue
    st.markdown("#### ➕ Apprendre un Sort (Catalogue Officiel)")
    spell_keys = list(db.SPELLS_DB.keys())
    col_as1, col_as2 = st.columns([3, 1])
    with col_as1:
        chosen_sp_name = st.selectbox("Choisir un sort dans le catalogue", spell_keys, key="add_spell_select")
        sp_meta = db.SPELLS_DB[chosen_sp_name]
        st.caption(f"Niveau : {sp_meta['level']} | École : {sp_meta['school']} | Incantation : {sp_meta['time']} | Portée : {sp_meta['range']} | {sp_meta['desc']}")
    with col_as2:
        st.write("")
        st.write("")
        if st.button("📖 Ajouter au Grimoire", use_container_width=True):
            char.known_spells.append(Spell(
                name=chosen_sp_name,
                level=sp_meta["level"],
                school=sp_meta["school"],
                casting_time=sp_meta["time"],
                range_area=sp_meta["range"],
                duration="1 heure" if sp_meta.get("conc") else "Instantanée",
                concentration=sp_meta.get("conc", False),
                description=sp_meta["desc"]
            ))
            st.success(f"Sort {chosen_sp_name} appris !")
            st.rerun()


# ------------------------------------------------------------------------------
# ONGLET 3 : APTITUDES DE CLASSE & DONS
# ------------------------------------------------------------------------------
with tab_traits:
    st.markdown("### ✨ Aptitudes de Classe & Capacités Spéciales")
    st.caption("Aptitudes calculées et mises à l'échelle dynamiquement selon vos niveaux dans chaque classe.")

    col_btn_sync, col_space = st.columns([4, 6])
    with col_btn_sync:
        if st.button("🔄 Synchroniser les aptitudes selon mes niveaux et sous-classes", use_container_width=True):
            updated_f, added_f = db.sync_character_features(char.classes, char.subclasses, char.traits_and_features)
            char.traits_and_features = updated_f
            if added_f:
                st.success(f"Aptitudes synchronisées ! Nouvelles aptitudes ajoutées : {', '.join(added_f)}")
            else:
                st.info("Toutes les aptitudes officielles correspondant à vos niveaux sont déjà présentes !")
            st.rerun()

    st.write("")

    if char.traits_and_features:
        for t_idx, tr_name in enumerate(char.traits_and_features):
            # Calcul dynamique de l'aptitude selon les niveaux de classe
            feature_info = db.get_dynamic_feature_info(tr_name, char.classes)

            with st.expander(f"🌟 **{feature_info['title']}**", expanded=True):
                st.markdown(f"🏷️ **Source :** `{feature_info['source']}` | ⚡ **Type d'action :** `{feature_info['type']}`")
                st.markdown(f"""
                <div style='background: rgba(0,0,0,0.3); padding: 12px 16px; border-radius: 6px; border-left: 4px solid {theme['accent']}; font-size: 1.05rem; line-height: 1.5; color: #e8dcc6;'>
                    {feature_info['desc']}
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                if st.button("🗑️ Retirer cette aptitude", key=f"del_feat_{t_idx}"):
                    char.traits_and_features.pop(t_idx)
                    st.rerun()
    else:
        st.info("Aucune aptitude enregistrée.")

    st.divider()

    # Ajouter une aptitude
    st.markdown("#### ➕ Ajouter une Aptitude depuis le Compendium")
    col_af1, col_af2 = st.columns([3, 1])
    with col_af1:
        db_feats = list(db.FEATURES_DB.keys())
        chosen_feat = st.selectbox("Sélectionner dans le catalogue", db_feats, key="select_feature_add")
        f_info = db.FEATURES_DB[chosen_feat]
        st.caption(f"Source : {f_info['source']} | Type : {f_info['type']}")
    with col_af2:
        st.write("")
        st.write("")
        if st.button("✨ Ajouter Aptitude", key="btn_add_feat", use_container_width=True):
            if chosen_feat not in char.traits_and_features:
                char.traits_and_features.append(chosen_feat)
                st.success(f"{chosen_feat} ajoutée !")
                st.rerun()

    # Aptitude personnalisée
    with st.expander("Créer une aptitude personnalisée sur-mesure"):
        custom_f_name = st.text_input("Nom de l'aptitude")
        custom_f_source = st.text_input("Source", value="Personnalisée")
        custom_f_type = st.text_input("Type", value="Action / Spécial")
        custom_f_desc = st.text_area("Descriptif complet")
        if st.button("Enregistrer cette aptitude sur-mesure"):
            if custom_f_name:
                char.traits_and_features.append(custom_f_name)
                db.FEATURES_DB[custom_f_name] = {
                    "source": custom_f_source,
                    "type": custom_f_type,
                    "desc": custom_f_desc
                }
                st.success(f"Aptitude {custom_f_name} créée et ajoutée !")
                st.rerun()


# ------------------------------------------------------------------------------
# ONGLET 4 : COMPÉTENCES & SAUVEGARDES
# ------------------------------------------------------------------------------
with tab_skills:
    st.markdown("### 📜 Maîtrises, Compétences & Sauvegardes")
    
    col_sk_left, col_sk_right = st.columns([6, 4])

    with col_sk_left:
        st.markdown("#### 🎯 Compétences")
        data_skills = []
        for sk_name, ab in SKILL_ABILITY_MAP.items():
            mod = char.get_skill_modifier(sk_name)
            is_exp = sk_name in char.skill_expertises
            is_prof = sk_name in char.skill_proficiencies
            badge = "⭐ Expertise (x2)" if is_exp else ("✅ Maîtrisé" if is_prof else "—")
            data_skills.append({
                "Compétence": sk_name,
                "Carac": ab.name,
                "Bonus": f"+{mod}" if mod >= 0 else f"{mod}",
                "Statut": badge
            })
        df_skills = pd.DataFrame(data_skills)
        st.dataframe(df_skills, hide_index=True, use_container_width=True, height=520)

    with col_sk_right:
        st.markdown("#### 🛡️ Jets de Sauvegarde")
        for ab in Ability:
            st_mod = char.get_saving_throw(ab)
            is_prof = ab in char.saving_throw_proficiencies
            mark = "🛡️ **Maîtrisé**" if is_prof else "—"
            st_val = f"+{st_mod}" if st_mod >= 0 else f"{st_mod}"
            st.markdown(f"""
            <div style="background: rgba(0,0,0,0.25); padding: 8px 12px; border-radius: 6px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <span><b>{ab.value}</b> ({ab.name})</span>
                <span style="color: {theme['accent']}; font-weight: bold; font-size: 1.15rem;">{st_val} <small style="color: #aaa;">| {mark}</small></span>
            </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# 10. PIED DE PAGE
# ==============================================================================
st.write("")
st.write("---")
st.caption(f"Chronique du Héros D&D 5e • Conçu pour **{char.name}** • Règles officielles D&D 5e SRD & Extensions en Français")
